"""Captura screenshots do sistema Biblioteca usando Selenium + Chrome.
Uso: pip install selenium && python docs/capturar_telas.py"""
import sys, os, subprocess, time, json, shutil, tempfile

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PROJ, 'docs', 'img')
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
if not os.path.exists(CHROME):
    CHROME = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

os.makedirs(OUT, exist_ok=True)

# 1. Iniciar servidor
print('>>> Iniciando servidor...')
proc = subprocess.Popen(
    [sys.executable, 'run.py'],
    cwd=PROJ, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)
time.sleep(6)

# 2. Configurar Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

opts = Options()
opts.add_argument('--headless=new')
opts.add_argument('--window-size=1280,800')
opts.add_argument('--disable-gpu')
opts.add_argument('--no-sandbox')
opts.add_argument('--disable-dev-shm-usage')
opts.add_argument(f'--user-data-dir={tempfile.mkdtemp(prefix="bib_")}')

driver = webdriver.Chrome(options=opts)

# 3. Login
print('>>> Autenticando...')
driver.get('http://127.0.0.1:5477/_screen_login?next=/dashboard')
time.sleep(2)

# 4. Capturar paginas
paginas = [
    ('login',       '/login'),
    ('dashboard',   '/dashboard'),
    ('livros',      '/livros'),
    ('alunos',      '/alunos'),
    ('emprestimos', '/emprestimos'),
    ('graficos',    '/graficos'),
    ('relatorios',  '/relatorios'),
    ('backup',      '/backup'),
    ('reservas',    '/reservas'),
    ('instituicao', '/instituicao'),
    ('usuarios',    '/usuarios'),
]

results = []
for nome, url in paginas:
    path = os.path.join(OUT, f'screen_{nome}.png')
    print(f'  Capturando {nome}...', end=' ')
    driver.get(f'http://127.0.0.1:5477{url}')
    time.sleep(2)
    driver.save_screenshot(path)
    kb = os.path.getsize(path) / 1024
    print(f'OK ({kb:.0f} KB)' if kb > 1 else 'FALHOU')
    results.append((nome, f'{kb:.0f} KB'))

# 5. Limpeza
print('>>> Finalizando...')
driver.quit()
proc.kill()
proc.wait()

print('\n=== RESULTADO ===')
for n, s in results:
    print(f'  {n:15s} {s}')
print(f'\nTotal: {len(results)} imagens em {OUT}')
