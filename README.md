# Biblioteca — Sistema de Controle de Acervo

Sistema desktop para controle de empréstimos de biblioteca escolar.
Roda no browser, sem instalação no cliente. Windows e Linux.

---

## Estrutura do Projeto

```
biblioteca/
├── run.py                  Ponto de entrada
├── requirements.txt        Dependencias Python
├── Biblioteca.spec         Config PyInstaller (build)
├── app/
│   ├── __init__.py         Fabrica do Flask
│   ├── database.py         Camada de banco de dados (SQLite)
│   ├── license.py          Sistema de licenciamento
│   ├── config_manager.py   Gerenciamento de config local
│   ├── services.py         Servicos compartilhados
│   ├── version.py          Versao do sistema
│   ├── version_control.py  Controle de versao do banco
│   ├── routes/
│   │   ├── auth.py         Login, logout, ativacao de licenca
│   │   ├── books.py        CRUD livros + importacao CSV
│   │   ├── students.py     CRUD alunos + importacao CSV + migracao de turma
│   │   ├── loans.py        Emprestimos, devolucoes, renovacoes, reservas
│   │   ├── reports.py      Relatorios com filtros
│   │   ├── settings.py     Instituicao, usuarios, backup, permissoes
│   │   └── api.py          Busca global, log de atividade
│   ├── templates/
│   │   ├── login.html      Tela de login + ativacao de licenca
│   │   └── app.html        SPA (todas as telas)
│   └── static/
│       ├── js/app.js       Logica do frontend
│       ├── css/app.css     Estilos
│       ├── chart.min.js    Chart.js v4.4.7 local
│       └── img/
├── instance/
│   └── biblioteca.db       Banco SQLite (criado automaticamente)
├── backups/                Backups locais (criado automaticamente)
├── release/                Executaveis organizados por sistema
│   ├── windows/
│   ├── linux/
│   └── ferramentas/
└── _dev/                   Scripts de desenvolvimento/utilitarios
```

---

## Executando em Desenvolvimento

```bash
pip install -r requirements.txt
python run.py
```

Acesse `http://127.0.0.1:5477` — Login: `admin@biblioteca.local` / `admin123`

---

## Build — Gerando Executaveis

### Windows
```bash
pyinstaller Biblioteca.spec --clean
```
Gera `release/windows/Biblioteca.exe`

### Linux (AppImage + raw binary + .sh wrapper, glibc 2.17+)
```bash
_dev/build_all.sh
```
Gera 3 artefatos em `release/linux/`:
- `Biblioteca-<versao>-x86_64.AppImage` (auto-contido, duplo clique)
- `Biblioteca-<versao>-x86_64.AppImage.raw` (binario raw sem FUSE)
- `biblioteca.sh` (wrapper que extrai e executa o .raw)

### Utilitarios
`release/ferramentas/` contem: GeradorLicenca.exe, rclone.exe, winfsp.msi

---

## Release (organizado)

```
release/
├── windows/
│   └── Biblioteca-<versao>.exe          (Windows, duplo clique)
├── linux/
│   ├── Biblioteca-<versao>-x86_64.AppImage (Linux, duplo clique)
│   ├── Biblioteca-<versao>-x86_64.AppImage.raw (raw sem FUSE)
│   ├── biblioteca.sh                    (wrapper shell)
│   ├── biblioteca-icon.png              (icone para atalho)
│   └── Biblioteca.desktop               (atalho .desktop)
└── ferramentas/
    ├── GeradorLicenca.exe               (gerador de licencas)
    ├── rclone.exe                       (backup em nuvem)
    ├── winfsp-2.1.25156.msi             (rclone dependencia)
    └── licencas.db                      (historico de licencas)
```

O executavel ja embute Python, Flask e todas as dependencias.
**O cliente nao instala nada.** Dados salvos em `%APPDATA%/Biblioteca/` (Windows) ou `~/.local/share/Biblioteca/` (Linux).

---

## Sistema de Licenciamento

