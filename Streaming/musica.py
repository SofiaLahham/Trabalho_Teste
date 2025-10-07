# Streaming/musica.py
from .arquivo_de_midia import ArquivoDeMidia

class Musica(ArquivoDeMidia):
    """Subclasse de ArquivoDeMidia que representa uma música."""

    def __init__(self, titulo: str, duracao: int, artista: str,
                 genero: str, reproducoes: int = 0):
        """Inicializa uma música com título, duração (s), artista e gênero."""
        super().__init__(titulo, duracao, artista, reproducoes)
        self.genero = (genero or "").strip()
        self.avaliacoes: list[int] = []

    def avaliar(self, nota: int) -> None:
        """Adiciona uma avaliação de 0 a 5 (inclusive)."""
        if not isinstance(nota, int) or nota < 0 or nota > 5:
            raise ValueError("A nota deve estar entre 0 e 5 (inteiro).")
        self.avaliacoes.append(nota)

    def media_avaliacoes(self) -> float:
        """Calcula e retorna a média das avaliações (0.0 se não houver)."""
        if not self.avaliacoes:
            return 0.0
        return sum(self.avaliacoes) / len(self.avaliacoes)

    def __str__(self) -> str:
        """Mostra informações principais da música."""
        return (f"Música: {self.titulo} | Artista: {self.artista} | "
                f"Gênero: {self.genero} | Reproduções: {self.reproducoes}")

    def __repr__(self) -> str:
        """Representação detalhada para depuração."""
        return (f"Musica(titulo='{self.titulo}', duracao={self.duracao}, "
                f"artista='{self.artista}', genero='{self.genero}', "
                f"reproducoes={self.reproducoes}, avaliacoes={len(self.avaliacoes)})")
