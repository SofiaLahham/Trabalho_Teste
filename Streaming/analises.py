# main.py
# Ponto de entrada do sistema: carrega dados, exibe menus e coordena as ações.

from datetime import datetime
from pathlib import Path

from Streaming import Menu, Musica, Podcast, Playlist, Usuario, Analises
from Streaming.arquivo_de_midia import ArquivoDeMidia

# --- caminhos padrão (enunciado) ---
ARQ_DADOS = Path("config/dados.md")
ARQ_LOG   = Path("logs/erros.log")
ARQ_REL   = Path("relatorios/relatorio.txt")

# --- coleções principais em memória ---
USUARIOS: list[Usuario] = []
MUSICAS: list[Musica] = []
PODCASTS: list[Podcast] = []
PLAYLISTS: list[Playlist] = []

# --- util simples de log (timestamp + mensagem) ---
def log_erro(msg: str) -> None:
    ARQ_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ARQ_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat(sep=' ', timespec='seconds')}] {msg}\n")

# --- grava relatório final com análises ---
def escrever_relatorio(texto: str) -> None:
    ARQ_REL.parent.mkdir(parents=True, exist_ok=True)
    ARQ_REL.write_text(texto, encoding="utf-8")

# --- busca usuário por nome (case-insensitive) ---
def encontrar_usuario(nome: str) -> Usuario | None:
    n = nome.strip().lower()
    for u in USUARIOS:
        if u.nome.strip().lower() == n:
            return u
    return None

# --- parser simples do dados.md (linhas com "|" separando campos) ---
def carregar_dados(caminho: Path) -> None:
    """
    Seções esperadas (nomes tolerantes): MÚSICAS, PODCASTS, USUÁRIOS, PLAYLISTS (opcional).
    Formatos:
      MÚSICAS  : titulo | duracao | artista | genero
      PODCASTS : titulo | duracao | artista(canal) | temporada | episodio | host
      USUÁRIOS : - Nome
      PLAYLISTS: nome | usuario | item1,item2,item3   (títulos separados por vírgula)
    """
    if not caminho.exists():
        log_erro(f"Arquivo de dados não encontrado: {caminho}")
        return

    sec = None
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        li = linha.strip()
        if not li or li.startswith("# Aqui"):
            continue

        # títulos de seção
        if li.startswith("#"):
            titulo = li.lstrip("#").strip().upper()
            if "MÚSICA" in titulo or "MUSICA" in titulo:
                sec = "MUSICAS"
            elif "PODCAST" in titulo:
                sec = "PODCASTS"
            elif "USUÁRI" in titulo or "USUARI" in titulo:
                sec = "USUARIOS"
            elif "PLAYLIST" in titulo:
                sec = "PLAYLISTS"
            else:
                sec = None
            continue

        # itens
        try:
            if sec == "USUARIOS":
                if li.startswith("-"):
                    nome = li.lstrip("-").strip()
                    if not encontrar_usuario(nome):
                        USUARIOS.append(Usuario(nome))
                    else:
                        log_erro(f"Usuário duplicado ignorado: {nome}")
            elif sec == "MUSICAS":
                if li.startswith("-"):
                    campos = [c.strip() for c in li.lstrip("-").split("|")]
                    if len(campos) != 4:
                        raise ValueError(f"Formato inválido (MÚSICAS): {li}")
                    titulo, duracao, artista, genero = campos
                    dur = int(duracao)
                    MUSICAS.append(Musica(titulo, dur, artista, genero))
            elif sec == "PODCASTS":
                if li.startswith("-"):
                    campos = [c.strip() for c in li.lstrip("-").split("|")]
                    if len(campos) != 6:
                        raise ValueError(f"Formato inválido (PODCASTS): {li}")
                    titulo, duracao, artista, temporada, episodio, host = campos
                    dur = int(duracao)
                    epi = int(episodio)
                    # artista (canal) vai no campo 'artista' herdado
                    PODCASTS.append(Podcast(titulo, dur, artista, temporada, epi, host))
            elif sec == "PLAYLISTS":
                # opcional: nome | usuario | tit1,tit2,tit3
                if li.startswith("-"):
                    campos = [c.strip() for c in li.lstrip("-").split("|")]
                    if len(campos) != 3:
                        raise ValueError(f"Formato inválido (PLAYLISTS): {li}")
                    nome_pl, nome_usuario, itens_str = campos
                    user = encontrar_usuario(nome_usuario)
                    if not user:
                        log_erro(f"Playlist com usuário inexistente: {nome_pl} / {nome_usuario}")
                        continue
                    try:
                        nova = user.criar_playlist(nome_pl)
                        PLAYLISTS.append(nova)
                    except ValueError as e:
                        log_erro(f"Playlist duplicada para usuário {nome_usuario}: {nome_pl} ({e})")
                        continue
                    # resolver itens por título (música ou podcast)
                    for t in [s.strip() for s in itens_str.split(",") if s.strip()]:
                        mid = ArquivoDeMidia.buscar_por_titulo(t)
                        if mid is None:
                            log_erro(f"Item inexistente na playlist '{nome_pl}': {t}")
                        else:
                            nova.adicionar_midia(mid)
        except ValueError as e:
            log_erro(f"Erro ao processar linha '{li}': {e}")
        except Exception as e:
            log_erro(f"Erro inesperado: {e} | linha='{li}'")

