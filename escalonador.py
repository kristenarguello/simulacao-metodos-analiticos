from typing import Optional

from evento import Evento


class Escalonador:
    def __init__(self):
        self.eventos: list[Evento] = []
        self.tempos: list[float] = []

    def add(self, evento: Evento):
        self.eventos.append(evento)
        self.eventos.sort(key=lambda ev: ev.tempo)

    def next_event(self) -> Evento | None:
        if len(self.eventos) == 0:
            return None

        return self.eventos.pop(0)
