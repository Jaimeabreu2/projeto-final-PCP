"""Testes das soluções concorrentes."""

import io
import unittest
from contextlib import redirect_stdout
from threading import Lock
from types import SimpleNamespace
from unittest.mock import patch

from grafo import carregar_matriz, criar_filosofos, criar_garrafas
from relatorio import exibir_comparacao, verificar_starvation
from solucoes import SolucaoGarcom, SolucaoOrdenacao


class TesteSolucoes(unittest.TestCase):
    def executar_solucao(self, solucao):
        matriz = carregar_matriz("matrizes/caso1.txt")
        garrafas = criar_garrafas(matriz)
        filosofos = criar_filosofos(matriz, garrafas)

        # Remove apenas as pausas para os testes terminarem rapidamente.
        with patch("filosofo.time.sleep", return_value=None):
            for filosofo in filosofos:
                filosofo.configurar_execucao(solucao, 2)
                filosofo.start()

            for filosofo in filosofos:
                filosofo.join(timeout=2)

        self.assertTrue(all(not filosofo.is_alive() for filosofo in filosofos))
        self.assertTrue(all(filosofo.erro is None for filosofo in filosofos))
        self.assertTrue(all(filosofo.vezes_bebeu == 2 for filosofo in filosofos))
        self.assertTrue(all(not garrafa.lock.locked() for garrafa in garrafas))

    def test_ordenacao_finaliza_sem_deadlock(self):
        self.executar_solucao(SolucaoOrdenacao())

    def test_garcom_finaliza_sem_deadlock(self):
        self.executar_solucao(SolucaoGarcom(5))

    def test_identifica_indicio_de_starvation(self):
        matriz = carregar_matriz("matrizes/caso1.txt")
        filosofos = criar_filosofos(matriz, criar_garrafas(matriz))

        for filosofo in filosofos:
            filosofo.tempo_com_sede = 1
            filosofo.vezes_bebeu = 1

        filosofos[-1].tempo_com_sede = 10

        self.assertTrue(verificar_starvation(filosofos))

    def test_garcom_desfaz_aquisicao_parcial_em_caso_de_erro(self):
        class LockComFalha:
            def acquire(self):
                raise RuntimeError("falha simulada")

        solucao = SolucaoGarcom(2)
        primeiro_lock = Lock()
        garrafas = [
            SimpleNamespace(identificador=0, lock=primeiro_lock),
            SimpleNamespace(identificador=1, lock=LockComFalha()),
        ]

        with self.assertRaises(RuntimeError):
            solucao.adquirir(garrafas)

        self.assertFalse(primeiro_lock.locked())
        self.assertTrue(solucao._permissoes.acquire(blocking=False))
        solucao._permissoes.release()

    def test_garcom_libera_os_demais_recursos_apos_erro(self):
        class LockComFalha:
            def release(self):
                raise RuntimeError("falha simulada")

        solucao = SolucaoGarcom(2)
        segundo_lock = Lock()
        segundo_lock.acquire()
        solucao._permissoes.acquire()
        garrafas = [
            SimpleNamespace(identificador=0, lock=LockComFalha()),
            SimpleNamespace(identificador=1, lock=segundo_lock),
        ]

        with self.assertRaises(RuntimeError):
            solucao.liberar(garrafas)

        self.assertFalse(segundo_lock.locked())
        self.assertTrue(solucao._permissoes.acquire(blocking=False))
        solucao._permissoes.release()

    def test_comparacao_mostra_metricas_e_conclusao(self):
        resumos = [
            {
                "solucao": "Ordenação de Recursos",
                "tempo_total": 20.0,
                "espera_geral": 0.5,
                "maior_espera": 0.8,
                "menor_espera": 0.2,
                "deadlock": False,
                "starvation": False,
            },
            {
                "solucao": "Garçom",
                "tempo_total": 22.0,
                "espera_geral": 0.6,
                "maior_espera": 0.7,
                "menor_espera": 0.3,
                "deadlock": False,
                "starvation": False,
            },
        ]

        saida = io.StringIO()
        with redirect_stdout(saida):
            exibir_comparacao(resumos)

        texto = saida.getvalue()
        self.assertIn("Menor", texto)
        self.assertIn("Deadlock", texto)
        self.assertIn("Starvation", texto)
        self.assertIn("Conclusão:", texto)


if __name__ == "__main__":
    unittest.main()
