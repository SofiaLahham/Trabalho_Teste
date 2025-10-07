# main.py
from pathlib import Path
from datetime import datetime

# Imports do pacote Streaming
from Streaming.menu import Menu
from Streaming.usuario import Usuario
from Streaming.musica import Musica
from Streaming.podcast import Podcast
from Streaming.playlist import Playlist
from Streaming.analises import Analises
from Streaming.arquivo_de_midia import ArquivoDeMidia

# --------------------------------- Coleções -----------------------------------
USUARIOS = []
MUSICAS = []
PODCASTS = []
PLAYLISTS = []

# ---------------------------------- Caminhos ----------------------------------
ARQ_DADOS = Path("config/dados.md")
ARQ_LOG = Path("logs/erros.log")
ARQ_REL = Path("relatorios/relatorio.txt")

# --------------------------------- Utilidades ---------------------------------
def _norm(s):
    return " ".join((s or "").strip().split()).lower()

def log_erro(msg):
    ARQ_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ARQ_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] {msg}\n")

def escrever_relatorio(texto):
    ARQ_REL.parent.mkdir(parents=True, exist_ok=True)
    ARQ_REL.write_text(texto, encoding="utf-8")

def encontrar_usuario(nome):
    alvo = _norm(nome)
    for u in USUARIOS:
        if _norm(u.nome) == alvo:
            return u
    return None

def _parse_inline_list(value):
    v = (value or "").strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1]
        return [x.strip() for x in inner.split(",") if x.strip()]
    return []

def _split_sections_md(text):
    """
    Divide por '---' e mapeia '# Título' -> bloco de linhas seguintes.
    Suporta: Usuários, Músicas, Podcasts, Playlists (variações de caixa/acentos).
    """
    parts = [b.strip() for b in text.split("---") if b.strip()]
    out = {}
    for block in parts:
        lines = [ln.rstrip() for ln in block.splitlines() if ln.strip()]
        if lines and lines[0].startswith("# "):
            title = lines[0][2:].strip()
            out[title] = "\n".join(lines[1:])
    return out

def _parse_items_block_md(block):
    """
    Lê itens no formato:
      - chave: valor
        outra: valor
    Retorna lista de dicts.
    """
    items = []
    current = None
    for line in (block or "").splitlines():
        if line.lstrip().startswith("- "):
            if current:
                items.append(current)
            current = {}
            body = line.strip()[2:]
            if body and ":" in body:
                k, v = body.split(":", 1)
                current[k.strip()] = v.strip()
        elif line.startswith("  "):
            ln = line.strip()
            if ":" in ln and current is not None:
                k, v = ln.split(":", 1)
                current[k.strip()] = v.strip()
    if current:
        items.append(current)
    return items

