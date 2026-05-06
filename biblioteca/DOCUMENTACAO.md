# 📚 Biblioteca - Sistema de Controle de Acervo
## Documentação Completa

---

## 📋 Índice
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
├── gerar_licenca.py            ← Gerador de licenças (desenvolvedor)
├── requirements.txt             ← Dependências Python
├── Biblioteca.spec              ← Configuração PyInstaller
├── build_windows.bat           ← Script de build para Windows
├── build_linux.sh              ← Script de build para Linux
├── server.bat                  ← Atalho para gerenciar servidor (Windows)
├── server.ps1                  ← Script PowerShell para gerenciar servidor
├── app/
│   ├── __init__.py             ← Fábrica da aplicação Flask
│   ├── database.py             ← Camada de banco de dados (SQLite puro)
│   ├── license.py              ← Sistema de licenciamento
│   ├── routes/
│   │   ├── __init__.py         ← (vazio, torna um pacote)
│   │   ├── auth.py             ← Login, logout, ativação de licença
│   │   ├── books.py            ← CRUD livros + importação CSV + códigos
│   │   ├── students.py         ← CRUD alunos + importação CSV
│   │   ├── loans.py            ← Empréstimos e devoluções
│   │   ├── reports.py          ← Relatórios com filtros
│   │   ├── settings.py         ← Instituição, usuários, backup, permissões
│   │   └── api.py              ← Busca global, log de atividade
│   ├── templates/
│   │   ├── login.html          ← Tela de login + ativação de licença
│   │   └── app.html            ← SPA principal (1937 linhas)
│   └── static/
│       └── img/
│           └── favicon.svg      ← Ícone do sistema
├── instance/                   ← Criada automaticamente
│   ├── biblioteca.db           ← Banco SQLite (criado automaticamente)
│   └── logos/                 ← Logos da instituição
├── backups/                    ← Backups locais (criado automaticamente)
├── build/                      ← Arquivos temporários do PyInstaller
├── dist/                       ← Saída do PyInstaller
└── release/                     ← Executável final para distribuição
    └── Biblioteca.exe         ← (Windows) ou "biblioteca" (Linux)
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
| `app/routes/auth.py` | ~125 | Autenticação e licenciamento |
| `app/routes/books.py` | ~158 | Gestão de livros |
| `app/routes/students.py` | ~123 | Gestão de alunos |
| `app/routes/loans.py` | ~103 | Empréstimos e devoluções |
| `app/routes/reports.py` | ~63 | Relatórios |
| `app/routes/settings.py` | ~324 | Configurações e usuários |
| `app/routes/api.py` | ~23 | API geral e busca |

### 3.3 Scripts Utilitários

| Arquivo | Propósito |
|---------|-----------|
| `gerar_licenca.py` | Gera chaves de licença (uso do desenvolvedor) |
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
| `server.ps1 / server.bat` | Gerencia servidor (start/stop/restart) |

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
| notes | TEXT | '' | Observações |

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
| active | INTEGER | 1 | Ativa (1) ou inativa (0) |

