# main.py
# Ponto de entrada: carrega dados, exibe menus e coordena as ações (Enunciado).

from pathlib import Path
from datetime import datetime

# Imports do pacote Streaming (mesmos nomes do enunciado)
from Streaming.menu import Menu
from Streaming.usuario import Usuario
from Streaming.musica import Musica
from Streaming.podcast import Podcast
from Streaming.playlist import Playlist
from Streaming.analises import Analises
from Streaming.arquivo_de_midia import ArquivoDeMidia

# ---------------------- caminhos padrão (enunciado) ----------------------
ARQ_DADOS = Path("config/dados.md")
ARQ_LOG   = Path("logs/erros.log")
ARQ_REL   = Path("relatorios/relatorio.txt")

# ---------------------- coleções em memória (simples) --------------------
USUARIOS:  list[Usuario]  = []
MUSICAS:   list[Musica]   = []
PODCASTS:  list[Podcast]  = []
PLAYLISTS: list[Playlist] = []

# --------------------------- util: escrever log --------------------------
def log_erro(msg: str) -> None:
    ARQ_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ARQ_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

# --------------------------- util: relatório -----------------------------
def escrever_relatorio(linhas: list[str]) -> None:
    ARQ_REL.parent.mkdir(parents=True, exist_ok=True)
    ARQ_REL.write_text("\n".join(linhas), encoding="utf-8")
    print(f"Relatório salvo em {ARQ_REL}")

# --------------------- buscar usuário por nome (casefold) ----------------
def encontrar_usuario(nome: str) -> Usuario | None:
    alvo = nome.strip().casefold()
    for u in USUARIOS:
        if u.nome.strip().casefold() == alvo:
            return u
    return None

# ----------------------- carregar config/dados.md ------------------------
def carregar_dados() -> None:
    """
    Seções aceitas (Markdown simples):
      # MÚSICAS  : - titulo | duracao(int) | artista | genero
      # PODCASTS : - titulo | duracao(int) | artista(canal) | temporada | episodio(int) | host
      # USUÁRIOS : - nome
    """
    if not ARQ_DADOS.exists():
        log_erro("Arquivo de dados não encontrado.")
        return

    sec = None
    for raw in ARQ_DADOS.read_text(encoding="utf-8").splitlines():
        linha = raw.strip()
        if not linha or linha.startswith("# Aqui"):
            continue

        if linha.startswith("#"):  # título de seção
            t = linha.lstrip("#").strip().upper()
            if "MUSICA" in t:   sec = "MUSICAS"
            elif "PODCAST" in t: sec = "PODCASTS"
            elif "USUARI" in t:  sec = "USUARIOS"
            else: sec = None
            continue

        if not sec or not linha.startswith("-"):
            # ignora linhas fora de seção ou sem "-"
            continue

        try:
            campos = [c.strip() for c in linha.lstrip("-").split("|")]
            if sec == "USUARIOS":
                if len(campos) != 1:
                    raise ValueError("USUÁRIOS exige 1 campo")
                nome = campos[0]
                if not encontrar_usuario(nome):
                    USUARIOS.append(Usuario(nome))
                else:
                    log_erro(f"Usuário duplicado ignorado: {nome}")

            elif sec == "MUSICAS":
                if len(campos) != 4:
                    raise ValueError("MÚSICAS exige 4 campos")
                titulo, duracao, artista, genero = campos
                d = int(duracao)
                MUSICAS.append(Musica(titulo, d, artista, genero))  # ArquivoDeMidia registra sozinho

            elif sec == "PODCASTS":
                if len(campos) != 6:
                    raise ValueError("PODCASTS exige 6 campos")
                titulo, duracao, artista, temporada, episodio, host = campos
                d = int(duracao)
                e = int(episodio)
                PODCASTS.append(Podcast(titulo, d, artista, temporada, e, host))

        except Exception as e:
            log_erro(f"Erro ao processar '{linha}': {e}")

# ---------------------------- telas auxiliares ---------------------------
def listar_musicas() -> None:
    if not MUSICAS:
        print("Nenhuma música cadastrada.")
        return
    for m in MUSICAS:
        print(f"Música: {m.titulo} | Artista: {m.artista} | Gênero: {m.genero} | Reproduções: {m.reproducoes}")

