# main.py
from pathlib import Path
from datetime import datetime
import unicodedata  # normalizar títulos de seção com acento

from Streaming.menu import Menu
from Streaming.usuario import Usuario
from Streaming.musica import Musica
from Streaming.podcast import Podcast
from Streaming.playlist import Playlist
from Streaming.analises import Analises
from Streaming.arquivo_de_midia import ArquivoDeMidia

# ------------------------------ coleções globais ------------------------------
USUARIOS: list[Usuario] = []
MUSICAS: list[Musica] = []
PODCASTS: list[Podcast] = []
PLAYLISTS: list[Playlist] = []

# caminhos padrão
ARQ_DADOS = Path("config/dados.md")
ARQ_LOG = Path("logs/erros.log")
ARQ_REL = Path("relatorios/relatorio.txt")

# ------------------------------ utilidades ------------------------------------
def log_erro(msg: str) -> None:
    """Acrescenta linha no log com data/hora."""
    ARQ_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ARQ_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def escrever_relatorio(texto: str) -> None:
    """Grava relatório final."""
    ARQ_REL.parent.mkdir(parents=True, exist_ok=True)
    ARQ_REL.write_text(texto, encoding="utf-8")

def _norm(s: str) -> str:
    """Normaliza para maiúsculas sem acento (ajuda nas seções do .md)."""
    s = unicodedata.normalize("NFD", s.upper())
    return "".join(ch for ch in s if unicodedata.category(ch) != "Mn")

def encontrar_usuario(nome: str) -> Usuario | None:
    """Busca usuário por nome (case-insensitive)."""
    alvo = nome.strip().lower()
    for u in USUARIOS:
        if u.nome.strip().lower() == alvo:
            return u
    return None

def _playlist_do_usuario(u: Usuario, nome_pl: str) -> Playlist | None:
    """Busca playlist por nome dentro do usuário."""
    alvo = nome_pl.strip().lower()
    for pl in u.playlists:
        if pl.nome.strip().lower() == alvo:
            return pl
    return None

# ------------------------------ parser do dados.md ----------------------------
def carregar_dados() -> None:
    """Lê config/dados.md e povoa USUARIOS/MUSICAS/PODCASTS."""
    if not ARQ_DADOS.exists():
        log_erro("Arquivo de dados não encontrado.")
        return

    sec = None  # M=musicas, P=podcasts, U=usuarios
    for linha in ARQ_DADOS.read_text(encoding="utf-8").splitlines():
        li = linha.strip()
        if not li or li.startswith("# Aqui"):
            continue

        # título de seção (aceita acento: MÚSICAS/USUÁRIOS)
        if li.startswith("#"):
            titulo = _norm(li.lstrip("#").strip())
            if "MUSICA" in titulo:
                sec = "M"
            elif "PODCAST" in titulo:
                sec = "P"
            elif "USUARIO" in titulo:
                sec = "U"
            else:
                sec = None
            continue

        # itens iniciando com "-"
        try:
            if sec == "U" and li.startswith("-"):
                nome = li.lstrip("-").strip()
                if not encontrar_usuario(nome):
                    USUARIOS.append(Usuario(nome))
                else:
                    log_erro(f"Tentativa de criar usuário duplicado: {nome}")

            elif sec == "M" and li.startswith("-"):
                campos = [c.strip() for c in li.lstrip("-").split("|")]
                if len(campos) != 4:
                    raise ValueError("MÚSICAS exige: titulo|duracao|artista|genero")
                t, d, a, g = campos
                dur = int(d)
                MUSICAS.append(Musica(t, dur, a, g))

            elif sec == "P" and li.startswith("-"):
                campos = [c.strip() for c in li.lstrip("-").split("|")]
                if len(campos) != 6:
                    raise ValueError("PODCASTS exige: titulo|duracao|artista|temporada|episodio|host")
                t, d, a, temp, epi, h = campos
                dur = int(d)
                ep = int(epi)
                PODCASTS.append(Podcast(t, dur, a, temp, ep, h))

        except Exception as e:
            log_erro(f"Erro ao processar linha: {linha} ({e})")

# ------------------------------ ações do menu ---------------------------------
def acao_reproduzir_midia(usuario: Usuario) -> None:
    """Reproduz mídia por título usando registro global de mídias."""
    titulo = input("Título da mídia (música/podcast): ").strip()
    mid = ArquivoDeMidia.buscar_por_titulo(titulo)
    if mid:
        usuario.ouvir_midia(mid)
    else:
        print("Mídia não encontrada.")
        log_erro(f"Tentativa de reprodução inválida: {titulo}")

def acao_listar_musicas() -> None:
    if not MUSICAS:
        print("Nenhuma música cadastrada.")
        return
    for m in MUSICAS:
        print(m)

def acao_listar_podcasts() -> None:
    if not PODCASTS:
        print("Nenhum podcast cadastrado.")
        return
    for p in PODCASTS:
        print(p)

def acao_listar_playlists() -> None:
    if not PLAYLISTS:
        print("Nenhuma playlist cadastrada.")
        return
    for pl in PLAYLISTS:
        print(pl)

def acao_reproduzir_playlist(usuario: Usuario) -> None:
    nome = input("Nome da playlist: ").strip()
    pl = _playlist_do_usuario(usuario, nome)
    if not pl:
        print("Playlist não encontrada para este usuário.")
        log_erro(f"Playlist inexistente para {usuario.nome}: {nome}")
        return
    pl.reproduzir()

