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
   
2. Execute o comando:
   
cd "C:\Users\Lenovo\Desktop\TG1\Trabalho_Teste"  
depois: python main.py
3. O sistema carregará automaticamente os dados da pasta config/.

4.Em caso de erros ou inconsistências, verifique o arquivo logs/erros.log.


