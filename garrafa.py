"""Representação das garrafas compartilhadas entre os filósofos."""

from threading import Lock


class Garrafa:
    """Recurso compartilhado associado a uma aresta do grafo."""

    def __init__(self, identificador: int, filosofo_a: int, filosofo_b: int):
        self.identificador = identificador
        self.filosofo_a = filosofo_a
        self.filosofo_b = filosofo_b

        # O lock garante que apenas um filósofo use a garrafa por vez.
        self.lock = Lock()

    def __str__(self) -> str:
        return (
            f"Garrafa {self.identificador} "
            f"(filósofos {self.filosofo_a} e {self.filosofo_b})"
        )
