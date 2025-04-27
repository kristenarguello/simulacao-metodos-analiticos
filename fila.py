from collections import deque


class Fila:
    def __init__(
        self,
        id: str,
        servers: int,
        capacity: int,
        min_arrival: float = 0.0,
        max_arrival: float = 0.0,
        min_service: float = 0.0,
        max_service: float = 0.0,
    ):
        """
        Classe que representa uma fila em um sistema de eventos discretos.

        Parâmetros
        ----------
        id : str
            Identificador único da fila.
        servers : int
            Número de servidores da fila (para simulações futuras).
        capacity : int
            Capacidade máxima (tamanho) da fila.
        min_arrival : float
            Tempo mínimo entre chegadas de clientes.
        max_arrival : float
            Tempo máximo entre chegadas de clientes.
        min_service : float
            Tempo mínimo de serviço.
        max_service : float
            Tempo máximo de serviço.
        """
        self.id = id
        self.servers = servers
        self.capacity = capacity
        self.min_arrival = min_arrival
        self.max_arrival = max_arrival
        self.min_service = min_service
        self.max_service = max_service

        # Armazena clientes em espera (FIFO)
        # self.queue = deque()
        # Tempo da última atualização para cálculo de médias
        self.last_time = 0.0
        # Contadores de estado
        self.customers = 0  # Número atual de clientes
        self.losses = 0  # Clientes perdidos por fila cheia
        # Acumula tempo em cada estado (0..capacity)
        self.times = [0.0] * (capacity + 1)

    def status(self) -> int:
        """Retorna o número de clientes na fila."""
        return self.customers

    def tem_espaco(self) -> bool:
        """Retorna True se ainda houver espaço na fila."""
        return self.customers < self.capacity

    def add_cliente(self) -> None:
        """
        Insere um cliente na fila (se houver espaço) e conta perda se não couber.

        Parâmetros
        ----------
        cliente : qualquer
            Identificador ou objeto do cliente.
        """
        if self.tem_espaco():
            # self.queue.append(cliente)
            self.customers += 1
        else:
            self.losses += 1

    def remove_cliente(self):
        """
        Remove (e retorna) o cliente que está há mais tempo na fila.
        Se a fila estiver vazia, retorna None.
        """
        if self.customers > 0:
            # cliente = self.queue.popleft()
            self.customers -= 1
            return 1
            # return cliente
        return None

    def acumula_tempo(self, current_time: float) -> None:
        """
        Atualiza o acumulador de tempo no estado atual (n clientes) desde
        a última chamada.

        Parâmetros
        ----------
        current_time : float
            Horário do evento que disparou esta atualização.
        """
        delta = current_time - self.last_time
        self.times[self.customers] += delta
        self.last_time = current_time

    def __repr__(self):
        return f"Fila(id={self.id!r}, customers={self.customers}, losses={self.losses})"
