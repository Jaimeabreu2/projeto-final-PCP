"""Ponto de entrada da simulação do Bar dos Filósofos."""

import argparse
import random
import subprocess
import sys
import time
from pathlib import Path

from grafo import (
    ErroMatriz,
    carregar_matriz,
    criar_filosofos,
    criar_garrafas,
)
from graficos import (
    ErroGrafico,
    gerar_graficos_comparacao,
    gerar_graficos_todos,
)
from log_simulacao import LogSimulacao
from relatorio_automatico import gerar_relatorio_txt
from relatorio import (
    criar_resumo,
    exibir_comparacao,
    exibir_comparacao_geral,
    exibir_relatorio,
    salvar_comparacao,
    salvar_comparacao_geral,
    salvar_resultados_individuais,
)
from solucoes import SolucaoGarcom, SolucaoOrdenacao

# Evita que o programa espere indefinidamente caso alguma thread trave.
LIMITE_SIMULACAO = 300


class ErroSimulacao(RuntimeError):
    """Erro usado quando alguma thread não termina corretamente."""


def determinar_quantidade_ciclos(quantidade_filosofos: int) -> int:
    """Define os ciclos usados nos três casos do trabalho."""
    return 3 if quantidade_filosofos == 12 else 6


def criar_parser() -> argparse.ArgumentParser:
    """Configura os argumentos aceitos pelo terminal."""
    parser = argparse.ArgumentParser(
        description="Simula o problema do Bar dos Filósofos."
    )
    parser.add_argument(
        "arquivo",
        type=Path,
        help="caminho da matriz ou 'todos' para executar os três casos",
    )
    parser.add_argument(
        "solucao",
        nargs="?",
        default="ordenacao",
        choices=["ordenacao", "garcom", "comparar", "todas"],
        help="solução de sincronização (padrão: ordenacao)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="semente usada para repetir os sorteios da simulação",
    )
    parser.add_argument(
        "--csv",
        action="store_true",
        help="salva os resultados na pasta resultados",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="mostra os eventos das threads durante a simulação",
    )
    parser.add_argument(
        "--graficos",
        action="store_true",
        help="gera gráficos comparativos na pasta resultados",
    )
    parser.add_argument(
        "--relatorio",
        action="store_true",
        help="gera um relatório automático em formato TXT",
    )
    return parser


def executar_simulacao(
    matriz: list[list[int]],
    tipo_solucao: str,
    verbose: bool = False,
) -> dict:
    """Cria os recursos e executa uma solução sobre a matriz."""
    # Cada execução precisa de threads e locks novos.
    garrafas = criar_garrafas(matriz)
    filosofos = criar_filosofos(matriz, garrafas)

    quantidade_ciclos = determinar_quantidade_ciclos(len(filosofos))
    log = LogSimulacao(verbose)

    if tipo_solucao == "ordenacao":
        solucao = SolucaoOrdenacao()
        nome_solucao = "Ordenação de Recursos"
    else:
        solucao = SolucaoGarcom(len(filosofos))
        nome_solucao = "Garçom"

    print(f"Iniciando a simulação com {quantidade_ciclos} ciclos...")
    inicio_simulacao = time.perf_counter()

    # start inicia todas as threads; join aguarda o término de cada uma.
    for filosofo in filosofos:
        filosofo.configurar_execucao(solucao, quantidade_ciclos, log)
        filosofo.start()

    prazo_final = time.perf_counter() + LIMITE_SIMULACAO
    for filosofo in filosofos:
        tempo_restante = max(0, prazo_final - time.perf_counter())
        filosofo.join(timeout=tempo_restante)

    if any(filosofo.is_alive() for filosofo in filosofos):
        raise ErroSimulacao(
            f"possível deadlock: a execução excedeu {LIMITE_SIMULACAO} segundos."
        )

    # Exceções de uma thread são verificadas novamente na thread principal.
    for filosofo in filosofos:
        if filosofo.erro is not None:
            raise ErroSimulacao(
                f"erro na thread do filósofo {filosofo.identificador}: "
                f"{filosofo.erro}"
            ) from filosofo.erro

    tempo_total = time.perf_counter() - inicio_simulacao

    print("Simulação finalizada sem deadlock.")
    exibir_relatorio(filosofos, tempo_total, nome_solucao)

    resumo = criar_resumo(filosofos, tempo_total, nome_solucao)
    resumo["filosofos"] = filosofos
    resumo["tipo_solucao"] = tipo_solucao
    return resumo