def listar_podcasts() -> None:
    if not PODCASTS:
        print("Nenhum podcast cadastrado.")
        return
    for p in PODCASTS:
        print(f"Podcast: {p.titulo} | Temporada: {p.temporada} | Episódio: {p.episodio} | Host: {p.host} | Duração: {p.duracao}s | Reproduções: {p.reproducoes}")

def listar_playlists_usuario(u: Usuario) -> None:
    if not u.playlists:
        print("Não há playlists.")
        return
    for pl in u.playlists:
        print(f"Playlist: {pl.nome} | Usuário: {u.nome} | Itens: {len(pl.itens)} | Reproduções: {pl.reproducoes}")

def listar_usuarios() -> None:
    if not USUARIOS:
        print("Nenhum usuário cadastrado.")
        return
    for u in USUARIOS:
        print(f"Usuário: {u.nome} | Playlists: {len(u.playlists)} | Histórico: {len(u.historico)} reproduções")

# --------------------- ações do menu do usuário logado -------------------
def acao_reproduzir_midia(u: Usuario) -> None:
    titulo = input("Título da mídia (música/podcast): ").strip()
    mid = ArquivoDeMidia.buscar_por_titulo(titulo)
    if not mid:
        print("Mídia não encontrada.")
        log_erro(f"Tentativa de reproduzir mídia inexistente: {titulo}")
        return
    try:
        u.ouvir_midia(mid)  # usa reproduzir() da própria mídia
    except Exception as e:
        log_erro(f"Erro ao reproduzir '{titulo}' para {u.nome}: {e}")

def acao_reproduzir_playlist(u: Usuario) -> None:
    nome = input("Nome da playlist: ").strip()
    alvo = next((p for p in u.playlists if p.nome.strip().casefold() == nome.casefold()), None)
    if not alvo:
        print("Playlist não encontrada para este usuário.")
        log_erro(f"Playlist inexistente para {u.nome}: {nome}")
        return
    alvo.reproduzir()

def acao_criar_playlist(u: Usuario) -> None:
    nome = input("Nome da nova playlist: ").strip()
    try:
        # bloqueia duplicidade para o MESMO usuário (enunciado)
        if any(p.nome.strip().casefold() == nome.casefold() for p in u.playlists):
            raise ValueError("Playlist já existe para este usuário.")
        pl = u.criar_playlist(nome)  # já adiciona em u.playlists
        PLAYLISTS.append(pl)
        print(f"Playlist '{pl.nome}' criada.")

        # >>> Requisito: criar playlist obrigando adicionar 1 música imediatamente
        print("\nAgora adicione uma música à playlist:")
        t = input("Qual o nome da música que você irá adicionar? ").strip()
        try:
            d = int(input("Qual a duração em segundos? ").strip())  # base usa inteiros
        except ValueError:
            log_erro("Duração inválida ao criar música na playlist.")
            print("Duração inválida.")
            return
        a = input("Quem é o cantor? ").strip()
        g = input("Qual o gênero musical? ").strip()
        mus = Musica(t, d, a, g)          # validação acontece na classe
        pl.adicionar_midia(mus)           # adiciona OBJETO, não string
        MUSICAS.append(mus)               # mantém também a lista global
        print(f"Música '{t}' adicionada à playlist '{pl.nome}'.")
    except ValueError as e:
        log_erro(f"Erro ao criar playlist '{nome}' para {u.nome}: {e}")
        print(e)

