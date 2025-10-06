# main.py
from pathlib import Path
from datetime import datetime
from Streaming.menu import Menu
from Streaming.usuario import Usuario
from Streaming.musica import Musica
from Streaming.podcast import Podcast
from Streaming.playlist import Playlist
from Streaming.analises import Analises
from Streaming.arquivo_de_midia import ArquivoDeMidia

# ------------------------------ Coleções globais ------------------------------
USUARIOS: list[Usuario] = []
MUSICAS: list[Musica] = []
PODCASTS: list[Podcast] = []
PLAYLISTS: list[Playlist] = []

# Caminhos padrão
ARQ_DADOS = Path("config/dados.md")
ARQ_LOG = Path("logs/erros.log")
ARQ_REL = Path("relatorios/relatorio.txt")

# ------------------------------ Funções úteis ---------------------------------
def log_erro(msg: str) -> None:
    """Registra erros no arquivo de log com data e hora."""
    ARQ_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ARQ_LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def escrever_relatorio(texto: str) -> None:
    """Grava o relatório final de análises."""
    ARQ_REL.parent.mkdir(parents=True, exist_ok=True)
    ARQ_REL.write_text(texto, encoding="utf-8")

def encontrar_usuario(nome: str) -> Usuario | None:
    """Procura um usuário pelo nome (ignora maiúsculas/minúsculas)."""
    for u in USUARIOS:
        if u.nome.lower() == nome.strip().lower():
            return u
    return None

def carregar_dados():
    """Lê config/dados.md e preenche listas de usuários, músicas e podcasts."""
    if not ARQ_DADOS.exists():
        log_erro("Arquivo de dados não encontrado.")
        return
    sec = None
    for linha in ARQ_DADOS.read_text(encoding="utf-8").splitlines():
        li = linha.strip()
        if not li or li.startswith("# Aqui"): continue
        if li.startswith("#"):
            titulo = li.lstrip("#").strip().upper()
            if "MUSICA" in titulo: sec = "M"
            elif "PODCAST" in titulo: sec = "P"
            elif "USUARIO" in titulo: sec = "U"
            else: sec = None
            continue
        try:
            if sec == "M":
                t, d, a, g = [x.strip() for x in li.lstrip("-").split("|")]
                MUSICAS.append(Musica(t, int(d), a, g))
            elif sec == "P":
                t, d, a, temp, epi, h = [x.strip() for x in li.lstrip("-").split("|")]
                PODCASTS.append(Podcast(t, int(d), a, temp, int(epi), h))
            elif sec == "U":
                nome = li.lstrip("-").strip()
                if not encontrar_usuario(nome):
                    USUARIOS.append(Usuario(nome))
        except Exception as e:
            log_erro(f"Erro ao processar linha: {linha} ({e})")

# ----------------------------- Funções auxiliares -----------------------------
def acao_reproduzir(usuario: Usuario):
    titulo = input("Título da mídia: ").strip()
    midia = ArquivoDeMidia.buscar_por_titulo(titulo)
    if midia:
        usuario.ouvir_midia(midia)
    else:
        print("Mídia não encontrada.")
        log_erro(f"Tentativa de reprodução inválida: {titulo}")

def acao_criar_playlist(usuario: Usuario):
    nome = input("Nome da nova playlist: ").strip()
    try:
        pl = usuario.criar_playlist(nome)
        PLAYLISTS.append(pl)
        print(f"Playlist '{pl.nome}' criada.")
    except ValueError as e:
        log_erro(str(e))
        print(e)

def acao_relatorio():
    """Gera e salva relatório com análises do sistema."""
    texto = []
    texto.append("=== RELATÓRIO DO SISTEMA ===")
    texto.append(f"Usuários: {len(USUARIOS)} | Músicas: {len(MUSICAS)} | Podcasts: {len(PODCASTS)}")
    top = Analises.top_musicas_reproduzidas(MUSICAS, 5)
    texto.append("\nTop 5 músicas mais reproduzidas:")
    texto += [f"- {m.titulo} ({m.reproducoes} plays)" for m in top] or ["- Nenhuma"]
    escrever_relatorio("\n".join(texto))
    print("Relatório salvo em relatorios/relatorio.txt")

# ------------------------------ Função principal ------------------------------
def main():
    """Ponto de entrada principal do sistema."""
    carregar_dados()
    menu = Menu()
    while True:
        op = menu.exibir_menu_inicial()
        if op == "1":  # Entrar como usuário
            nome = input("Nome do usuário: ").strip()
            u = encontrar_usuario(nome)
            if not u:
                print("Usuário não encontrado.")
                continue
            while True:
                opu = menu.exibir_menu_usuario(u.nome)
                if opu == "1": acao_reproduzir(u)
                elif opu == "2": [print(m) for m in MUSICAS]
                elif opu == "3": [print(p) for p in PODCASTS]
                elif opu == "4": [print(p) for p in PLAYLISTS]
                elif opu == "5": acao_criar_playlist(u)
                elif opu == "6": acao_relatorio()
                elif opu == "7": break
                else: print("Opção inválida.")
        elif op == "2":  # Criar novo usuário
            nome = input("Nome: ").strip()
            if encontrar_usuario(nome):
                print("Usuário já existe.")
                log_erro(f"Duplicado: {nome}")
            else:
                USUARIOS.append(Usuario(nome))
                print("Usuário criado.")
        elif op == "3": [print(u) for u in USUARIOS]
        elif op == "4": break
        else: print("Opção inválida.")

# -------------------------------- Execução ------------------------------------
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_erro(f"Erro crítico: {e}")
        print("Erro crítico. Verifique logs/erros.log.")
