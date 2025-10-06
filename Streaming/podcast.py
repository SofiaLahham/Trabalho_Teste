# Streaming/podcast.py
from .arquivo_de_midia import ArquivoDeMidia

class Podcast(ArquivoDeMidia):
    """Subclasse de ArquivoDeMidia que representa um podcast."""

    def __init__(self, titulo: str, duracao: int, artista: str,
                 temporada: str, episodio: int, host: str, reproducoes: int = 0):
        """Inicializa um objeto Podcast."""
        super().__init__(titulo, duracao, artista, reproducoes)
        self.temporada = temporada.strip()
        self.host = host.strip()
        if not isinstance(episodio, int) or episodio <= 0:
            raise ValueError("Episódio inválido: deve ser um número inteiro positivo.")
        self.episodio = episodio

    def __str__(self) -> str:
        """Mostra informações principais do podcast."""
        return (f"Podcast: {self.titulo} | Temporada: {self.temporada} | "
                f"Episódio: {self.episodio} | Host: {self.host} | "
                f"Duração: {self.duracao}s | Reproduções: {self.reproducoes}")
