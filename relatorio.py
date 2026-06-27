"""Apresentação dos resultados da simulação no terminal."""

import csv
from pathlib import Path

from filosofo import Filosofo

FATOR_STARVATION = 2
ESPERA_MINIMA_STARVATION = 0.1


def verificar_starvation(filosofos: list[Filosofo]) -> bool:
    """Verifica se uma espera individual está muito acima da média geral."""
    esperas = [filosofo.calcular_espera_media() for filosofo in filosofos]
    espera_geral = sum(esperas) / len(esperas)

    if espera_geral == 0:
        return False

    maior_espera = max(esperas)
    return (
        maior_espera >= ESPERA_MINIMA_STARVATION
        and maior_espera > FATOR_STARVATION * espera_geral
    )


def exibir_tabela(filosofos: list[Filosofo]) -> None:
    """Exibe os tempos individuais de cada filósofo."""
    cabecalho = (
        f"{'Filósofo':<10}"
        f"{'Tranquilo':>12}"
        f"{'Com sede':>12}"
        f"{'Bebendo':>12}"
        f"{'Bebeu':>8}"
        f"{'Espera média':>16}"
    )

    print(cabecalho)
    print("-" * len(cabecalho))

    for filosofo in filosofos:
        print(
            f"F{filosofo.identificador:<9}"
            f"{filosofo.tempo_tranquilo:>11.2f}s"
            f"{filosofo.tempo_com_sede:>11.2f}s"
            f"{filosofo.tempo_bebendo:>11.2f}s"
            f"{filosofo.vezes_bebeu:>8}"
            f"{filosofo.calcular_espera_media():>15.2f}s"
        )


def exibir_relatorio(
    filosofos: list[Filosofo],
    tempo_total: float,
    nome_solucao: str,
) -> None:
    """Exibe a tabela e o resumo geral da execução."""
    esperas = [filosofo.calcular_espera_media() for filosofo in filosofos]
    maior_espera = max(esperas)
    menor_espera = min(esperas)

    print()
    print("=" * 70)
    print("RESULTADOS DA SIMULAÇÃO")
    print(f"Solução utilizada: {nome_solucao}")
    print("=" * 70)
    exibir_tabela(filosofos)
    print()
    print(f"Tempo total da simulação: {tempo_total:.2f}s")
    print(f"Maior espera média: {maior_espera:.2f}s")
    print(f"Menor espera média: {menor_espera:.2f}s")
    print(f"Diferença entre as esperas: {maior_espera - menor_espera:.2f}s")
    print("Deadlock detectado: Não")
    print(
        "Indício de starvation: "
        f"{'Sim' if verificar_starvation(filosofos) else 'Não'}"
    )


def criar_resumo(
    filosofos: list[Filosofo],
    tempo_total: float,
    nome_solucao: str,
) -> dict:
    """Monta o resumo usado na comparação das soluções."""
    esperas = [filosofo.calcular_espera_media() for filosofo in filosofos]

    return {
        "solucao": nome_solucao,
        "tempo_total": tempo_total,
        "espera_geral": sum(esperas) / len(esperas),
        "maior_espera": max(esperas),
        "menor_espera": min(esperas),
        "deadlock": False,
        "starvation": verificar_starvation(filosofos),
    }


def exibir_comparacao(resumos: list[dict]) -> None:
    """Exibe as principais métricas das soluções lado a lado."""
    print()
    print("=" * 125)
    print("COMPARAÇÃO ENTRE AS SOLUÇÕES")
    print("=" * 125)
    print(
        f"{'Solução':<23}"
        f"{'Tempo total':>13}"
        f"{'Espera geral':>15}"
        f"{'Maior':>11}"
        f"{'Menor':>11}"
        f"{'Diferença':>13}"
        f"{'Deadlock':>12}"
        f"{'Starvation':>14}"
    )
    print("-" * 125)

    for resumo in resumos:
        diferenca = resumo["maior_espera"] - resumo["menor_espera"]
        print(
            f"{resumo['solucao']:<23}"
            f"{resumo['tempo_total']:>12.2f}s"
            f"{resumo['espera_geral']:>14.2f}s"
            f"{resumo['maior_espera']:>10.2f}s"
            f"{resumo['menor_espera']:>10.2f}s"
            f"{diferenca:>12.2f}s"
            f"{'Sim' if resumo['deadlock'] else 'Não':>12}"
            f"{'Sim' if resumo['starvation'] else 'Não':>14}"
        )

    menor_tempo = min(resumos, key=lambda item: item["tempo_total"])
    mais_equilibrada = min(
        resumos,
        key=lambda item: item["maior_espera"] - item["menor_espera"],
    )

    print()
    print(
        f"Conclusão: {menor_tempo['solucao']} teve o menor tempo total, "
        f"enquanto {mais_equilibrada['solucao']} apresentou a espera "
        "mais equilibrada entre os filósofos."
    )