def acao_concatenar_playlists(u: Usuario) -> None:
    a = input("Nome da playlist A: ").strip()
    b = input("Nome da playlist B: ").strip()
    pa = next((p for p in u.playlists if p.nome.strip().casefold() == a.casefold()), None)
    pb = next((p for p in u.playlists if p.nome.strip().casefold() == b.casefold()), None)
    if not pa or not pb:
        print("Playlist A ou B não encontrada.")
        log_erro(f"Concatenação inválida para {u.nome}: A='{a}' B='{b}'")
        return
    nova = pa + pb                               # __add__: mesmo nome da A e soma reproduções
    base = nova.nome
    suf = 1
    # evita nome colidindo com outra playlist do mesmo usuário
    while any(p.nome.strip().casefold() == nova.nome.strip().casefold() for p in u.playlists):
        suf += 1
        nova.nome = f"{base} ({suf})"
    u.playlists.append(nova)
    PLAYLISTS.append(nova)
    print(f"Playlist concatenada criada: {nova.nome}")

def acao_gerar_relatorio() -> None:
    linhas: list[str] = []
    linhas.append("=== RELATÓRIO DO SISTEMA ===")
    linhas.append(f"Usuários: {len(USUARIOS)} | Músicas: {len(MUSICAS)} | Podcasts: {len(PODCASTS)}")
    linhas.append("")
    # Top músicas (posição, título, reproduções)
    top = Analises.top_musicas_reproduzidas(MUSICAS, 5)  # passa posicional (base)
    linhas.append("Top 5 músicas mais reproduzidas:")
    if not top:
        linhas.append("- Nenhuma")
    else:
        for m in top:
            linhas.append(f"- {m.titulo} ({m.reproducoes})")
    # Playlist mais popular
    pop = Analises.playlist_mais_popular(PLAYLISTS)
    linhas.append("")
    linhas.append(f"Playlist mais popular: {pop.nome if pop else 'N/A'}")
    # Usuário mais ativo
    ativo = Analises.usuario_mais_ativo(USUARIOS)
    linhas.append(f"Usuário mais ativo: {ativo.nome if ativo else 'N/A'}")
    # Médias por música
    medias = Analises.media_avaliacoes(MUSICAS)
    linhas.append("")
    linhas.append("Médias de avaliação por música:")
    if not medias:
        linhas.append("- (vazio)")
    else:
        for titulo, media in medias.items():
            linhas.append(f"- {titulo}: {media:.2f}")
    # Total de reproduções
    total = Analises.total_reproducoes(USUARIOS)
    linhas.append("")
    linhas.append(f"Total de reproduções no sistema: {total}")
    escrever_relatorio(linhas)

# ------------------------------- fluxo geral ------------------------------
def main() -> None:
    carregar_dados()                 # carrega config/dados.md
    menu = Menu()

    while True:
        op = menu.exibir_menu_inicial()
        if op == "1":  # Entrar como usuário
            nome = input("Nome do usuário: ").strip()
            u = encontrar_usuario(nome)
            if not u:
                print("Usuário não encontrado.")
                continue
            # menu do usuário
            while True:
                opu = menu.exibir_menu_usuario(u.nome)
                if opu == "1":
                    acao_reproduzir_midia(u)
                elif opu == "2":
                    listar_musicas()
                elif opu == "3":
                    listar_podcasts()
                elif opu == "4":
                    listar_playlists_usuario(u)
                elif opu == "5":
                    acao_reproduzir_playlist(u)
                elif opu == "6":
                    acao_criar_playlist(u)
                elif opu == "7":
                    acao_concatenar_playlists(u)
                elif opu == "8":
                    acao_gerar_relatorio()
                elif opu == "9":
                    break
                else:
                    print("Opção inválida.")
        elif op == "2":  # Criar novo usuário
            nome = input("Nome do novo usuário: ").strip()
            if encontrar_usuario(nome):
                print("Usuário já existe.")
                log_erro(f"Tentativa de criar usuário duplicado: {nome}")
            else:
                try:
                    USUARIOS.append(Usuario(nome))
                    print("Usuário criado com sucesso.")
                except ValueError as e:
                    print("Nome inválido.")
                    log_erro(f"Erro ao criar usuário '{nome}': {e}")
        elif op == "3":  # Listar usuários
            listar_usuarios()
        elif op == "4":  # Sair
            print("Encerrando o sistema.")
            break
        else:
            print("Opção inválida.")

# ------------------------------ bootstrap --------------------------------
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_erro(f"Erro crítico no main: {e}")
        print("Erro crítico. Veja logs/erros.log.")
