# Streaming/arquivo_de_midia.py

class ArquivoDeMidia:
    """
    Classe base para qualquer tipo de mídia (música, podcast, etc.).
    Define atributos e comportamentos comuns.
    """

    """Lista com todas as mídias registradas (usada para buscas)."""
    registroMidia = []  # todas as mídias criadas

    @staticmethod
    def _norm(s: str) -> str:
        """Normaliza textos: strip, compacta espaços e lowercase."""
        return " ".join((s or "").strip().split()).lower()

    def __init__(self, titulo: str, duracao: int, artista: str, reproducoes: int = 0):
        """Inicializa a mídia com validações simples."""
        self.titulo = (titulo or "").strip()
        self.artista = (artista or "").strip()

        if not isinstance(duracao, int) or duracao <= 0:
            raise ValueError("Duração inválida: deve ser um inteiro positivo.")
        self.duracao = duracao

        if not isinstance(reproducoes, int) or reproducoes < 0:
            raise ValueError("Reproduções inválidas: deve ser um inteiro >= 0.")
        self.reproducoes = reproducoes

        ArquivoDeMidia.registroMidia.append(self)

    @classmethod
    def buscar_por_titulo(cls, titulo: str):
        """Busca mídia pelo título (case-insensitive; normaliza espaços)."""
        t = cls._norm(titulo)
        for m in cls.registroMidia:
            if cls._norm(m.titulo) == t:
                return m
        return None

    def reproduzir(self):
        self.reproducoes += 1
        print(f"Reproduzindo: '{self.titulo}' - {self.artista} ({self.duracao}s)")


    def __eq__(self, other) -> bool:
        """Compara por (titulo, artista) com normalização case-insensitive."""
        if not isinstance(other, ArquivoDeMidia):
            return NotImplemented
        return (
            self._norm(self.titulo) == self._norm(other.titulo)
            and self._norm(self.artista) == self._norm(other.artista)
        )

    def __str__(self) -> str:
        """Resumo textual da mídia."""
        return (f"Mídia: {self.titulo} | Artista: {self.artista} | "
                f"Duração: {self.duracao}s | Reproduções: {self.reproducoes}")

    def __repr__(self) -> str:
        """Representação detalhada para depuração."""
        cls = self.__class__.__name__
        return (f"{cls}(titulo='{self.titulo}', duracao={self.duracao}, "
                f"artista='{self.artista}', reproducoes={self.reproducoes})")
