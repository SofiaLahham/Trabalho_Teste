# main.py
from pathlib import Path
from datetime import datetime

# --- imports do pacote (nomes exigidos no enunciado) ---
from Streaming.menu import Menu
from Streaming.usuario import Usuario
from Streaming.musica import Musica
from Streaming.podcast import Podcast
from Streaming.playlist import Playlist
from Streaming.analises import Analises
from Streaming.arquivo_de_midia import ArquivoDeMidia

# ------------------------------ coleções globais ------------------------------
USUARIOS: list[Usuario] = []
MUSICAS:  list[Musica]  = []
PODCASTS: list[Podcast] = []
PLAYLISTS:list[Playlist]= []

# ------------------------------ caminhos padrão -------------------------------
ARQ_DADOS = Path("config/dados.md")
ARQ_LOG   = Path("logs/erros.log")
ARQ_REL   = Path("relatorios/relatorio.txt")

# ------------------------------- utilidades ----------------------------------
def log_erro(msg: str) -> None:
    """Anexa linha de erro com timestamp (sem libs externas)."""
    ARQ_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ARQ_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")


def escrever_relatorio(texto: str) -> None:
    """Salva relatório final em relatorios/relatorio.txt."""
    ARQ_REL.parent.mkdir(parents=True, exist_ok=True)
    ARQ_REL.write_text(texto, encoding="utf-8")


def encontrar_usuario(nome: str) -> Usuario | None:
    """Procura usuário pelo nome (case-insensitive)."""
    n = nome.strip().lower()
    for u in USUARIOS:
        if u.nome.strip().lower() == n:
            return u
    return None


# ------------------------- carga do config/dados.md ---------------------------
def carregar_dados() -> None:
    """
    Parser simples do arquivo markdown:
      # MÚSICAS  -> - titulo | duracao | artista | genero
      # PODCASTS -> - titulo | duracao | artista | temporada | episodio | host
      # USUÁRIOS -> - nome
    """
    if not ARQ_DADOS.exists():
        log_erro("Arquivo de dados não encontrado.")
        return

    sec = None
    linhas = ARQ_DADOS.read_text(encoding="utf-8").splitlines()
    for raw in linhas:
        li = raw.strip()
        if not li or li.startswith("# Aqui"):
            continue

        # títulos de seção (tolerante a acentos/maiúsculas)
        if li.startswith("#"):
            t = li.lstrip("#").strip().upper()
            if "MUSICA" in t or "MÚSICA" in t:
                sec = "M"
            elif "PODCAST" in t:
                sec = "P"
            elif "USUARIO" in t or "USUÁRIO" in t:
                sec = "U"
            else:
                sec = None
            continue

        try:
            if sec == "M":  # músicas
                if not li.startswith("-"):
                    raise ValueError("Linha de MÚSICAS deve iniciar com '-'")
                campos = [c.strip() for c in li.lstrip("-").split("|")]
                if len(campos) != 4:
                    raise ValueError("MÚSICAS: esperado 4 campos")
                titulo, duracao, artista, genero = campos
                dur = int(duracao)
                MUSICAS.append(Musica(titulo, dur, artista, genero))

            elif sec == "P":  # podcasts
                if not li.startswith("-"):
                    raise ValueError("Linha de PODCASTS deve iniciar com '-'")
                campos = [c.strip() for c in li.lstrip("-").split("|")]
                if len(campos) != 6:
                    raise ValueError("PODCASTS: esperado 6 campos")
                titulo, duracao, artista, temporada, episodio, host = campos
                dur = int(duracao)
                epi = int(episodio)
                PODCASTS.append(Podcast(titulo, dur, artista, temporada, epi, host))

            elif sec == "U":  # usuários
                if not li.startswith("-"):
                    raise ValueError("Linha de USUÁRIOS deve iniciar com '-'")
                nome = li.lstrip("-").strip()
                if not encontrar_usuario(nome):
                    USUARIOS.append(Usuario(nome))
                else:
                    log_erro(f"Usuário duplicado ignorado: {nome}")
        except Exception as e:
            log_erro(f"Erro ao processar linha: {raw} ({e})")


# ------------------------------- ações de menu --------------------------------
def listar_musicas() -> None:
    if not MUSICAS:
        print("Não há músicas.")
        return
    for m in MUSICAS:
        print(m)


def listar_podcasts() -> None:
    if not PODCASTS:
        print("Não há podcasts.")
        return
    for p in PODCASTS:
        print(p)


def listar_playlists() -> None:
    if not PLAYLISTS:
        print("Não há playlists.")
        return
    for pl in PLAYLISTS:
        print(pl)


def listar_usuarios() -> None:
    if not USUARIOS:
        print("Não há usuários.")
        return
    for u in USUARIOS:
        print(u)


def acao_reproduzir_midia(usuario: Usuario) -> None:
    """Reproduz música/podcast pelo título (busca global por título)."""
    titulo = input("Título da mídia (música/podcast): ").strip()
    mid = ArquivoDeMidia.buscar_por_titulo(titulo)
    if mid is None:
        print("Mídia não encontrada.")
        log_erro(f"Tentativa de reproduzir mídia inexistente: {titulo}")
        return
    try:
        usuario.ouvir_midia(mid)
    except Exception as e:
        log_erro(f"Erro ao reproduzir '{titulo}' para {usuario.nome}: {e}")


