 # Streaming/musica.py
from .arquivo_de_midia import ArquivoDeMidia

class Musica(ArquivoDeMidia):
    """
    Subclasse de ArquivoDeMidia que representa uma música.
    Atributos extras: genero (str) e avaliacoes (list[int]).
    """

    def __init__(self, titulo: str, duracao: int, artista: str,
                 genero: str, reproducoes: int = 0, avaliacoes: list[int] | None = None):
        """
        Inicializa a música com gênero e lista de avaliações (opcional).
        - genero: string como 'Rock', 'Pop', 'Rap', etc.
        - avaliacoes: lista de notas inteiras no intervalo [0, 5]
        """
        super().__init__(titulo, duracao, artista, reproducoes)

        self.genero = genero.strip()

        # Evitar default mutável
        self.avaliacoes: list[int] = [] if avaliacoes is None else list(avaliacoes)

        # Valida todas as avaliações passadas (se houver)
        for nota in self.avaliacoes:
            if not isinstance(nota, int) or nota < 0 or nota > 5:
                raise ValueError("Avaliação inválida: cada nota deve ser um inteiro entre 0 e 5.")

    def avaliar(self, nota: int) -> None:
        """
        Adiciona uma avaliação à música.
        Regra do enunciado: nota deve estar entre 0 e 5 (inteiro).
        """
        if not isinstance(nota, int) or nota < 0 or nota > 5:
            raise ValueError("Avaliação inválida: use um inteiro entre 0 e 5.")
        self.avaliacoes.append(nota)

    def __str__(self) -> str:
        """Representação amigável com dados principais da música."""
        qtd_av = len(self.avaliacoes)
        return (f"Música: {self.titulo} | Artista: {self.artista} | Gênero: {self.genero} | "
                f"Duração: {self.duracao}s | Reproduções: {self.reproducoes} | "
                f"Avaliações: {qtd_av}")

    def __repr__(self) -> str:
        """Representação detalhada para depuração."""
        cls = self.__class__.__name__
        return (f"{cls}(titulo='{self.titulo}', duracao={self.duracao}, "
                f"artista='{self.artista}', genero='{self.genero}', "
                f"reproducoes={self.reproducoes}, avaliacoes={self.avaliacoes})")