# ------------------------------- Carga de dados -------------------------------
def carregar_dados():
    """
    Lê config/dados.md no padrão do professor e preenche:
    USUARIOS, MUSICAS, PODCASTS, PLAYLISTS.
    Idempotente; registra erros sem interromper a execução.
    """
    if not ARQ_DADOS.exists():
        log_erro("Arquivo de dados não encontrado.")
        return

    # Idempotência
    USUARIOS[:] = []
    MUSICAS[:] = []
    PODCASTS[:] = []
    PLAYLISTS[:] = []
    ArquivoDeMidia.registroMidia[:] = []

    try:
        raw = ARQ_DADOS.read_text(encoding="utf-8")
    except Exception as e:
        log_erro(f"Falha ao ler {ARQ_DADOS}: {e}")
        return

    sections = _split_sections_md(raw)
    sections_ci = { _norm(k): v for k, v in sections.items() }
    def sec(name):
        return sections_ci.get(_norm(name), "")

    # ------------------------ MÚSICAS ------------------------
    for m in _parse_items_block_md(sec("Músicas")) + _parse_items_block_md(sec("Musicas")):
        try:
            titulo  = (m.get("titulo", "")).strip()
            artista = (m.get("artista", "")).strip()
            genero  = (m.get("genero", "")).strip()
            duracao = int(m.get("duracao", "0"))
            if duracao <= 0:
                log_erro(f"Música '{titulo}': duração inválida ({duracao}).")
                continue
            if any(_norm(x.titulo) == _norm(titulo) for x in MUSICAS):
                continue
            MUSICAS.append(Musica(titulo, duracao, artista, genero))
        except Exception as e:
            log_erro(f"Erro ao criar música {m}: {e}")

    # ------------------------ PODCASTS -----------------------
    for p in _parse_items_block_md(sec("Podcasts")):
        try:
            titulo    = (p.get("titulo", "")).strip()
            temporada = (p.get("temporada", "")).strip()
            host      = (p.get("host", "")).strip()
            duracao   = int(p.get("duracao", "0"))
            episodio  = int(p.get("episodio", "0"))
            if duracao <= 0 or episodio <= 0:
                log_erro(f"Podcast '{titulo}': duração/episódio inválido (dur={duracao}, ep={episodio}).")
                continue
            if any(_norm(x.titulo) == _norm(titulo) for x in PODCASTS):
                continue

            # Compatível com duas possíveis assinaturas do Podcast:
            # 1) Podcast(titulo, duracao, host, temporada, episodio)
            # 2) Podcast(titulo, duracao, artista, temporada, episodio, host)
            ok = False
            try:
                PODCASTS.append(Podcast(titulo, duracao, host, temporada, episodio))
                ok = True
            except TypeError:
                pass
            if not ok:
                try:
                    PODCASTS.append(Podcast(titulo, duracao, host, temporada, episodio, host))
                    ok = True
                except Exception as e2:
                    log_erro(f"Assinatura incompatível para Podcast '{titulo}': {e2}")
            if not ok:
                log_erro(f"Falha ao criar podcast '{titulo}'.")
        except ValueError:
            log_erro(f"Podcast '{p.get('titulo','')}': episódio inválido '{p.get('episodio','')}'.")
        except Exception as e:
            log_erro(f"Erro ao criar podcast {p}: {e}")

    # ------------------------ USUÁRIOS -----------------------
    for u in _parse_items_block_md(sec("Usuários")) + _parse_items_block_md(sec("Usuarios")):
        try:
            nome = (u.get("nome", "")).strip()
            if not nome:
                continue
            if encontrar_usuario(nome) is None:
                USUARIOS.append(Usuario(nome))
        except Exception as e:
            log_erro(f"Erro ao criar usuário {u}: {e}")

    # Índices para resolver itens por título (case-insensitive)
    idx_musicas  = { _norm(m.titulo): m for m in MUSICAS }
    idx_podcasts = { _norm(p.titulo): p for p in PODCASTS }

    # ------------------------ PLAYLISTS ----------------------
    for pl in _parse_items_block_md(sec("Playlists")):
        try:
            nome   = (pl.get("nome", "")).strip()
            dono   = (pl.get("usuario", "")).strip()
            itens  = _parse_inline_list(pl.get("itens", "[]"))
            if not nome:
                log_erro("Playlist sem nome ignorada.")
                continue
            u = encontrar_usuario(dono)
            if not u:
                log_erro(f"Playlist '{nome}': usuário inexistente '{dono}'.")
                continue
            if any(_norm(p.nome) == _norm(nome) for p in u.playlists):
                log_erro(f"Playlist duplicada para '{dono}': '{nome}'.")
                continue

            playlist = u.criar_playlist(nome)
            PLAYLISTS.append(playlist)

            vistos = set()
            for titulo_item in itens:
                key = _norm(titulo_item)
                if key in vistos:
                    log_erro(f"Item repetido na playlist '{nome}': '{titulo_item}'.")
                    continue
                vistos.add(key)
                midia = idx_musicas.get(key) or idx_podcasts.get(key)
                if not midia:
                    log_erro(f"Item inexistente na playlist '{nome}': '{titulo_item}'.")
                    continue
                playlist.adicionar_midia(midia)
        except Exception as e:
            log_erro(f"Erro ao criar playlist {pl}: {e}")

# -------------------------------- Ações de menu -------------------------------
def acao_reproduzir(usuario):
    titulo = input("Título da mídia (música/podcast): ").strip()
    midia = ArquivoDeMidia.buscar_por_titulo(titulo)
    if midia:
        usuario.ouvir_midia(midia)
    else:
        print("Mídia não encontrada.")
        log_erro(f"Tentativa de reprodução inválida: {titulo}")

def acao_criar_playlist(usuario):
    """
    Cria playlist e obriga adicionar pelo menos 1 música.
    Perguntas obrigatórias:
      - Qual o nome da música que você irá adicionar?
      - Qual a duração em minutos? (converte para segundos)
      - Quem é o cantor?
      - Qual o gênero musical?
    Depois: loop (1 - Sim / 2 - Não) para adicionar mais músicas.
    """
    nome = input("Nome da nova playlist: ").strip()
    try:
        pl = usuario.criar_playlist(nome)
        PLAYLISTS.append(pl)
        print(f"Playlist '{pl.nome}' criada.")

        def _perguntar_e_adicionar_musica(dest):
            try:
                titulo = input("Qual o nome da música que você irá adicionar? ").strip()
                minutos_txt = input("Qual a duração em minutos? ").strip()
                minutos = int(minutos_txt)
                if minutos <= 0:
                    print("Duração inválida (minutos deve ser > 0).")
                    log_erro(f"Duração inválida (min) ao criar música '{titulo}' em '{dest.nome}'.")
                    return False
                duracao = minutos * 60
                artista = input("Quem é o cantor? ").strip()
                genero  = input("Qual o gênero musical? ").strip()
                nova = Musica(titulo, duracao, artista, genero)
                dest.adicionar_midia(nova)
                print(f"Música '{titulo}' adicionada à playlist '{dest.nome}'.")
                return True
            except ValueError:
                print("Duração inválida. Informe um número inteiro para minutos.")
                log_erro(f"Valor inválido para minutos ao criar música em '{dest.nome}'.")
                return False
            except Exception as e:
                print("Não foi possível adicionar a música.")
                log_erro(f"Falha ao adicionar música em '{dest.nome}': {e}")
                return False

        # pelo menos 1 música (repete até conseguir adicionar uma válida)
        while True:
            if _perguntar_e_adicionar_musica(pl):
                break

        # loop 1-Sim / 2-Não
        while True:
            print("\nDeseja adicionar mais uma música?")
            print("1 - Sim")
            print("2 - Não")
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "1":
                _perguntar_e_adicionar_musica(pl)
            elif opcao == "2":
                break
            else:
                print("Opção inválida. Digite 1 para Sim ou 2 para Não.")

    except ValueError as e:
        print(e)
        log_erro(str(e))

