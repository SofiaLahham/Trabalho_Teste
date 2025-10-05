# Streaming/playlist.py
from .arquivo_de_midia import ArquivoDeMidia
from .usuario import Usuario

class Playlist:
    """
    Representa uma playlist do sistema.
    Atributos: nome (str), usuario (Usuario), itens (list[ArquivoDeMidia]), reproducoes (int).
    """

    def __init__(self, nome: str, usuario: Usuario):
        """Cria uma playlist vazia para um usuário."""
        nome_limpo = nome.strip()
        if not nome_limpo:
            raise ValueError("Nome de playlist inválido.")
        if not isinstance(usuario, Usuario):
            raise ValueError("Usuário inválido para a playlist.")

        self.nome = nome_limpo            # nome da playlist
        self.usuario = usuario            # dono/criador da playlist
        self.itens: list[ArquivoDeMidia] = []  # lista de mídias (músicas/podcasts)
        self.reproducoes = 0              # contador de execuções da playlist

    def adicionar_midia(self, midia: ArquivoDeMidia) -> None:
        """Adiciona uma mídia (música/podcast) à playlist."""
        if not isinstance(midia, ArquivoDeMidia):
            raise ValueError("Apenas objetos de mídia podem ser adicionados.")
        self.itens.append(midia)          # adiciona no final da lista

    def remover_midia(self, midia: ArquivoDeMidia) -> None:
        """Remove uma mídia da playlist."""
        if midia in self.itens:
            self.itens.remove(midia)      # remove a primeira ocorrência
        else:
            raise ValueError("Mídia não encontrada na playlist.")

    def reproduzir(self) -> None:
        """
        Reproduz todos os itens da playlist.
        Soma 1 nas reproduções da playlist e em cada mídia contida.
        """
        if len(self.itens) == 0:
            print(f"Playlist '{self.nome}' está vazia.")
            return

        print(f"\n▶ Reproduzindo playlist: {self.nome} (itens: {len(self.itens)})")
        for midia in self.itens:
            midia.reproduzir()            # chama o método reproduzir() de cada mídia
        self.reproducoes += 1
        print(f"▶ Fim da playlist '{self.nome}'. Reproduções: {self.reproducoes}")

    def __add__(self, outra: "Playlist") -> "Playlist":
        """
        Concatena duas playlists.
        Mantém o nome da primeira, concatena itens e soma as reproduções.
        """
        if not isinstance(outra, Playlist):
            return NotImplemented

        nova = Playlist(self.nome, self.usuario)     # nova playlist com mesmo nome e usuário
        nova.itens = list(self.itens) + list(outra.itens)  # junta os itens das duas
        nova.reproducoes = self.reproducoes + outra.reproducoes
        return nova

    def __len__(self) -> int:
        """Retorna a quantidade de itens da playlist."""
        return len(self.itens)

    def __getitem__(self, index: int) -> ArquivoDeMidia:
        """Permite acessar itens por índice: playlist[0]."""
        return self.itens[index]

    def __eq__(self, outra: object) -> bool:
        """
        Compara playlists:
        - Mesmo nome (case-insensitive)
        - Mesmo usuário
        - Mesmos títulos de mídias (ignora ordem)
        """
        if not isinstance(outra, Playlist):
            return NotImplemented

        if self.usuario is not outra.usuario:
            return False

        if self.nome.strip().lower() != outra.nome.strip().lower():
            return False

        # cria listas com os títulos das mídias, em minúsculas
        def titulos(pl):
            return [m.titulo.strip().lower() for m in pl.itens]

        a = sorted(titulos(self))
        b = sorted(titulos(outra))
        return a == b

    def __str__(self) -> str:
        """Mostra um resumo da playlist."""
        return (f"Playlist: {self.nome} | Usuário: {self.usuario.nome} | "
                f"Itens: {len(self.itens)} | Reproduções: {self.reproducoes}")

    def __repr__(self) -> str:
        """Representação detalhada para depuração."""
        cls = self.__class__.__name__
        return (f"{cls}(nome='{self.nome}', usuario='{self.usuario.nome}', "
                f"itens={len(self.itens)}, reproducoes={self.reproducoes})")
