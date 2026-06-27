"""Testes integrados dos casos e comandos obrigatórios."""

import io
import random
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import main
from grafo import carregar_matriz, criar_filosofos, criar_garrafas
from solucoes import SolucaoGarcom, SolucaoOrdenacao


class TesteIntegracao(unittest.TestCase):
    casos = [
        ("caso1.txt", 6),
        ("caso2.txt", 6),
        ("caso3.txt", 3),
    ]

    def test_quantidade_de_ciclos_dos_tres_casos(self):
        for nome, ciclos_esperados in self.casos:
            with self.subTest(caso=nome):
                matriz = carregar_matriz(f"matrizes/{nome}")
                ciclos = main.determinar_quantidade_ciclos(len(matriz))
                self.assertEqual(ciclos, ciclos_esperados)

    def test_solucoes_concluem_os_ciclos_e_liberam_locks(self):
        for nome, ciclos in self.casos:
            matriz = carregar_matriz(f"matrizes/{nome}")

            for tipo_solucao in ("ordenacao", "garcom"):
                with self.subTest(caso=nome, solucao=tipo_solucao):
                    garrafas = criar_garrafas(matriz)
                    filosofos = criar_filosofos(matriz, garrafas)
                    solucao = (
                        SolucaoOrdenacao()
                        if tipo_solucao == "ordenacao"
                        else SolucaoGarcom(len(filosofos))
                    )

                    with patch("filosofo.time.sleep", return_value=None):
                        for filosofo in filosofos:
                            filosofo.configurar_execucao(solucao, ciclos)
                            filosofo.start()
                        for filosofo in filosofos:
                            filosofo.join(timeout=3)

                    self.assertTrue(
                        all(not filosofo.is_alive() for filosofo in filosofos)
                    )
                    self.assertTrue(
                        all(filosofo.erro is None for filosofo in filosofos)
                    )
                    self.assertTrue(
                        all(filosofo.vezes_bebeu == ciclos for filosofo in filosofos)
                    )
                    self.assertTrue(
                        all(not garrafa.lock.locked() for garrafa in garrafas)
                    )

                    if isinstance(solucao, SolucaoGarcom):
                        permissoes_recuperadas = 0
                        for _ in range(len(filosofos) - 1):
                            if solucao._permissoes.acquire(blocking=False):
                                permissoes_recuperadas += 1

                        self.assertEqual(
                            permissoes_recuperadas,
                            len(filosofos) - 1,
                        )
                        self.assertFalse(
                            solucao._permissoes.acquire(blocking=False)
                        )

                        for _ in range(permissoes_recuperadas):
                            solucao._permissoes.release()

    def test_tres_comandos_funcionam_nos_tres_casos(self):
        for nome, _ in self.casos:
            for comando in ("ordenacao", "garcom", "comparar"):
                with self.subTest(caso=nome, comando=comando):
                    saida = io.StringIO()
                    argumentos = ["main.py", f"matrizes/{nome}", comando]

                    with (
                        patch.object(sys, "argv", argumentos),
                        patch("filosofo.time.sleep", return_value=None),
                        redirect_stdout(saida),
                    ):
                        codigo = main.main()

                    texto = saida.getvalue()
                    self.assertEqual(codigo, 0)
                    self.assertIn("Tempo total da simulação", texto)
                    self.assertIn("Maior espera média", texto)
                    self.assertIn("Menor espera média", texto)
                    self.assertIn("Deadlock detectado: Não", texto)
                    self.assertIn("Indício de starvation:", texto)

                    if comando == "comparar":
                        self.assertIn("COMPARAÇÃO ENTRE AS SOLUÇÕES", texto)
                        self.assertIn("Conclusão:", texto)

    def test_seed_e_aceita_e_reaplicada_na_comparacao(self):
        valores_sorteados = []

        def simulacao_resumida(matriz, tipo_solucao, verbose=False):
            valores_sorteados.append(random.random())
            return {
                "solucao": tipo_solucao,
                "tempo_total": 1.0,
                "espera_geral": 0.1,
                "maior_espera": 0.2,
                "menor_espera": 0.1,
                "deadlock": False,
                "starvation": False,
            }

        argumentos = [
            "main.py",
            "matrizes/caso1.txt",
            "comparar",
            "--seed",
            "42",
        ]

        with (
            patch.object(sys, "argv", argumentos),
            patch("main.executar_simulacao", side_effect=simulacao_resumida),
            redirect_stdout(io.StringIO()),
        ):
            codigo = main.main()

        self.assertEqual(codigo, 0)
        self.assertEqual(len(valores_sorteados), 2)
        self.assertEqual(valores_sorteados[0], valores_sorteados[1])

    def test_comando_todos_executa_duas_solucoes_nos_tres_casos(self):
        execucoes = []

        def simulacao_resumida(matriz, tipo_solucao, verbose=False):
            execucoes.append((len(matriz), tipo_solucao, random.random()))
            return {
                "solucao": tipo_solucao,
                "tempo_total": 1.0,
                "espera_geral": 0.1,
                "maior_espera": 0.2,
                "menor_espera": 0.1,
                "deadlock": False,
                "starvation": False,
            }

        argumentos = ["main.py", "todos", "--seed", "42"]
        saida = io.StringIO()

        with (
            patch.object(sys, "argv", argumentos),
            patch("main.executar_simulacao", side_effect=simulacao_resumida),
            redirect_stdout(saida),
        ):
            codigo = main.main()

        self.assertEqual(codigo, 0)
        self.assertEqual(
            [(tamanho, solucao) for tamanho, solucao, _ in execucoes],
            [
                (5, "ordenacao"),
                (5, "garcom"),
                (6, "ordenacao"),
                (6, "garcom"),
                (12, "ordenacao"),
                (12, "garcom"),
            ],
        )
        self.assertEqual(len({valor for _, _, valor in execucoes}), 1)
        self.assertIn("COMPARAÇÃO GERAL DOS TRÊS CASOS", saida.getvalue())

    def test_argumento_verbose_e_aceito(self):
        argumentos = [
            "main.py",
            "matrizes/caso1.txt",
            "ordenacao",
            "--verbose",
        ]

        with patch.object(sys, "argv", argumentos):
            opcoes = main.criar_parser().parse_args()

        self.assertTrue(opcoes.verbose)

    def test_execucao_com_e_sem_verbose(self):
        matriz = carregar_matriz("matrizes/caso1.txt")

        with patch("filosofo.time.sleep", return_value=None):
            saida_limpa = io.StringIO()
            with redirect_stdout(saida_limpa):
                main.executar_simulacao(matriz, "ordenacao", verbose=False)

            saida_ordenacao = io.StringIO()
            with redirect_stdout(saida_ordenacao):
                main.executar_simulacao(matriz, "ordenacao", verbose=True)

            saida_garcom = io.StringIO()
            with redirect_stdout(saida_garcom):
                main.executar_simulacao(matriz, "garcom", verbose=True)

        texto_limpo = saida_limpa.getvalue()
        texto_verbose = saida_ordenacao.getvalue()
        texto_garcom = saida_garcom.getvalue()

        self.assertNotIn("ficou com sede", texto_limpo)
        self.assertIn("ficou tranquilo", texto_verbose)
        self.assertIn("ficou com sede", texto_verbose)
        self.assertIn("deseja as garrafas", texto_verbose)
        self.assertIn("tentando pegar", texto_verbose)
        self.assertIn("pegou G", texto_verbose)
        self.assertIn("está bebendo", texto_verbose)
        self.assertIn("liberou G", texto_verbose)
        self.assertIn("terminou seus ciclos", texto_verbose)
        self.assertIn("pediu permissão ao garçom", texto_garcom)
        self.assertIn("recebeu permissão do garçom", texto_garcom)
        self.assertIn("devolveu a permissão ao garçom", texto_garcom)

    def test_comando_todos_aceita_todos_os_diferenciais(self):
        execucoes = []

        def simulacao_resumida(matriz, tipo_solucao, verbose=False):
            execucoes.append((len(matriz), tipo_solucao))
            nome = (
                "Ordenação de Recursos"
                if tipo_solucao == "ordenacao"
                else "Garçom"
            )
            return {
                "solucao": nome,
                "tempo_total": 1.0,
                "espera_geral": 0.1,
                "maior_espera": 0.2,
                "menor_espera": 0.1,
                "deadlock": False,
                "starvation": False,
            }

        argumentos = [
            "main.py",
            "todos",
            "--seed",
            "42",
            "--csv",
            "--graficos",
            "--relatorio",
        ]

        with (
            patch.object(sys, "argv", argumentos),
            patch("main.executar_simulacao", side_effect=simulacao_resumida),
            patch(
                "main.salvar_comparacao_geral",
                return_value=Path("resultados/comparativo.csv"),
            ) as salvar_csv,
            patch(
                "main.gerar_graficos_todos",
                return_value=[
                    Path("resultados/tempo.png"),
                    Path("resultados/espera.png"),
                ],
            ) as gerar_graficos,
            patch(
                "main.gerar_relatorio_txt",
                return_value=Path("resultados/relatorio.txt"),
            ) as gerar_relatorio,
            redirect_stdout(io.StringIO()),
        ):
            codigo = main.main()

        self.assertEqual(codigo, 0)
        self.assertEqual(len(execucoes), 6)
        salvar_csv.assert_called_once()
        gerar_graficos.assert_called_once()
        gerar_relatorio.assert_called_once()


if __name__ == "__main__":
    unittest.main()
