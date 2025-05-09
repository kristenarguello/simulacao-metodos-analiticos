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


def next_rnd() -> float:
    global rnd_idx
    if rnd_idx >= len(rndnumbers):
        print(
            "⚠️  Todos os números aleatórios foram consumidos. Encerrando simulação..."
        )
        raise StopIteration
    r = rndnumbers[rnd_idx]
    rnd_idx += 1
    return r


def acumula_tempo(
    filas: dict[str, Fila],
    current_time: float,
):
    for fila in filas.values():
        fila.acumula_tempo(current_time)


def chegada(
    evento: Evento,
    filas: dict[str, Fila],
    escalonador: Escalonador,
):
    global TEMPO_GLOBAL
    fila = evento.fila

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


def passagem(
    evento: Evento,
    filas: dict[str, Fila],
    escalonador: Escalonador,
    network: dict[str, list[tuple[str, float]]],
):
    global TEMPO_GLOBAL
    fila_atual = filas[evento.fila.id]

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
                fila=fila_atual,
            )
        )

    # roteamento do cliente que acabou de sair dessa fila
    destino = sorteia_destino(
        network=network,
        filas=filas,
        origem=fila_atual,
    )

    if destino.startswith("sa"):
        escalonador.add(
            Evento(
                tipo="saida",
                tempo=next_service_time(fila_atual),
                fila=fila_atual,
            ),
        )
    else:
        destino = filas[destino]
        if not destino.add_cliente():  # perda no destino
            return

        if destino.customers <= destino.servers:
            escalonador.add(
                Evento(
                    tipo="passagem",
                    tempo=next_service_time(destino),
                    fila=destino,
                )
            )


def sorteia_destino(
    network: dict[str, list[tuple[str, float]]],
    filas: dict[str, Fila],
    origem: Fila,
) -> str:
    if network.get(origem.id) is None:
        raise ValueError(f"Fila {origem.id} não tem destinos definidos.")

    destinos = network[origem.id]
    prob = random.uniform(0.0, 1.0)

    soma = 0.0
    for destino, f_prob in destinos:
        soma += f_prob
        if prob < soma:
            return destino

    raise ValueError(
        f"Erro ao sortear destino: soma das probabilidades {soma} não é 1.0 ou número aleatório {prob} fora de faixa"
    )


def saida(
    evento: Evento,
    filas: dict[str, Fila],
    escalonador: Escalonador,
):
    global TEMPO_GLOBAL
    fila: Fila = filas[evento.fila.id]

    acumula_tempo(filas, evento.tempo)

    TEMPO_GLOBAL = evento.tempo
    fila.remove_cliente()


def next_service_time(fila: Fila):
    return TEMPO_GLOBAL + (
        fila.min_service + (fila.max_service - fila.min_service) * next_rnd()
    )


def main(config):
    global rndnumbers
    filas: dict[str, Fila] = {}
    network: dict[str, list[tuple[str, float]]] = {}  # origin, [target, prob]

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
                fila=filas[fila_nome],
            )
        )
    try:
        while True:
            evento = escalonador.next_event()

            if evento is None:
                print("Fim da simulação")
                break

            if evento.tipo == "chegada":
                chegada(
                    evento=evento,
                    filas=filas,
                    escalonador=escalonador,
                )

            elif evento.tipo == "passagem":  # # make sure the events are
                passagem(
                    evento=evento,
                    filas=filas,
                    escalonador=escalonador,
                    network=network,
                )

            elif evento.tipo == "saida":
                saida(
                    evento=evento,
                    filas=filas,
                    escalonador=escalonador,
                )
    except ValueError as e:
        print(f"Erro: {e}")
    except StopIteration:
        print("Quantidade de números aleatórios finalizada.")

    # Impressão dos resultados
    print("=" * 57)
    print("=" * 22 + "    REPORT   " + "=" * 22)
    print("=" * 57)

    for name in filas:
        fila = filas[name]

        print("*" * 57)
        print(f"Queue:   {name} (G/G/{fila.servers}/{fila.capacity})")  # Ex: G/G/1/99
        print(f"Arrival: {fila.min_arrival} ... {fila.max_arrival}")
        print(f"Service: {fila.min_service} ... {fila.max_service}")
        print("*" * 57)

        print(f"{'State':>7} {'Time':>20} {'Probability':>20}")
        for i in range(len(fila.times)):
            tempo = fila.times[i]
            prob = tempo / TEMPO_GLOBAL
            print(f"{i:7d} {tempo:20.4f} {prob * 100:19.2f}%")

        print(f"\nNumber of losses: {fila.losses}\n")

    print("=" * 57)
    print(f"Simulation average time: {TEMPO_GLOBAL:.4f}")
    print("=" * 57)


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
