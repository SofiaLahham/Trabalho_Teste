# Streaming/arquivo_de_midia.py

from datetime import datetime
from pathlib import Path

class ArquivoDeMidia:
    """
    Classe base para qualquer tipo de mídia (música, podcast, etc.)
    Define atributos e comportamentos comuns.
    A igualdade (__eq__) compara título e artista, sem diferenciar maiúsculas/minúsculas.
    """

    # Lista de instâncias de qualquer mídia criada
    # Usada para buscas por título em todo o sistema
    registroMidia = []  

    def __init__(self, titulo: str, duracao: int, artista: str, reproducoes: int = 0):
        # Título da mídia
        self.titulo = titulo.strip()
        # Duração em segundos (int)
        self.duracao = int(duracao)
        # Nome do artista/intérprete
        self.artista = artista.strip()
        # Contador de execuções iniciado em zero
        self.reproducoes = int(reproducoes)

        # Adiciona a nova mídia ao registro global de mídias
        ArquivoDeMidia.registroMidia.append(self)

    @classmethod
    def buscar_por_titulo(cls, titulo: str):
        """Procura uma mídia pelo título (ignora maiúsculas e espaços)."""
        t = titulo.strip().lower()
        for m in cls.registroMidia:
            if m.titulo.strip().lower() == t:
                return m
        return None

    # Métodos obrigatórios especiais
    def reproduzir(self) -> None:
        """Simula a reprodução da mídia e mostra informações básicas."""
        self.reproducoes += 1
        print(f"-> Reproduzindo: '{self.titulo}' — {self.artista} ({self.duracao}s). "
              f"Total de reproduções: {self.reproducoes}")

    def __eq__(self, other) -> bool:
        """Dois arquivos são iguais se tiverem o mesmo título e artista."""
        if not isinstance(other, ArquivoDeMidia):
            return NotImplemented
        return (self.titulo.strip().lower() == other.titulo.strip().lower() and
                self.artista.strip().lower() == other.artista.strip().lower())

    def __str__(self) -> str:
        """Retorna uma string amigável com as informações principais."""
        return (f"A mídia '{self.titulo}' do artista {self.artista} | "
                f"Duração: {self.duracao}s | Reproduções: {self.reproducoes}")

    def __repr__(self) -> str:
        """Representação detalhada (usada para depuração)."""
        cls = self.__class__.__name__
        return (f"{cls}(titulo='{self.titulo}', duracao={self.duracao}, "
                f"artista='{self.artista}', reproducoes={self.reproducoes})")
