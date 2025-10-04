# Streaming/arquivo_de_midia.py

class ArquivoDeMidia:
    """
    Classe base para qualquer tipo de mídia (música, podcast, etc.)
    Define atributos e comportamentos comuns.
    A igualdade (__eq__) compara título e artista, sem diferenciar maiúsculas/minúsculas.
    """

    # Lista de todas as mídias criadas
    # Usada para buscas por título em todo o sistema
    registroMidia = []

    def __init__(self, titulo: str, duracao: int, artista: str, reproducoes: int = 0):
        """Inicializa os atributos básicos de uma mídia."""
        self.titulo = titulo.strip()
        self.artista = artista.strip()

        # Validação da duração (deve ser inteiro positivo)
        if not isinstance(duracao, int) or duracao <= 0:
            raise ValueError("Duração inválida: deve ser um inteiro positivo.")
        self.duracao = duracao

        # Validação das reproduções (inteiro >= 0)
        if not isinstance(reproducoes, int) or reproducoes < 0:
            raise ValueError("Reproduções inválidas: deve ser um inteiro maior ou igual a zero.")
        self.reproducoes = reproducoes

        # Adiciona a mídia ao registro global
        ArquivoDeMidia.registroMidia.append(self)

    @classmethod
    def buscar_por_titulo(cls, titulo: str):
        """Procura uma mídia pelo título (ignora maiúsculas e espaços)."""
        t = titulo.strip().lower()
        for m in cls.registroMidia:
            if m.titulo.strip().lower() == t:
                return m
        return None

    def reproduzir(self) -> None:
        """Simula a reprodução da mídia e mostra informações básicas."""
        self.reproducoes += 1
        print(f"▶ Reproduzindo: '{self.titulo}' — {self.artista} ({self.duracao}s). "
              f"Total de reproduções: {self.reproducoes}")

    def __eq__(self, other) -> bool:
        """Dois arquivos são iguais se tiverem o mesmo título e artista."""
        if not isinstance(other, ArquivoDeMidia):
            return NotImplemented
        return (self.titulo.strip().lower() == other.titulo.strip().lower() and
                self.artista.strip().lower() == other.artista.strip().lower())

    def __str__(self) -> str:
        """Retorna uma string amigável com as informações principais."""
        return (f"Mídia: {self.titulo} | Artista: {self.artista} | "
                f"Duração: {self.duracao}s | Reproduções: {self.reproducoes}")

    def __repr__(self) -> str:
        """Representação detalhada (para depuração)."""
        cls = self.__class__.__name__
        return (f"{cls}(titulo='{self.titulo}', duracao={self.duracao}, "
                f"artista='{self.artista}', reproducoes={self.reproducoes})")
