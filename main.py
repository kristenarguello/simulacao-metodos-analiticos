from escalonador import Escalonador
from evento import Evento
from fila import Fila

TEMPO_GLOBAL = 0.0


def acumula_tempo(evento: Evento, f: Fila):
    global TEMPO_GLOBAL
    f.contabiliza_tempo(evento.tempo - TEMPO_GLOBAL)
    TEMPO_GLOBAL = evento.tempo


def passagem(evento: Evento, f1: Fila, f2: Fila, escalonador: Escalonador):
    global TEMPO_GLOBAL

    acumula_tempo(evento, f1)
    acumula_tempo(evento, f2)

    f1.out()
    if f1.status() >= f1.servers:
        escalonador.add(
            Evento(
                tipo="passagem",
                tempo=TEMPO_GLOBAL,
                aleatorio=next_r(f1.min_service, f1.max_service),
            )
        )
    if f2.status() < f2.capacity:
        f2.in_()
        if f2.status() <= f2.servers:
            escalonador.add(
                Evento(
                    tipo="saida",
                    tempo=TEMPO_GLOBAL,
                    aleatorio=next_r(f2.min_service, f2.max_service),
                )
            )
    else:
        f2.loss()


def chegada(fila: Fila, evento: Evento, escalonador: Escalonador):
    acumula_tempo(evento, fila)
    if fila.capacity < fila.capacity:
        fila.in_()
        if fila.status() <= fila.servers:
            escalonador.add(
                Evento(
                    tipo="saida",
                    tempo=evento.tempo,
                    aleatorio=next_r(fila.min_service, fila.max_service),
                )
            )
    else:
        fila.loss()
    escalonador.add(
        Evento(
            tipo="chegada",
            tempo=evento.tempo,
            aleatorio=next_r(fila.min_arrival, fila.max_arrival),
        )
    )


def saida(fila: Fila, evento: Evento, escalonador: Escalonador):
    acumula_tempo(evento, fila)
    fila.out()
    if fila.status() >= fila.servers:
        escalonador.add(
            Evento(
                tipo="saida",
                tempo=evento.tempo,
                aleatorio=next_r(fila.min_service, fila.max_service),
            )
        )


def next_random(seed=987654321, a=214013, c=2531011, m=98765432112):
    pseudo = (a * seed + c) % m
    return float(pseudo) / m


def next_r(a: float, b: float):
    # U(a, b) = a + [(b - a)*x] para gerar um número uniformemente distribuído entre "a" e "b
    """
    Gera um número aleatório entre a e b (inclusive)
    """
    return a + ((b - a) * next_random())


# TODO: Receber os parâmetros de entrada
# numero de filas
# numero de servidores
# tempos de chegada/saída
def main():
    pass
    # Inicializa o escalonador

    # Adicionar o primeiro evento de chegada

    # Inicializa as filas

    # main loop


if __name__ == "__main__":
    # TODO: usar argparse para receber os parâmetros de entrada
    main()