def acao_concatenar_playlists(usuario):
    a = input("Nome da playlist A: ").strip()
    b = input("Nome da playlist B: ").strip()
    pa = pb = None
    for p in usuario.playlists:
        if _norm(p.nome) == _norm(a):
            pa = p
        if _norm(p.nome) == _norm(b):
            pb = p
    if not pa or not pb:
        print("Playlist A ou B não encontrada.")
        log_erro(f"Concatenação inválida para {usuario.nome}: A='{a}' B='{b}'")
        return

    nova = pa + pb
    base = nova.nome
    suf = 1
    while any(_norm(p.nome) == _norm(nova.nome) for p in usuario.playlists):
        suf += 1
        nova.nome = f"{base} ({suf})"
    usuario.playlists.append(nova)
    PLAYLISTS.append(nova)
    print(f"Playlist concatenada criada: {nova.nome}")

def acao_relatorio():
    linhas = []
    linhas.append("=== RELATÓRIO DO SISTEMA ===")
    linhas.append(f"Usuários: {len(USUARIOS)} | Músicas: {len(MUSICAS)} | Podcasts: {len(PODCASTS)} | Playlists: {len(PLAYLISTS)}")

    top = Analises.top_musicas_reproduzidas(MUSICAS, 5)
    linhas.append("\nTop 5 músicas mais reproduzidas:")
    if top:
        for i, m in enumerate(top, start=1):
            linhas.append(f"{i}. {m.titulo} - {m.artista} ({m.reproducoes})")
    else:
        linhas.append("- (vazio)")

    pop = Analises.playlist_mais_popular(PLAYLISTS)
    linhas.append("\nPlaylist mais popular:")
    linhas.append("- (vazio)" if pop is None else f"- {pop.nome} ({pop.reproducoes} execuções)")

    ativo = Analises.usuario_mais_ativo(USUARIOS)
    linhas.append("\nUsuário mais ativo:")
    linhas.append("- (vazio)" if ativo is None else f"- {ativo.nome} ({len(ativo.historico)} reproduções)")

    medias = Analises.media_avaliacoes(MUSICAS)
    linhas.append("\nMédias de avaliação por música:")
    if medias:
        for t, m in medias.items():
            linhas.append(f"- {t}: {m:.2f}")
    else:
        linhas.append("- (vazio)")

    total = Analises.total_reproducoes(USUARIOS)
    linhas.append(f"\nTotal de reproduções no sistema: {total}")

    escrever_relatorio("\n".join(linhas))
    print(f"Relatório salvo em {ARQ_REL}")

# --------------------------------- Fluxo main ---------------------------------
def main():
    carregar_dados()
    menu = Menu()

    while True:
        op = menu.exibir_menu_inicial()

        if op == "1":
            nome = input("Nome do usuário: ").strip()
            u = encontrar_usuario(nome)
            if not u:
                print("Usuário não encontrado.")
                continue

            while True:
                opu = menu.exibir_menu_usuario(u.nome)

                if opu == "1":
                    acao_reproduzir(u)
                elif opu == "2":
                    if not MUSICAS: print("Nenhuma música cadastrada.")
                    else:
                        for m in MUSICAS: print(m)
                elif opu == "3":
                    if not PODCASTS: print("Nenhum podcast cadastrado.")
                    else:
                        for p in PODCASTS: print(p)
                elif opu == "4":
                    if not PLAYLISTS: print("Não há playlists.")
                    else:
                        for pl in PLAYLISTS: print(pl)
                elif opu == "5":
                    nome_pl = input("Nome da playlist: ").strip()
                    alvo = None
                    for p in u.playlists:
                        if _norm(p.nome) == _norm(nome_pl):
                            alvo = p
                            break
                    if not alvo:
                        print("Playlist não encontrada para este usuário.")
                        log_erro(f"Playlist inexistente para {u.nome}: {nome_pl}")
                    else:
                        alvo.reproduzir()
                elif opu == "6":
                    acao_criar_playlist(u)
                elif opu == "7":
                    acao_concatenar_playlists(u)
                elif opu == "8":
                    acao_relatorio()
                elif opu == "9":
                    break
                else:
                    print("Opção inválida.")

        elif op == "2":
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

        elif op == "3":
            if not USUARIOS: print("Não há usuários.")
            else:
                for u in USUARIOS: print(u)

        elif op == "4":
            print("Encerrando o sistema.")
            break

        else:
            print("Opção inválida.")

# --------------------------------- Execução -----------------------------------
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_erro(f"Erro crítico: {e}")
        print("Erro crítico. Verifique logs/erros.log.")
