# Streaming/menu.py

class Menu:
    """
    Classe responsável por exibir e gerenciar os menus do sistema de streaming.
    Contém o menu inicial e o menu do usuário.
    """

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

    def exibir_menu_inicial(self):
        """Mostra o menu principal e retorna a escolha do usuário."""
        print("\n=== MENU INICIAL ===")
        for chave, descricao in self.opcoes_iniciais.items(): # chave = número da opção / descricao = texto exibido na tela
            print(f"{chave} - {descricao}")
        return input("Escolha uma opção: ")

    def exibir_menu_usuario(self, nome_usuario: str):
        print(f"\n=== MENU DO USUÁRIO: {nome_usuario} ===")
        # chave = número da opção / descricao = texto exibido na tela
        for chave, descricao in self.opcoes_usuario.items():
            print(f"{chave} - {descricao}")
        return input("Escolha uma opção: ")

    def __str__(self):
        """Retorna uma descrição simples da classe."""
        return "Classe responsável pelos menus do sistema de streaming."
