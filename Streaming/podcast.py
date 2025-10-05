# Streaming/podcast.py
from .arquivo_de_midia import ArquivoDeMidia

class Podcast(ArquivoDeMidia):
    """
    Subclasse de ArquivoDeMidia que representa um podcast.
    Atributos extras: temporada (str), episodio (int) e host (str).
    """

    def __init__(self, titulo: str, duracao: int, artista: str,
                 temporada: str, episodio: int, host: str, reproducoes: int = 0):
        """
        Inicializa um objeto Podcast.
        - temporada: nome da temporada (ex: 'TechTalks')
        - episodio: número inteiro do episódio
        - host: nome do apresentador principal
        """
        super().__init__(titulo, duracao, artista, reproducoes)

        self.temporada = temporada.strip()
        self.host = host.strip()

        # Validação do episódio
        if not isinstance(episodio, int) or episodio <= 0:
            raise ValueError("Episódio inválido: deve ser um número inteiro positivo.")
        self.episodio = episodio

    def __str__(self) -> str:
        """Representação amigável com as principais informações do podcast."""
        return (f"Podcast: {self.titulo} | Temporada: {self.temporada} | "
                f"Episódio: {self.episodio} | Host: {self.host} | "
                f"Duração: {self.duracao}s | Reproduções: {self.reproducoes}")

    def __repr__(self) -> str:
        """Representação detalhada para depuração."""
        cls = self.__class__.__name__
        return (f"{cls}(titulo='{self.titulo}', duracao={self.duracao}, artista='{self.artista}', "
                f"temporada='{self.temporada}', episodio={self.episodio}, host='{self.host}', "
                f"reproducoes={self.reproducoes})")
