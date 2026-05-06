# 📚 Biblioteca — Sistema de Controle de Acervo

Sistema desktop para controle de empréstimos de biblioteca escolar.
Roda no browser, sem instalação no cliente. Windows e Linux.

---

## 🗂 Estrutura do Projeto

```
biblioteca/
├── run.py                  ← Ponto de entrada principal
├── gerar_licenca.py        ← Gerador de licenças (uso do desenvolvedor)
├── requirements.txt        ← Dependências Python
├── build_windows.bat       ← Build para Windows (.exe)
├── build_linux.sh          ← Build para Linux (binário)
├── app/
│   ├── __init__.py         ← Fábrica do Flask
│   ├── database.py         ← Models SQLAlchemy (SQLite)
│   ├── license.py          ← Sistema de licenciamento por hardware
│   ├── routes/
│   │   ├── auth.py         ← Login, logout, ativação de licença
│   │   ├── books.py        ← CRUD livros + importação CSV
│   │   ├── students.py     ← CRUD alunos + importação CSV
│   │   ├── loans.py        ← Empréstimos e devoluções
│   │   ├── reports.py      ← Relatórios com filtros
│   │   ├── settings.py     ← Instituição, usuários, backup
│   │   └── api.py          ← Busca global, log de atividade
│   └── templates/
│       ├── login.html      ← Tela de login + ativação de licença
│       └── app.html        ← SPA principal (todas as telas)
├── instance/
│   └── biblioteca.db       ← Banco SQLite (criado automaticamente)
└── backups/                ← Backups locais (criado automaticamente)
```

---

## 🚀 Rodando em Desenvolvimento

### Pré-requisitos
- Python 3.10+ instalado na **sua** máquina de desenvolvimento

### Instalar dependências
```bash
pip install -r requirements.txt
```

### Iniciar o sistema
```bash
python run.py
```
O browser abrirá automaticamente em `http://127.0.0.1:5477`

### Login padrão
- **E-mail:** `admin@biblioteca.local`
- **Senha:** `admin123`

> ⚠️ Troque a senha do admin após o primeiro acesso!

---

## 📦 Gerando o Executável (cliente não precisa de Python)

### Windows (.exe)
Execute na sua máquina Windows com Python instalado:
```
build_windows.bat
```
Gera: `release/Biblioteca.exe`

### Linux (binário)
Execute na sua máquina Linux com Python instalado:
```bash
chmod +x build_linux.sh
./build_linux.sh
```
Gera: `release/biblioteca`

### O que o cliente recebe
```
📁 Biblioteca/
   Biblioteca.exe      ← duplo clique para abrir
   instance/           ← criada automaticamente (banco de dados)
   backups/            ← criada automaticamente (backups locais)
```

O executável já embutee Python, Flask e todas as dependências.
**O cliente não instala nada.**

---

## 🔐 Sistema de Licenciamento

### Como funciona
1. O app gera um **ID de Máquina** baseado no hardware (MAC, hostname, OS)
2. O ID aparece na tela de login do cliente
3. Você usa `gerar_licenca.py` para criar uma chave vinculada àquele ID
4. O cliente digita a chave na tela de login — licença ativada

### Gerar uma licença
Na **sua** máquina (com Python):
```bash
python gerar_licenca.py
```
Informe o Machine ID do cliente, o nome da instituição e o prazo.
O script gera uma chave no formato `XXXXX-XXXXX-XXXXX-XXXXX-XXXXX`.

### Características de segurança
- Chave **vinculada ao hardware** — não funciona em outra máquina
- Chave **assinada com HMAC-SHA256** — não pode ser falsificada
- Validade configurável (1, 2 ou 3 anos)
- Validação 100% offline — sem servidor externo

---

## 📊 Funcionalidades

| Módulo | Recursos |
|---|---|
| **Dashboard** | Estatísticas em tempo real, empréstimos recentes, alertas de atraso |
| **Livros** | Cadastro, edição, busca, importação CSV, status de disponibilidade |
| **Alunos** | Cadastro, edição, busca por nome/matrícula/turma, importação CSV |
| **Empréstimos** | Novo empréstimo (scanner ou manual), devolução, prazo flexível (7/14/21/30 dias) |
| **Relatórios** | 6 tipos, filtros por turma/aluno/período/categoria, impressão |
| **Atividade** | Log completo de todas as operações |
| **Usuários** | Multi-usuário, perfis admin/operador, troca de senha |
| **Instituição** | Nome, CNPJ, endereço, prazo padrão de empréstimo |
| **Backup** | Download manual do .db, restauração, histórico de backups |

---

## 📥 Importação CSV

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

## 🔧 Configurações Avançadas

### Trocar a porta do servidor
Em `run.py`, altere a variável `PORT = 5477`

### Trocar a chave secreta de licença
Em `app/license.py`, altere `LICENSE_SECRET`.
⚠️ Se alterar após já ter gerado licenças, todas as licenças anteriores param de funcionar.

### Backup automático antes de fechar
Ainda não implementado — planejado para próxima versão.
Por enquanto, use o botão "Baixar Backup" na aba Backup.

---

## 🐛 Resolução de Problemas

**Browser não abre automaticamente**
Abra manualmente: `http://127.0.0.1:5477`

**Porta já em uso**
Altere `PORT` em `run.py` para outro número (ex: 5478)

**Erro de banco de dados**
Apague `instance/biblioteca.db` para recriar do zero (perde os dados!)

**Licença não aceita**
Verifique se o Machine ID informado ao gerar a licença é exatamente igual ao mostrado na tela de login.
