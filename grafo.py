"""Leitura e validação do grafo representado por uma matriz de adjacência."""

from pathlib import Path

from filosofo import Filosofo
from garrafa import Garrafa

Matriz = list[list[int]]


class ErroMatriz(ValueError):
    """Erro usado quando a matriz de entrada é inválida."""


def ler_matriz(caminho: str | Path) -> Matriz:
    """Lê uma matriz de um arquivo de texto.

    Os valores podem ser separados por vírgulas ou espaços. Linhas vazias são
    ignoradas para não invalidar um arquivo apenas por sua formatação.
    """
    caminho = Path(caminho)

    if caminho.suffix.lower() != ".txt":
        raise ErroMatriz("o arquivo de entrada deve possuir a extensão .txt.")

    try:
        conteudo = caminho.read_text(encoding="utf-8-sig")
    except FileNotFoundError as erro:
        raise FileNotFoundError(f"arquivo não encontrado: {caminho}") from erro
    except UnicodeDecodeError as erro:
        raise ErroMatriz(
            "não foi possível ler o arquivo como texto UTF-8."
        ) from erro

    matriz: Matriz = []

    # Cada linha útil do arquivo se transforma em uma linha da matriz.
    for numero_linha, texto in enumerate(conteudo.splitlines(), start=1):
        texto = texto.strip()
        if not texto:
            continue

        partes = texto.replace(",", " ").split()
        try:
            linha = [int(valor) for valor in partes]
        except ValueError as erro:
            raise ErroMatriz(
                f"linha {numero_linha}: todos os valores devem ser 0 ou 1."
            ) from erro

        matriz.append(linha)

    return matriz


def validar_matriz(matriz: Matriz) -> None:
    """Valida as regras de uma matriz de adjacência não direcionada."""
    if not matriz:
        raise ErroMatriz("a matriz está vazia.")

    ordem = len(matriz)

    # Primeiro são verificadas as regras de cada linha e da diagonal.
    for i, linha in enumerate(matriz):
        if len(linha) != ordem:
            raise ErroMatriz(
                f"a matriz deve ser quadrada: a linha {i + 1} possui "
                f"{len(linha)} valor(es), mas eram esperados {ordem}."
            )

        for j, valor in enumerate(linha):
            if valor not in (0, 1):
                raise ErroMatriz(
                    f"valor inválido na posição [{i}][{j}]: "
                    "use apenas 0 ou 1."
                )

        if linha[i] != 0:
            raise ErroMatriz(
                f"a diagonal principal deve ser zero: posição [{i}][{i}]."
            )

        if sum(linha) == 0:
            raise ErroMatriz(
                f"o filósofo {i} não possui nenhuma garrafa adjacente."
            )

    # Em um grafo não direcionado, M[i][j] deve ser igual a M[j][i].
    for i in range(ordem):
        for j in range(i + 1, ordem):
            if matriz[i][j] != matriz[j][i]:
                raise ErroMatriz(
                    "a matriz deve ser simétrica: "
                    f"as posições [{i}][{j}] e [{j}][{i}] são diferentes."
                )


def carregar_matriz(caminho: str | Path) -> Matriz:
    """Lê, valida e devolve uma matriz de adjacência."""
    matriz = ler_matriz(caminho)
    validar_matriz(matriz)
    return matriz


def criar_garrafas(matriz: Matriz) -> list[Garrafa]:
    """Cria uma garrafa para cada aresta presente na matriz."""
    garrafas = []
    identificador = 0

    # Somente a parte acima da diagonal é percorrida para evitar duplicatas.
    for i in range(len(matriz)):
        for j in range(i + 1, len(matriz)):
            if matriz[i][j] == 1:
                garrafas.append(Garrafa(identificador, i, j))
                identificador += 1

    return garrafas


def criar_filosofos(matriz: Matriz, garrafas: list[Garrafa]) -> list[Filosofo]:
    """Cria um filósofo para cada vértice e associa suas garrafas."""
    filosofos = []

    for identificador in range(len(matriz)):
        # Uma garrafa pertence ao filósofo se ele for um dos seus extremos.
        garrafas_adjacentes = [
            garrafa
            for garrafa in garrafas
            if identificador in (garrafa.filosofo_a, garrafa.filosofo_b)
        ]
        filosofos.append(Filosofo(identificador, garrafas_adjacentes))

    return filosofos
