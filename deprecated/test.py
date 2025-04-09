# Função para gerar a lista de números pseudoaleatórios
def pseudo_random_generator(seed, a, c, m, n=1000):
    pseudos = []
    pseudo = seed
    for i in range(n):
        pseudo = (a * pseudo + c) % m
        pseudos.append(pseudo)
    return pseudos


# Parâmetros do gerador (utilizados conforme fornecidos)
SEED = 987654321
A = 214013
C = 2531011
M = 98765432112
COUNT = 100000  # quantidade de números a serem utilizados na simulação

# Gerando a lista de pseudoaleatórios e normalizando entre 0 e 1
pseudolist = pseudo_random_generator(SEED, A, C, M, n=COUNT)
pseudolist = [p / M for p in pseudolist]
random_index = 0  # índice para consumir os números da lista


def get_next_random():
    """Retorna o próximo número pseudoaleatório da lista."""
    global random_index
    if random_index < len(pseudolist):
        r = pseudolist[random_index]
        random_index += 1
        return r
    else:
        raise Exception("Acabaram os números pseudoaleatórios.")


# Parâmetros da simulação
tempo_inicial = 2.0  # tempo do primeiro evento de chegada
# Parâmetros da fila (serão ajustados conforme o cenário)
# Usaremos capacidade total = 5 (incluindo os clientes em atendimento)
CAPACIDADE = 5
SERVIDORES = 1  # para o cenário G/G/1/5 (alterar para 2 para G/G/2/5)

# Intervalos para os tempos (ex.: chegadas entre 2 e 5, atendimento entre 3 e 5)
INTER_ARRIVAL_MIN = 2.0
INTER_ARRIVAL_MAX = 5.0
SERVICE_TIME_MIN = 3.0
SERVICE_TIME_MAX = 5.0

# Variáveis globais de simulação
current_time = 0.0  # tempo corrente da simulação
ultimo_evento_time = 0.0  # tempo do último evento processado
FILA = 0  # número de clientes no sistema (em espera + em serviço)
busy_servers = 0  # servidores ocupados
lost_customers = 0  # número de clientes perdidos por falta de espaço

# Agenda de eventos: lista de dicionários com "time" e "type"
EVENTOS = []

# Acumulação do tempo que o sistema passou em cada estado (0, 1, 2, ...)
tempo_estado = {}  # chave: número de clientes; valor: tempo acumulado


def schedule_event(event_type, event_time):
    """Agenda um evento adicionando-o à lista de eventos."""
    global EVENTOS
    EVENTOS.append({"time": event_time, "type": event_type})
    # Mantém a lista ordenada pelo tempo
    EVENTOS.sort(key=lambda ev: ev["time"])


def get_next_event():
    """Retorna e remove o próximo evento (com menor tempo) da agenda."""
    if EVENTOS:
        return EVENTOS.pop(0)
    return None


def random_uniform(min_val, max_val):
    """Gera um número aleatório com distribuição uniforme entre min_val e max_val."""
    r = get_next_random()
    return min_val + (max_val - min_val) * r


def atualiza_tempo_estado(new_time):
    """Atualiza a acumulação do tempo para o estado atual da fila."""
    global ultimo_evento_time, FILA, tempo_estado
    delta = new_time - ultimo_evento_time
    tempo_estado[FILA] = tempo_estado.get(FILA, 0) + delta
    ultimo_evento_time = new_time


def process_chegada(event):
    """Processa um evento de chegada."""
    global FILA, lost_customers, busy_servers, current_time

    atualiza_tempo_estado(event["time"])
    current_time = event["time"]

    # Agenda a próxima chegada, se houver números disponíveis
    try:
        proxima_chegada = current_time + random_uniform(
            INTER_ARRIVAL_MIN, INTER_ARRIVAL_MAX
        )
        schedule_event("chegada", proxima_chegada)
    except Exception as e:
        # Se acabarem os números, não agenda nova chegada
        pass

    # Verifica se há espaço na fila
    if FILA < CAPACIDADE:
        FILA += 1
        # Se houver servidor livre, inicia o atendimento imediatamente
        if busy_servers < SERVIDORES:
            busy_servers += 1
            tempo_servico = random_uniform(SERVICE_TIME_MIN, SERVICE_TIME_MAX)
            schedule_event("saida", current_time + tempo_servico)
    else:
        # Fila cheia: cliente perdido
        lost_customers += 1