# --- telas auxiliares (listar) ---
def listar_usuarios() -> None:
    if not USUARIOS:
        print("Não há usuários.")
        return
    for u in USUARIOS:
        print(u)

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

# --- ações do menu do usuário logado ---
def acao_reproduzir_musica(usuario: Usuario) -> None:
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

def acao_reproduzir_playlist(usuario: Usuario) -> None:
    nome = input("Nome da playlist: ").strip()
    alvo = None
    # procura entre as playlists do usuário
    for p in usuario.playlists:
        if p.nome.strip().lower() == nome.lower():
            alvo = p
            break
    if not alvo:
        print("Playlist não encontrada para este usuário.")
        log_erro(f"Playlist inexistente para {usuario.nome}: {nome}")
        return
    alvo.reproduzir()

def acao_criar_playlist(usuario: Usuario) -> None:
    nome = input("Nome da nova playlist: ").strip()
    try:
        pl = usuario.criar_playlist(nome)
        PLAYLISTS.append(pl)
        print(f"Playlist criada: {pl.nome}")
    except ValueError as e:
        print("Não foi possível criar playlist.")
        log_erro(f"Erro ao criar playlist '{nome}' para {usuario.nome}: {e}")

def acao_concatenar_playlists(usuario: Usuario) -> None:
    a = input("Nome da playlist A: ").strip()
    b = input("Nome da playlist B: ").strip()
    pa = pb = None
    for p in usuario.playlists:
        if p.nome.strip().lower() == a.lower():
            pa = p
        if p.nome.strip().lower() == b.lower():
            pb = p
    if not pa or not pb:
        print("Playlist A ou B não encontrada.")
        log_erro(f"Concatenação inválida para {usuario.nome}: A='{a}' B='{b}'")
        return
    nova = pa + pb
    # nome da nova = nome da A (regra do enunciado)
    # evitar duplicidade de nome: se já existir, acrescenta sufixo numérico simples
    base = nova.nome
    suf = 1
    while any(p.nome.strip().lower() == nova.nome.strip().lower() for p in usuario.playlists):
        suf += 1
        nova.nome = f"{base} ({suf})"
    usuario.playlists.append(nova)
    PLAYLISTS.append(nova)
    print(f"Playlist concatenada criada: {nova.nome}")

def acao_gerar_relatorio() -> None:
    # Gera estatísticas conforme Analises
    texto = []
    texto.append("=== RELATÓRIO DO SISTEMA ===")
    texto.append(f"Usuários: {len(USUARIOS)} | Músicas: {len(MUSICAS)} | Podcasts: {len(PODCASTS)} | Playlists: {len(PLAYLISTS)}")

    # top músicas por reproduções (Top 5)
    top5 = Analises.top_musicas_reproduzidas(MUSICAS, 5)
    texto.append("\nTop músicas reproduzidas:")
    if not top5:
        texto.append("- (vazio)")
    else:
        for i, m in enumerate(top5, start=1):
            texto.append(f"{i}. {m.titulo} - {m.artista} ({m.reproducoes} plays)")

    # playlist mais popular
    pop = Analises.playlist_mais_popular(PLAYLISTS)
    texto.append("\nPlaylist mais popular:")
    texto.append("- (vazio)" if pop is None else f"- {pop.nome} ({pop.reproducoes} execuções)")

    # usuário mais ativo
    ativo = Analises.usuario_mais_ativo(USUARIOS)
    texto.append("\nUsuário mais ativo:")
    texto.append("- (vazio)" if ativo is None else f"- {ativo.nome} ({len(ativo.historico)} reproduções)")

    # médias de avaliações
    medias = Analises.media_avaliacoes(MUSICAS)
    texto.append("\nMédias de avaliação por música:")
    if not medias:
        texto.append("- (vazio)")
    else:
        for t, m in medias.items():
            texto.append(f"- {t}: {m:.2f}")

    # total de reproduções (histórico somado)
    tot = Analises.total_reproducoes(USUARIOS)
    texto.append(f"\nTotal de reproduções (histórico somado): {tot}")

    escrever_relatorio("\n".join(texto))
    print(f"Relatório gerado em: {ARQ_REL}")

# --- fluxo principal ---
def main():
    # 1) Carga inicial dos dados
    carregar_dados(ARQ_DADOS)

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
                if opu == "1":
                    acao_reproduzir_musica(u)
                elif opu == "2":
                    listar_musicas()
                elif opu == "3":
                    listar_podcasts()
                elif opu == "4":
                    listar_playlists()
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

if __name__ == "__main__":
    main()
