SERVIDORES = 1
CAPACIDADE = 5
PRIMEIRA_CHEGADA = 2
ARRIVAL_MIN = 2
ARRIVAL_MAX = 5
SERVICE_MIN = 3
SERVICE_MAX = 5  # TODO: esses min e max nao tao sendo usados, deveriam ser usados no pseudo random generator.... mas nao 'e o que o pseudo no moodle mostra

COUNT = 10  # quantidade de números a serem utilizados na simulação

FILA = 0
TEMPO_GLOBAL = 0

# selecionados na atividade anterior
PREV = 987654321
A = 214013
C = 2531011
M = 98765432112

TEMPOS = []
EVENTOS = []
PERDA = 0


def pseudo_random_generator(seed, a, c, m, n=1000):
    """ "
    seed: previous generated random number
    a: multiplier
    c: increment
    m: modulo
    n: number of random numbers to generate (default 1000)
    """

    pseudos = []
    pseudo = seed
    for i in range(n):
        pseudo = (a * pseudo + c) % m
        pseudos.append(pseudo)
    return pseudos


def next_random() -> float:
    """
    pega o próximo pseudo random numero
    """
    global PREV
    PREV = pseudo_random_generator(PREV, A, C, M, 1)[0]
    return float(PREV) / M


def next_event() -> dict | None:
    """
    pega o proximo evento (o evento que deve acontecer primeiro)
    """
    if len(EVENTOS) == 0:
        return None
    evento = EVENTOS.pop(0)
    print(f"Evento: {str(evento)}")
    return evento


def agendar(evento: str):
    """
    adiciona na lista de eventos a hora que o evento deve acontecer
        tempo global + próximo pseudo aleatorio
    e o tipo do evento (chegada ou saída)
    por fim, ordena a lista de acordo com a ordem de tempo
    """
    EVENTOS.append(
        {
            "time": TEMPO_GLOBAL + next_random(),
            "type": evento,
        }
    )
    EVENTOS.sort(key=lambda ev: ev["time"])


def saida(evento: dict):
    """
    aciona a saída de um cliente:
        calcula o delta do último estado da fila
        decrementa a fila
        se a fila é maior ou igual que a quantidade de servidores totais,
            agenda uma nova saída (ou seja, tinha alguém esperando pra ser atendido)
    """
    global FILA, SERVIDORES, TEMPO_GLOBAL

    calcular_tempo_estados(evento["time"])

    FILA -= 1
    if FILA >= SERVIDORES:
        agendar("saida")


def chegada(evento: dict):
    """
    aciona a chegada de um cliente:
        calcula o delta do último estado da fila
        incrementa a fila
        se a fila é menor que a capacidade, quem chegou pode entrar na fila
            se estiver cheia, aumenta a perda
        se o número de servidores ocupados é menor que a quantidade de servidores totais,
            agenda uma nova saída (ou seja, tinha alguém esperando pra ser atendido e tem gente liberado pra atender)
    """
    global FILA, CAPACIDADE, SERVIDORES, TEMPO_GLOBAL, PERDA
    calcular_tempo_estados(evento["time"])
    if FILA < CAPACIDADE:
        FILA += 1
        if FILA <= SERVIDORES:
            agendar("saida")
    else:
        PERDA += 1
    agendar("chegada")


def calcular_tempo_estados(tempo_evento: float):
    """
    calcula o delta tempo do último estado
        a posicao da quantidade de gente que teve na fila ate o momento
        é incrementada com o tempo do evento - tempo global
        e o tempo global é atualizado para o tempo do evento
    """
    global TEMPOS, TEMPO_GLOBAL

    TEMPOS[FILA] += tempo_evento - TEMPO_GLOBAL
    TEMPO_GLOBAL = tempo_evento


def main():
    global TEMPOS, EVENTOS
    TEMPOS = [0.0] * (CAPACIDADE + 1)
    EVENTOS = [
        {
            "time": PRIMEIRA_CHEGADA,
            "type": "chegada",
        }
    ]

    for i in range(COUNT):
        event = next_event()
        if event is None:
            print("Não há mais eventos")
            break

        if event["type"] == "chegada":
            chegada(event)
        elif event["type"] == "saida":
            saida(event)


def probabilities():
    for i in range(CAPACIDADE + 1):
        print(f"Probabilidade de {i} clientes na fila: {TEMPOS[i] / TEMPO_GLOBAL}")


def tempos_acumulados():
    for i in range(CAPACIDADE + 1):
        print(f"Tempo acumulado de {i} clientes na fila: {TEMPOS[i]}")


def printar_terminal():
    print("\n\n---------------------------------------------------------------------")
    print("- CONFIGURACOES -")
    print(f"Tipo de fila: G/G/{SERVIDORES}/{CAPACIDADE}")
    print(f"Primeira chegada: {PRIMEIRA_CHEGADA}")
    print(f"Chegadas entre: {ARRIVAL_MIN} e {ARRIVAL_MAX}")
    print(f"Serviços entre: {SERVICE_MIN} e {SERVICE_MAX}")
    print(f"Tempo de simulação: {COUNT}")
    print("\nVariaveis para pseudo aleatorios:")
    print(f"Seed: {PREV}")

    print("\n\n- RESULTADOS -")
    print("Tempos acumulados: ")
    tempos_acumulados()
    print("\nProbabilidades:")
    probabilities()
    print(f"\nTempo global: {TEMPO_GLOBAL}")
    print(f"\nPerda: {PERDA}")


if __name__ == "__main__":
    main()
    printar_terminal()
