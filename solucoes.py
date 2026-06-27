"""Estratégias de sincronização usadas pelos filósofos."""

from threading import Lock, Semaphore

from garrafa import Garrafa
from log_simulacao import LogSimulacao


def registrar_evento(log: LogSimulacao | None, mensagem: str) -> None:
    """Registra uma mensagem quando um log foi fornecido."""
    if log is not None:
        log.registrar(mensagem)


def nomes_das_garrafas(garrafas: list[Garrafa]) -> str:
    """Monta uma lista curta de identificadores para o log."""
    return " e ".join(f"G{garrafa.identificador}" for garrafa in garrafas)


class SolucaoOrdenacao:
    """Adquire as garrafas seguindo uma ordem global de identificadores."""

    def adquirir(
        self,
        garrafas: list[Garrafa],
        filosofo: int | None = None,
        log: LogSimulacao | None = None,
    ) -> None:
        # A mesma ordem global elimina a possibilidade de espera circular.
        for garrafa in sorted(garrafas, key=lambda item: item.identificador):
            registrar_evento(
                log,
                f"F{filosofo} tentando pegar G{garrafa.identificador}.",
            )
            garrafa.lock.acquire()
            registrar_evento(
                log,
                f"F{filosofo} pegou G{garrafa.identificador}.",
            )

    def liberar(
        self,
        garrafas: list[Garrafa],
        filosofo: int | None = None,
        log: LogSimulacao | None = None,
    ) -> None:
        # A ordem inversa deixa a liberação coerente com a aquisição.
        for garrafa in sorted(
            garrafas,
            key=lambda item: item.identificador,
            reverse=True,
        ):
            garrafa.lock.release()
        registrar_evento(
            log,
            f"F{filosofo} liberou {nomes_das_garrafas(garrafas)}.",
        )


class SolucaoGarcom:
    """Controla a entrada dos filósofos e a retirada das garrafas."""

    def __init__(self, quantidade_filosofos: int):
        # O enunciado permite no máximo N - 1 filósofos tentando beber.
        limite = max(1, quantidade_filosofos - 1)
        self._permissoes = Semaphore(limite)
        self._controle_retirada = Lock()

    def adquirir(
        self,
        garrafas: list[Garrafa],
        filosofo: int | None = None,
        log: LogSimulacao | None = None,
    ) -> None:
        registrar_evento(log, f"F{filosofo} pediu permissão ao garçom.")
        self._permissoes.acquire()
        registrar_evento(log, f"F{filosofo} recebeu permissão do garçom.")
        garrafas_adquiridas = []

        try:
            # Apenas um filósofo por vez monta seu conjunto de garrafas.
            with self._controle_retirada:
                for garrafa in garrafas:
                    registrar_evento(
                        log,
                        f"F{filosofo} tentando pegar G{garrafa.identificador}.",
                    )
                    garrafa.lock.acquire()
                    garrafas_adquiridas.append(garrafa)
                    registrar_evento(
                        log,
                        f"F{filosofo} pegou G{garrafa.identificador}.",
                    )
        except Exception:
            # Desfaz a aquisição parcial antes de devolver o erro.
            for garrafa in reversed(garrafas_adquiridas):
                garrafa.lock.release()
            self._permissoes.release()
            raise

    def liberar(
        self,
        garrafas: list[Garrafa],
        filosofo: int | None = None,
        log: LogSimulacao | None = None,
    ) -> None:
        primeiro_erro = None

        for garrafa in garrafas:
            try:
                garrafa.lock.release()
            except Exception as erro:
                # Tenta liberar as demais mesmo se uma delas apresentar erro.
                if primeiro_erro is None:
                    primeiro_erro = erro

        # A vaga do garçom só é devolvida após liberar todas as garrafas.
        self._permissoes.release()
        registrar_evento(
            log,
            f"F{filosofo} liberou {nomes_das_garrafas(garrafas)} "
            "e devolveu a permissão ao garçom.",
        )

        if primeiro_erro is not None:
            raise primeiro_erro