def acao_criar_playlist(usuario: Usuario) -> None:
    """Cria playlist para o usuário e registra também no índice global."""
    nome = input("Nome da nova playlist: ").strip()
    try:
        pl = usuario.criar_playlist(nome)  # valida duplicidade por usuário
        if pl not in PLAYLISTS:
            PLAYLISTS.append(pl)
        print(f"Playlist '{pl.nome}' criada.")
    except ValueError as e:
        print("Não foi possível criar playlist.")
        log_erro(f"Erro ao criar playlist '{nome}' para {usuario.nome}: {e}")


def acao_reproduzir_playlist(usuario: Usuario) -> None:
    """Reproduz playlist do usuário (nome case-insensitive)."""
    nome_in = input("Nome da playlist: ").strip().lower()

    # 1) busca primeiro nas playlists do próprio usuário
    alvo = next((p for p in usuario.playlists
                 if p.nome.strip().lower() == nome_in), None)

    # 2) fallback: busca no índice global comparando pelo NOME do usuário
    if not alvo:
        uname = usuario.nome.strip().lower()
        alvo = next((p for p in PLAYLISTS
                     if p.nome.strip().lower() == nome_in
                     and p.usuario.nome.strip().lower() == uname), None)

    if not alvo:
        print("Playlist não encontrada para este usuário.")
        log_erro(f"Playlist inexistente para {usuario.nome}: {nome_in}")
        return

    alvo.reproduzir()


def acao_concatenar_playlists(usuario: Usuario) -> None:
    """Concatena duas playlists do usuário usando __add__."""
    a = input("Nome da playlist A (destino): ").strip().lower()
    b = input("Nome da playlist B (origem) : ").strip().lower()

    pa = next((p for p in usuario.playlists if p.nome.strip().lower() == a), None)
    pb = next((p for p in usuario.playlists if p.nome.strip().lower() == b), None)

    if not pa or not pb:
        print("Playlist A ou B não encontrada.")
        log_erro(f"Concatenação inválida para {usuario.nome}: A='{a}' B='{b}'")
        return

    nova = pa + pb  # mantém nome da A e soma reproduções (regra do enunciado)

    # evita nome exatamente duplicado na coleção do usuário
    base = nova.nome
    suf = 1
    while any(p.nome.strip().lower() == nova.nome.strip().lower()
              for p in usuario.playlists):
        suf += 1
        nova.nome = f"{base} ({suf})"

    usuario.playlists.append(nova)
    PLAYLISTS.append(nova)
    print(f"Playlist concatenada criada: {nova.nome}")


def acao_gerar_relatorio() -> None:
    """Gera relatório agregando as análises exigidas."""
    linhas: list[str] = []
    linhas.append("=== RELATÓRIO DO SISTEMA ===")
    linhas.append(f"Usuários: {len(USUARIOS)} | Músicas: {len(MUSICAS)} | Podcasts: {len(PODCASTS)}")
    linhas.append("")

    # Top músicas (usa argumento posicional para evitar problemas)
    linhas.append("Top 5 músicas mais reproduzidas:")
    top5 = Analises.top_musicas_reproduzidas(MUSICAS, 5)
    if not top5:
        linhas.append("- (vazio)")
    else:
        for m in top5:
            linhas.append(f"- {m.titulo} ({m.reproducoes})")
    linhas.append("")

    # Playlist mais popular
    pop = Analises.playlist_mais_popular(PLAYLISTS)
    linhas.append(f"Playlist mais popular: {pop.nome if pop else 'N/A'}")

    # Usuário mais ativo
    ativo = Analises.usuario_mais_ativo(USUARIOS)
    linhas.append(f"Usuário mais ativo: {ativo.nome if ativo else 'N/A'}")
    linhas.append("")

    # Médias de avaliação por música
    linhas.append("Médias de avaliação por música:")
    medias = Analises.media_avaliacoes(MUSICAS)
    if not medias:
        linhas.append("- (vazio)")
    else:
        for titulo, media in medias.items():
            linhas.append(f"- {titulo}: {media:.2f}")
    linhas.append("")

    # Total de reproduções (histórico somado)
    total = Analises.total_reproducoes(USUARIOS)
    linhas.append(f"Total de reproduções no sistema: {total}")

    escrever_relatorio("\n".join(linhas))
    print(f"Relatório salvo em {ARQ_REL}")


# -------------------------------- fluxo principal -----------------------------
def main() -> None:
    carregar_dados()            # lê config/dados.md e preenche listas
    menu = Menu()

    while True:
        op = menu.exibir_menu_inicial()
        if op == "1":  # Entrar como usuário
            nome = input("Nome do usuário: ").strip()
            u = encontrar_usuario(nome)
            if not u:
                print("Usuário não encontrado.")
                continue

            # menu interno do usuário
            while True:
                opu = menu.exibir_menu_usuario(u.nome)
                if   opu == "1": acao_reproduzir_midia(u)
                elif opu == "2": listar_musicas()
                elif opu == "3": listar_podcasts()
                elif opu == "4": listar_playlists()
                elif opu == "5": acao_reproduzir_playlist(u)
                elif opu == "6": acao_criar_playlist(u)
                elif opu == "7": acao_concatenar_playlists(u)
                elif opu == "8": acao_gerar_relatorio()
                elif opu == "9": break
                else: print("Opção inválida.")

        elif op == "2":  # Criar novo usuário
            nome = input("Nome do novo usuário: ").strip()
            if encontrar_usuario(nome):
                print("Usuário já existe.")
                log_erro(f"Tentativa de criar usuário duplicado: {nome}")
            else:
                try:
                    USUARIOS.append(Usuario(nome))
                    print("Usuário criado.")
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


# --------------------------------- execução -----------------------------------
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_erro(f"Erro crítico: {e}")
        print("Erro crítico. Veja logs/erros.log.")
