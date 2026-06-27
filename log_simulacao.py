"""Saída segura dos eventos produzidos pelas threads."""

from threading import Lock


class LogSimulacao:
    """Imprime mensagens completas sem sobreposição entre as threads."""

    def __init__(self, ativo: bool = False):
        self.ativo = ativo
        self._print_lock = Lock()

    def registrar(self, mensagem: str) -> None:
        """Mostra uma mensagem somente quando o modo verbose está ativo."""
        if not self.ativo:
            return

        with self._print_lock:
            print(mensagem, flush=True)
