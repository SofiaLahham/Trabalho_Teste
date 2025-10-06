# Streaming/analises.py

from typing import List, Dict, Optional
from .musica import Musica
from .playlist import Playlist
from .usuario import Usuario


class Analises:
    @staticmethod
    def top_musicas_reproduzidas(musicas: List[Musica], top_n: int) -> List[Musica]:
        return sorted(musicas, key=lambda m: m.reproducoes, reverse=True)[:top_n]

    @staticmethod
    def playlist_mais_popular(playlists: List[Playlist]) -> Optional[Playlist]:
        if not playlists:
            return None
        return max(playlists, key=lambda p: p.reproducoes)

    @staticmethod
    def usuario_mais_ativo(usuarios: List[Usuario]) -> Optional[Usuario]:
        if not usuarios:
            return None
        return max(usuarios, key=lambda u: len(u.historico))

    @staticmethod
    def media_avaliacoes(musicas: List[Musica]) -> Dict[str, float]:
        medias = {}
        for m in musicas:
            if hasattr(m, "avaliacoes") and m.avaliacoes:
                medias[m.titulo] = sum(m.avaliacoes) / len(m.avaliacoes)
        return medias

    @staticmethod
    def total_reproducoes(usuarios: List[Usuario]) -> int:
        return sum(len(u.historico) for u in usuarios)
