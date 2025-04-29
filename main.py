import argparse
import random

import yaml

from escalonador import Escalonador
from evento import Evento
from fila import Fila

TEMPO_GLOBAL = 0.0
rndnumbers = []
rnd_idx = 0

random_limit = 0


def next_rnd():
    global rnd_idx
    if rnd_idx >= len(rndnumbers):
        print(
            "⚠️  Todos os números aleatórios foram consumidos. Encerrando simulação..."
        )
        raise StopIteration
    r = rndnumbers[rnd_idx]
    rnd_idx += 1
    return r


def acumula_tempo(filas, current_time: float):
    lista_filas: list[Fila] = list(filas.values())
    for fila in lista_filas:
        fila.acumula_tempo(current_time)


def chegada(
    evento: Evento,
    filas,
    escalonador: Escalonador,
):
    global TEMPO_GLOBAL
    fila: Fila = filas[evento.fila]

    acumula_tempo(filas, evento.tempo)
    TEMPO_GLOBAL = evento.tempo

    if fila.tem_espaco():
        fila.add_cliente()
        escalonador.add(
            Evento(
                tipo="passagem",
                tempo=next_service_time(fila),
                fila=evento.fila,
            )
        )
    else:
        fila.losses += 1

    # Agenda próxima chegada
    escalonador.add(
        Evento(
            tipo="chegada",
            tempo=next_service_time(fila),
            fila=evento.fila,
        )
    )


def passagem(evento: Evento, filas, escalonador: Escalonador, network):
    global TEMPO_GLOBAL
    fila_atual = filas[evento.fila]

    acumula_tempo(filas, evento.tempo)
    TEMPO_GLOBAL = evento.tempo

    # terminou um serviço
    fila_atual.remove_cliente()

    # se ainda sobra gente na fila além dos servidores em ação,
    # significa que alguém estava esperando e entra em serviço agora
    if fila_atual.customers >= fila_atual.servers:
        escalonador.add(
            Evento(
                tipo="passagem",
                tempo=next_service_time(fila_atual),
                fila=fila_atual.id,
            )
        )

    # roteamento do cliente que acabou de sair dessa fila
    destino = sorteia_destino(network, fila_atual.id)

    fila_dest = filas[destino]
    if not fila_dest.add_cliente():  # perda no destino
        return

    if destino.startswith("sa"):
        escalonador.add(
            Evento(
                tipo="saida",
                tempo=next_service_time(fila_atual),
                fila=fila_atual,
            ),
        )

    if fila_dest.customers <= fila_dest.servers:
        escalonador.add(
            Evento(
                tipo="passagem",
                tempo=next_service_time(fila_dest),
                fila=destino,
            )
        )


def sorteia_destino(network, origem) -> str:
    if origem not in network:
        raise ValueError(f"Origem {origem} não encontrada na rede.")
    destinos = network[origem]
    x = random.uniform(0, 1)  # TODO: make sure of this

    soma = 0.0
    for destino, prob in destinos:
        if x < soma:
            return destino
        else:
            soma += prob

    raise ValueError(
        f"Erro ao sortear destino: soma das probabilidades {soma} não é igual a 1."
    )


def saida(evento, filas, escalonador):
    global TEMPO_GLOBAL
    fila: Fila = filas[evento.fila]

    acumula_tempo(filas, evento.tempo)

    TEMPO_GLOBAL = evento.tempo
    fila.remove_cliente()


def next_service_time(fila: Fila):
    return TEMPO_GLOBAL + (
        fila.min_service + (fila.max_service - fila.min_service) * next_rnd()
    )


def main(config):
    global rndnumbers

    filas = {}
    network = {}

    # Pré-processa números aleatórios
    if "seeds" in config:
        random.seed(config["seeds"][0])
        rndnumbers = [
            random.random() for _ in range(config["rndnumbersPerSeed"])
        ]  # TODO: need to change this random generator thing
    else:
        rndnumbers = config["rndnumbers"]

    escalonador = Escalonador()

    # Cria filas
    for fila_nome, fila_cfg in config["queues"].items():
        fila = Fila(
            id=fila_nome,
            servers=fila_cfg["servers"],
            capacity=fila_cfg["capacity"],
            min_arrival=fila_cfg.get("minArrival", 0),
            max_arrival=fila_cfg.get("maxArrival", 0),
            min_service=fila_cfg["minService"],
            max_service=fila_cfg["maxService"],
        )
        filas[fila_nome] = fila

    # Cria o mapa da rede
    for regra in config["network"]:
        source = regra["source"]
        target = regra["target"]
        prob = regra["probability"]
        if source not in network:
            network[source] = []
        network[source].append((target, prob))

    # Adiciona eventos de chegada
    for fila_nome, chegada_tempo in config["arrivals"].items():
        escalonador.add(
            Evento(
                tipo="chegada",
                tempo=chegada_tempo,
                fila=fila_nome,
            )
        )
    try:
        while True:
            evento = escalonador.next_event()
            # only queues 2 and 3 can have saida events
            # queue one

            if evento is None:
                print("Fim da simulação")
                break

            if evento.tipo == "chegada":
                chegada(
                    evento,
                    filas,
                    escalonador,
                )

            elif evento.tipo == "passagem":  # # make sure the events are
                passagem(
                    evento,
                    filas,
                    escalonador,
                    network,
                )

            elif evento.tipo == "saida":
                saida(evento, filas, escalonador)
    except ValueError as e:
        print(f"Erro: {e}")
    except StopIteration:
        print("Quantidade de números aleatórios finalizada.")

    # Impressão dos resultados
    for nome, fila in filas.items():
        print(f"Fila {nome}: {fila.losses} perdas na fila")
        print(f"Tempo de simulação: {TEMPO_GLOBAL}")
        for i in range(fila.capacity + 1):
            print(f"Probabilidade de {i} clientes: {fila.times[i] / TEMPO_GLOBAL}")


def unknown_tag_handler(loader, tag_suffix, node):
    return loader.construct_mapping(node)


class IgnoreUnknownLoader(yaml.SafeLoader):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulador de filas")
    parser.add_argument(
        "--config", type=str, required=True, help="Arquivo de configuração YAML"
    )
    args = parser.parse_args()

    path = args.config

    IgnoreUnknownLoader.add_multi_constructor("", unknown_tag_handler)

    with open(path, "r") as f:
        data = yaml.load(f, Loader=IgnoreUnknownLoader)

    # print(data)

    main(data)
