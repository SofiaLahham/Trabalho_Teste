from pathlib import Path
from datetime import datetime

# Imports alinhados com a sua estrutura de pastas/arquivos
from Streaming.menu import Menu
from Streaming.usuario import Usuario
from Streaming.musica import Musica
from Streaming.podcast import Podcast
from Streaming.playlist import Playlist
from Streaming.analises import Analises


# ----------------------- utilidades de log e relatório -----------------------
LOG_PATH = Path("logs/erros.log")
REL_PATH = Path("relatorios/relatorio.txt")

def log_erro(msg: str):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

def salvar_relatorio_txt(musicas, playlists, usuarios, destino: Path = REL_PATH):
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


# ----------------------- controlador do app (regras) ------------------------
class StreamingApp:
    def __init__(self):
        self.usuarios: list[Usuario] = []
        self.musicas: list[Musica] = []
        self.podcasts: list[Podcast] = []
        self.playlists: list[Playlist] = []

    def criar_novo_usuario(self, nome: str) -> Usuario:
        u = Usuario(nome)
        self.usuarios.append(u)
        return u

    # ajuda: procurar mídia por título dentre músicas e podcasts
    def buscar_midia_por_titulo(self, titulo: str):
        for m in self.musicas:
            if m.titulo.lower() == titulo.lower():
                return m
        for p in self.podcasts:
            if p.titulo.lower() == titulo.lower():
                return p
        return None


# ----------------------- fluxo principal ------------------------------------
def main():
    menu = Menu()
    app = StreamingApp()

    # (opcional) dados de exemplo rápidos
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
                case "1":  # Reproduzir uma música
                    titulo = input("Título da música a reproduzir: ").strip()
                    midia = app.buscar_midia_por_titulo(titulo)
                    if midia:
                        usuario_logado.ouvir_midia(midia)
                    else:
                        print("Música não encontrada.")

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

                case "6":  # Criar nova playlist
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
                            pl.adicionar_midia(midia)  # passa o OBJETO, não string
                            print("Mídia adicionada.")
                        else:
                            print("Não encontrada.")

                case "7":  # Concatenar playlists
                    destino = input("Playlist 1 (destino): ").strip()
                    juntar = input("Playlist 2 (a ser juntada): ").strip()
                    p1 = next((p for p in app.playlists if p.nome.lower() == destino.lower()), None)
                    p2 = next((p for p in app.playlists if p.nome.lower() == juntar.lower()), None)
                    if p1 and p2:
                        nova = p1 + p2  # __add__ mantém nome da primeira e soma reproduções
                        # substitui p1 pela nova concatenada
                        app.playlists = [p if p is not p1 else nova for p in app.playlists]
                        print(f"Playlists concatenadas em '{nova.nome}'. Itens: {len(nova)}")
                    else:
                        print("Playlist de destino ou origem não encontrada.")

                case "8":  # Gerar relatório
                    salvar_relatorio_txt(app.musicas, app.playlists, app.usuarios)

                case "9":  # Sair do usuário logado
                    print(f"👤 Usuário '{usuario_logado.nome}' saiu da conta.")
                    usuario_logado = None

                case _:
                    print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log_erro(f"Erro crítico no main: {e}")
        print("Erro crítico. Veja logs/erros.log.")