1. O app gera um **ID de Máquina** baseado no hardware (MAC, hostname, SO)
2. O ID aparece na tela de login do cliente
3. Use `GeradorLicenca.exe` (`release/ferramentas/`) para criar uma chave vinculada aquele ID (interface com botao "Excluir Selecionada" + tecla Delete)
4. O cliente digita a chave na tela de login — licenca ativada

- Chave vinculada ao hardware — nao funciona em outra maquina
- Assinada com HMAC-SHA256
- Validade configuravel (1, 2 ou 3 anos)
- 100% offline — sem servidor externo

---

## Funcionalidades

| Modulo | Recursos |
|---|---|
| **Dashboard** | Estatisticas em tempo real, alertas de atraso, emprestimos recentes, modal "Sobre" |
| **Graficos** | Graficos Chart.js ampliados: emprestimos/dia, livros por categoria, mais emprestados, emprestimos por turma |
| **Livros** | Cadastro, edicao, busca, importacao CSV, codigo de barras, etiquetas com busca e ordenacao, auto-incremento de patrimonio, ordenacao numerica |
| **Alunos** | Cadastro, edicao, ativar/desativar, busca, importacao CSV |
| **Alunos > Turmas** | Inativar turma inteira, migracao em lote com opcao de inativar alunos, editar turma em lote com modal dedicado |
| **Emprestimos** | Scanner ou manual, devolucao, renovacao, prazo flexivel, carrinho, busca com relevancia |
| **Reservas** | Fila por livro, notificacao na devolucao, bloqueio de auto-reserva, botao "Emprestar" direto na reserva (fulfill) |
| **Relatorios** | 10 tipos, filtros, rankings, impressao com CSS otimizado |
| **Atividade** | Log completo de todas as operacoes |
| **Usuarios** | Multi-usuario, admin/operador, 15 permissoes granulares |
| **Instituicao** | Nome, CNPJ, endereco, upload de logo (admin) |
| **Categorias** | Gerenciamento de categorias + prazo padrao de emprestimo (loan_days_default) |
| **Backup** | Automatico ao sair, download, restauracao, lista com 3 backups, restaurar da lista |
| **Cloud Backup** | Upload para Google Drive via rclone (opcional) |

---

## Importacao CSV (Apenas Admin)

### Livros — colunas aceitas:
```
patrimonio, titulo, autor, isbn, categoria, editora
```

### Alunos — colunas aceitas:
```
matricula, nome, turma, telefone, email
```

Salve o Excel como CSV (UTF-8) antes de importar.

---

## Configuracoes Avancadas

### Trocar a porta do servidor
Em `run.py`, altere a variável `PORT = 5477`

### Trocar a chave secreta de licença
Em `app/license.py`, altere `LICENSE_SECRET` (padrão: `b'biblio-lic-hmac-secret-key-2025'`).
Se alterar apos ja ter gerado licencas, todas as licencas anteriores param de funcionar.

---

## Backup na Nuvem (opcional via rclone)

O sistema detecta automaticamente se o **rclone** esta instalado. Se estiver, mostra um botao "Enviar para Nuvem" na pagina de Backup.

### Instalação rápida

**Windows:** Baixe de https://rclone.org e copie `rclone.exe` para a pasta `release/ferramentas/`.

**Linux:** `sudo apt install rclone`

### Configurar Google Drive
```bash
rclone config create gdrive drive
```

Depois de autorizar no navegador, o backup será enviado para `gdrive:Biblioteca/backups/`.

---

## Resolucao de Problemas

**Browser não abre automaticamente**
Abra manualmente: `http://127.0.0.1:5477`

**Porta já em uso**
O sistema mata automaticamente qualquer processo na porta 5477 ao iniciar.
Se ainda assim houver conflito, altere `PORT` em `run.py` para outro número (ex: 5478).

**Erro de banco de dados**
Apague `instance/biblioteca.db` para recriar do zero (perde os dados!)

**Licença não aceita**
Verifique se o Machine ID informado ao gerar a licença é exatamente igual ao mostrado na tela de login.
