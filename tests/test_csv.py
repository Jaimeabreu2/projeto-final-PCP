"""Testes da exportação dos resultados para CSV."""

import csv
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main
from filosofo import Filosofo
from relatorio import (
    salvar_comparacao,
    salvar_comparacao_geral,
    salvar_resultados_individuais,
)


class TesteCsv(unittest.TestCase):
    def test_argumento_csv_e_aceito(self):
        argumentos = [
            "main.py",
            "matrizes/caso1.txt",
            "ordenacao",
            "--csv",
        ]

        with patch.object(sys, "argv", argumentos):
            opcoes = main.criar_parser().parse_args()

        self.assertTrue(opcoes.csv)

    def test_cria_csv_individual_com_cabecalho_correto(self):
        filosofo = Filosofo(0, [])
        filosofo.tempo_tranquilo = 2.0
        filosofo.tempo_com_sede = 1.0
        filosofo.tempo_bebendo = 1.0
        filosofo.vezes_bebeu = 1

        with tempfile.TemporaryDirectory() as temporaria:
            pasta = Path(temporaria) / "resultados"
            caminho = salvar_resultados_individuais(
                [filosofo],
                "caso1",
                "ordenacao",
                "Ordenação de Recursos",
                pasta,
            )

            self.assertTrue(caminho.exists())
            with caminho.open(encoding="utf-8", newline="") as arquivo:
                leitor = csv.reader(arquivo)
                cabecalho = next(leitor)

        self.assertEqual(
            cabecalho,
            [
                "caso",
                "solucao",
                "filosofo",
                "tempo_tranquilo",
                "tempo_com_sede",
                "tempo_bebendo",
                "vezes_bebeu",
                "espera_media",
            ],
        )

    def test_cria_csv_comparativo_com_cabecalho_correto(self):
        resumo = {
            "solucao": "Ordenação de Recursos",
            "tempo_total": 10.0,
            "espera_geral": 0.5,
            "maior_espera": 0.8,
            "menor_espera": 0.2,
            "deadlock": False,
            "starvation": False,
        }

        with tempfile.TemporaryDirectory() as temporaria:
            pasta = Path(temporaria) / "resultados"
            caminho = salvar_comparacao([resumo], "caso1", pasta)

            self.assertTrue(caminho.exists())
            with caminho.open(encoding="utf-8", newline="") as arquivo:
                leitor = csv.reader(arquivo)
                cabecalho = next(leitor)

        self.assertEqual(
            cabecalho,
            [
                "caso",
                "solucao",
                "tempo_total",
                "espera_media_geral",
                "maior_espera_media",
                "menor_espera_media",
                "diferenca_espera",
                "deadlock",
                "starvation",
            ],
        )

    def test_cria_csv_geral_dos_tres_casos(self):
        resumos = []
        for caso in ("caso1", "caso2", "caso3"):
            for solucao in ("Ordenação de Recursos", "Garçom"):
                resumos.append(
                    {
                        "caso": caso,
                        "solucao": solucao,
                        "tempo_total": 10.0,
                        "espera_geral": 0.5,
                        "maior_espera": 0.8,
                        "menor_espera": 0.2,
                        "deadlock": False,
                        "starvation": False,
                    }
                )

        with tempfile.TemporaryDirectory() as temporaria:
            pasta = Path(temporaria) / "resultados"
            caminho = salvar_comparacao_geral(resumos, pasta)

            self.assertEqual(caminho.name, "comparativo_todos_os_casos.csv")
            self.assertTrue(caminho.exists())
            with caminho.open(encoding="utf-8", newline="") as arquivo:
                linhas = list(csv.DictReader(arquivo))

        self.assertEqual(len(linhas), 6)
        self.assertEqual(
            list(linhas[0]),
            [
                "caso",
                "solucao",
                "tempo_total",
                "espera_media_geral",
                "maior_espera_media",
                "menor_espera_media",
                "diferenca_espera",
                "deadlock",
                "starvation",
            ],
        )


if __name__ == "__main__":
    unittest.main()
