# Streaming/podcast.py
from .arquivo_de_midia import ArquivoDeMidia

class Podcast(ArquivoDeMidia):
    """Subclasse de ArquivoDeMidia que representa um podcast."""

    def __init__(self, titulo: str, duracao: int, host: str,
                 temporada: str, episodio: int, reproducoes: int = 0):
        """
        Inicializa um podcast.
        - host é mapeado para o atributo 'artista' da classe base.
        - episodio deve ser um inteiro > 0.
        """
        host_limpo = (host or "").strip()
        temporada_limpa = (temporada or "").strip()

        if not host_limpo:
            raise ValueError("Host inválido: não pode ser vazio.")
        if not temporada_limpa:
            raise ValueError("Temporada inválida: não pode ser vazia.")
        if not isinstance(episodio, int) or episodio <= 0:
            raise ValueError("Episódio inválido: deve ser um inteiro positivo.")

        # Em ArquivoDeMidia, 'artista' representa quem apresenta/assina o conteúdo.
        # Para Podcast, usamos o 'host' como 'artista' na base.
        super().__init__(titulo, duracao, host_limpo, reproducoes)

        self.temporada = temporada_limpa
        self.episodio = episodio
        self.host = host_limpo

    def __str__(self) -> str:
        """Mostra informações principais do podcast."""
        return (f"Podcast: {self.titulo} | Temporada: {self.temporada} | "
                f"Episódio: {self.episodio} | Host: {self.host} | "
                f"Duração: {self.duracao}s | Reproduções: {self.reproducoes}")

    def __repr__(self) -> str:
        """Representação detalhada para depuração."""
        return (f"Podcast(titulo='{self.titulo}', duracao={self.duracao}, "
                f"host='{self.host}', temporada='{self.temporada}', "
                f"episodio={self.episodio}, reproducoes={self.reproducoes})")
