from typing import Literal


class Evento:
    def __init__(
        self,
        tipo: Literal["chegada", "saida", "passagem"],
        tempo: float,
        aleatorio: float,
    ):
        self.tipo = tipo
        self.tempo = tempo + aleatorio
