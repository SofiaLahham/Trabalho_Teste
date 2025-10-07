# Streaming/menu.py

class Menu:
    """Classe responsável por exibir e gerenciar os menus do sistema."""

    def __init__(self):
        """Inicializa as opções disponíveis nos menus."""
        self.opcoes_iniciais = {
            "1": "Entrar como usuário",
            "2": "Criar novo usuário",
            "3": "Listar usuários",
            "4": "Sair"
        }

        self.opcoes_usuario = {
            "1": "Reproduzir uma música",
            "2": "Listar músicas",
            "3": "Listar podcasts",
            "4": "Listar playlists",
            "5": "Reproduzir uma playlist",
            "6": "Criar nova playlist",
            "7": "Concatenar playlists",
            "8": "Gerar relatório",
            "9": "Sair"
        }

    def exibir_menu_inicial(self) -> str:
        """Mostra o menu principal e retorna a escolha do usuário (sem espaços)."""
        print("\n=== MENU INICIAL ===")
        for chave, descricao in self.opcoes_iniciais.items():
            print(f"{chave} - {descricao}")
        return input("Escolha uma opção: ").strip()

    def exibir_menu_usuario(self, nome_usuario: str) -> str:
        """Mostra o menu do usuário logado e retorna a escolha (sem espaços)."""
        print(f"\n=== MENU DO USUÁRIO: {nome_usuario} ===")
        for chave, descricao in self.opcoes_usuario.items():
            print(f"{chave} - {descricao}")
        return input("Escolha uma opção: ").strip()
