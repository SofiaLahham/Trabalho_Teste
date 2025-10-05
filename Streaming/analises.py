# Streaming/analises.py
from .musica import Musica
from .playlist import Playlist
from .usuario import Usuario

class Analises:
    """
    Métodos estáticos para gerar estatísticas do sistema.
    - top_musicas_reproduzidas
    - playlist_mais_popular
    - usuario_mais_ativo
    - media_avaliacoes
    - total_reproducoes
    """

    @staticmethod
    def top_musicas_reproduzidas(musicas: list[Musica], top_n: int) -> list[Musica]:
        """Retorna as top_n músicas com mais reproduções (ordem decrescente)."""
        if not isinstance(top_n, int) or top_n <= 0:
            return []  # nada a retornar se top_n não for válido
        # ordena por reproducoes (maior primeiro)
        ordenadas = sorted(musicas, key=lambda m: m.reproducoes, reverse=True)
        return ordenadas[:top_n]

    @staticmethod
    def playlist_mais_popular(playlists: list[Playlist]) -> Playlist | None:
        """Retorna a playlist com maior número de reproduções (ou None se vazio)."""
        if not playlists:
            return None
        # max por atributo reproducoes (em empate, retorna a primeira)
        mais = playlists[0]
        for p in playlists[1:]:
            if p.reproducoes > mais.reproducoes:
                mais = p
        return mais

    @staticmethod
    def usuario_mais_ativo(usuarios: list[Usuario]) -> Usuario | None:
        """
        Retorna o usuário que mais ouviu músicas/podcasts.
        Critério: maior tamanho do histórico (len(usuario.historico)).
        """
        if not usuarios:
            return None
        ativo = usuarios[0]
        for u in usuarios[1:]:
            if len(u.historico) > len(ativo.historico):
                ativo = u
        return ativo

    @staticmethod
    def media_avaliacoes(musicas: list[Musica]) -> dict[str, float]:
        """
        Retorna {titulo: média} para cada música.
        Se não houver avaliações, a média é 0.0 (simples e explícito).
        """
        resultado: dict[str, float] = {}
        for m in musicas:
            if getattr(m, "avaliacoes", None) and len(m.avaliacoes) > 0:
                soma = 0
                for nota in m.avaliacoes:
                    soma += nota    # soma manual (sem libs externas)
                resultado[m.titulo] = soma / len(m.avaliacoes)
            else:
                resultado[m.titulo] = 0.0
        return resultado

    @staticmethod
    def total_reproducoes(usuarios: list[Usuario]) -> int:
        """
        Retorna o total de reproduções feitas por todos os usuários.
        Critério do enunciado: conta os plays realizados (tamanho do histórico).
        """
        total = 0
        for u in usuarios:
            total += len(u.historico)
        return total

    def __str__(self) -> str:
        """Descrição simples da classe de análises."""
        return "Classe com métodos estáticos para análises do sistema."

    def __repr__(self) -> str:
        """Representação curta para depuração."""
        return "Analises()"
