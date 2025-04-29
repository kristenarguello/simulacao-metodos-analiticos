from typing import Literal


class Evento:
    def __init__(
        self,
        tipo: Literal["chegada", "saida", "passagem"],
        tempo: float,
        fila: str = "",
    ):
        self.fila = fila
        self.tipo = tipo
        self.tempo = tempo
