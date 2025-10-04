# main.py
from pathlib import Path
from datetime import datetime

# Imports alinhados com a sua estrutura
from Streaming.menu import Menu
from Streaming.usuario import Usuario
from Streaming.musica import Musica
from Streaming.podcast import Podcast
from Streaming.playlist import Playlist
from Streaming.analises import Analises

# ------------------------------ caminhos padrão ------------------------------
CONFIG_PATH = Path("config/dados.md")
LOG_PATH = Path("logs/erros.log")
REL_PATH = Path("relatorios/relatorio.txt")


# --------------------------------- utilidades --------------------------------
def log_erro(msg: str) -> None:
    """Acrescenta uma linha no arquivo de log com data/hora."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")


def parse_dados_md(caminho: Path) -> dict:
    """
    Parser simples do 'config/dados.md' (sem libs externas).
    Seções aceitas (case-insensitive):
      # MUSICAS   ->  - titulo | duracao(int) | artista | genero
      # PODCASTS  ->  - titulo | duracao(int) | artista | temporada | episodio(int) | host
      # USUARIOS  ->  - nome
    Linhas devem começar com '-'. Espaços são tolerados.
    """
    dados = {"MUSICAS": [], "PODCASTS": [], "USUARIOS": []}
    sec = None

    if not caminho.exists():
        return dados

    linhas = caminho.read_text(encoding="utf-8").splitlines()
    for n, raw in enumerate(linhas, start=1):
        line = raw.strip()
        if not line or line.startswith("//"):
            continue

        up = line.upper()
        if up.startswith("# MUSICAS"):
            sec = "MUSICAS";  continue
        if up.startswith("# PODCASTS"):
            sec = "PODCASTS"; continue
        if up.startswith("# USUARIOS"):
            sec = "USUARIOS"; continue

        if not sec:
            log_erro(f"Linha {n}: fora de seção válida -> {raw}")
            continue

        if not line.startswith("-"):
            log_erro(f"Linha {n}: esperado '-' no início -> {raw}")
            continue

        campos = [c.strip() for c in line[1:].split("|")]

        try:
            if sec == "MUSICAS":
                if len(campos) != 4:
                    raise ValueError("MUSICAS exige 4 campos")
                titulo, duracao, artista, genero = campos
                duracao = int(duracao)
                if duracao <= 0:
                    raise ValueError("duração inválida")
                dados["MUSICAS"].append((titulo, duracao, artista, genero))

            elif sec == "PODCASTS":
                if len(campos) != 6:
                    raise ValueError("PODCASTS exige 6 campos")
                titulo, duracao, artista, temporada, episodio, host = campos
                duracao = int(duracao)
                episodio = int(episodio)
                if duracao <= 0 or episodio < 0:
                    raise ValueError("valores inválidos")
                dados["PODCASTS"].append((titulo, duracao, artista, temporada, episodio, host))

            elif sec == "USUARIOS":
                if len(campos) != 1:
                    raise ValueError("USUARIOS exige 1 campo (nome)")
                nome = campos[0]
                dados["USUARIOS"].append(nome)

        except Exception as e:
            log_erro(f"Linha {n} ({sec}): {e} -> {raw}")

    return dados


def carregar_dados_do_arquivo(app: "StreamingApp") -> None:
    """Preenche app.musicas, app.podcasts e app.usuarios usando config/dados.md."""
    data = parse_dados_md(CONFIG_PATH)

    # Usuários (evita duplicar pelo nome formatado)
    for nome in data["USUARIOS"]:
        nome_fmt = nome.strip().title()
        if not any(u.nome == nome_fmt for u in app.usuarios):
            app.usuarios.append(Usuario(nome_fmt))

    # Músicas (evita duplicar por título)
    for (titulo, duracao, artista, genero) in data["MUSICAS"]:
        if not any(m.titulo.lower() == titulo.lower() for m in app.musicas):
            app.musicas.append(Musica(titulo, duracao, artista, genero))

    # Podcasts (evita duplicar por título)
    for (titulo, duracao, artista, temporada, episodio, host) in data["PODCASTS"]:
        if not any(p.titulo.lower() == titulo.lower() for p in app.podcasts):
            app.podcasts.append(Podcast(titulo, duracao, artista, temporada, episodio, host))


def salvar_relatorio_txt(musicas, playlists, usuarios, destino: Path = REL_PATH) -> None:
    """Gera/atualiza o relatório com análises agregadas."""
    destino.parent.mkdir(parents=True, exist_ok=True)

    top = Analises.top_musicas_reproduzidas(musicas, top_n=10)
    pl_pop = Analises.playlist_mais_popular(playlists)
    user_ativo = Analises.usuario_mais_ativo(usuarios)
    medias = Analises.media_avaliacoes(musicas)
    total = Analises.total_reproducoes(usuarios)

    linhas = []
    linhas.append("=== Relatório do Streaming ===")
    linhas.append(f"Usuários: {len(usuarios)}")
    linhas.append(f"Músicas: {len(musicas)}")
    linhas.append(f"Playlists: {len(playlists)}")
    linhas.append("")
    linhas.append("Top músicas por reproduções:")
    for m in top:
        linhas.append(f"- {m.titulo} ({m.reproducoes})")
    linhas.append("")
    linhas.append(f"Playlist mais popular: {pl_pop.nome if pl_pop else 'N/A'}")
    linhas.append(f"Usuário mais ativo: {user_ativo.nome if user_ativo else 'N/A'}")
    linhas.append("")
    linhas.append("Média de avaliações por música:")
    for k, v in medias.items():
        linhas.append(f"- {k}: {v:.2f}")
    linhas.append("")
    linhas.append(f"Total de reproduções no sistema: {total}")

    destino.write_text("\n".join(linhas), encoding="utf-8")
    print(f"Relatório salvo em {destino}")


# ------------------------------- controlador APP -----------------------------
class StreamingApp:
    """Camada de regra de negócio do sistema."""
    def __init__(self):
        self.usuarios: list[Usuario] = []
        self.musicas: list[Musica] = []
        self.podcasts: list[Podcast] = []
        self.playlists: list[Playlist] = []

    def criar_novo_usuario(self, nome: str) -> Usuario:
        u = Usuario(nome)
        self.usuarios.append(u)
        return u

    def buscar_midia_por_titulo(self, titulo: str):
        """Procura por título (case-insensitive) em músicas e podcasts."""
        t = titulo.strip().lower()
        for m in self.musicas:
            if m.titulo.lower() == t:
                return m
        for p in self.podcasts:
            if p.titulo.lower() == t:
                return p
        return None


# ----------------------------------- fluxo -----------------------------------
def main() -> None:
    menu = Menu()
    app = StreamingApp()

    # 1) Carrega do arquivo (regra de ouro do enunciado)
    carregar_dados_do_arquivo(app)

    # 2) Fallback opcional (se o arquivo estiver vazio)
    if not app.musicas and not app.podcasts:
        app.musicas.extend([
            Musica("Flor e o Beija-Flor", 210, "Henrique & Juliano", "Sertanejo"),
            Musica("Imagine", 183, "John Lennon", "Rock"),
            Musica("As It Was", 168, "Harry Styles", "Pop"),
        ])
        app.podcasts.extend([
            Podcast("DevTalk", 3600, "Canal X", "T1", 1, "Ana"),
            Podcast("DadosCast", 2800, "PUCRS", "T2", 3, "Otávio"),
        ])

    usuarios = app.usuarios
    usuario_logado: Usuario | None = None

    while True:
        if not usuario_logado:
            opcao = menu.exibir_menu_inicial()

            match opcao:
                case "1":  # Entrar como usuário
                    if not usuarios:
                        print("Nenhum usuário cadastrado. Crie um novo usuário primeiro.")
                    else:
                        print("Usuários disponíveis:")
                        for i, u in enumerate(usuarios, start=1):
                            print(f"{i} - {u.nome}")
                        try:
                            escolha = int(input("Digite o número do usuário: "))
                        except ValueError:
                            print("Entrada inválida. Digite apenas números.")
                            continue
                        if 1 <= escolha <= len(usuarios):
                            usuario_logado = usuarios[escolha - 1]
                            print(f"Usuário '{usuario_logado.nome}' logado com sucesso!")
                        else:
                            print("Opção inválida.")

                case "2":  # Criar novo usuário
                    novo_nome = input("Digite o nome do novo usuário: ").strip()
                    if not novo_nome:
                        print("Nome de usuário não pode ser vazio.")
                    elif any(u.nome == novo_nome.strip().title() for u in usuarios):
                        print("Já existe um usuário com esse nome.")
                        log_erro(f"Usuário duplicado: {novo_nome}")
                    else:
                        u = app.criar_novo_usuario(novo_nome)
                        print(f"Usuário '{u.nome}' criado com sucesso!")

                case "3":  # Listar usuários
                    if not usuarios:
                        print("Nenhum usuário cadastrado.")
                    else:
                        print("=== LISTA DE USUÁRIOS ===")
                        for u in usuarios:
                            print("-", u.nome)

                case "4":  # Sair
                    print("Saindo do sistema...")
                    return

                case _:
                    print("Opção inválida. Tente novamente.")

        else:
            opcao = menu.exibir_menu_usuario(usuario_logado.nome)

            match opcao:
                case "1":  # Reproduzir uma música/podcast pelo título
                    titulo = input("Título da mídia a reproduzir: ").strip()
                    midia = app.buscar_midia_por_titulo(titulo)
                    if midia:
                        usuario_logado.ouvir_midia(midia)
                    else:
                        print("Mídia não encontrada.")

                case "2":  # Listar músicas
                    if not app.musicas:
                        print("Nenhuma música cadastrada.")
                    else:
                        print("\nMÚSICAS:")
                        for m in app.musicas:
                            print(m)

                case "3":  # Listar podcasts
                    if not app.podcasts:
                        print("Nenhum podcast cadastrado.")
                    else:
                        print("\nPODCASTS:")
                        for p in app.podcasts:
                            print(p)

                case "4":  # Listar playlists
                    if not app.playlists:
                        print("Nenhuma playlist cadastrada.")
                    else:
                        print("\nPLAYLISTS:")
                        for pl in app.playlists:
                            print(pl)

                case "5":  # Reproduzir uma playlist
                    nome_pl = input("Nome da playlist a reproduzir: ").strip()
                    pl = next((p for p in app.playlists if p.nome.lower() == nome_pl.lower()), None)
                    if pl:
                        print(f"Reproduzindo playlist '{pl.nome}':")
                        pl.reproduzir()
                    else:
                        print("Playlist não encontrada.")

                case "6":  # Criar nova playlist (+ opção de adicionar mídia)
                    nome = input("Nome da nova playlist: ").strip()
                    if not nome:
                        print("Nome inválido.")
                        continue
                    pl = Playlist(nome, usuario_logado)
                    app.playlists.append(pl)
                    print(f"Playlist '{pl.nome}' criada.")

                    add = input("Adicionar uma mídia agora? (s/N) ").strip().lower()
                    if add == "s":
                        titulo = input("Título exato da música/podcast: ").strip()
                        midia = app.buscar_midia_por_titulo(titulo)
                        if midia:
                            pl.adicionar_midia(midia)  # passa OBJETO, não string
                            print("Mídia adicionada.")
                        else:
                            print("Não encontrada.")

                case "7":  # Concatenar playlists (mantém nome da 1ª e soma reproduções)
                    destino = input("Playlist 1 (destino): ").strip()
                    juntar = input("Playlist 2 (a ser juntada): ").strip()
                    p1 = next((p for p in app.playlists if p.nome.lower() == destino.lower()), None)
                    p2 = next((p for p in app.playlists if p.nome.lower() == juntar.lower()), None)
                    if p1 and p2:
                        nova = p1 + p2
                        # substitui p1 pela nova concatenada
                        app.playlists = [p if p is not p1 else nova for p in app.playlists]
                        print(f"Playlists concatenadas em '{nova.nome}'. Itens: {len(nova)}")
                    else:
                        print("Playlist de destino ou origem não encontrada.")

                case "8":  # Gerar relatório agregado
                    salvar_relatorio_txt(app.musicas, app.playlists, app.usuarios)

                case "9":  # Sair do usuário logado
                    print(f"👤 Usuário '{usuario_logado.nome}' saiu da conta.")
                    usuario_logado = None

                case _:
                    print("Opção inválida. Tente novamente.")


# --------------------------------- bootstrap ---------------------------------
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_erro(f"Erro crítico no main: {e}")
        print("Erro crítico. Veja logs/erros.log.")
