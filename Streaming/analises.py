# Streaming/analises.py

from __future__ import annotations

# Importações apenas para tipos/atributos usados nas análises
from .musica import Musica
from .playlist import Playlist
from .usuario import Usuario
from .arquivo_de_midia import ArquivoDeMidia


class Analises:
    """
    Métodos estáticos de análise do sistema.
    - Não modificam os objetos (somente leitura).
    - Não usam bibliotecas externas.
    """

    @staticmethod
    def top_musicas_reproduzidas(musicas: list[Musica], top_n: int) -> list[Musica]:
        """
        Retorna as 'top_n' músicas com mais reproduções.
        - Se 'top_n' <= 0 ou 'musicas' vazia/None, retorna [].
        - Empates: desempata por título (case-insensitive).
        """
        if not musicas or top_n <= 0:
            return []
        ordenadas = sorted(
            musicas,
            key=lambda m: (-getattr(m, "reproducoes", 0), getattr(m, "titulo", "").lower())
        )
        return ordenadas[:top_n]

    @staticmethod
    def playlist_mais_popular(playlists: list[Playlist]) -> Playlist | None:
        """
        Retorna a playlist com maior número de reproduções.
        - Se a lista estiver vazia/None, retorna None.
        - Empates: desempata por nome (case-insensitive).
        """
        if not playlists:
            return None
        return max(
            playlists,
            key=lambda p: (getattr(p, "reproducoes", 0), getattr(p, "nome", "").lower())
        )

    @staticmethod
    def usuario_mais_ativo(usuarios: list[Usuario]) -> Usuario | None:
        """
        Retorna o usuário com maior quantidade de itens no histórico.
        - Se a lista estiver vazia/None, retorna None.
        - Empates: desempata por nome (case-insensitive).
        """
        if not usuarios:
            return None
        return max(
            usuarios,
            key=lambda u: (len(getattr(u, "historico", [])), getattr(u, "nome", "").lower())
        )

    @staticmethod
    def media_avaliacoes(musicas: list[Musica]) -> dict[str, float]:
        """
        Calcula a média das avaliações por música.
        - Retorna dict: {titulo: media}.
        - Ignora músicas sem avaliações válidas.
        - Considera somente notas inteiras no intervalo [0, 5].
        """
        resultados: dict[str, float] = {}
        if not musicas:
            return resultados

        for m in musicas:
            avals = getattr(m, "avaliacoes", [])
            # Filtra apenas inteiros entre 0 e 5
            vals: list[int] = []
            for x in avals:
                try:
                    xi = int(x)
                    if 0 <= xi <= 5:
                        vals.append(xi)
                except Exception:
                    # Valor não numérico -> ignora
                    continue

            if vals:
                resultados[getattr(m, "titulo", "")] = sum(vals) / len(vals)

        return resultados

    @staticmethod
    def total_reproducoes(usuarios: list[Usuario]) -> int:
        """
        Total de reproduções do sistema.
        - Estratégia principal: somar reproduções das mídias registradas em
          'ArquivoDeMidia.registroMidia' (fonte única e consistente quando mantida).
        - Fallback: se ocorrer problema (ex.: atributo ausente), soma o tamanho
          dos históricos dos usuários (estimativa simples para não falhar).
        """
        try:
            return sum(getattr(m, "reproducoes", 0) for m in getattr(ArquivoDeMidia, "registroMidia", []))
        except Exception:
            return sum(len(getattr(u, "historico", [])) for u in (usuarios or []))