def executar_todos_os_casos(
    seed: int | None,
    gerar_csv: bool,
    verbose: bool = False,
    gerar_graficos: bool = False,
    gerar_relatorio: bool = False,
    comando: str = "",
) -> int:
    """Executa Ordenação e Garçom nos três casos do trabalho."""
    caminhos = [
        Path("matrizes/caso1.txt"),
        Path("matrizes/caso2.txt"),
        Path("matrizes/caso3.txt"),
    ]
    resumos_gerais = []
    informacoes_casos = []
    arquivos_csv = []
    arquivos_graficos = []

    try:
        for caminho in caminhos:
            matriz = carregar_matriz(caminho)
            informacoes_casos.append(
                {
                    "caso": caminho.stem,
                    "filosofos": len(matriz),
                    "garrafas": sum(sum(linha) for linha in matriz) // 2,
                    "ciclos": determinar_quantidade_ciclos(len(matriz)),
                }
            )
            print()
            print("#" * 70)
            print(f"EXECUTANDO {caminho.stem.upper()}")
            print("#" * 70)

            for tipo in ("ordenacao", "garcom"):
                if seed is not None:
                    random.seed(seed)

                resumo = executar_simulacao(matriz, tipo, verbose)
                resumo["caso"] = caminho.stem
                resumos_gerais.append(resumo)
    except (OSError, ErroMatriz, ErroSimulacao) as erro:
        print(f"Erro: {erro}")
        return 1

    exibir_comparacao_geral(resumos_gerais)

    if gerar_csv:
        caminho_csv = salvar_comparacao_geral(resumos_gerais)
        arquivos_csv.append(caminho_csv)
        print(f"CSV geral salvo em: {caminho_csv}")

    if gerar_graficos:
        try:
            caminhos_graficos = gerar_graficos_todos(resumos_gerais)
        except ErroGrafico as erro:
            print(f"Erro: {erro}")
            return 1

        for caminho in caminhos_graficos:
            print(f"Gráfico salvo em: {caminho}")
        arquivos_graficos.extend(caminhos_graficos)

    if gerar_relatorio:
        caminho_relatorio = gerar_relatorio_txt(
            resumos_gerais,
            informacoes_casos,
            comando,
            seed,
            "relatorio_todos_os_casos.txt",
            arquivos_csv,
            arquivos_graficos,
        )
        print(f"Relatório salvo em: {caminho_relatorio}")

    return 0


def main() -> int:
    """Lê a entrada, executa a opção escolhida e informa o resultado."""
    argumentos = criar_parser().parse_args()
    comando = subprocess.list2cmdline(["python", *sys.argv])

    if str(argumentos.arquivo).lower() == "todos":
        if argumentos.seed is not None:
            print(f"Seed utilizada: {argumentos.seed}")
        return executar_todos_os_casos(
            argumentos.seed,
            argumentos.csv,
            argumentos.verbose,
            argumentos.graficos,
            argumentos.relatorio,
            comando,
        )

    try:
        matriz = carregar_matriz(argumentos.arquivo)
    except (OSError, ErroMatriz) as erro:
        print(f"Erro: {erro}")
        return 1

    # Cada aresta aparece duas vezes em uma matriz simétrica.
    quantidade_garrafas = sum(sum(linha) for linha in matriz) // 2
    print("Matriz carregada e validada com sucesso.")
    print(f"Quantidade de filósofos: {len(matriz)}")
    print(f"Quantidade de garrafas: {quantidade_garrafas}")
    if argumentos.seed is not None:
        print(f"Seed utilizada: {argumentos.seed}")

    # "todas" foi mantido como alias do modo "comparar".
    tipos = (
        ["ordenacao", "garcom"]
        if argumentos.solucao in ("comparar", "todas")
        else [argumentos.solucao]
    )
    resumos = []
    try:
        for tipo in tipos:
            if argumentos.seed is not None:
                # Reinicia a sequência para cada solução da comparação.
                random.seed(argumentos.seed)
            resumos.append(
                executar_simulacao(matriz, tipo, argumentos.verbose)
            )
    except ErroSimulacao as erro:
        print(f"Erro: {erro}")
        return 1

    if len(resumos) == 2:
        exibir_comparacao(resumos)

    arquivos_csv = []
    arquivos_graficos = []

    if argumentos.csv:
        caso = argumentos.arquivo.stem

        for resumo in resumos:
            caminho = salvar_resultados_individuais(
                resumo["filosofos"],
                caso,
                resumo["tipo_solucao"],
                resumo["solucao"],
            )
            arquivos_csv.append(caminho)
            print(f"CSV individual salvo em: {caminho}")

        if len(resumos) == 2:
            caminho = salvar_comparacao(resumos, caso)
            arquivos_csv.append(caminho)
            print(f"CSV comparativo salvo em: {caminho}")

    if argumentos.graficos:
        if not argumentos.csv:
            print(
                "Aviso: use também --csv para manter os dados dos gráficos."
            )

        if len(resumos) != 2:
            print(
                "Aviso: os gráficos exigem o modo comparar "
                "ou o comando todos."
            )
        else:
            try:
                caminhos_graficos = gerar_graficos_comparacao(
                    resumos,
                    argumentos.arquivo.stem,
                )
            except ErroGrafico as erro:
                print(f"Erro: {erro}")
                return 1

            for caminho in caminhos_graficos:
                print(f"Gráfico salvo em: {caminho}")
            arquivos_graficos.extend(caminhos_graficos)

    if argumentos.relatorio:
        caso = argumentos.arquivo.stem
        informacoes_casos = [
            {
                "caso": caso,
                "filosofos": len(matriz),
                "garrafas": quantidade_garrafas,
                "ciclos": determinar_quantidade_ciclos(len(matriz)),
            }
        ]
        nome_modo = (
            "comparar"
            if argumentos.solucao in ("comparar", "todas")
            else argumentos.solucao
        )
        caminho_relatorio = gerar_relatorio_txt(
            [
                {**resumo, "caso": caso}
                for resumo in resumos
            ],
            informacoes_casos,
            comando,
            argumentos.seed,
            f"relatorio_{caso}_{nome_modo}.txt",
            arquivos_csv,
            arquivos_graficos,
        )
        print(f"Relatório salvo em: {caminho_relatorio}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