**Categorias padrão:** Romance, Ficção, Infantil, Didático, Poesia, Biografia, HQ/Mangá, Outro

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
   python gerar_licenca.py
   # Escolhe opção 1
   # Informa: Machine ID, Nome da Instituição, Validade
   # Chave gerada: XXXXX-XXXXX-XXXXX-XXXXX
   # Arquivo salvo: chave_gerada.txt
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
LICENSE_SECRET = b'biblio-lic-secret-2026-!@#XkP9m'
```
⚠️ **Atenção:** Se alterar após já ter gerado licenças, todas as licenças anteriores pararão de funcionar.

---

## 6. Criação de Executáveis

### 6.1 Pré-requisitos para Build
- Python 3.10+ instalado
- Pip funcionando
- PyInstaller (instalado automaticamente pelo script)

### 6.2 Windows (.exe)

**Método 1: Script automático (recomendado)**
```bash
.\build_windows.bat
```

O script:
1. Localiza o Python instalado (testa várias localizações)
2. Instala dependências: `flask`, `werkzeug`, `pyinstaller`
3. Limpa builds anteriores (`dist/`, `build/`)
4. Executa PyInstaller com configurações:
   - `--onefile`: Gera um único .exe
   - `--noconsole`: Sem janela de console
   - `--add-data`: Inclui templates e static
   - `--hidden-import`: Inclui dependências do Flask
5. Copia o resultado para `release/Biblioteca.exe`

**Método 2: Manual**
```bash
pip install flask werkzeug pyinstaller
pyinstaller Biblioteca.spec
```

### 6.3 Linux (binário)

```bash
chmod +x build_linux.sh
./build_linux.sh
```

### 6.4 O que o Cliente Recebe

O cliente recebe **apenas o arquivo `.exe`** (ou binário no Linux). Não é necessário enviar pastas adicionais, pois:
- Templates e estáticos são embutidos no `.exe` pelo PyInstaller (`--onefile`)
- Na primeira execução, o sistema cria automaticamente ao lado do `.exe`:
  - `instance/` (pasta com o banco de dados `biblioteca.db`)
  - `backups/` (pasta para backups locais)

### 6.5 Distribuição com Banco Vazio

Para uma **nova instalação limpa** (sem dados de teste):
1. Gere o executável (`build_windows.bat` ou `build_linux.sh`)
2. Envie **apenas o `.exe`** para o cliente
3. **Não envie** o arquivo `biblioteca.db`

Quando o cliente executar o `.exe` pela primeira vez, a função `init_db()` detecta que o banco não existe e:
- Cria a pasta `instance/`
- Cria o arquivo `biblioteca.db` com todas as tabelas vazias
- Insere apenas o usuário admin padrão (`admin@biblioteca.local` / `admin123`)
- Insere as categorias padrão (Romance, Ficção, etc.)

⚠️ **Importante:** Se você já tem um `biblioteca.db` na pasta de desenvolvimento, ele é usado para testes locais. O executável gerado **não carrega** esse banco junto. Ele sempre cria um novo se não encontrar um `instance/biblioteca.db` no caminho.

Para **testar como se fosse uma instalação nova**, basta apagar a pasta `instance/` antes de rodar `python run.py`.

---

## 7. Funcionalidades

### 7.1 Dashboard
- Estatísticas em tempo real (total livros, alunos, empréstimos, atrasos)
- Empréstimos recentes
- Alertas de atraso

### 7.2 Livros
- Cadastro com patrimônio (obrigatório), título, autor, ISBN, categoria, editora, ano
- Busca por patrimônio/título/autor
- Importação em massa via CSV
- Geração de código de barras (Code128) para etiquetas
- Status de disponibilidade em tempo real
- Edição e exclusão (se sem empréstimos ativos)
- **Paginação:** Carrega 50 livros por vez (otimizado para +3800 livros)

### 7.3 Alunos
- Cadastro com matrícula (obrigatório), nome, turma, telefone, e-mail
- Busca por nome/matrícula/turma
- Importação em massa via CSV
- Visualização de empréstimos ativos e status de atraso
- Edição e exclusão (se sem empréstimos)

### 7.4 Empréstimos
- Novo empréstimo (busca por patrimônio ou seleção manual)
- Devolução (por empréstimo ou por patrimônio - scanner)
- Prazo flexível (7/14/21/30 dias ou data personalizada)
- Uso do prazo padrão da instituição se não informado
- Alertas visuais para atrasos e cálculo de dias em atraso

### 7.5 Relatórios
- **Empréstimos Ativos** (filtra por turma)
- **Empréstimos Atrasados** (filtra por turma)
- **Histórico de Aluno** (por período)
- **Movimentação** (empréstimos/devoluções por período)
- **Inventário** (por categoria, status disponível/emprestado)
- **Mais Emprestados** (top 20, por período/categoria)
- Impressão de relatórios (CSS @media print)

### 7.6 Atividade
- Log completo de todas as operações
- Filtra por tipo de ação e usuário
- Data/hora e descrição detalhada

### 7.7 Usuários e Permissões
- Multi-usuário (admin e operator)
- Admin: acesso total
- Operator: permissões granulares (13 permissões)
- Troca de senha própria
- Edição e exclusão de usuários (admin)

**Permissões de Operador:**
- Cadastrar/Editar/Excluir livros
- Cadastrar/Editar/Excluir alunos
- Criar empréstimos/Devolver livros
- Ver relatórios/Imprimir códigos
- Gerenciar categorias/Fazer backup
- Ver log de atividades

### 7.8 Instituição
- Nome, CNPJ, endereço, telefone, e-mail
- Definição do prazo padrão de empréstimo
- Upload de logo (PNG/JPG/GIF/SVG)

### 7.9 Backup e Limpeza
- Download do banco SQLite (.db)
- Restauração de backup
- Histórico de backups locais
- Backup automático antes de restauração/limpeza
- Limpeza seletiva de dados de teste (admin)

---

## 8. Documentação dos Scripts Python

### 8.1 `run.py` - Ponto de Entrada
**Propósito:** Inicializa e executa a aplicação Flask

**Funcionalidades:**
- Detecta se está rodando como executável (PyInstaller) ou script Python
- Ajusta caminhos do sistema conforme o ambiente
- Abre o browser automaticamente após 1.5 segundos
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

### 8.3 `app/database.py` - Camada de Banco de Dados (613 linhas)
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
- `list_books(q, page, per_page)` - Listagem com busca e paginação (50 por página)
- `get_book(book_id)` - Obtém livro por ID
- `get_book_by_patrimony(patrimony)` - Busca por patrimônio
- `create_book(data)` - Cadastra livro
- `update_book(book_id, data)` - Edita livro
- `_book_dict(r)` - Converte row em dict com status de disponibilidade
- `deactivate_book(book_id)` - Desativa livro (soft delete)

#### Alunos:
- `list_students(q)` - Listagem com busca
- `get_student(student_id)` - Obtém aluno por ID
- `get_student_by_enrollment(enrollment)` - Busca por matrícula
- `create_student(data)` - Cadastra aluno
- `update_student(student_id, data)` - Edita aluno (inclui matrícula)
- `deactivate_student(student_id)` - Desativa aluno

#### Empréstimos:
- `list_loans(status, q)` - Lista por status (active/overdue/returned)
- `get_loan(loan_id)` - Obtém empréstimo por ID
- `get_active_loan_for_book(book_id)` - Busca empréstimo ativo de um livro
- `create_loan(data)` - Cria novo empréstimo
- `return_loan(loan_id)` - Registra devolução
- `_process_row(r, today)` - Processa row com cálculo de atraso

#### Dashboard:
- `dashboard_stats()` - Estatísticas para o painel principal

#### Relatórios:
- `report_active_loans(class_name)` - Empréstimos ativos
- `report_overdue(class_name)` - Empréstimos atrasados
- `report_student_history(student_id, date_from, date_to)` - Histórico de aluno
- `report_movement(date_from, date_to, type)` - Movimentação por período
- `report_inventory(category, status)` - Inventário de acervo
- `report_most_borrowed(date_from, date_to, category)` - Livros mais emprestados
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

### 8.5 `gerar_licenca.py` - Gerador de Licenças (125 linhas)
**Propósito:** Ferramenta para o desenvolvedor gerar licenças

**Uso:** `python gerar_licenca.py`

**Menu:**
- **Opção 0:** Auto-teste (gera e valida localmente)
- **Opção 1:** Gerar nova licença
  - Solicita Machine ID do cliente
  - Solicita nome da instituição
  - Escolhe validade: 1, 2, 3 anos ou personalizado
  - Gera chave e salva em `chave_gerada.txt`
- **Opção 2:** Validar/verificar uma chave existente
- **Opção 9:** Sair

---

### 8.6 `app/routes/auth.py` - Autenticação (125 linhas)
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

### 8.7 `app/routes/books.py` - Livros (158 linhas)
**Propósito:** Gestão completa do acervo

**Rotas Web:**
- `GET /dashboard` - Painel principal
- `GET /livros` - Página de livros

**API REST:**
- `GET /api/books?q=&page=&per_page=` - Lista com busca e paginação
- `GET /api/books/<id>` - Detalhes de um livro
- `GET /api/books/by-patrimony/<pat>` - Busca por patrimônio
- `POST /api/books` - Cadastra livro (requer `can_create_books`)
- `PUT /api/books/<id>` - Edita livro (requer `can_edit_books`)
- `DELETE /api/books/<id>` - Remove livro (apenas admin, se sem empréstimos)
- `POST /api/books/import-csv` - Importação em massa via CSV
  - Aceita colunas: `patrimonio/patrimônio/PAT`, `titulo/título/title`, `autor/author`, `isbn`, `categoria/category`, `editora/publisher`, `ano/year`
- `GET /api/books/<id>/barcode` - Gera código de barras (Code128) como PNG
- `GET /api/dashboard/stats` - Estatísticas do dashboard

---

### 8.8 `app/routes/students.py` - Alunos (123 linhas)
**Propósito:** Gestão completa de alunos

**Rotas Web:**
- `GET /alunos` - Página de alunos

**API REST:**
- `GET /api/students?q=` - Lista com busca
- `GET /api/students/<id>` - Detalhes
- `GET /api/students/by-enrollment/<mat>` - Busca por matrícula
- `POST /api/students` - Cadastra (requer `can_create_students`)
- `PUT /api/students/<id>` - Edita (requer `can_edit_students`)
  - Permite alteração de matrícula
  - Valida duplicidade de matrícula
- `DELETE /api/students/<id>` - Remove (apenas admin, se sem empréstimos)
- `POST /api/students/import-csv` - Importação em massa via CSV
  - Aceita colunas: `matricula/matrícula/enrollment`, `nome/name`, `turma/class`, `telefone/phone`, `email`

---

### 8.9 `app/routes/loans.py` - Empréstimos (103 linhas)
**Propósito:** Gestão de empréstimos e devoluções

**Rotas Web:**
- `GET /emprestimos` - Página de empréstimos

**API REST:**
- `GET /api/loans?status=&q=` - Lista (status: active/overdue/returned)
- `GET /api/loans/<id>` - Detalhes
- `POST /api/loans` - Novo empréstimo (requer `can_create_loans`)
  - Aceita `book_id`, `student_id`, `due_date` (data) ou `due_days` (dias)
  - Se nenhum prazo informado, usa padrão da instituição (14 dias)
- `POST /api/loans/<id>/return` - Devolução (requer `can_return_books`)
- `POST /api/loans/return-by-patrimony` - Devolução via patrimônio
- `GET /api/loans/lookup-patrimony/<pat>` - Busca empréstimo ativo por patrimônio

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

### 8.11 `app/routes/settings.py` - Configurações (324 linhas)
**Propósito:** Configurações da instituição, usuários, backup e permissões

**Rotas Web:**
- `GET /instituicao` - Dados da instituição
- `GET /usuarios` - Gerenciar usuários
- `GET /permissoes` - Permissões de operador
- `GET /backup` - Backup e restauração
- `GET /limpeza` - Limpeza de dados (admin)

**API REST:**
- `GET/PUT /api/institution` - Consulta/atualiza instituição
- `GET /api/institution/loan-days` - Prazo padrão de empréstimo
- `POST /api/institution/logo` - Upload de logo
- `GET /api/institution/logo-file` - Exibe logo
- `GET/POST /api/users` - Lista/cria usuários
- `PUT /api/users/<id>` - Edita usuário
- `DELETE /api/users/<id>` - Remove usuário (admin)
- `POST /api/users/change-password` - Troca própria senha
- `GET /api/operator-permissions` - Consulta permissões (admin)
- `POST /api/operator-permissions` - Salva permissões (admin)
- `GET /api/backup/download` - Download do .db (requer `can_backup`)
- `POST /api/backup/restore` - Restaura backup (admin)
- `GET /api/backup/list` - Lista backups
- `GET/POST /api/categories` - Lista/cria categorias (requer `can_manage_categories`)
- `DELETE /api/categories/<id>` - Remove categoria
- `GET /api/books/import-template` - Download template CSV livros
- `GET /api/students/import-template` - Download template CSV alunos
- `POST /api/cleanup` - Limpa dados de teste (admin)

---

### 8.12 `app/routes/api.py` - API Geral (23 linhas)
**Propósito:** API geral e busca global

**API REST:**
- `GET /api/activity` - Log de atividades (requer `can_view_activity`)
- `GET /api/search?q=` - Busca global (livros e alunos, mínimo 2 caracteres)

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
build_windows.bat
```
O executável será gerado em `release/Biblioteca.exe`.

