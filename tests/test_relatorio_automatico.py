"""Testes da geração automática do relatório em TXT."""

import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import main
from relatorio_automatico import gerar_relatorio_txt


class TesteRelatorioAutomatico(unittest.TestCase):
    def test_argumento_relatorio_e_opcional(self):
        argumentos = [
            "main.py",
            "matrizes/caso1.txt",
            "comparar",
            "--relatorio",
        ]

        with patch.object(sys, "argv", argumentos):
            opcoes = main.criar_parser().parse_args()
        self.assertTrue(opcoes.relatorio)

        with patch.object(sys, "argv", argumentos[:-1]):
            opcoes_sem_relatorio = main.criar_parser().parse_args()
        self.assertFalse(opcoes_sem_relatorio.relatorio)

    def test_cria_relatorio_com_metricas_e_conclusao(self):
        filosofos = [
            SimpleNamespace(vezes_bebeu=6),
            SimpleNamespace(vezes_bebeu=6),
        ]
        resumos = [
            {
                "caso": "caso1",
                "solucao": "Ordenação de Recursos",
                "tempo_total": 20.0,
                "espera_geral": 0.5,
                "maior_espera": 0.8,
                "menor_espera": 0.2,
                "deadlock": False,
                "starvation": False,
                "filosofos": filosofos,
            },
            {
                "caso": "caso1",
                "solucao": "Garçom",
                "tempo_total": 22.0,
                "espera_geral": 0.6,
                "maior_espera": 0.9,
                "menor_espera": 0.3,
                "deadlock": False,
                "starvation": True,
                "filosofos": filosofos,
            },
        ]
        informacoes = [
            {
                "caso": "caso1",
                "filosofos": 5,
                "garrafas": 5,
                "ciclos": 6,
            }
        ]

        with tempfile.TemporaryDirectory() as temporaria:
            pasta = Path(temporaria) / "resultados"
            csv = pasta / "resultado.csv"
            grafico = pasta / "grafico.png"
            caminho = gerar_relatorio_txt(
                resumos,
                informacoes,
                "python main.py matrizes/caso1.txt comparar --seed 42",
                42,
                "relatorio_caso1_comparar.txt",
                [csv],
                [grafico],
                pasta,
            )
            conteudo = caminho.read_text(encoding="utf-8")

        self.assertEqual(caminho.name, "relatorio_caso1_comparar.txt")
        self.assertIn("SIMULAÇÃO DO PROBLEMA DO BAR DOS FILÓSOFOS", conteudo)
        self.assertIn("Data e hora:", conteudo)
        self.assertIn("Comando executado:", conteudo)
        self.assertIn("Seed utilizada: 42", conteudo)
        self.assertIn("Tempo total", conteudo)
        self.assertIn("Espera média", conteudo)
        self.assertIn("Deadlock", conteudo)
        self.assertIn("Starvation", conteudo)
        self.assertIn(str(csv), conteudo)
        self.assertIn(str(grafico), conteudo)
        self.assertIn("CONCLUSÃO", conteudo)
        self.assertIn("A execução foi concluída sem deadlock.", conteudo)
        self.assertIn("possível desequilíbrio de espera", conteudo)


if __name__ == "__main__":
    unittest.main()
