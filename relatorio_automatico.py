"""Geração de um relatório textual simples da execução."""

from datetime import datetime
from pathlib import Path


def montar_tabela_resumos(resumos: list[dict]) -> list[str]:
    """Monta uma tabela textual com as principais métricas."""
    linhas = [
        (
            f"{'Caso':<8}{'Solução':<23}{'Tempo total':>13}"
            f"{'Espera média':>14}{'Maior':>10}{'Menor':>10}"
            f"{'Diferença':>12}{'Deadlock':>11}{'Starvation':>13}"
        ),
        "-" * 114,
    ]

    for resumo in resumos:
        diferenca = resumo["maior_espera"] - resumo["menor_espera"]
        linhas.append(
            f"{resumo['caso']:<8}"
            f"{resumo['solucao']:<23}"
            f"{resumo['tempo_total']:>12.2f}s"
            f"{resumo['espera_geral']:>13.2f}s"
            f"{resumo['maior_espera']:>9.2f}s"
            f"{resumo['menor_espera']:>9.2f}s"
            f"{diferenca:>11.2f}s"
            f"{'Sim' if resumo['deadlock'] else 'Não':>11}"
            f"{'Sim' if resumo['starvation'] else 'Não':>13}"
        )

    return linhas


def montar_conclusao(resumos: list[dict], ciclos_concluidos: bool) -> list[str]:
    """Cria uma conclusão curta a partir dos resultados obtidos."""
    linhas = []

    if any(resumo["deadlock"] for resumo in resumos):
        linhas.append("Foi identificado um possível deadlock na execução.")
    else:
        linhas.append("A execução foi concluída sem deadlock.")

    if ciclos_concluidos:
        linhas.append(
            "Todos os filósofos completaram a quantidade esperada de ciclos."
        )

    casos = list(dict.fromkeys(resumo["caso"] for resumo in resumos))
    for caso in casos:
        resumos_caso = [
            resumo for resumo in resumos if resumo["caso"] == caso
        ]

        if len(resumos_caso) == 1:
            linhas.append(
                f"No {caso}, foi executada a solução "
                f"{resumos_caso[0]['solucao']}."
            )
            continue

        menor_tempo = min(resumos_caso, key=lambda item: item["tempo_total"])
        menor_espera = min(
            resumos_caso,
            key=lambda item: item["espera_geral"],
        )
        linhas.append(
            f"No {caso}, {menor_tempo['solucao']} apresentou menor tempo "
            f"total, enquanto {menor_espera['solucao']} apresentou menor "
            "espera média geral."
        )

    if any(resumo["starvation"] for resumo in resumos):
        linhas.append(
            "Foi identificado um possível desequilíbrio de espera nesta "
            "execução. Isso não significa necessariamente erro, pois os "
            "tempos podem variar devido à aleatoriedade e ao escalonamento "
            "das threads."
        )
    else:
        linhas.append("Não foi identificado forte indício de starvation.")

    return linhas


def verificar_ciclos(
    resumos: list[dict],
    informacoes_casos: list[dict],
) -> bool:
    """Confere se os filósofos concluíram os ciclos esperados."""
    ciclos_por_caso = {
        informacao["caso"]: informacao["ciclos"]
        for informacao in informacoes_casos
    }

    for resumo in resumos:
        filosofos = resumo.get("filosofos", [])
        ciclos = ciclos_por_caso[resumo["caso"]]
        if any(filosofo.vezes_bebeu != ciclos for filosofo in filosofos):
            return False

    return True


def gerar_relatorio_txt(
    resumos: list[dict],
    informacoes_casos: list[dict],
    comando: str,
    seed: int | None,
    nome_arquivo: str,
    arquivos_csv: list[Path] | None = None,
    arquivos_graficos: list[Path] | None = None,
    pasta: str | Path = "resultados",
) -> Path:
    """Gera e salva o relatório automático em formato TXT."""
    if not resumos:
        raise ValueError("não há resultados para gerar o relatório.")

    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / nome_arquivo
    arquivos_csv = arquivos_csv or []
    arquivos_graficos = arquivos_graficos or []
    solucoes = list(dict.fromkeys(resumo["solucao"] for resumo in resumos))

    linhas = [
        "SIMULAÇÃO DO PROBLEMA DO BAR DOS FILÓSOFOS",
        "=" * 55,
        f"Data e hora: {datetime.now():%d/%m/%Y %H:%M:%S}",
        f"Comando executado: {comando}",
        f"Seed utilizada: {seed if seed is not None else 'não informada'}",
        f"Casos executados: {', '.join(info['caso'] for info in informacoes_casos)}",
        f"Soluções executadas: {', '.join(solucoes)}",
        "",
        "CONFIGURAÇÃO DOS CASOS",
        "-" * 55,
    ]

    for informacao in informacoes_casos:
        linhas.append(
            f"{informacao['caso']}: "
            f"{informacao['filosofos']} filósofos, "
            f"{informacao['garrafas']} garrafas e "
            f"{informacao['ciclos']} ciclos por filósofo."
        )

    linhas.extend(["", "MÉTRICAS PRINCIPAIS", "-" * 107])
    linhas.extend(montar_tabela_resumos(resumos))

    linhas.extend(["", "ARQUIVOS CSV GERADOS", "-" * 55])
    linhas.extend(
        [str(caminho_csv) for caminho_csv in arquivos_csv]
        or ["Nenhum arquivo CSV foi solicitado."]
    )

    linhas.extend(["", "GRÁFICOS GERADOS", "-" * 55])
    linhas.extend(
        [str(caminho_grafico) for caminho_grafico in arquivos_graficos]
        or ["Nenhum gráfico foi solicitado."]
    )

    linhas.extend(["", "CONCLUSÃO", "-" * 55])
    linhas.extend(
        montar_conclusao(
            resumos,
            verificar_ciclos(resumos, informacoes_casos),
        )
    )

    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return caminho
