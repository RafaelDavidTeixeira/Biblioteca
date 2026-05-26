# 📚 Biblioteca - Sistema de Controle de Acervo
## Documentação Completa

---

## Indice
1. [Visão Geral](#1-visão-geral)
2. [Estrutura de Arquivos](#2-estrutura-de-arquivos)
3. [Arquivos Python - Propósito](#3-arquivos-python---propósito)
4. [Banco de Dados](#4-banco-de-dados)
5. [Sistema de Licenciamento](#5-sistema-de-licenciamento)
6. [Criação de Executáveis](#6-criação-de-executáveis)
7. [Funcionalidades](#7-funcionalidades)
8. [Documentação dos Scripts Python](#8-documentação-dos-scripts-python)
9. [Instalação e Uso](#9-instalação-e-uso)
10. [Resolução de Problemas](#10-resolução-de-problemas)

---

## 1. Visão Geral

O **Biblioteca** é um sistema desktop para controle de empréstimos de biblioteca escolar, desenvolvido em **Python/Flask**. O sistema roda no browser local, sem necessidade de instalação no cliente (quando distribuído como executável). Suporta **Windows** e **Linux**.

### Características Principais:
- Interface web moderna e responsiva (SPA - Single Page Application)
- Banco de dados SQLite local (sem servidor externo)
- Licenciamento por hardware (machine-locked)
- Sistema multi-usuário (admin/operador)
- Importação em massa via CSV
- Relatórios gerenciais
- Build para executáveis independentes

### Tecnologias Utilizadas:
- **Backend:** Python 3.10+, Flask, SQLite
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Build:** PyInstaller
- **Licenciamento:** HMAC-SHA256 + Machine Fingerprint

---

## 2. Estrutura de Arquivos

```
biblioteca/
├── run.py                      ← Ponto de entrada principal
├── app/
│   ├── __init__.py             ← Fábrica da aplicação Flask
│   ├── database.py             ← Camada de banco de dados (SQLite puro)
│   ├── license.py              ← Sistema de licenciamento
│   ├── config_manager.py       ← Gerenciamento de config local
│   ├── services.py             ← Servicos compartilhados (email, etc)
│   ├── version.py              ← Versão atual do sistema
│   ├── version_control.py      ← Controle de versão do banco
│   ├── routes/
│   │   ├── __init__.py         ← (vazio, torna um pacote)
│   │   ├── auth.py             ← Login, logout, ativação de licença
│   │   ├── books.py            ← CRUD livros + importação CSV + códigos
│   │   ├── students.py         ← CRUD alunos + importação CSV
│   │   ├── loans.py            ← Empréstimos, devoluções, renovações e reservas
│   │   ├── reports.py          ← Relatórios com filtros
│   │   ├── settings.py         ← Instituição, usuários, backup, permissões
│   │   └── api.py              ← Busca global, log de atividade
│   ├── templates/
│   │   ├── login.html          ← Tela de login + ativação de licença
│   │   └── app.html            ← SPA principal (~789 linhas)
│   └── static/
│       ├── js/app.js           ← Lógica do frontend
│       ├── css/app.css         ← Estilos do sistema
│       ├── chart.min.js        ← Chart.js v4.4.7 (local, sem CDN)
│       └── img/
│           └── favicon.svg     ← Ícone do sistema
├── backups/                    ← Backups locais (mantidos 3 recentes)
├── release/                    ← Executaveis organizados por SO
│   ├── windows/                ← Biblioteca.exe
│   ├── linux/                  ← AppImage + icone + atalho
│   └── ferramentas/            ← GeradorLicenca, rclone, etc
├── _dev/                       ← Scripts de build, dev e utilitários
│   ├── GeradorLicenca.spec     ← Config PyInstaller do gerador
│   ├── gerar_chave_cli.spec    ← Config PyInstaller do CLI
│   ├── app_licenca.py          ← Código-fonte do gerador GUI
│   ├── gerar_chave_cli.py      ← Código-fonte do gerador CLI
│   ├── old_backups/            ← Backups antigos
│   ├── instance_dev/           ← Banco e logos de desenvolvimento
│   ├── requirements.txt        ← Dependências Python
│   └── ...                     ← Scripts utilitários
├── DOCUMENTACAO.md              ← Documentação técnica completa
├── MANUAL_USUARIO.md            ← Manual do usuário
└── README.md                    ← Visão geral rápida
```

---

## 3. Arquivos Python - Propósito

### 3.1 Core do Sistema

| Arquivo | Linhas | Propósito |
|---------|--------|-----------|
| `run.py` | ~50 | Ponto de entrada, inicializa servidor Flask |
| `app/__init__.py` | ~40 | Fábrica Flask, configuração inicial |
| `app/database.py` | ~613 | Camada de banco de dados SQLite |
| `app/license.py` | ~79 | Sistema de licenciamento |

### 3.2 Rotas da Aplicação (Blueprints)

| Arquivo | Linhas | Propósito |
|---------|--------|-----------|
| `app/routes/auth.py` | ~222 | Autenticação e licenciamento |
| `app/routes/books.py` | ~188 | Gestão de livros |
| `app/routes/students.py` | ~123 | Gestão de alunos |
| `app/routes/loans.py` | ~301 | Empréstimos, devoluções, renovações e reservas |
| `app/routes/reports.py` | ~63 | Relatórios |
| `app/routes/settings.py` | ~516 | Configurações, categorias, usuários |
| `app/routes/api.py` | ~23 | API geral e busca |

### 3.3 Scripts Utilitários

| Arquivo | Propósito |
|---------|-----------|
| `app_licenca.py` | Código-fonte do GeradorLicenca.exe (GUI Tkinter) |
| `gerar_chave_cli.py` | Código-fonte do gerador de chaves CLI |
| `identificar_ignorados.py` | Analisa itens rejeitados na importação CSV |
| `analisar_rejeitados.py` | Analisa rejeitados (versão alternativa) |
| `analisar_csv.py` | Análise completa de CSV antes de importar |
| `validar_csv.py` | Validação de arquivos CSV |
| `fix_import.py` | Corrige problemas de importação |
| `check_db.py` | Verifica estado do banco de dados |
| `check_import_log.py` | Verifica logs de importação |
| `check_books.py` | Verifica livros no banco |
| `verificar_log.py` | Verifica logs de atividade |
| `limpar_dados_teste.py` | Limpeza de dados de teste |

---

## 4. Banco de Dados

O sistema utiliza **SQLite** puro (sem SQLAlchemy). O arquivo fica em `instance/biblioteca.db`.

### 4.1 Tabelas e Campos

#### **institution** - Dados da Instituição
| Campo | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| id | INTEGER PK | | ID único |
| name | TEXT | 'Minha Escola' | Nome da instituição |
| cnpj | TEXT | '' | CNPJ |
| address | TEXT | '' | Endereço |
| phone | TEXT | '' | Telefone |
| email | TEXT | '' | E-mail |
| loan_days_default | INTEGER | 14 | Prazo padrão de empréstimo |
| logo_path | TEXT | '' | Caminho do logo |
| updated_at | TEXT | | Data de atualização |

#### **users** - Usuários do Sistema
| Campo | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| id | INTEGER PK AUTOINCREMENT | | ID único |
| name | TEXT | | Nome |
| email | TEXT UNIQUE | | E-mail (login) |
| password_hash | TEXT | | Hash da senha |
| role | TEXT | 'operator' | Perfil: admin/operator |
| active | INTEGER | 1 | Ativo (1) ou inativo (0) |
| created_at | TEXT | | Data de criação |
| last_login | TEXT | | Último login |

**Usuário padrão:** `admin@biblioteca.local` / `admin123`

#### **books** - Acervo/Livros
| Campo | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| id | INTEGER PK AUTOINCREMENT | | ID único |
| patrimony | TEXT UNIQUE | | Número de patrimônio (obrigatório) |
| title | TEXT | | Título (obrigatório) |
| author | TEXT | '' | Autor |
| isbn | TEXT | '' | ISBN |
| category | TEXT | '' | Categoria |
| publisher | TEXT | '' | Editora |
| year | INTEGER | | Ano de publicação |
| notes | TEXT | '' | Observações |
| active | INTEGER | 1 | Ativo (1) ou inativo (0) |
| created_at | TEXT | | Data de cadastro |

#### **students** - Alunos
| Campo | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| id | INTEGER PK AUTOINCREMENT | | ID único |
| name | TEXT | | Nome (obrigatório) |
| enrollment | TEXT UNIQUE | | Matrícula (obrigatório) |
| class_name | TEXT | '' | Turma |
| phone | TEXT | '' | Telefone |
| email | TEXT | '' | E-mail |
| notes | TEXT | '' | Observações |
| active | INTEGER | 1 | Ativo (1) ou inativo (0) |
| created_at | TEXT | | Data de cadastro |

#### **loans** - Empréstimos
| Campo | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| id | INTEGER PK AUTOINCREMENT | | ID único |
| book_id | INTEGER FK | | Livro (FK books.id) |
| student_id | INTEGER FK | | Aluno (FK students.id) |
| user_id | INTEGER FK | | Operador (FK users.id) |
| borrowed_at | TEXT | | Data do empréstimo |
| due_date | TEXT | | Data de vencimento |
| returned | INTEGER | 0 | Devolvido (1) ou não (0) |
| returned_at | TEXT | | Data da devolução |
| renewed | INTEGER | 0 | Quantidade de renovações |
| renewed_at | TEXT | | Data da última renovação |
| notes | TEXT | '' | Observações |

#### **reservations** - Reservas
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER PK AUTOINCREMENT | ID único |
| book_id | INTEGER FK | Livro (FK books.id) |
| student_id | INTEGER FK | Aluno (FK students.id) |
| user_id | INTEGER FK | Operador que criou (FK users.id) |
| status | TEXT | 'active' ou 'fulfilled' ou 'cancelled' |
| reserved_at | TEXT | Data da reserva |
| fulfilled_at | TEXT | Data de atendimento (quando livro é emprestado) |

#### **activity_log** - Log de Atividades
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER PK AUTOINCREMENT | ID único |
| type | TEXT | Tipo: login, register_book, update_book, delete_book, register_student, update_student, delete_student, borrow, return, import_books, import_students, backup, cleanup, update_institution, update_permissions, create_user, create_category |
| description | TEXT | Descrição da ação |
| user_id | INTEGER FK | Usuário (FK users.id) |
| created_at | TEXT | Data/hora da ação |

#### **license_info** - Licenciamento
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | INTEGER PK | (sempre 1) |
| machine_id | TEXT | ID da máquina |
| license_key | TEXT | Chave de licença |
| institution_name | TEXT | Nome da instituição licenciada |
| valid_until | TEXT | Data de expiração (ISO format) |
| activated_at | TEXT | Data de ativação |
| is_valid | INTEGER | Válida (1) ou inválida (0) |

#### **categories** - Categorias de Livros
| Campo | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| id | INTEGER PK AUTOINCREMENT | | ID único |
| name | TEXT UNIQUE | | Nome da categoria |
| loan_days_default | INTEGER | 14 | Prazo padrão de empréstimo para esta categoria |
| active | INTEGER | 1 | Ativa (1) ou inativa (0) |

**Categorias padrão:** 56 categorias semeadas automaticamente na primeira execução (abrangendo todas as áreas do conhecimento e gêneros literários).

#### **operator_permissions** - Permissões de Operador
| Campo | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| id | INTEGER PK CHECK (id=1) | 1 | (sempre 1) |
| can_create_books | INTEGER | 1 | Pode cadastrar livros |
| can_edit_books | INTEGER | 1 | Pode editar livros |
| can_delete_books | INTEGER | 0 | Pode excluir livros |
| can_create_students | INTEGER | 1 | Pode cadastrar alunos |
| can_edit_students | INTEGER | 1 | Pode editar alunos |
| can_delete_students | INTEGER | 0 | Pode excluir alunos |
| can_create_loans | INTEGER | 1 | Pode criar empréstimos |
| can_return_books | INTEGER | 1 | Pode registrar devoluções |
| can_renew_loans | INTEGER | 1 | Pode renovar empréstimos |
| can_manage_reservations | INTEGER | 1 | Pode gerenciar reservas |
| can_view_reports | INTEGER | 1 | Pode ver relatórios |
| can_print_barcodes | INTEGER | 1 | Pode imprimir códigos |
| can_manage_categories | INTEGER | 0 | Pode gerenciar categorias |
| can_backup | INTEGER | 0 | Pode fazer backup |
| can_view_activity | INTEGER | 1 | Pode ver log de atividades |
| updated_at | TEXT | | Data de atualização |

---

## 5. Sistema de Licenciamento

### 5.1 Visão Geral
O sistema utiliza licenciamento **machine-locked** (vinculado ao hardware) com as seguintes características:

- **Offline:** Não requer servidor externo para validação
- **Seguro:** Assinado com HMAC-SHA256
- **Vinculado:** Funciona apenas no computador onde foi ativado
- **Flexível:** Validade configurável (1, 2, 3 anos ou personalizado)

### 5.2 Fluxo de Licenciamento

1. **Cliente instala e executa o sistema**
   - O ID da máquina é gerado automaticamente
   - Aparece na tela de login: `ID da Máquina: XXXX-XXXX-XXXX-XXXX`

2. **Cliente informa o ID ao desenvolvedor**

3. **Desenvolvedor gera a licença:**
   ```bash
   python _dev/gerar_licenca.py
   ```

4. **Desenvolvedor envia a chave ao cliente**

5. **Cliente ativa o sistema:**
   - Na tela de login, clica em "Licença do Sistema"
   - Cola a chave no campo e clica "Ativar"
   - Sistema valida e ativa

### 5.3 Geração da Machine ID (`app/license.py`)
Baseada em 4 componentes do hardware/SO:
```python
raw = '|'.join([
    hex(uuid.getnode()),      # MAC address
    platform.node(),          # Hostname
    platform.system(),        # SO (Windows/Linux)
    platform.machine()        # Arquitetura
])
# Hash SHA-256, pega 16 chars, formata: XXXX-XXXX-XXXX-XXXX
```

### 5.4 Geração da Chave de Licença (`app/license.py`)
```
Componentes (12 bytes totais):
- machine_id hash: 4 bytes (SHA-256 truncado)
- expiration: 4 bytes (data em ordinal, big-endian)
- HMAC-SHA256 signature: 4 bytes (truncado)

Codificação: Base32 → 4 grupos de 5 caracteres
Formato: XXXXX-XXXXX-XXXXX-XXXXX
```

### 5.5 Validação (no cliente)
1. Decodifica Base32
2. Extrai: payload (8 bytes) + assinatura (4 bytes)
3. Verifica HMAC-SHA256 (com `LICENSE_SECRET`)
4. Verifica se machine_id corresponde à máquina atual
5. Verifica se não está expirada

### 5.6 Chave Secreta
Em `app/license.py`:
```python
LICENSE_SECRET = b'biblio-lic-hmac-secret-key-2025'

**Atencao:** Se alterar apos ja ter gerado licencas, todas as licencas anteriores pararao de funcionar.

---

## 6. Criação de Executáveis

### 6.1 Pré-requisitos para Build
- Python 3.10+ instalado
- Pip funcionando
- PyInstaller: `pip install pyinstaller`

### 6.2 Windows (.exe)

```bash
pyinstaller Biblioteca.spec --clean
```

Gera `dist/Biblioteca.exe` -> copiar para `release/windows/Biblioteca.exe`.

### 6.3 Linux (AppImage + raw binary + .sh wrapper)

Build automatizado com Python 3.12 standalone (compativel glibc 2.17+):

```bash
_dev/build_all.sh
```

Gera 3 artefatos em `release/linux/`:
- `Biblioteca-<versao>-x86_64.AppImage` — auto-contido (FUSE)
- `Biblioteca-<versao>-x86_64.AppImage.raw` — binario raw (sem FUSE)
- `biblioteca.sh` — wrapper que extrai e executa o .raw

### 6.4 O que o Cliente Recebe

O cliente recebe **apenas o executavel** da sua plataforma. Nao e necessario enviar pastas adicionais, pois:
- Templates e estaticos sao embutidos no executavel pelo PyInstaller (`--onefile`)
- Na primeira execucao, o sistema cria automaticamente:
  - **Windows:** `%APPDATA%/Biblioteca/instance/` e `%APPDATA%/Biblioteca/backups/`
  - **Linux:** `~/.local/share/Biblioteca/instance/` e `~/.local/share/Biblioteca/backups/`

### 6.5 Distribuicao com Banco Vazio

Para uma **nova instalacao limpa** (sem dados de teste):
1. Gere o executavel (`pyinstaller Biblioteca.spec` no Windows, `_dev/build_all.sh` no Linux)
2. Envie **apenas o executavel** para o cliente
3. **Nao envie** o arquivo `biblioteca.db`

Quando o cliente executar pela primeira vez, a funcao `init_db()` detecta que o banco nao existe e:
- Cria a pasta `instance/`
- Cria o arquivo `biblioteca.db` com todas as tabelas vazias
- Insere apenas o usuario admin padrao (`admin@biblioteca.local` / `admin123`)
- Insere as categorias padrao (Romance, Ficcao, etc.)

**Importante:** Se voce ja tem um `biblioteca.db` na pasta de desenvolvimento, ele é usado para testes locais. O executável gerado **não carrega** esse banco junto. Ele sempre cria um novo se não encontrar um `instance/biblioteca.db` no caminho.

Para **testar como se fosse uma instalação nova**, basta apagar a pasta `instance/` antes de rodar `python run.py`.

---

## 7. Funcionalidades

### 7.1 Dashboard
- Estatisticas em tempo real (total livros, alunos, emprestimos, atrasos)
- Emprestimos recentes
- Alertas de atraso
- Modal "Sobre" com info da versao e dados do sistema

### 7.2 Graficos (Chart.js)
- Pagina dedicada com graficos interativos (ampliados para melhor visualizacao)
- **Emprestimos/dia:** ultimos 30 dias
- **Livros por categoria:** top 8
- **Livros mais emprestados:** top 10
- **Emprestimos por turma:** top 10
- Chart.js v4.4.7 servido localmente (sem CDN)

### 7.3 Livros
- Cadastro com patrimonio (obrigatorio), titulo, autor, ISBN, categoria, editora, ano
- Busca por patrimonio/titulo/autor
- Importacao em massa via CSV (admin apenas)
- Geracao de codigo de barras (Code128) para etiquetas
- Pagina de etiquetas com **busca** e **ordenacao** por patrimonio, titulo ou autor
- Auto-incremento de patrimonio ao cadastrar
- Status de disponibilidade em tempo real
- Edicao (inclui alteracao de patrimonio) e exclusao (se sem emprestimos ativos)

### 7.4 Alunos
- Cadastro com matricula (obrigatorio), nome, turma, telefone, e-mail
- Busca por nome/matricula/turma
- Importacao em massa via CSV (admin apenas)
- Visualizacao de emprestimos ativos e status de atraso
- Ativar/Desativar aluno (filtro: ativos/inativos/todos)
- Bloqueio de desativacao se possuir emprestimos ativos
- Status visual: "Regular" (verde), "Pendencia" (vermelho), "Inativo" (cinza)
- **Inativar Turma:** modal dedicado para desativar todos os alunos de uma turma de uma vez
- **Editar Turma:** modal dedicado para migracao em lote com opcao de inativar alunos individualmente

### 7.5 Emprestimos
- Novo emprestimo (scanner ou manual, com carrinho de multiplos livros)
- Devolucao (por emprestimo ou por patrimonio - scanner)
- **Renovacao** de emprestimos (com verificacao de reservas de terceiros)
- **Reservas:** criar reserva para livro emprestado, fila ordenada por data
- Bloqueio de auto-reserva (aluno nao pode reservar livro que ele mesmo pegou)
- Notificacao de reserva na devolucao
- Botao "Emprestar" direto na reserva (fulfill) — realiza o emprestimo automaticamente
- Prazo flexivel (7/14/21/30 dias ou data personalizada)
- Uso do prazo padrao da instituicao se nao informado
- Alertas visuais para atrasos e calculo de dias em atraso
- **Busca** por aluno, matricula, livro ou patrimonio com ordenacao por relevancia
- **Coluna "Reserva"** na listagem mostrando pendencias

### 7.6 Relatorios
- **Emprestimos Ativos** (filtra por turma)
- **Emprestimos Atrasados** (filtra por turma)
- **Historico de Aluno** (por periodo, mostra "(Inativo)" se aluno desativado)
- **Movimentacao** (emprestimos/devolucoes por periodo)
- **Inventario** (por categoria, status disponivel/emprestado)
- **Mais Emprestados** (top 20, por periodo/categoria)
- **Ranking de Alunos** (alunos que mais leram no periodo, inclui inativos)
- **Ranking de Turmas** (turmas com maior volume de leitura)
- Cabecalho da instituicao com logo, CNPJ, endereco e contato
- Impressao de relatorios (CSS @media print)

### 7.7 Atividade
- Log completo de todas as operacoes
- Filtra por tipo de acao e usuario
- Data/hora e descricao detalhada

### 7.8 Usuarios e Permissoes
- Multi-usuario (admin e operator)
- Admin: acesso total
- Operator: permissoes granulares (15 permissoes)
- Troca de senha propria
- Edicao e exclusao de usuarios (admin)

**Permissoes de Operador:**
- Cadastrar/Editar/Excluir livros
- Cadastrar/Editar/Excluir alunos
- Criar emprestimos/Devolver livros/Renovar emprestimos
- Gerenciar reservas
- Ver relatorios/Imprimir codigos
- Gerenciar categorias/Fazer backup
- Ver log de atividades
- Importar/Exportar CSV: exclusivo admin

### 7.9 Instituicao
- Nome, CNPJ, endereco, telefone, e-mail
- Upload de logo (PNG/JPG/GIF/SVG)
- Visivel apenas para administradores

### 7.10 Categorias
- Listagem e gerenciamento de categorias de livros
- 56 categorias padrao semeadas automaticamente
- Definicao do prazo padrao de emprestimo (`loan_days_default`)
- Acesso via sidebar separado da Instituicao

### 7.11 Backup e Limpeza
- Download do banco SQLite (.db)
- Restauracao de backup via upload ou pela lista
- Lista com os 3 backups mais recentes + botao Restaurar
- Backup automatico ao fechar o sistema (botao Sair)
- Backup automatico antes de restauracao/limpeza
- Backup em nuvem via rclone (opcional)
- Limpeza de dados (admin)

---

## 8. Documentação dos Scripts Python

### 8.1 `run.py` - Ponto de Entrada
**Propósito:** Inicializa e executa a aplicação Flask

**Funcionalidades:**
- Detecta se está rodando como executável (PyInstaller) ou script Python
- Ajusta caminhos do sistema conforme o ambiente
- **Mata qualquer processo existente na porta 5477 antes de iniciar** (`_kill_existing_server()`)
- Abre o browser automaticamente após 1.5 segundos via `_try_open_browser()`
  - **Linux:** usa script shell que força PATH, verifica $DISPLAY e tenta browsers com `--no-sandbox`, com fallbacks
  - **Windows:** usa `webbrowser.open()` nativo
- Configura a porta padrão: **5477**
- Exibe credenciais padrão no console: `admin@biblioteca.local` / `admin123`
- Executa o servidor Flask no host `127.0.0.1` (apenas local)

**Uso:**
```bash
python run.py
```

---

### 8.2 `app/__init__.py` - Fábrica Flask
**Propósito:** Cria e configura a aplicação Flask

**Funcionalidades:**
- Define `SECRET_KEY` para segurança de sessão
- Configura caminhos: `BASE_DIR`, `BACKUP_DIR`, `DB_PATH`
- Inicializa o banco de dados (`database.init_db()`)
- Registra todos os Blueprints (rotas) da aplicação
- Cria pastas necessárias (`backups/`, `instance/`)

---

### 8.3 `app/database.py` - Camada de Banco de Dados (~1147 linhas)
**Propósito:** Gerencia todas as operações do banco SQLite (sem SQLAlchemy)

**Funções Principais:**

#### Inicialização:
- `init_db(db_path)` - Inicializa o banco e cria tabelas
- `get_conn()` - Retorna conexão com SQLite (WAL mode, foreign keys ativas)
- `_create_tables()` - Cria todas as tabelas se não existirem
- `_seed_defaults()` - Insere dados padrão (admin, categorias)
- `_migrate_columns()` - Migração de esquema (adiciona colunas se faltarem)

#### Instituição:
- `get_institution()` - Obtém dados da instituição
- `update_institution(data)` - Atualiza dados da instituição
- `update_institution_logo(path)` - Atualiza logo

#### Usuários:
- `get_user_by_email(email)` - Busca por e-mail
- `get_user_by_login_identifier(identifier)` - Login flexível (e-mail/nome)
- `list_users()` - Lista todos os usuários
- `create_user(data)` - Cria novo usuário
- `update_user(user_id, data)` - Atualiza usuário
- `deactivate_user(user_id)` - Desativa usuário
- `update_last_login(user_id)` - Atualiza último login
- `check_user_password(user_id, password)` - Verifica senha
- `change_user_password(user_id, new_password)` - Troca senha

#### Livros:
- `list_books(q)` - Listagem com busca (sem paginação)
- `get_book(book_id)` - Obtém livro por ID
- `get_book_by_patrimony(patrimony)` - Busca por patrimônio
- `create_book(data)` - Cadastra livro
- `update_book(book_id, data)` - Edita livro (inclui patrimônio)
- `search_books(q, limit)` - Busca rápida (para modal de empréstimos)
- `_book_dict(r)` - Converte row em dict com status de disponibilidade
- `deactivate_book(book_id)` - Desativa livro (soft delete)

#### Alunos:
- `list_students(q, active_filter)` - Listagem com busca e filtro (active/inactive/all)
- `get_student(student_id)` - Obtém aluno por ID
- `get_student_by_enrollment(enrollment)` - Busca por matrícula
- `create_student(data)` - Cadastra aluno
- `update_student(student_id, data)` - Edita aluno (inclui matrícula)
- `set_student_active(student_id, active)` - Ativa/desativa aluno
- `cancel_student_reservations(student_id)` - Cancela reservas ao desativar

#### Empréstimos:
- `list_loans(status, q)` - Lista por status (active/overdue/returned/all) com busca
- `get_loan(loan_id)` - Obtém empréstimo por ID
- `get_active_loan_for_book(book_id)` - Busca empréstimo ativo de um livro
- `create_loan(book_id, student_id, due_date, user_id)` - Cria novo empréstimo
- `return_loan(loan_id)` - Registra devolução (verifica reserva pendente)
- `renew_loan(loan_id, extra_days)` - Renova empréstimo (bloqueia se houver reserva)
- `_process_row(r, today)` - Processa row com cálculo de atraso

#### Reservas:
- `create_reservation(book_id, student_id, user_id)` - Cria reserva (bloqueia auto-reserva)
- `cancel_reservation(rid)` - Cancela reserva
- `get_active_reservations(book_id)` - Lista reservas ativas
- `get_next_reservation_for_book(book_id)` - Próximo da fila
- `check_reservation_on_loan(book_id, student_id)` - Verifica se outro aluno tem reserva
- `fulfill_reservation(rid)` - Marca reserva como atendida

#### Dashboard:
- `dashboard_stats()` - Estatísticas para o painel principal
- `dashboard_charts()` - Dados para gráficos (empréstimos/dia, livros por categoria, top books, empréstimos por turma)

#### Relatórios:
- `report_active_loans(class_name)` - Empréstimos ativos
- `report_overdue(class_name)` - Empréstimos atrasados
- `report_student_history(student_id, date_from, date_to)` - Histórico de aluno
- `report_movement(date_from, date_to, type)` - Movimentação por período
- `report_inventory(category, status)` - Inventário de acervo
- `report_most_borrowed(date_from, date_to, category)` - Livros mais emprestados
- `report_student_ranking(date_from, date_to)` - Ranking de alunos (inclui inativos)
- `report_class_ranking(date_from, date_to)` - Ranking de turmas
- `get_classes()` - Lista turmas distintas
- `get_categories()` - Lista categorias

#### Licença:
- `get_license()` - Obtém info de licença
- `save_license(data)` - Salva licença ativada
- `invalidate_license()` - Invalida licença

#### Permissões:
- `get_operator_permissions()` - Obtém permissões de operador
- `save_operator_permissions(data)` - Salva permissões

#### Utilitários:
- `log_activity(type, description, user_id)` - Registra no log
- `global_search(q)` - Busca global em livros e alunos
- `_fmt_date(date_str)` - Formata data (DD/MM/YYYY)
- `_fmt_dt(dt_str)` - Formata data/hora

---

### 8.4 `app/license.py` - Licenciamento (79 linhas)
**Propósito:** Gerencia licenciamento por hardware

**Funções:**

- `get_machine_id()` - Gera ID único baseado em:
  - Endereço MAC
  - Nome do host
  - Sistema operacional
  - Arquitetura
  - Formato: `XXXX-XXXX-XXXX-XXXX` (16 caracteres hex)

- `generate_license_key(machine_id, institution, valid_days)` - Gera chave:
  - Formato ultra-compacto: 4 grupos de 5 caracteres
  - Base32 encoding
  - Assinada com HMAC-SHA256
  - Machine-locked (vinculada ao hardware)
  - Contém data de expiração embutida

- `validate_license_key(license_key, machine_id)` - Valida:
  - Verifica formato e tamanho
  - Verifica assinatura HMAC
  - Verifica se a chave é para esta máquina
  - Verifica se não está expirada
  - Retorna `{'valid': bool, 'error': str, 'valid_until': date}`

---

### 8.5 Ferramentas de Licenciamento

#### `GeradorLicenca.exe` — Gerador GUI (Tkinter)
Executável com interface gráfica. Basta abrir, preencher Machine ID, instituição e validade, e clicar em "Gerar Chave". A chave aparece na tela e pode ser copiada.

#### `gerar_chave_cli.exe` — Gerador CLI (fallback)
Executável de linha de comando. Útil para debug ou quando a interface gráfica não abre.

**Uso:**
```cmd
gerar_chave_cli.exe
```
Informe o Machine ID, ou deixe em branco para usar o ID da máquina local.

#### `_dev/app_licenca.py` — Código-fonte do Gerador GUI
**Propósito:** Código-fonte usado para gerar o `GeradorLicenca.exe`.

**Funcionalidades:**
- Interface Tkinter com campos: Machine ID, Instituição, Validade
- Gera chave via `generate_license_key()` do `app.license`
- Botão "Copiar" para copiar a chave gerada
- **Botão "Excluir Selecionada"** + tecla **Delete** para remover licenças da lista
- Funcoes de licenca embutidas diretamente no .exe (sem importacao externa)

---

### 8.6 `app/routes/auth.py` - Autenticação (~216 linhas)
**Propósito:** Gerencia login, logout e ativação de licença

**Rotas Web:**
- `GET /` - Redireciona para dashboard ou login
- `GET/POST /login` - Tela de login
  - Login flexível: aceita e-mail, nome ou identificador
  - Exibe Machine ID para ativação de licença
  - Mostra status da licença (ativa/inativa)
- `GET /license-check` - Tela de verificação de licença (após login)
- `GET /logout` - Encerra sessão

**API:**
- `POST /api/license/activate` - Ativa licença via AJAX
- `GET /api/license/status` - Retorna status da licença (JSON)

**Decorators (middleware):**
- `@login_required` - Exige usuário logado
- `@license_required` - Exige licença ativa
- `@auth_required` - Exige login + licença
- `@admin_required` - Exige ser administrador

---

### 8.7 `app/routes/books.py` - Livros (~188 linhas)
**Propósito:** Gestão completa do acervo

**Rotas Web:**
- `GET /dashboard` - Painel principal
- `GET /livros` - Página de livros

**API REST:**
- `GET /api/books?q=&sort_by=patrimony&sort_dir=asc` - Lista com busca e ordenação (patrimônio como inteiro)
- `GET /api/books/<id>` - Detalhes de um livro
- `GET /api/books/by-patrimony/<pat>` - Busca por patrimônio
- `GET /api/books/search?q=&limit=` - Busca rápida com relevância (alunos primeiro, depois livros, depois empréstimos)
- `GET /api/books/next-patrimony` - Próximo número de patrimônio disponível (auto-incremento)
- `POST /api/books` - Cadastra livro (requer `can_create_books`)
- `PUT /api/books/<id>` - Edita livro (requer `can_edit_books`, inclui patrimônio)
- `DELETE /api/books/<id>` - Remove livro (apenas admin, se sem empréstimos ativos)
- `POST /api/books/import-csv` - Importação em massa via CSV
- `GET /api/books/<id>/barcode` - Gera código de barras (Code128) como PNG
- `GET /api/dashboard/stats` - Estatísticas do dashboard
- `GET /api/dashboard/charts` - Dados para gráficos

---

### 8.8 `app/routes/students.py` - Alunos (~123 linhas)
**Propósito:** Gestão completa de alunos

**Rotas Web:**
- `GET /alunos` - Página de alunos

**API REST:**
- `GET /api/students?q=&active=` - Lista com busca e filtro (active/inactive/all)
- `GET /api/students/<id>` - Detalhes
- `GET /api/students/by-enrollment/<mat>` - Busca por matrícula
- `POST /api/students` - Cadastra (requer `can_create_students`)
- `PUT /api/students/<id>` - Edita (requer `can_edit_students`)
  - Permite alteração de matrícula
  - Valida duplicidade de matrícula
- `POST /api/students/<id>/toggle-active` - Ativa/desativa (com validação de empréstimos)
- `DELETE /api/students/<id>` - Remove (apenas admin, se sem empréstimos)
- `POST /api/students/import-csv` - Importação em massa via CSV

---

### 8.9 `app/routes/loans.py` - Empréstimos (~301 linhas)
**Propósito:** Gestão de empréstimos, devoluções, renovações e reservas

**Rotas Web:**
- `GET /emprestimos` - Página de empréstimos
- `GET /reservas` - Página de reservas

**API REST:**
- `GET /api/loans?status=active&q=` - Lista empréstimos (active, returned, overdue, all)
- `POST /api/loans` - Cria empréstimo (requer `can_create_loans`)
- `POST /api/loans/<id>/return` - Devolução (requer `can_return_books`)
- `POST /api/loans/<id>/renew` - Renovação (requer `can_renew_loans`)
- `GET /api/loans/check/<book_id>` - Verifica status do livro (emprestado/reservado)
- `GET /api/loans/student-history/<student_id>` - Histórico do aluno
- `GET /api/reservations` - Lista reservas ativas
- `POST /api/reservations` - Cria reserva (requer `can_manage_reservations`)
- `POST /api/reservations/<id>/fulfill` - Atende reserva: cria empréstimo com prazo padrão e marca como atendida (requer `can_create_loans`)
- `DELETE /api/reservations/<id>` - Cancela reserva (requer `can_manage_reservations`)
- `GET /api/reservations/check/<student_id>/<book_id>` - Verifica reserva existente

---

### 8.10 `app/routes/reports.py` - Relatórios (63 linhas)
**Propósito:** Relatórios gerenciais com filtros

**Rotas Web:**
- `GET /relatorios` - Página de relatórios

**API REST:**
- `GET /api/reports/active-loans?class_name=` - Empréstimos ativos
- `GET /api/reports/overdue?class_name=` - Empréstimos atrasados
- `GET /api/reports/student-history?student_id=&date_from=&date_to=` - Histórico de aluno
- `GET /api/reports/movement?date_from=&date_to=&type=` - Movimentação (type: all/borrows/returns)
- `GET /api/reports/inventory?category=&status=` - Inventário (status: available/borrowed)
- `GET /api/reports/most-borrowed?date_from=&date_to=&category=` - Mais emprestados
- `GET /api/reports/classes` - Lista de turmas
- `GET /api/reports/categories` - Lista de categorias

---

### 8.11 `app/routes/settings.py` - Configurações (~516 linhas)
**Propósito:** Configurações da instituição, categorias, usuários, backup e permissões

**Rotas Web:**
- `GET /instituicao` - Dados da instituição (admin)
- `GET /categorias` - Categorias e prazo padrão de empréstimo
- `GET /usuarios` - Gerenciar usuários
- `GET /permissoes` - Permissões de operador (admin)
- `GET /backup` - Backup e restauração
- `GET /limpeza` - Limpeza de dados (admin)

**API REST:**
- `GET/PUT /api/institution` - Consulta/atualiza instituição
- `GET /api/institution/loan-days-default` - Prazo padrão de empréstimo
- `POST /api/institution/logo` - Upload de logo
- `GET /api/institution/logo-file` - Exibe logo
- `GET/POST /api/users` - Lista/cria usuários
- `PUT /api/users/<id>` - Edita usuário
- `DELETE /api/users/<id>` - Remove usuário (admin)
- `POST /api/users/change-password` - Troca própria senha
- `POST /api/system/shutdown` - Força backup e desliga o servidor
- `GET /api/operator-permissions` - Consulta permissões (qualquer usuário logado)
- `POST /api/operator-permissions` - Salva permissões (admin)
- `GET /api/backup/download` - Download do .db (requer `can_backup`)
- `POST /api/backup/restore` - Restaura backup (admin)
- `GET /api/backup/list` - Lista backups
- `GET/POST /api/categories` - Lista/cria categorias (requer `can_manage_categories`)
- `PUT /api/categories/<id>` - Edita categoria (nome e prazo padrão)
- `DELETE /api/categories/<id>` - Remove categoria
- `GET /api/books/import-template` - Download template CSV livros
- `GET /api/students/import-template` - Download template CSV alunos
- `POST /api/cleanup` - Limpa dados de teste (admin)

---

### 8.12 `app/routes/api.py` - API Geral (23 linhas)
**Propósito:** API geral e busca global

**API REST:**
- `GET /api/activity` - Log de atividades (requer `can_view_activity`)
- `GET /api/search?q=` - Busca global com relevância: alunos primeiro, depois livros, depois empréstimos (mínimo 2 caracteres)

---

### 8.13 Scripts Utilitários

#### `identificar_ignorados.py`
**Para que serve:** Analisa um arquivo CSV antes de importar e identifica quais itens seriam ignorados (rejeitados).

**Uso:**
```bash
python identificar_ignorados.py arquivo.csv
```

**O que faz:**
- Lista itens com patrimônio/título vazio
- Lista itens com patrimônio já existente no banco
- Lista itens com patrimônio duplicado no próprio CSV
- Gera relatório em `analise_importacao.txt`

#### `analisar_rejeitados.py`
**Para que serve:** Versão alternativa para análise de CSV e itens rejeitados.

**Uso:**
```bash
python analisar_rejeitados.py arquivo.csv
```

#### `analisar_csv.py`
**Para que serve:** Análise completa de arquivo CSV antes de importar.

#### `validar_csv.py`
**Para que serve:** Validação de arquivos CSV para importação.

#### `fix_import.py`
**Para que serve:** Corrige problemas de importação de CSV.

#### `check_db.py`
**Para que serve:** Verifica estado do banco de dados e logs de importação.

**Uso:**
```bash
python check_db.py
```

**O que faz:**
- Lista todas as tabelas no banco
- Mostra logs de importação (tabela `activity_log`)

#### `check_import_log.py`
**Para que serve:** Verifica logs de importação de livros.

#### `check_books.py`
**Para que serve:** Verifica livros cadastrados no banco.

#### `verificar_log.py`
**Para que serve:** Verifica logs de atividade do sistema.

#### `limpar_dados_teste.py`
**Para que serve:** Limpeza de dados de teste do banco.

#### `server.ps1` e `server.bat`
**Para que serve:** Gerencia o servidor Flask (start/stop/restart) no Windows.

**Uso:**
```powershell
.\server.ps1 start    # Inicia servidor
.\server.ps1 stop     # Para servidor
.\server.ps1 restart  # Reinicia servidor
```
ou
```bash
server.bat start
server.bat stop
server.bat restart
```

**O que faz:**
- Cria arquivo `server.pid` com o PID do processo
- Ao parar, mata o processo pelo PID e verifica a porta 5000
- Remove o arquivo PID ao encerrar

---

## 9. Instalação e Uso

### 9.1 Para Desenvolvimento

1. **Clone/extraia o projeto**
2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
   Ou manualmente:
   ```bash
   pip install flask werkzeug Pillow python-barcode qrcode
   ```

3. **Execute:**
   ```bash
   python run.py
   ```

4. **Acesse:** `http://127.0.0.1:5477`

5. **Login padrão:**
   - Usuário: `admin@biblioteca.local`
   - Senha: `admin123`

### 9.2 Para Distribuição (Criar Executável)

**Windows:**
```bash
pip install flask werkzeug pyinstaller
pyinstaller Biblioteca.spec
```
O executável será gerado em `dist/Biblioteca.exe` → copiar para `release/Biblioteca.exe`.

**Linux:**
```bash
pip install flask werkzeug pyinstaller
pyinstaller Biblioteca.spec
```
O executável será gerado em `dist/Biblioteca` → copiar para `release/Biblioteca-linux` e dar `chmod +x`.

### 9.3 Para o Cliente

1. Extraia a pasta `Biblioteca` em qualquer local
2. Dê duplo clique em `Biblioteca.exe`
3. O sistema abrirá automaticamente no navegador
4. Na primeira tela, ative sua licença:
   - Copie o "ID da Máquina" que aparece na tela
   - Envie este ID ao administrador do sistema
   - Receba a chave de ativação e digite na tela
   - Clique em "Ativar"
5. Faça login:
   - Usuário padrão: `admin@biblioteca.local`
   - Senha padrão: `admin123`
    - TROQUE A SENHA APOS O PRIMEIRO ACESSO!

---

## 10. Resolução de Problemas

### 10.1 Browser não abre automaticamente
Abra manualmente: `http://127.0.0.1:5477`

### 10.2 Porta já em uso
Altere `PORT` em `run.py` para outro número (ex: 5478, 8080)

### 10.3 Erro de banco de dados
Apague `instance/biblioteca.db` para recriar do zero (perde todos os dados!)

### 10.4 Licença não aceita
- Verifique se o Machine ID informado ao gerar a licença é exatamente igual ao mostrado na tela de login
- Verifique se a data do computador do cliente está correta
- Use o "Auto-teste" em `gerar_licenca.py` para debug

### 10.5 Build falha (Windows)
- Antivírus pode estar bloqueando o PyInstaller (desative temporariamente)
- Sem permissão de escrita na pasta (execute como Administrador)
- Erro de dependência (veja o log do PyInstaller)

### 10.6 Servidor não para (processo pendurado)
O sistema **mata automaticamente** qualquer processo na porta 5477 ao reiniciar.
Se precisar matar manualmente:
```powershell
taskkill /f /im Biblioteca.exe
```

### 10.7 Edição de aluno não atualiza matrícula
- Reinicie o servidor após alterações no código
- Limpe o cache do navegador (Ctrl+Shift+R ou Ctrl+F5)
- Verifique se o banco está sendo atualizado testando:
  ```bash
  python -c "from app.database import init_db, get_student; init_db('instance/biblioteca.db'); s = get_student(1589); print('Matrícula:', s['enrollment'])"
  ```

### 10.8 Página de livros lenta (+3000 livros)
O sistema já possui paginação implementada (50 livros por vez). Se ainda estiver lento:
- Verifique se as alterações no `database.py` e `books.py` foram aplicadas
- Reinicie o servidor
- Verifique o log do console para erros

---

## 11. Ativação de Licença - Passo a Passo

### Para o Cliente:
1. Execute o `Biblioteca.exe`
2. Na tela de login, clique em "Licença do Sistema"
3. Copie o **ID da Máquina** (ex: `A1B2-C3D4-E5F6-G7H8`)
4. Envie este ID para o desenvolvedor

### Para o Desenvolvedor:
1. Execute `python gerar_licenca.py`
2. Escolha a opção **1** (Gerar nova licença)
3. Informe o **Machine ID** recebido do cliente
4. Informe o **Nome da Instituição**
5. Escolha a **Validade** (1, 2, 3 anos ou personalizado)
6. A chave será gerada e salva em `chave_gerada.txt`
7. Envie a chave ao cliente

### Para o Cliente (continuação):
5. Na tela de ativação, cole a **chave de licença** recebida
6. Clique em "Ativar"
7. Se tudo estiver correto, aparecerá "Licença ativada com sucesso!"
8. Faça login e comece a usar o sistema

---

## 12. Dependências (requirements.txt)

```
flask>=3.0.0
werkzeug>=3.0.0
Pillow>=10.0.0
python-barcode>=0.15.1
qrcode>=7.4.2
```

**Dependências para build:**
- pyinstaller (não está no requirements.txt, instalado pelo script de build)

---

## 13. Templates HTML

### 13.1 `app/templates/login.html` (174 linhas)
**Propósito:** Tela de login e ativação de licença

**Elementos:**
- Formulário de login (usuário/e-mail e senha)
- Exibe erros de autenticação
- Painel de licença (expandível)
- Mostra Machine ID
- Campo para ativar chave de licença
- Status da licença (Ativa/Inativa)
- JavaScript para login AJAX e ativação de licença

### 13.2 `app/templates/app.html` (~789 linhas)
**Propósito:** SPA (Single Page Application) - todas as telas do sistema

**Características:**
- Interface moderna com CSS e JS externos (`static/js/app.js`, `static/css/app.css`) — todo o JS foi externalizado de `app.html` para `app.js`
- Sidebar fixa com navegação
- Todas as páginas carregadas via JavaScript/AJAX
- Design responsivo
- Fontes: DM Sans (texto), Playfair Display (títulos)
- Paleta: cores neutras com destaque em `#e07a5f` (terracota)
- Ícones SVG inline
- Formatação de datas brasileira (DD/MM/YYYY)
- Máscaras de input
- Busca global com dropdown de resultados
- Filtros e ordenação
- Códigos de barras exibidos em modal
- Impressão otimizada (@media print)
- Chart.js v4.4.7 local com gráficos ampliados (canvas 200px)
- Controle de permissões no frontend (applyPermissions)
- Botão trocar usuário e sair com backup automático
- Nome da instituição exibido na sidebar
- Pesquisa e coluna de reservas na página de empréstimos
- Busca global com relevância: alunos > livros > empréstimos

---

## 14. Informações para Distribuição

### O que o desenvolvedor entrega:
```
Release/
├── windows/
│   └── Biblioteca.exe
├── linux/
│   ├── Biblioteca-<versao>-x86_64.AppImage
│   ├── biblioteca-icon.png
│   └── Biblioteca.desktop
└── ferramentas/
    ├── GeradorLicenca.exe
    ├── rclone.exe
    ├── winfsp.msi
    └── licencas.db
```

### Conteúdo sugerido para README.txt do cliente:
```
BIBLIOTECA - Sistema de Controle de Acervo

1. Dê um duplo clique em "Biblioteca.exe"
2. O sistema abrirá automaticamente no seu navegador
3. Na primeira tela, ative sua licença:
   - Copie o "ID da Máquina" que aparece na tela
   - Envie este ID ao administrador do sistema
   - Receba a chave de ativação e digite na tela
   - Clique em "Ativar"
4. Faça login:
   - Usuário padrão: admin@biblioteca.local
   - Senha padrão: admin123
    - TROQUE A SENHA APOS O PRIMEIRO ACESSO!
5. Para sair, use o botao Sair no canto inferior esquerdo

Suporte: [seu contato]
```

---

## 15. Configurações e Personalização

### 15.1 Trocar Porta do Servidor
Em `run.py`, altere:
```python
PORT = 5477  # Troque para a porta desejada
```

### 15.2 Trocar Chave Secreta de Licença
Em `app/license.py`, altere:
```python
LICENSE_SECRET = b'biblio-lic-hmac-secret-key-2025'  # Mude para sua chave
```
**Atencao:** Se alterar apos ja ter gerado licencas, todas as licencas anteriores pararao de funcionar.

### 15.3 Adicionar Ícone no Executável (Windows)
1. Coloque o arquivo `icon.ico` em `app/static/img/`
2. O `build_windows.bat` detectará automaticamente

### 15.4 Categorias Padrão
Alterar em `app/database.py`, função `_seed_defaults()`:
```python
default_cats = ['Romance', 'Ficção', 'Infantil', 'Didático', 'Poesia', 'Biografia', 'HQ/Mangá', 'Outro']
```

### 15.5 Tempo de Auto-logout
O sistema não possui auto-logout implementado nativamente (pode ser adicionado futuramente).

---

## 16. Backup na Nuvem (rclone)

Opcional. O sistema detecta automaticamente se o **rclone** esta instalado e mostra um botao "Enviar para Nuvem" na pagina de Backup.

### 16.1 Instalação

**Windows:**
```cmd
:: Baixar: https://rclone.org/downloads
:: Extrair e copiar rclone.exe para a pasta do Biblioteca:
copy rclone.exe release\rclone.exe
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install rclone
```

### 16.2 Configurar Google Drive

```bash
rclone config create gdrive drive
```
O navegador abre para autorizar. Depois de autorizar, o remote `gdrive` fica pronto.

Outros provedores: `rclone config` e siga o menu interativo.

### 16.3 Testar

```bash
rclone ls gdrive:
```

### 16.4 Como funciona no sistema

- Ao acessar a página **Backup**, o sistema verifica se o rclone está disponível
- Se estiver, mostra o botao **Enviar para Nuvem**
- O backup (.db) é copiado para `gdrive:Biblioteca/backups/`
- Totalmente opcional — sem rclone o backup local continua normal

---

## 17. Status do Projeto

**Build:** `release/` contém executáveis organizados por sistema:

```
release/
├── windows/
│   └── Biblioteca.exe
├── linux/
│   ├── Biblioteca-<versao>-x86_64.AppImage
│   ├── biblioteca-icon.png
│   └── Biblioteca.desktop
└── ferramentas/
    ├── GeradorLicenca.exe
    ├── rclone.exe
    ├── winfsp.msi
    └── licencas.db
```

---

**Documentação gerada em:** 22/05/2026  
**Sistema:** Biblioteca - Sistema de Controle de Acervo  
**Versão atual:** 1.0.29
