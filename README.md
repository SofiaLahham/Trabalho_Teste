# TG1 – Streaming de Música 
Trabalho da disciplina **Programação Orientada a Dados – PUCRS**

## Descrição  
Sistema de streaming musical simplificado, inspirado em plataformas como o Spotify.  
Permite cadastrar e reproduzir músicas e podcasts, criar playlists personalizadas e gerar relatórios automáticos de uso.  
A leitura inicial dos dados é feita a partir de arquivos `.md` localizados na pasta `config/`.

## Alunos e Professor  
**Alunos:** Sofia Lahham e Rafael Magalhães  
**Turma:** 11 – Programação Orientada a Dados (POD)  
**Professor:** Me. Otávio Parraga  

---

## Estrutura de Pastas do Projeto  

Abaixo está a organização principal do repositório, conforme o padrão exigido no TG1:  

<img width="297" height="716" alt="image" src="https://github.com/user-attachments/assets/0b5eaeca-eab0-48dd-b885-6d9148ad03eb" />

**Descrição:**  
- `main.py` → ponto de entrada do sistema (menu principal e carregamento de dados).  
- `Streaming/` → contém todas as classes principais (`Usuario`, `Musica`, `Podcast`, `Playlist`, `Analises`, etc.).  
- `config/` → arquivos `.md` usados para carregar os dados iniciais e exemplos de teste.  
- `logs/` → guarda os registros de erros e mensagens de inconsistência (`erros.log`).  
- `relatorios/` → relatório final gerado automaticamente (`relatorio.txt`).  

## Como Executar  

1. Abra o terminal no diretório principal do projeto.
   
2. Execute o comando: `cd "C:\Users\Lenovo\Desktop\TG1\Trabalho_Teste" ` e depois: `python main.py`
3. O sistema carregará automaticamente os dados da pasta config/.

4.Em caso de erros ou inconsistências, verifique o arquivo logs/erros.log.


## Funcionalidades Principais  

### Usuários  
- Criação e login de usuários.  
- Registro do histórico de mídias reproduzidas.  
- Associação de playlists ao usuário logado.  
- Implementado em `Streaming/usuario.py`.

### Músicas e Podcasts  
- As classes `Musica` e `Podcast` herdam de `ArquivoDeMidia`.  
- `Musica` possui sistema de **avaliações (0 a 5)** e atributo de **gênero**.  
- `Podcast` inclui **temporada**, **episódio** e **host**.  
- Métodos especiais implementados: `__str__`, `__repr__`, `__eq__`.  
- Implementados em `Streaming/musica.py` e `Streaming/podcast.py`.

### Playlists  
- Criação e exclusão de playlists personalizadas.  
- Adição e remoção de mídias.  
- Reprodução automática (toca todas as mídias contidas).  
- Concatenação de duas playlists com o operador `+`.  
- Implementado em `Streaming/playlist.py`.

### Análises e Relatórios  
- **Top músicas reproduzidas**  
- **Playlist mais popular**  
- **Usuário mais ativo**  
- **Média de avaliações**  
- **Total de reproduções no sistema**  
- Relatório gerado automaticamente em `relatorios/relatorio.txt`.  
- Implementado em `Streaming/analises.py`.

### Leitura de Arquivos `.md`  
- Leitura automática dos dados da pasta `config/` (`dados.md`, `ExemploDeEntrada1`, `ExemploDeEntrada2`).  
- Em caso de erro (duração inválida, episódio não numérico, duplicidades etc.), o sistema **não é interrompido** — o problema é registrado em `logs/erros.log`.  
- Implementado diretamente no `main.py`.

## Prints e Demonstrações  

### Menu Inicial  

<img width="203" height="133" alt="image" src="https://github.com/user-attachments/assets/9a70f133-a3f8-4141-a673-828725216764" />

O sistema inicia exibindo o menu principal com as opções:  
1) Entrar como usuário  
2) Criar novo usuário  
3) Listar usuários  
4) Sair

### Menu do Usuário  

O **Menu do Usuário** exibe todas as funcionalidades disponíveis após o login.  
Cada opção representa uma operação controlada pela classe `Menu`, localizada no pacote `Streaming/`.

<img width="294" height="212" alt="image" src="https://github.com/user-attachments/assets/3f5f7d72-12a1-4488-b73e-aa47d18ebcd9" />

Após o login, o menu exibe as principais ações disponíveis:  
1. Reproduzir uma mídia  
2. Listar músicas  
3. Listar podcasts  
4. Listar playlists  
5. Reproduzir uma playlist  
6. Criar nova playlist  
7. Concatenar playlists  
8. Gerar relatório  
9. Sair  

## Relatório Gerado  

<img width="677" height="388" alt="image" src="https://github.com/user-attachments/assets/6385ff3f-ae5d-4541-bf81-6076d6e7344b" />


O relatório mostra estatísticas atualizadas de uso, como:  
- Total de usuários, músicas e podcasts.  
- Top 5 músicas mais reproduzidas.  
- Playlist mais popular.  
- Usuário mais ativo.  
- Média de avaliações.  

## Inovação  

A inovação desenvolvida neste projeto foi a **criação interativa de playlists pelo próprio usuário**, diretamente no menu do sistema.

Durante a execução do programa, o usuário pode criar uma nova playlist personalizada e inserir músicas manualmente, informando:  
- Nome da música  
- Duração em segundos  
- Artista  
- Gênero musical  

O sistema valida as informações inseridas (por exemplo, impede duração menor ou igual a zero) e adiciona automaticamente a nova música à playlist criada.

Essa funcionalidade torna o sistema mais dinâmico, permitindo que novas músicas e playlists sejam criadas **sem necessidade de editar os arquivos de configuração**.

**Exemplo de uso da inovação:**

<img width="541" height="677" alt="image" src="https://github.com/user-attachments/assets/073bdc6b-ccd2-43c5-9a49-75a18b8be259" />
