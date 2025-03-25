from geracao_aleatorios import pseudo_random_generator

CAPACIDADE = 3
SERVIDORES = 2
global FILA = 0

global TEMPO_GLOBAL = 0

PRIMEIRA_CHEGADA = 0
ARRIVAL_MIN = 0
ARRIVAL_MAX = 1
SERVICE_MIN = 0
SERVICE_MAX = 1

# selecionados na atividade anterior
COUNT = 100000  # quantidade de números a serem utilizados na simulação
SEED = 987654321
A = 214013
C = 2531011
M = 98765432112

global TEMPOS = []
global EVENTOS = []

# stats
PERDA = 0

def next_random() -> float:
    """
    pega o próximo pseudo random numero
    """
    PREV = pseudo_random_generator(PREV, A, C, M, 1)[0]
    return (float)PREV/M

def next_event():
    """
    pega o proximo evento (o evento que deve acontecer primeiro)
    """
    if len(EVENTOS) == 0:
        return None
    return EVENTOS.pop(0)

def agendar(evento:dict):
    """
    adiciona na lista de eventos a hora que o evento deve acontecer
        tempo global + próximo pseudo aleatorio
    e o tipo do evento (chegada ou saída)
    por fim, ordena a lista de acordo com a ordem de tempo
    """
    # adicionar no EVENTOS com o tempo que seria scheduled o evento em si
    if evento == "chegada":
        EVENTOS.append({"time": TEMPO_GLOBAL + next_random(), "type": "chegada"})
    elif evento == "saida":
        EVENTOS.append({"time": TEMPO_GLOBAL + next_random(), "type": "saida"})
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

def chegada(evento :dict):
    """
    aciona a chegada de um cliente: 
        calcula o delta do último estado da fila
        incrementa a fila
        se a fila é menor que a capacidade, quem chegou pode entrar na fila
            se estiver cheia, aumenta a perda
        se o número de servidores ocupados é menor que a quantidade de servidores totais,
            agenda uma nova saída (ou seja, tinha alguém esperando pra ser atendido e tem gente liberado pra atender)
    """
    global FILA, CAPACIDADE, SERVIDORES, TEMPO_GLOBAL
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
    for i in range(COUNT): 
        event = next_event()  
        if event["type"] == "chegada": 
            chegada(event)
        elif event["type"] == "saida": 
            saida(event)


if __name__ == "__main__":
    main()
