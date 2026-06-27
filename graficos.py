"""Geração dos gráficos comparativos da simulação."""

from pathlib import Path


class ErroGrafico(RuntimeError):
    """Erro usado quando um gráfico não pode ser gerado."""


def carregar_pyplot():
    """Carrega o matplotlib somente quando os gráficos forem solicitados."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as erro:
        raise ErroGrafico(
            "matplotlib não está instalado. Execute: "
            "python -m pip install matplotlib"
        ) from erro

    return plt


def salvar_grafico_barras(
    rotulos: list[str],
    valores: list[float],
    titulo: str,
    eixo_y: str,
    caminho: Path,
) -> None:
    """Cria um gráfico de barras simples e salva em PNG."""
    plt = carregar_pyplot()
    figura, eixo = plt.subplots(figsize=(8, 5))
    barras = eixo.bar(rotulos, valores, color=["#4C78A8", "#F58518"])

    eixo.set_title(titulo)
    eixo.set_ylabel(eixo_y)
    eixo.grid(axis="y", linestyle="--", alpha=0.4)
    eixo.bar_label(barras, fmt="%.2f")
    figura.tight_layout()
    figura.savefig(caminho, dpi=150)
    plt.close(figura)


def gerar_graficos_comparacao(
    resumos: list[dict],
    caso: str,
    pasta: str | Path = "resultados",
) -> list[Path]:
    """Gera os gráficos das duas soluções para um único caso."""
    if len(resumos) != 2:
        raise ErroGrafico(
            "são necessários os resultados das duas soluções."
        )

    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    rotulos = [resumo["solucao"] for resumo in resumos]

    caminho_tempo = pasta / f"grafico_tempo_total_{caso}.png"
    salvar_grafico_barras(
        rotulos,
        [resumo["tempo_total"] for resumo in resumos],
        f"Tempo total - {caso}",
        "Tempo (segundos)",
        caminho_tempo,
    )

    caminho_espera = pasta / f"grafico_espera_media_{caso}.png"
    salvar_grafico_barras(
        rotulos,
        [resumo["espera_geral"] for resumo in resumos],
        f"Espera média geral - {caso}",
        "Tempo (segundos)",
        caminho_espera,
    )

    return [caminho_tempo, caminho_espera]


def gerar_graficos_todos(
    resumos: list[dict],
    pasta: str | Path = "resultados",
) -> list[Path]:
    """Gera gráficos com os três casos e as duas soluções."""
    casos = ["caso1", "caso2", "caso3"]
    solucoes = ["Ordenação de Recursos", "Garçom"]
    resultados = {
        (resumo["caso"], resumo["solucao"]): resumo
        for resumo in resumos
    }

    if any(
        (caso, solucao) not in resultados
        for caso in casos
        for solucao in solucoes
    ):
        raise ErroGrafico(
            "faltam resultados de algum caso ou solução para os gráficos."
        )

    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    caminhos = [
        pasta / "grafico_tempo_total_todos.png",
        pasta / "grafico_espera_media_todos.png",
    ]
    metricas = [
        ("tempo_total", "Tempo total por caso e solução", "Tempo (segundos)"),
        (
            "espera_geral",
            "Espera média geral por caso e solução",
            "Tempo (segundos)",
        ),
    ]
    plt = carregar_pyplot()

    for caminho, (metrica, titulo, eixo_y) in zip(caminhos, metricas):
        figura, eixo = plt.subplots(figsize=(9, 5))
        posicoes = list(range(len(casos)))
        largura = 0.36

        for indice, solucao in enumerate(solucoes):
            # O deslocamento coloca as duas soluções lado a lado.
            deslocamento = -largura / 2 if indice == 0 else largura / 2
            valores = [
                resultados[(caso, solucao)][metrica]
                for caso in casos
            ]
            barras = eixo.bar(
                [posicao + deslocamento for posicao in posicoes],
                valores,
                largura,
                label=solucao,
            )
            eixo.bar_label(barras, fmt="%.2f")

        eixo.set_title(titulo)
        eixo.set_ylabel(eixo_y)
        eixo.set_xticks(posicoes, casos)
        eixo.legend()
        eixo.grid(axis="y", linestyle="--", alpha=0.4)
        figura.tight_layout()
        figura.savefig(caminho, dpi=150)
        plt.close(figura)

    return caminhos
