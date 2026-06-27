"""Testes da geração opcional de gráficos."""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main
from graficos import gerar_graficos_comparacao, gerar_graficos_todos

MATPLOTLIB_DISPONIVEL = importlib.util.find_spec("matplotlib") is not None


def criar_resumo(caso: str, solucao: str, valor: float) -> dict:
    """Cria dados pequenos para os testes dos gráficos."""
    return {
        "caso": caso,
        "solucao": solucao,
        "tempo_total": valor,
        "espera_geral": valor / 10,
        "maior_espera": valor / 8,
        "menor_espera": valor / 12,
        "deadlock": False,
        "starvation": False,
    }


class TesteGraficos(unittest.TestCase):
    def test_argumento_graficos_e_opcional(self):
        argumentos = [
            "main.py",
            "matrizes/caso1.txt",
            "comparar",
            "--graficos",
        ]
        with patch.object(sys, "argv", argumentos):
            opcoes = main.criar_parser().parse_args()
        self.assertTrue(opcoes.graficos)

        with patch.object(sys, "argv", argumentos[:-1]):
            opcoes_sem_graficos = main.criar_parser().parse_args()
        self.assertFalse(opcoes_sem_graficos.graficos)

    @unittest.skipUnless(MATPLOTLIB_DISPONIVEL, "matplotlib não instalado")
    def test_gera_graficos_de_um_caso(self):
        resumos = [
            criar_resumo("caso1", "Ordenação de Recursos", 10),
            criar_resumo("caso1", "Garçom", 12),
        ]

        with tempfile.TemporaryDirectory() as temporaria:
            caminhos = gerar_graficos_comparacao(
                resumos,
                "caso1",
                temporaria,
            )

            self.assertEqual(len(caminhos), 2)
            self.assertTrue(all(caminho.exists() for caminho in caminhos))
            self.assertTrue(all(caminho.stat().st_size > 0 for caminho in caminhos))

    @unittest.skipUnless(MATPLOTLIB_DISPONIVEL, "matplotlib não instalado")
    def test_gera_graficos_dos_tres_casos(self):
        resumos = []
        for indice, caso in enumerate(("caso1", "caso2", "caso3"), start=1):
            resumos.append(
                criar_resumo(caso, "Ordenação de Recursos", 10 + indice)
            )
            resumos.append(criar_resumo(caso, "Garçom", 12 + indice))

        with tempfile.TemporaryDirectory() as temporaria:
            caminhos = gerar_graficos_todos(resumos, Path(temporaria))

            self.assertEqual(
                [caminho.name for caminho in caminhos],
                [
                    "grafico_tempo_total_todos.png",
                    "grafico_espera_media_todos.png",
                ],
            )
            self.assertTrue(all(caminho.exists() for caminho in caminhos))
            self.assertTrue(all(caminho.stat().st_size > 0 for caminho in caminhos))


if __name__ == "__main__":
    unittest.main()