def exibir_comparacao_geral(resumos: list[dict]) -> None:
    """Exibe as duas soluções nos três casos do trabalho."""
    print()
    print("=" * 135)
    print("COMPARAÇÃO GERAL DOS TRÊS CASOS")
    print("=" * 135)
    print(
        f"{'Caso':<8}"
        f"{'Solução':<23}"
        f"{'Tempo total':>13}"
        f"{'Espera geral':>15}"
        f"{'Maior':>11}"
        f"{'Menor':>11}"
        f"{'Diferença':>13}"
        f"{'Deadlock':>12}"
        f"{'Starvation':>14}"
    )
    print("-" * 135)

    for resumo in resumos:
        diferenca = resumo["maior_espera"] - resumo["menor_espera"]
        print(
            f"{resumo['caso']:<8}"
            f"{resumo['solucao']:<23}"
            f"{resumo['tempo_total']:>12.2f}s"
            f"{resumo['espera_geral']:>14.2f}s"
            f"{resumo['maior_espera']:>10.2f}s"
            f"{resumo['menor_espera']:>10.2f}s"
            f"{diferenca:>12.2f}s"
            f"{'Sim' if resumo['deadlock'] else 'Não':>12}"
            f"{'Sim' if resumo['starvation'] else 'Não':>14}"
        )


def salvar_resultados_individuais(
    filosofos: list[Filosofo],
    caso: str,
    solucao: str,
    nome_solucao: str,
    pasta: str | Path = "resultados",
) -> Path:
    """Salva os tempos individuais dos filósofos em um arquivo CSV."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / f"resultado_{caso}_{solucao}.csv"
    colunas = [
        "caso",
        "solucao",
        "filosofo",
        "tempo_tranquilo",
        "tempo_com_sede",
        "tempo_bebendo",
        "vezes_bebeu",
        "espera_media",
    ]

    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()

        for filosofo in filosofos:
            escritor.writerow(
                {
                    "caso": caso,
                    "solucao": nome_solucao,
                    "filosofo": filosofo.identificador,
                    "tempo_tranquilo": f"{filosofo.tempo_tranquilo:.6f}",
                    "tempo_com_sede": f"{filosofo.tempo_com_sede:.6f}",
                    "tempo_bebendo": f"{filosofo.tempo_bebendo:.6f}",
                    "vezes_bebeu": filosofo.vezes_bebeu,
                    "espera_media": f"{filosofo.calcular_espera_media():.6f}",
                }
            )

    return caminho


def salvar_comparacao(
    resumos: list[dict],
    caso: str,
    pasta: str | Path = "resultados",
) -> Path:
    """Salva as métricas gerais das duas soluções em um arquivo CSV."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / f"resultado_{caso}_comparar.csv"
    colunas = [
        "caso",
        "solucao",
        "tempo_total",
        "espera_media_geral",
        "maior_espera_media",
        "menor_espera_media",
        "diferenca_espera",
        "deadlock",
        "starvation",
    ]

    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()

        for resumo in resumos:
            escritor.writerow(
                {
                    "caso": caso,
                    "solucao": resumo["solucao"],
                    "tempo_total": f"{resumo['tempo_total']:.6f}",
                    "espera_media_geral": f"{resumo['espera_geral']:.6f}",
                    "maior_espera_media": f"{resumo['maior_espera']:.6f}",
                    "menor_espera_media": f"{resumo['menor_espera']:.6f}",
                    "diferenca_espera": (
                        f"{resumo['maior_espera'] - resumo['menor_espera']:.6f}"
                    ),
                    "deadlock": "Sim" if resumo["deadlock"] else "Não",
                    "starvation": "Sim" if resumo["starvation"] else "Não",
                }
            )

    return caminho


def salvar_comparacao_geral(
    resumos: list[dict],
    pasta: str | Path = "resultados",
) -> Path:
    """Salva em CSV a comparação das soluções nos três casos."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / "comparativo_todos_os_casos.csv"
    colunas = [
        "caso",
        "solucao",
        "tempo_total",
        "espera_media_geral",
        "maior_espera_media",
        "menor_espera_media",
        "diferenca_espera",
        "deadlock",
        "starvation",
    ]

    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()

        for resumo in resumos:
            escritor.writerow(
                {
                    "caso": resumo["caso"],
                    "solucao": resumo["solucao"],
                    "tempo_total": f"{resumo['tempo_total']:.6f}",
                    "espera_media_geral": f"{resumo['espera_geral']:.6f}",
                    "maior_espera_media": f"{resumo['maior_espera']:.6f}",
                    "menor_espera_media": f"{resumo['menor_espera']:.6f}",
                    "diferenca_espera": (
                        f"{resumo['maior_espera'] - resumo['menor_espera']:.6f}"
                    ),
                    "deadlock": "Sim" if resumo["deadlock"] else "Não",
                    "starvation": "Sim" if resumo["starvation"] else "Não",
                }
            )

    return caminho
