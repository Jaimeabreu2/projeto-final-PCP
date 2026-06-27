"""Representação dos filósofos do bar."""

import random
import time
from threading import Thread

from garrafa import Garrafa
from log_simulacao import LogSimulacao


class Filosofo(Thread):
    """Thread que representa um filósofo durante a simulação."""

    def __init__(self, identificador: int, garrafas: list[Garrafa]):
        super().__init__(name=f"Filosofo-{identificador}", daemon=True)

        self.identificador = identificador
        self.garrafas = garrafas
        self.estado = "tranquilo"
        self.vezes_bebeu = 0
        self._solucao = None
        self._quantidade_ciclos = 0
        self._log = LogSimulacao()
        self.erro: Exception | None = None

        # Estes tempos serão atualizados durante a simulação.
        self.tempo_tranquilo = 0.0
        self.tempo_com_sede = 0.0
        self.tempo_bebendo = 0.0

    def configurar_execucao(
        self,
        solucao,
        quantidade_ciclos: int,
        log: LogSimulacao | None = None,
    ) -> None:
        """Define a solução e o número de vezes que o filósofo beberá."""
        self._solucao = solucao
        self._quantidade_ciclos = quantidade_ciclos
        if log is not None:
            self._log = log

    def escolher_garrafas(self) -> list[Garrafa]:
        """Sorteia um subconjunto das garrafas adjacentes."""
        # Nos grafos fornecidos, cada filósofo possui pelo menos duas garrafas.
        quantidade_minima = min(2, len(self.garrafas))
        quantidade = random.randint(quantidade_minima, len(self.garrafas))
        return random.sample(self.garrafas, quantidade)

    def run(self) -> None:
        """Executa os ciclos tranquilo, com sede e bebendo."""
        try:
            self._executar_ciclos()
        except Exception as erro:
            # O programa principal verificará o erro após o término da thread.
            self.erro = erro

    def _executar_ciclos(self) -> None:
        """Executa internamente os ciclos configurados."""
        if self._solucao is None:
            raise RuntimeError(
                f"o filósofo {self.identificador} não possui uma estratégia."
            )

        for _ in range(self._quantidade_ciclos):
            # Estado 1: aguarda um tempo aleatório sem usar recursos.
            self.estado = "tranquilo"
            self._log.registrar(f"F{self.identificador} ficou tranquilo.")
            inicio = time.perf_counter()
            time.sleep(random.uniform(0, len(self.garrafas)))
            self.tempo_tranquilo += time.perf_counter() - inicio

            # Estado 2: o tempo de espera termina após obter todas as garrafas.
            self.estado = "com sede"
            self._log.registrar(f"F{self.identificador} ficou com sede.")
            garrafas_desejadas = self.escolher_garrafas()
            nomes = " e ".join(
                f"G{garrafa.identificador}" for garrafa in garrafas_desejadas
            )
            self._log.registrar(
                f"F{self.identificador} deseja as garrafas {nomes}."
            )
            inicio = time.perf_counter()
            self._solucao.adquirir(
                garrafas_desejadas,
                self.identificador,
                self._log,
            )
            self.tempo_com_sede += time.perf_counter() - inicio

            try:
                # Estado 3: bebe por um segundo com os recursos bloqueados.
                self.estado = "bebendo"
                self._log.registrar(f"F{self.identificador} está bebendo.")
                inicio = time.perf_counter()
                time.sleep(1)
                self.tempo_bebendo += time.perf_counter() - inicio
                self.vezes_bebeu += 1
            finally:
                # O finally libera as garrafas mesmo se ocorrer algum erro.
                self._solucao.liberar(
                    garrafas_desejadas,
                    self.identificador,
                    self._log,
                )

            self.estado = "tranquilo"
            self._log.registrar(
                f"F{self.identificador} voltou ao estado tranquilo."
            )

        self.estado = "tranquilo"
        self._log.registrar(f"F{self.identificador} terminou seus ciclos.")

    def calcular_espera_media(self) -> float:
        """Calcula a espera média antes de cada vez que o filósofo bebeu."""
        if self.vezes_bebeu == 0:
            return 0.0

        return self.tempo_com_sede / self.vezes_bebeu

    def __str__(self) -> str:
        ids_garrafas = [garrafa.identificador for garrafa in self.garrafas]
        return (
            f"Filósofo {self.identificador} | estado: {self.estado} | "
            f"garrafas: {ids_garrafas}"
        )