def process_saida(event):
    """Processa um evento de saída (final de atendimento)."""
    global FILA, busy_servers, current_time

    atualiza_tempo_estado(event["time"])
    current_time = event["time"]

    # Um cliente concluiu o atendimento
    FILA -= 1
    busy_servers -= 1

    # Se houver clientes aguardando e servidor livre, inicia próximo atendimento
    if FILA - busy_servers > 0 and busy_servers < SERVIDORES:
        busy_servers += 1
        tempo_servico = random_uniform(SERVICE_TIME_MIN, SERVICE_TIME_MAX)
        schedule_event("saida", current_time + tempo_servico)


def simula_fila(
    capacidade,
    servidores,
    inter_arrival_min,
    inter_arrival_max,
    service_min,
    service_max,
    total_randoms,
):
    """
    Realiza a simulação da fila.
    Parâmetros:
      capacidade: capacidade total da fila (incluindo os clientes em serviço)
      servidores: número de servidores
      inter_arrival_min, inter_arrival_max: intervalo de tempo entre chegadas
      service_min, service_max: intervalo de tempo de atendimento
      total_randoms: número máximo de números pseudoaleatórios a serem utilizados
    Retorna:
      dicionário com tempo total de simulação, tempos acumulados por estado e número de clientes perdidos.
    """
    global \
        CAPACIDADE, \
        SERVIDORES, \
        INTER_ARRIVAL_MIN, \
        INTER_ARRIVAL_MAX, \
        SERVICE_TIME_MIN, \
        SERVICE_TIME_MAX
    global \
        current_time, \
        ultimo_evento_time, \
        FILA, \
        busy_servers, \
        lost_customers, \
        EVENTOS, \
        tempo_estado, \
        pseudolist, \
        random_index

    # Atualiza os parâmetros globais
    CAPACIDADE = capacidade
    SERVIDORES = servidores
    INTER_ARRIVAL_MIN = inter_arrival_min
    INTER_ARRIVAL_MAX = inter_arrival_max
    SERVICE_TIME_MIN = service_min
    SERVICE_TIME_MAX = service_max

    # Reinicializa variáveis de simulação
    current_time = 0.0
    ultimo_evento_time = 0.0
    FILA = 0
    busy_servers = 0
    lost_customers = 0
    EVENTOS = []
    tempo_estado = {}
    random_index = 0  # reinicia o índice para os números pseudoaleatórios

    # Agenda o primeiro evento de chegada
    schedule_event("chegada", tempo_inicial)

    # Loop principal: enquanto houver números pseudoaleatórios e eventos agendados
    while random_index < total_randoms and EVENTOS:
        event = get_next_event()
        if event is None:
            break
        if event["type"] == "chegada":
            process_chegada(event)
        elif event["type"] == "saida":
            process_saida(event)

    # Atualiza o tempo acumulado até o final da simulação
    atualiza_tempo_estado(current_time)

    # Calcula a distribuição de probabilidade dos estados
    total_tempo = current_time
    prob_estados = {
        estado: tempo / total_tempo for estado, tempo in tempo_estado.items()
    }

    return {
        "tempo_simulacao": total_tempo,
        "tempo_estado": tempo_estado,
        "prob_estados": prob_estados,
        "clientes_perdidos": lost_customers,
        "randoms_usados": random_index,
    }


def print_resultado(cenario, resultado):
    print(f"\n--- Resultado da simulação {cenario} ---")
    print(f"Tempo total de simulação: {resultado['tempo_simulacao']:.2f}")
    print("Tempo acumulado por estado (número de clientes no sistema):")
    for estado in sorted(resultado["tempo_estado"].keys()):
        print(
            f"  Estado {estado}: {resultado['tempo_estado'][estado]:.2f} "
            f"(Probabilidade: {resultado['prob_estados'][estado] * 100:.2f}%)"
        )
    print(f"Clientes perdidos: {resultado['clientes_perdidos']}")
    print(
        f"Total de números pseudoaleatórios utilizados: {resultado['randoms_usados']}"
    )


# Simulação para o cenário G/G/1/5 (1 servidor, capacidade 5)
resultado_GG1 = simula_fila(
    capacidade=5,
    servidores=1,
    inter_arrival_min=2.0,
    inter_arrival_max=5.0,
    service_min=3.0,
    service_max=5.0,
    total_randoms=COUNT,
)

# Para o cenário G/G/2/5, basta alterar o número de servidores para 2
resultado_GG2 = simula_fila(
    capacidade=5,
    servidores=2,
    inter_arrival_min=2.0,
    inter_arrival_max=5.0,
    service_min=3.0,
    service_max=5.0,
    total_randoms=COUNT,
)

print_resultado("G/G/1/5", resultado_GG1)
print_resultado("G/G/2/5", resultado_GG2)
