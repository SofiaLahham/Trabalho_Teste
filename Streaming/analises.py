# Streaming/analises.py
from .musica import Musica
from .playlist import Playlist
from .usuario import Usuario

class Analises:
    """Classe com métodos estáticos para gerar análises e estatísticas do sistema."""

    @staticmethod
    def top_musicas_reproduzidas(musicas: list[Musica], n: int):
        """Retorna as n músicas mais reproduzidas."""
        return sorted(musicas, key=lambda m: m.reproducoes, reverse=True)[:n]

    @staticmethod
    def playlist_mais_popular(playlists: list[Playlist]):
        """Retorna a playlist com mais reproduções."""
        if not playlists:
            return None
        return max(playlists, key=lambda p: p.reproducoes)

    @staticmethod
    def usuario_mais_ativo(usuarios: list[Usuario]):
        """Retorna o usuário com mais reproduções no histórico."""
        if not usuarios:
            return None
        return max(usuarios, key=lambda u: len(u.historico))

    @staticmethod
    def media_avaliacoes(musicas: list[Musica]):
        """Calcula a média das avaliações para cada música."""
        medias = {}
        for m in musicas:
            medias[m.titulo] = m.media_avaliacoes()
        return medias

    @staticmethod
    def total_reproducoes(usuarios: list[Usuario]):
        """Soma o total de reproduções do histórico de todos os usuários."""
        return sum(len(u.historico) for u in usuarios)
