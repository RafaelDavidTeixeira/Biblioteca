# Alterações na Sessão - 15/05/2026

## Correções Críticas

### 1. GeradorLicenca.exe — Import Quebrada

**Problema:** `GeradorLicenca.exe` gerava chaves inválidas ou não funcionava.

**Causa:** `_dev/app_licenca.py:8` importava `from license import ...` (sem `app.`), enquanto o módulo está em `app/license.py`. O `GeradorLicenca.spec` tinha `datas=[('license.py', '.')]` que antes copiava manualmente o arquivo. Após remover o `datas`, a importação `from license` não encontrava o módulo no bundle.

**Correção:** `_dev/app_licenca.py:8` — alterado `from license import ...` para `from app.license import ...`. Removido o `datas` desnecessário do spec. Reconstruído o executável.

---

### 2. Kill-before-start em run.py

**Problema:** Se o navegador fosse fechado sem clicar em "Sair ⏻", o servidor Flask continuava rodando em segundo plano. Ao tentar abrir o exe novamente, a porta 5477 estava ocupada.

**Solução:** Adicionada função `_kill_existing_server()` em `run.py` que:
- **Windows:** usa `netstat -ano` + `taskkill /F /PID`
- **Linux:** usa `fuser <port>/tcp` + `kill -9`
- Executada no início de `main()`, antes de `create_app()`

---

## Melhorias

### 3. Documentação atualizada
- `README.md`, `DOCUMENTACAO.md`, `MANUAL_USUARIO.md`: refletem nova estrutura de release (GeradorLicenca.exe, gerar_chave_cli.exe, Biblioteca-linux), caminho de dados via APPDATA, kill-before-start, e ferramentas de licenciamento GUI/CLI.

---

## Sessões Anteriores

### Sessão - 07/05/2026

#### Correções Críticas

##### 1. Permissões de Operador não Persistiam (BUG CRÍTICO)

**Problema:** Alterações nas permissões do operador eram perdidas após logout/login.

**Causas (3 bugs encadeados):**

- **Bug 1 — `app/database.py`:** `get_operator_permissions()` — `c.commit()` estava após `return dict(row)`, tornando-se código inalcançável. A cada requisição, o INSERT do registro padrão era feito mas nunca commitado — SQLite dava rollback ao fechar a conexão.
  
- **Bug 2 — `app/database.py`:** `save_operator_permissions()` usava `UPDATE` em `id=1`. Como o Bug 1 impedia a criação do registro, nenhuma linha com `id=1` existia — o UPDATE afetava 0 registros e retornava `{ok: true}` silenciosamente.

- **Bug 3 — `app/routes/settings.py`:** A rota GET `/api/operator-permissions` usava `@admin_required`. Quando o operador logava e o frontend chamava `loadOperatorPermissions()`, recebia 403. O `api()` redirecionava para `/login`, impedindo o operador de usar o sistema.

**Correções:**
- `app/database.py:1124-1140`: `c.commit()` movido para antes do `return dict(row)`
- `app/database.py:1142-1147`: `UPDATE` trocado por `INSERT OR REPLACE` (cria a linha se não existir)
- `app/routes/settings.py:329-332`: GET `/api/operator-permissions` alterado de `@admin_required` para `@auth_required`. Apenas o POST (salvar) permanece `@admin_required`.

---

#### Melhorias

##### 2. Botão "Trocar Usuário"
- `app/templates/app.html:304`: Adicionado botão ⇄ ao lado do ⏻ Sair
- Redireciona para `/logout` (apenas logout, sem criar backup)

##### 3. Pesquisa em Empréstimos
- `app/templates/app.html`: Campo de busca adicionado ao header da página de Empréstimos
- Filtra por aluno, matrícula, livro, patrimônio (backend já suportava via `q` param)
- Input com debounce de 300ms para evitar requisições excessivas

##### 4. Coluna "Reserva" na Lista de Empréstimos
- `app/database.py:597-605`: Adicionado subquery `reservation_count` na `_LOAN_SELECT`
- `app/templates/app.html`: Nova coluna "Reserva" na tabela de empréstimos mostrando quantidade de reservas pendentes (📌 N)

##### 5. Controle de Permissão nos Botões de Empréstimo
- `app/templates/app.html`: Botões "Novo Empréstimo" e "Registrar Devolução" agora têm classes `.perm-create-loans` e `.perm-return-books`
- `applyPermissions()` agora esconde esses botões conforme as permissões `can_create_loans` e `can_return_books`

---

#### Organização de Arquivos

##### Movidos para `_dev/`:
| Arquivo/Pasta | Motivo |
|---|---|
| `LINUX.txt` | Instruções de build Linux, uso do desenvolvedor |
| `Biblioteca.spec` | Configuração PyInstaller, build tooling |
| `biblioteca.db` (raiz) | Cópia do banco de desenvolvimento |
| `build/` | Artefatos temporários do PyInstaller |

##### Removidos (vazios):
- `dist/` — vazio
- `release/` — vazio

##### Backups antigos movidos para `_dev/old_backups/`:
- Todos os `pre_cleanup_*.db`, `pre_restore_*.db`, `backup_antes_limpeza_*.db`
- Backups de database antigos (mantidos apenas os 3 mais recentes de cada tipo)

---

#### Arquivos Alterados nesta Sessão

| Arquivo | Alteração |
|---------|-----------|
| `app/database.py` | Fix commit permissions, INSERT OR REPLACE, reservation_count subquery |
| `app/routes/settings.py` | GET permissões alterado para @auth_required |
| `app/templates/app.html` | Search empréstimos, coluna reserva, trocar usuário, permissões botões |
| `README.md` | Atualizado com v2.0, estrutura, funcionalidades |
| `_dev/ALTERACOES_SESSAO.md` | Este arquivo |
