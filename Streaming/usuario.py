# Streaming/usuario.py
from .arquivo_de_midia import ArquivoDeMidia
from .playlist import Playlist  # construtor esperado: Playlist(nome: str, usuario: 'Usuario')

class Usuario:
    """
    Representa um usuário do sistema de streaming.
    Atributos: nome (str), playlists (list[Playlist]), historico (list[ArquivoDeMidia]).
    Contador de instâncias: qntd_instancias.
    """

    """Contador de usuários criados (exigido no enunciado)"""
    qntd_instancias = 0

    def __init__(self, nome: str):
        """Inicializa o usuário com nome, listas vazias de playlists e histórico."""
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("Nome de usuário inválido.")

        """Atributos principais"""
        self.nome = nome_limpo              # nome do usuário
        self.playlists = []                 # playlists criadas por este usuário
        self.historico = []                 # mídias reproduzidas por este usuário

        """Incrementa o contador de instâncias"""
        Usuario.qntd_instancias += 1

    def ouvir_midia(self, midia: ArquivoDeMidia) -> None:
        """
        Reproduz uma mídia (música ou podcast) e registra no histórico.
        Regra: usar o método reproduzir() da própria mídia.
        """
        if not isinstance(midia, ArquivoDeMidia):
            raise ValueError("A mídia informada é inválida.")
        midia.reproduzir()
        self.historico.append(midia)

    def criar_playlist(self, nome: str) -> Playlist:
        """
        Cria uma nova playlist para este usuário.
        - Não permite duplicar nome de playlist para o mesmo usuário (case-insensitive).
        - Retorna o objeto Playlist criado.
        """
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("Nome de playlist inválido.")

        """Bloqueia duplicidade de playlist para o mesmo usuário (exigência do enunciado)"""
        for p in self.playlists:
            if p.nome.strip().lower() == nome_limpo.lower():
                raise ValueError("Playlist já existe para este usuário.")

        """Cria e adiciona a nova playlist"""
        nova = Playlist(nome_limpo, self)
        self.playlists.append(nova)
        return nova

    def __str__(self) -> str:
        """Mostra um resumo simples do usuário."""
        return (f"Usuário: {self.nome} | "
                f"Playlists: {len(self.playlists)} | "
                f"Histórico: {len(self.historico)} reproduções")

    def __repr__(self) -> str:
        """Representação detalhada para depuração."""
        cls = self.__class__.__name__
        return (f"{cls}(nome='{self.nome}', "
                f"playlists={len(self.playlists)}, historico={len(self.historico)})")
