# Streaming/musica.py
from .arquivo_de_midia import ArquivoDeMidia

class Musica(ArquivoDeMidia):
    """Subclasse de ArquivoDeMidia que representa uma música."""

    def __init__(self, titulo: str, duracao: int, artista: str,
                 genero: str, reproducoes: int = 0):
        """Inicializa uma música com título, duração, artista e gênero."""
        super().__init__(titulo, duracao, artista, reproducoes)
        self.genero = genero.strip()
        self.avaliacoes = []

    def avaliar(self, nota: int) -> None:
        """Adiciona uma avaliação de 1 a 5."""
        if nota < 1 or nota > 5:
            raise ValueError("A nota deve estar entre 1 e 5.")
        self.avaliacoes.append(nota)

    def media_avaliacoes(self) -> float:
        """Calcula e retorna a média das avaliações."""
        if not self.avaliacoes:
            return 0.0
        return sum(self.avaliacoes) / len(self.avaliacoes)

    def __str__(self) -> str:
        """Mostra informações principais da música."""
        return (f"Música: {self.titulo} | Artista: {self.artista} | "
                f"Gênero: {self.genero} | Reproduções: {self.reproducoes}")
