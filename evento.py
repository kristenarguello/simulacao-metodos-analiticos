from typing import Literal

from fila import Fila


class Evento:
    def __init__(
        self,
        tipo: Literal["chegada", "saida", "passagem"],
        tempo: float,
        fila: Fila,
    ):
        self.fila = fila
        self.tipo = tipo
        self.tempo = tempo
