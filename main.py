import argparse

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
                fila=1,
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
                    fila=2,
                )
            )
    else:
        f2.loss()


def chegada(fila: Fila, evento: Evento, escalonador: Escalonador):
    acumula_tempo(evento, fila)
    if fila.status() < fila.capacity:
        fila.in_()
        if fila.status() <= fila.servers:
            if fila.id == 1:
                escalonador.add(
                    Evento(
                        tipo="passagem",
                        tempo=evento.tempo,
                        aleatorio=next_r(fila.min_service, fila.max_service),
                        fila=fila.id,
                    )
                )
            else:
                escalonador.add(
                    Evento(
                        tipo="saida",
                        tempo=evento.tempo,
                        aleatorio=next_r(fila.min_service, fila.max_service),
                        fila=fila.id,
                    )
                )
    else:
        fila.loss()
    escalonador.add(
        Evento(
            tipo="chegada",
            tempo=evento.tempo,
            aleatorio=next_r(fila.min_arrival, fila.max_arrival),
            fila=fila.id,
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
                fila=fila.id,
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


def main(
    servers1: int,
    min_arrival1: float,
    max_arrival1: float,
    min_service1: float,
    max_service1: float,
    capacity1: int,
    servers2: int,
    min_arrival2: float,
    max_arrival2: float,
    min_service2: float,
    max_service2: float,
    capacity2: int,
    num_iteracoes: int,
):
    # Inicializa o escalonador
    escalonador = Escalonador()

    # Adicionar o primeiro evento de chegada (qual evento?)
    escalonador.add(
        Evento(
            tipo="chegada",
            tempo=1.5,
            aleatorio=0.0,
            fila=1,
        )
    )

    # Inicializa as filas
    fila_1 = Fila(
        id=1,
        servers=servers1,
        capacity=capacity1,
        min_arrival=min_arrival1,  # use the arrival interval for queue 1
        max_arrival=max_arrival1,
        min_service=min_service1,  # use the service interval for queue 1
        max_service=max_service1,
    )

    fila_2 = Fila(
        id=2,
        servers=servers2,
        capacity=capacity2,
        min_arrival=min_arrival2,  # even though Fila 2 receives customers from queue 1, you can set this as needed (here we use the service interval)
        max_arrival=max_arrival2,
        min_service=min_service2,  # service interval for queue 2
        max_service=max_service2,
    )
    # main loop
    for _ in range(num_iteracoes):
        evento = escalonador.next_event()
        if evento is None:
            print("Nenhum evento agendado")
            break

        if evento.tipo == "chegada":
            chegada(fila_1, evento, escalonador)

        elif evento.tipo == "saida":
            saida(fila_2, evento, escalonador)

        elif evento.tipo == "passagem":
            passagem(evento, fila_1, fila_2, escalonador)

    # Exibe os resultados
    print(f"Fila 1: {fila_1.losses} perdas na fila")
    print(f"Fila 2: {fila_2.losses} perdas na fila")
    print("Tempo de simulação: ", TEMPO_GLOBAL)

    for i in range(fila_1.capacity + 1):
        print(
            f"Probabilidade de {i} clientes na fila 1: {fila_1.times[i] / TEMPO_GLOBAL}"
        )
    for i in range(fila_2.capacity + 1):
        print(
            f"Probabilidade de {i} clientes na fila 2: {fila_2.times[i] / TEMPO_GLOBAL}"
        )

    for i in range(fila_1.capacity + 1):
        print(
            f"Tempo acumulado de {i} clientes na fila 1: {fila_1.times[i]}",
        )

    for i in range(fila_2.capacity + 1):
        print(
            f"Tempo acumulado de {i} clientes na fila 2: {fila_2.times[i]}",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulação de métodos analíticos")
    parser.add_argument(
        "--servers1", type=int, required=True, help="Número de servidores da fila 1"
    )

    parser.add_argument(
        "--min_arrival1",
        type=float,
        required=True,
        help="Tempo mínimo entre chegadas da fila 1",
    )
    parser.add_argument(
        "--max_arrival1",
        type=float,
        required=True,
        help="Tempo máximo entre chegadas da fila 1",
    )
    parser.add_argument(
        "--min_service1",
        type=float,
        required=True,
        help="Tempo mínimo de serviço da fila 1",
    )
    parser.add_argument(
        "--max_service1",
        type=float,
        required=True,
        help="Tempo máximo de serviço da fila 1",
    )
    parser.add_argument(
        "--capacity1",
        type=int,
        required=True,
        help="Capacidade máxima da fila 1",
    )
    parser.add_argument(
        "--servers2", type=int, required=True, help="Número de servidores da fila 2"
    )
    parser.add_argument(
        "--min_arrival2",
        type=float,
        required=True,
        help="Tempo mínimo entre chegadas da fila 2",
    )
    parser.add_argument(
        "--max_arrival2",
        type=float,
        required=True,
        help="Tempo máximo entre chegadas da fila 2",
    )
    parser.add_argument(
        "--min_service2",
        type=float,
        required=True,
        help="Tempo mínimo de serviço da fila 2",
    )
    parser.add_argument(
        "--max_service2",
        type=float,
        required=True,
        help="Tempo máximo de serviço da fila 2",
    )
    parser.add_argument(
        "--capacity2",
        type=int,
        required=True,
        help="Capacidade máxima da fila 2",
    )
    parser.add_argument(
        "--num_iteracoes",
        type=int,
        required=True,
        help="Número de iterações para a simulação",
    )
    args = parser.parse_args()

    main(
        args.servers1,
        args.min_arrival1,
        args.max_arrival1,
        args.min_service1,
        args.max_service1,
        args.capacity1,
        args.servers2,
        args.min_arrival2,
        args.max_arrival2,
        args.min_service2,
        args.max_service2,
        args.capacity2,
        args.num_iteracoes,
    )
