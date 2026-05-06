# 📚 Biblioteca - Manual do Usuário

## Índice
1. [Primeiro Acesso](#1-primeiro-acesso)
2. [Tela Principal (Dashboard)](#2-tela-principal-dashboard)
3. [Cadastro de Livros](#3-cadastro-de-livros)
4. [Cadastro de Alunos](#4-cadastro-de-alunos)
5. [Empréstimos e Devoluções](#5-empréstimos-e-devoluções)
6. [Relatórios](#6-relatórios)
7. [Configurações da Instituição](#7-configurações-da-instituição)
8. [Usuários e Permissões](#8-usuários-e-permissões)
9. [Backup e Restauração](#9-backup-e-restauração)
10. [Perguntas Frequentes](#10-perguntas-frequentes)

---

## 1. Primeiro Acesso

### 1.1 Abrindo o Sistema
- Dê **duplo clique** no arquivo `Biblioteca.exe`
- Aguarde alguns segundos — o navegador abrirá automaticamente
- Se o navegador não abrir, acesse: `http://127.0.0.1:5477`

### 1.2 Ativação da Licença
Na tela de login:
1. Clique em **"Licença do Sistema"**
2. Copie o **ID da Máquina** exibido
3. Envie esse ID ao responsável pelo sistema
4. Quando receber a chave de ativação, cole no campo e clique em **"Ativar"**

### 1.3 Login Inicial
- **Usuário:** `admin@biblioteca.local`
- **Senha:** `admin123`
- ⚠️ **Troque a senha imediatamente após o primeiro acesso!**

### 1.4 Configuração Inicial
Após o login, vá em **Instituição** e configure:
- Nome da escola/biblioteca
- CNPJ, endereço, telefone, e-mail
- Prazo padrão de empréstimo (7, 14, 21 ou 30 dias)
- Logo (opcional)

---

## 2. Tela Principal (Dashboard)

O Dashboard exibe um resumo do sistema:
- **Total de Livros:** Quantidade de itens no acervo
- **Total de Alunos:** Alunos cadastrados
- **Empréstimos Ativos:** Livros emprestados no momento
- **Empréstimos Atrasados:** Livros não devolvidos no prazo
- **Empréstimos Recentes:** Lista das últimas movimentações

---

## 3. Cadastro de Livros

### 3.1 Cadastrar Livro Individual
1. Vá em **Livros** na barra lateral
2. Clique em **"Novo Livro"**
3. Preencha:
   - **Patrimônio:** Número de identificação (obrigatório e único)
   - **Título:** Nome do livro (obrigatório)
   - **Autor, ISBN, Categoria, Editora, Ano** (opcionais)
4. Clique em **"Salvar"**

### 3.2 Importação em Massa (CSV)
1. Clique em **"Importar CSV"**
2. Selecione ou arraste o arquivo CSV
3. O arquivo deve ter as colunas: `patrimonio`, `titulo`, `autor`, `isbn`, `categoria`, `editora`, `ano`
4. Clique em **"Importar"**
5. O sistema exibirá o resultado: quantos foram importados e quantos foram ignorados (patrimônio duplicado ou campos obrigatórios vazios)

💡 **Dica:** Para baixar o modelo de CSV, clique em **"Baixar Modelo CSV"** na tela de importação.

### 3.3 Buscar Livros
Use o campo de busca para pesquisar por:
- Número de patrimônio
- Título
- Autor

### 3.4 Etiquetas de Patrimônio
1. Clique no ícone de **código de barras** ao lado do livro
2. Imprima ou salve a etiqueta para colar no livro físico

### 3.5 Editar/Remover Livros
- **Editar:** Clique no ícone de lápis ✏️
- **Remover:** Clique no ícone de lixeira 🗑️ (apenas admin, e se o livro não tiver empréstimos ativos)

---

## 4. Cadastro de Alunos

### 4.1 Cadastrar Aluno Individual
1. Vá em **Alunos** na barra lateral
2. Clique em **"Novo Aluno"**
3. Preencha:
   - **Matrícula:** Número de identificação (obrigatório e único)
   - **Nome:** Nome completo do aluno (obrigatório)
   - **Turma, Telefone, E-mail, Observações** (opcionais)
4. Clique em **"Salvar"**

### 4.2 Importação em Massa (CSV)
1. Clique em **"Importar CSV"**
2. O arquivo deve ter: `matricula`, `nome`, `turma`, `telefone`, `email`
3. Clique em **"Importar"**

### 4.3 Buscar Alunos
Pesquise por nome, matrícula ou turma.

### 4.4 Ver Empréstimos do Aluno
Ao lado de cada aluno, o sistema mostra:
- Se possui empréstimo ativo
- Se há atraso (exibido em vermelho)

---

## 5. Empréstimos e Devoluções

### 5.1 Novo Empréstimo
1. Vá em **Empréstimos** na barra lateral
2. Clique em **"Novo Empréstimo"**
3. **Selecionar Livro:** Digite o número de patrimônio ou selecione na lista
4. **Selecionar Aluno:** Digite o nome ou matrícula
5. **Prazo de Devolução:**
   - Escolha entre 7, 14, 21 ou 30 dias
   - Ou clique em **"Data personalizada"** para escolher uma data específica
6. Clique em **"Registrar Empréstimo"**

### 5.2 Devolução
**Método 1 — Por Empréstimo:**
1. Na lista de empréstimos ativos, clique em **"Devolver"** no empréstimo desejado

**Método 2 — Por Patrimônio (ideal para leitor de código de barras):**
1. Clique em **"Devolução por Patrimônio"**
2. Escaneie ou digite o número de patrimônio
3. A devolução é registrada automaticamente

### 5.3 Visualizar Atrasados
- Use o filtro **"Atrasados"** para ver todos os livros fora do prazo
- O sistema mostra quantos dias de atraso cada empréstimo possui

---

## 6. Relatórios

Vá em **Relatórios** para acessar:

| Relatório | Descrição |
|-----------|-----------|
| **Empréstimos Ativos** | Todos os livros emprestados no momento |
| **Empréstimos Atrasados** | Livros não devolvidos no prazo |
| **Histórico de Aluno** | Todos os empréstimos de um aluno em um período |
| **Movimentação** | Empréstimos e devoluções em um período |
| **Inventário** | Lista completa do acervo (por categoria/status) |
| **Mais Emprestados** | Top 20 livros com mais empréstimos |
| **Ranking de Alunos** | Alunos com mais livros lidos no período |
| **Ranking de Turmas** | Turmas com maior volume de leitura |

**Todos os relatórios podem ser impressos** clicando no botão **"Imprimir"**.

---

## 7. Configurações da Instituição

Vá em **Instituição** para:
- Alterar nome, CNPJ, endereço, telefone e e-mail
- Definir o prazo padrão de empréstimo
- Fazer upload da logo da instituição (aparece nos relatórios impressos)

---

## 8. Usuários e Permissões

### 8.1 Tipos de Usuário
- **Admin:** Acesso total ao sistema
- **Operador:** Acesso limitado conforme permissões definidas pelo admin

### 8.2 Gerenciar Usuários
1. Vá em **Usuários** na barra lateral
2. **Novo Usuário:** Preencha nome, e-mail, senha e perfil
3. **Editar:** Clique no lápis ✏️
4. **Remover:** Clique na lixeira 🗑️ (apenas admin)
5. **Trocar Senha:** Cada usuário pode trocar sua própria senha

### 8.3 Permissões do Operador
O admin pode habilitar/desabilitar individualmente:
- Cadastrar/Editar/Excluir livros
- Cadastrar/Editar/Excluir alunos
- Criar empréstimos/Devolver livros
- Ver relatórios/Imprimir códigos
- Gerenciar categorias/Fazer backup
- Ver log de atividades

---

## 9. Backup e Restauração

### 9.1 Backup
1. Vá em **Backup** na barra lateral
2. Clique em **"Baixar Backup"**
3. Um arquivo `.db` será baixado — guarde-o em local seguro

### 9.2 Restauração
1. Clique em **"Restaurar Backup"**
2. Selecione o arquivo `.db` de backup
3. Confirme a restauração (um backup automático é feito antes)

### 9.3 Histórico de Backups
O sistema mantém cópias automáticas na pasta `backups/` na mesma pasta do executável.

---

## 10. Perguntas Frequentes

### O sistema precisa de internet?
**Não.** O sistema funciona 100% offline. O banco de dados é local (SQLite). A única exceção é a tela de login, que abre no navegador, mas tudo roda na sua máquina (`127.0.0.1`).

### Posso usar em vários computadores ao mesmo tempo?
**Não.** O sistema é projetado para uso em uma única máquina. O banco de dados é local e não há sincronização entre computadores.

### O que acontece se eu apagar o banco de dados?
Todos os dados serão perdidos. Na próxima execução, o sistema criará um banco vazio com apenas o usuário admin padrão. Por isso, faça backups regulares.

### Como trocar a senha?
Vá em **Usuários**, clique no seu usuário e selecione **"Trocar Senha"**.

### A licença expira. O que acontece?
Quando a licença expira, o sistema impede o login. Entre em contato com o responsável para gerar uma nova chave de ativação.

### Posso usar leitor de código de barras?
**Sim!** O campo de patrimônio aceita entrada direta de leitor de código de barras. Na devolução por patrimônio, basta escanear o código.

### O sistema funciona no Linux?
Sim. O processo é o mesmo: execute o binário e acesse pelo navegador.

### Onde ficam salvos os dados?
Em `instance/biblioteca.db`, na mesma pasta do executável.

### Como parar o sistema?
- **Windows:** Feche o navegador e use o ícone na barra de tarefas para fechar, ou execute `server.bat stop`
- **Linux:** Execute `./server.ps1 stop` ou mate o processo com `Ctrl+C` no terminal

---

**Versão do Manual:** 1.0  
**Última atualização:** 06/05/2026
