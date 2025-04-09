class Fila:
    def __init__(
        self,
        servers: int,
        capacity: int,
        min_arrival: float,
        max_arrival: float,
        min_service: float,
        max_service: float,
    ):
        """
        Classe que representa uma fila em um sistema de eventos discretos.

        Parametros
        ----------
        server : int
            Numero de servidores da fila.
        capacity : int
            Capacidade maxima (tamanho) da fila.
        min_arrival : float
            Tempo minimo entre chegadas de clientes.
        max_arrival : float
            Tempo maximo entre chegadas de clientes.
        min_service : float
            Tempo minimo de servico.
        max_service : float
            Tempo maximo de servico.
        """
        self.servers = servers
        self.capacity = capacity
        self.min_arrival = min_arrival
        self.max_arrival = max_arrival
        self.min_service = min_service
        self.max_service = max_service

        self.times = [0.0] * (capacity + 1)

        # Contadores de estado
        self.customers = 0  # Número atual de clientes na fila
        self.losses = 0  # Número de clientes perdidos (se fila cheia)

    def status(self) -> int:
        return self.customers

    # =============
    # SETTERS / PROCEDIMENTOS
    # =============
    def loss(self) -> int:
        """
        (int) Loss():
        Incrementa a propriedade Loss (perdas) em uma unidade,
        contabilizando mais uma perda (quando a fila ja estava cheia).

        Retorna o valor atualizado de Loss.
        """
        self.losses += 1
        return self.losses

    def in_(self) -> None:
        """
        (void) In():
        Incrementa a propriedade Customers em uma unidade, contabilizando que
        chegou um cliente na fila. Se a fila estiver cheia, conta como perda.
        """
        if self.customers < self.capacity:
            self.customers += 1
        else:
            # Se a fila estiver no limite, incrementa perda.
            self.loss()

    def out(self) -> None:
        """
        (void) Out():
        Decrementa a propriedade Customers em uma unidade, contabilizando que
        um cliente saiu da fila (atendimento finalizado ou abandono).
        """
        if self.customers > 0:
            self.customers -= 1

    def contabiliza_tempo(self, tempo: float):
        self.times[self.capacity] += tempo

    def __repr__(self):
        """
        Retorna uma representacao em string da Fila,
        util para debug ou logs.
        """
        return ""