def acao_criar_playlist(usuario: Usuario) -> None:
    """Cria playlist e obriga a adicionar 1 música (pedido do professor)."""
    nome = input("Nome da nova playlist: ").strip()
    try:
        pl = usuario.criar_playlist(nome)          # valida duplicidade por usuário
        PLAYLISTS.append(pl)
        print(f"Playlist '{pl.nome}' criada.")
    except ValueError as e:
        print(e)
        log_erro(f"Erro ao criar playlist '{nome}' para {usuario.nome}: {e}")
        return

    # Perguntas obrigatórias para adicionar uma música
    print("\nAgora adicione uma música à playlist:")
    t = input("Qual o nome da música que você irá adicionar? ").strip()
    try:
        d = int(input("Qual a duração em segundos? ").strip())
    except ValueError:
        print("Duração inválida (use números).")
        log_erro("Duração inválida ao adicionar música na criação de playlist.")
        return
    a = input("Quem é o cantor? ").strip()
    g = input("Qual o gênero musical? ").strip()

    try:
        nova = Musica(t, d, a, g)
        MUSICAS.append(nova)  # mantém catálogo visível
        pl.adicionar_midia(nova)
        print(f"Música '{t}' adicionada à playlist '{pl.nome}'.")
    except Exception as e:
        print("Não foi possível adicionar a música.")
        log_erro(f"Falha ao adicionar música '{t}' em '{pl.nome}': {e}")

def acao_concatenar_playlists(usuario: Usuario) -> None:
    a = input("Nome da playlist A: ").strip()
    b = input("Nome da playlist B: ").strip()
    pa = _playlist_do_usuario(usuario, a)
    pb = _playlist_do_usuario(usuario, b)
    if not pa or not pb:
        print("Playlist de destino ou origem não encontrada.")
        log_erro(f"Concatenação inválida para {usuario.nome}: A='{a}' B='{b}'")
        return
    nova = pa + pb
    # evita conflito de nome no mesmo usuário
    base = nova.nome
    suf = 1
    while _playlist_do_usuario(usuario, nova.nome):
        suf += 1
        nova.nome = f"{base} ({suf})"
    usuario.playlists.append(nova)
    PLAYLISTS.append(nova)
    print(f"Playlist concatenada criada: {nova.nome}")

def acao_gerar_relatorio() -> None:
    """Gera relatório agregando as análises pedidas."""
    linhas: list[str] = []
    linhas.append("=== RELATÓRIO DO SISTEMA ===")
    linhas.append(f"Usuários: {len(USUARIOS)} | Músicas: {len(MUSICAS)} | Podcasts: {len(PODCASTS)}")
    linhas.append("")

    # Top músicas (usa parâmetro posicional para evitar erro de nome)
    top = Analises.top_musicas_reproduzidas(MUSICAS, 5)
    linhas.append("Top 5 músicas mais reproduzidas:")
    if not top:
        linhas.append("- Nenhuma")
    else:
        for m in top:
            linhas.append(f"- {m.titulo} ({m.reproducoes})")
    linhas.append("")

    # Playlist mais popular
    pl = Analises.playlist_mais_popular(PLAYLISTS)
    linhas.append(f"Playlist mais popular: {pl.nome if pl else 'N/A'}")

    # Usuário mais ativo
    u = Analises.usuario_mais_ativo(USUARIOS)
    linhas.append(f"Usuário mais ativo: {u.nome if u else 'N/A'}")
    linhas.append("")

    # Médias de avaliação por música
    medias = Analises.media_avaliacoes(MUSICAS)
    linhas.append("Médias de avaliação por música:")
    if not medias:
        linhas.append("- N/A")
    else:
        for k, v in medias.items():
            linhas.append(f"- {k}: {v:.2f}")
    linhas.append("")

    # Total de reproduções
    total = Analises.total_reproducoes(USUARIOS)
    linhas.append(f"Total de reproduções no sistema: {total}")

    escrever_relatorio("\n".join(linhas))
    print(f"Relatório salvo em {ARQ_REL}")

# ------------------------------ função principal ------------------------------
def main() -> None:
    carregar_dados()  # puxa do config/dados.md
    menu = Menu()

    while True:
        op = menu.exibir_menu_inicial()
        if op == "1":  # Entrar como usuário
            nome = input("Nome do usuário: ").strip()
            u = encontrar_usuario(nome)
            if not u:
                print("Usuário não encontrado.")
                continue

            # menu do usuário logado
            while True:
                opu = menu.exibir_menu_usuario(u.nome)
                if opu == "1":
                    acao_reproduzir_midia(u)
                elif opu == "2":
                    acao_listar_musicas()
                elif opu == "3":
                    acao_listar_podcasts()
                elif opu == "4":
                    acao_listar_playlists()
                elif opu == "5":
                    acao_reproduzir_playlist(u)
                elif opu == "6":
                    acao_criar_playlist(u)
                elif opu == "7":
                    acao_concatenar_playlists(u)
                elif opu == "8":
                    acao_gerar_relatorio()
                elif opu == "9":
                    break  # sair do usuário
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
            if not USUARIOS:
                print("Não há usuários.")
            else:
                for u in USUARIOS:
                    print(u)

        elif op == "4":  # Sair do sistema
            print("Encerrando o sistema.")
            break

        else:
            print("Opção inválida.")

# --------------------------------- execução -----------------------------------
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_erro(f"Erro crítico: {e}")
        print("Erro crítico. Veja logs/erros.log.")