**Linux:**
```bash
chmod +x build_linux.sh
./build_linux.sh
```
O executável será gerado em `release/biblioteca`.

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
   - ⚠️ TROQUE A SENHA APÓS O PRIMEIRO ACESSO!

---

## 10. Resolução de Problemas

### 10.1 Browser não abre automaticamente
Abra manualmente: `http://127.0.0.1:5477`

### 10.2 Porta já em uso
Altere `PORT` em `run.py` para outro número (ex: 5478, 8080)

### 10.3 Erro de banco de dados
Apague `instance/biblioteca.db` para recriar do zero (⚠️ perde todos os dados!)

### 10.4 Licença não aceita
- Verifique se o Machine ID informado ao gerar a licença é exatamente igual ao mostrado na tela de login
- Verifique se a data do computador do cliente está correta
- Use o "Auto-teste" em `gerar_licenca.py` para debug

### 10.5 Build falha (Windows)
- Antivírus pode estar bloqueando o PyInstaller (desative temporariamente)
- Sem permissão de escrita na pasta (execute como Administrador)
- Erro de dependência (veja o log do PyInstaller)

### 10.6 Servidor não para (processo pendurado)
Use o script `server.ps1`:
```powershell
.\server.ps1 stop
```
Ou manualmente:
```powershell
taskkill /f /im python.exe
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

### 13.2 `app/templates/app.html` (1937 linhas)
**Propósito:** SPA (Single Page Application) - todas as telas do sistema

**Características:**
- Interface moderna com CSS embutido (1937 linhas)
- Sidebar fixa com navegação
- Todas as páginas carregadas via JavaScript/AJAX
- Design responsivo
- Fontes: DM Sans (texto), Playfair Display (títulos)
- Paleta: cores neutras com destaque em `#e07a5f` (terracota)
- Ícones SVG inline
- Formatação de datas brasileira (DD/MM/YYYY)
- Máscaras de input
- Busca global com dropdown de resultados
- Paginação (livros: 50 por página)
- Filtros e ordenação
- Códigos de barras exibidos em modal
- Impressão otimizada (@media print)

