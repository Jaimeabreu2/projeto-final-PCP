"""Testes da leitura e da criação dos elementos do grafo."""

import unittest
from pathlib import Path

from grafo import (
    ErroMatriz,
    carregar_matriz,
    criar_filosofos,
    criar_garrafas,
    validar_matriz,
)


class TesteMatriz(unittest.TestCase):
    def test_carrega_os_tres_casos(self):
        quantidades_esperadas = {
            "caso1.txt": (5, 5),
            "caso2.txt": (6, 8),
            "caso3.txt": (12, 21),
        }

        for nome, (vertices, arestas) in quantidades_esperadas.items():
            with self.subTest(caso=nome):
                matriz = carregar_matriz(Path("matrizes") / nome)
                garrafas = criar_garrafas(matriz)

                self.assertEqual(len(matriz), vertices)
                self.assertEqual(len(garrafas), arestas)

    def test_rejeita_matrizes_invalidas(self):
        matrizes_invalidas = [
            [],
            [[0, 1, 0], [1, 0, 1]],
            [[0, 2], [2, 0]],
            [[1, 0], [0, 0]],
            [[0, 1], [0, 0]],
            [[0, 0], [0, 0]],
        ]

        for matriz in matrizes_invalidas:
            with self.subTest(matriz=matriz):
                with self.assertRaises(ErroMatriz):
                    validar_matriz(matriz)

    def test_associa_as_garrafas_aos_filosofos(self):
        matriz = carregar_matriz("matrizes/caso1.txt")
        garrafas = criar_garrafas(matriz)
        filosofos = criar_filosofos(matriz, garrafas)

        for filosofo, linha in zip(filosofos, matriz):
            self.assertEqual(len(filosofo.garrafas), sum(linha))

        for garrafa in garrafas:
            self.assertIn(garrafa, filosofos[garrafa.filosofo_a].garrafas)
            self.assertIn(garrafa, filosofos[garrafa.filosofo_b].garrafas)


if __name__ == "__main__":
    unittest.main()