---

## 14. Informações para Distribuição

### O que o desenvolvedor entrega:
```
📁 Release/
   Biblioteca.exe (Windows) ou biblioteca (Linux)
   DOCUMENTACAO.md (este arquivo)
   README.txt (instruções básicas)
```

### Conteúdo sugerido para README.txt do cliente:
```
BIBLIOTECA - Sistema de Controle de Acervo

1. Extraia esta pasta em qualquer local do computador
2. Dê um duplo clique em "Biblioteca.exe"
3. O sistema abrirá automaticamente no seu navegador
4. Na primeira tela, ative sua licença:
   - Copie o "ID da Máquina" que aparece na tela
   - Envie este ID ao administrador do sistema
   - Receba a chave de ativação e digite na tela
   - Clique em "Ativar"
5. Faça login:
   - Usuário padrão: admin@biblioteca.local
   - Senha padrão: admin123
   - ⚠️ TROQUE A SENHA APÓS O PRIMEIRO ACESSO!

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
LICENSE_SECRET = b'biblio-lic-secret-2026-!@#XkP9m'  # Mude para sua chave
```
⚠️ **Atenção:** Se alterar após já ter gerado licenças, todas as licenças anteriores pararão de funcionar.

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

## 16. Status do Projeto

**Versão:** 1.0

**Testes:** Os scripts na raiz (`test_*.py`, `debug_*.py`, etc.) são ferramentas de debug/desenvolvimento, não testes automatizados.

**Build:** Já possui executável em `release/Biblioteca.exe` (Windows)

**Pendências identificadas:**
- Backup automático antes de fechar (mencionado como "planejado para próxima versão")
- Quantidade de livros (`quantity`) está no banco mas não totalmente implementada na lógica de empréstimos (sempre trata como 1)
- Ajuste fino na responsividade para telas muito pequenas

---

**Documentação gerada em:** 02/05/2026  
**Sistema:** Biblioteca - Sistema de Controle de Acervo  
**Desenvolvido por:** [Seu Nome/Empresa]  
**Contato para suporte:** [seu contato]
