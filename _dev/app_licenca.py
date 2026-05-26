"""
GERADOR DE LICENCAS — Interface Grafica (Tkinter)
Versao standalone para desenvolvimento.
"""
import sys, os, sqlite3, tkinter as tk, hashlib, hmac, base64, uuid, platform, json
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta, date

# ── Funções de licença (embutidas para standalone) ──
_LICENSE_SECRET = b'biblio-lic-hmac-secret-key-2025'
def _get_machine_id():
    raw = '|'.join([hex(uuid.getnode()), platform.node(), platform.system(), platform.machine()])
    h = hashlib.sha256(raw.encode()).hexdigest()[:16].upper()
    return '-'.join([h[i:i+4] for i in range(0, 16, 4)])
def _generate_license_key(machine_id, institution='', valid_days=365):
    exp = date.today().toordinal() + valid_days
    nonce = uuid.uuid4().bytes[:3]
    mid_hash = hashlib.sha256(machine_id.encode()).digest()[:4]
    exp_bytes = exp.to_bytes(4, 'big')
    payload = mid_hash + exp_bytes + nonce
    sig = hmac.new(_LICENSE_SECRET, payload, hashlib.sha256).digest()[:4]
    combined = payload + sig
    encoded = base64.b32encode(combined).decode().rstrip('=')
    groups = [encoded[i:i+6] for i in range(0, len(encoded), 6)]
    return '-'.join(groups)
def _validate_license_key(license_key, machine_id):
    try:
        clean = license_key.replace('-', '').replace(' ', '').upper()
        if not clean: return {'valid': False, 'error': 'Chave vazia'}
        pad = (8 - len(clean) % 8) % 8
        try: decoded = base64.b32decode(clean + '=' * pad)
        except: return {'valid': False, 'error': 'Formato de chave inválido'}
        if len(decoded) < 12: return {'valid': False, 'error': 'Chave muito curta'}
        payload = decoded[:11] if len(decoded) >= 15 else decoded[:8]
        sig_stored = decoded[11:15] if len(decoded) >= 15 else decoded[8:12]
        sig_exp = hmac.new(_LICENSE_SECRET, payload, hashlib.sha256).digest()[:4]
        if not hmac.compare_digest(sig_stored, sig_exp):
            return {'valid': False, 'error': 'Assinatura inválida'}
        mid_hash = hashlib.sha256(machine_id.encode()).digest()[:4]
        if payload[:4] != mid_hash:
            return {'valid': False, 'error': 'Licença não é válida para esta máquina'}
        exp = date.fromordinal(int.from_bytes(payload[4:8], 'big'))
        if date.today() > exp: return {'valid': False, 'error': f'Licença expirada em {exp.strftime("%d/%m/%Y")}'}
        return {'valid': True, 'valid_until': exp.strftime('%d/%m/%Y'), 'error': None}
    except Exception as ex:
        return {'valid': False, 'error': f'Chave inválida: {ex}'}
generate_license_key = _generate_license_key
validate_license_key = _validate_license_key
get_machine_id = _get_machine_id

_BASE = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
_DB = os.path.join(_BASE, 'licencas.db')


def _get_db():
    db = sqlite3.connect(_DB)
    db.row_factory = sqlite3.Row
    db.execute('''CREATE TABLE IF NOT EXISTS licenses
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         machine_id TEXT NOT NULL,
         institution TEXT NOT NULL,
         valid_days INTEGER NOT NULL,
         valid_until TEXT NOT NULL,
         license_key TEXT NOT NULL,
         created_at TEXT NOT NULL DEFAULT (datetime('now','localtime')))''')
    db.commit()
    return db


class LicenseApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Gerador de Licencas — Biblioteca')
        self.root.geometry('980x620')
        self.root.resizable(False, False)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self._build_gerar_tab(self.notebook)
        self._build_validar_tab(self.notebook)
        self._build_historico_tab(self.notebook)
        self._build_auto_tab(self.notebook)

    # ── GERAR ──
    def _build_gerar_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=16)
        notebook.add(frame, text='  Gerar Licenca  ')

        ttk.Label(frame, text='ID da Maquina do Cliente:', font=('',10)).grid(row=0, column=0, sticky='w', pady=(0,4))
        self.mid_entry = ttk.Entry(frame, width=56, font=('Consolas',10))
        self.mid_entry.grid(row=1, column=0, columnspan=3, sticky='ew', pady=(0,12))

        ttk.Label(frame, text='Nome da Instituicao:', font=('',10)).grid(row=2, column=0, sticky='w', pady=(0,4))
        self.inst_entry = ttk.Entry(frame, width=56, font=('',10))
        self.inst_entry.grid(row=3, column=0, columnspan=3, sticky='ew', pady=(0,12))

        ttk.Label(frame, text='Validade:', font=('',10)).grid(row=4, column=0, sticky='w', pady=(0,4))
        self.valid_days = tk.StringVar(value='365')
        days_frame = ttk.Frame(frame)
        days_frame.grid(row=5, column=0, columnspan=3, sticky='w', pady=(0,4))
        for text, val in [('1 ano (365 dias)', '365'), ('2 anos (730 dias)', '730'), ('3 anos (1095 dias)', '1095'), ('Personalizado', '0')]:
            ttk.Radiobutton(days_frame, text=text, variable=self.valid_days, value=val).pack(side='left', padx=(0,12))

        self.custom_days_frame = ttk.Frame(frame)
        self.custom_days_frame.grid(row=6, column=0, columnspan=3, sticky='w', pady=(0,12))
        ttk.Label(self.custom_days_frame, text='Dias:').pack(side='left')
        self.custom_days_entry = ttk.Entry(self.custom_days_frame, width=10, font=('',10))
        self.custom_days_entry.pack(side='left', padx=(4,0))
        self.custom_days_entry.insert(0, '365')
        self.custom_days_frame.grid_remove()

        def on_validity_change(*_):
            if self.valid_days.get() == '0':
                self.custom_days_frame.grid()
            else:
                self.custom_days_frame.grid_remove()
        self.valid_days.trace_add('write', on_validity_change)

        ttk.Separator(frame, orient='horizontal').grid(row=7, column=0, columnspan=3, sticky='ew', pady=12)

        self.gen_btn = ttk.Button(frame, text='  GERAR CHAVE  ', command=self._generate)
        self.gen_btn.grid(row=8, column=0, sticky='w')

        ttk.Label(frame, text='Chave Gerada:', font=('',10)).grid(row=9, column=0, sticky='w', pady=(12,4))
        key_frame = ttk.Frame(frame)
        key_frame.grid(row=10, column=0, columnspan=3, sticky='ew')
        self.key_display = tk.Text(key_frame, height=3, width=56, font=('Consolas',14,'bold'), wrap='word',
                                    relief='solid', borderwidth=1, bg='#f5fff5')
        self.key_display.pack(side='left', fill='both', expand=True)
        scroll_key = ttk.Scrollbar(key_frame, orient='vertical', command=self.key_display.yview)
        scroll_key.pack(side='right', fill='y')
        self.key_display.configure(yscrollcommand=scroll_key.set)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=11, column=0, columnspan=3, sticky='ew', pady=(8,0))
        ttk.Button(btn_frame, text='Copiar Chave', command=self._copy_key).pack(side='left', padx=(0,8))
        ttk.Button(btn_frame, text='Salvar em Arquivo...', command=self._save_key).pack(side='left')
        self.status_label = ttk.Label(frame, text='', foreground='green', font=('',9))
        self.status_label.grid(row=12, column=0, columnspan=3, sticky='w', pady=(6,0))

        frame.columnconfigure(1, weight=1)

    # ── VALIDAR ──
    def _build_validar_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=16)
        notebook.add(frame, text='  Validar Chave  ')

        ttk.Label(frame, text='Chave de Licenca:', font=('',10)).grid(row=0, column=0, sticky='w', pady=(0,4))
        self.v_key_entry = ttk.Entry(frame, width=56, font=('Consolas',11))
        self.v_key_entry.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0,12))

        ttk.Label(frame, text='ID da Maquina:', font=('',10)).grid(row=2, column=0, sticky='w', pady=(0,4))
        self.v_mid_entry = ttk.Entry(frame, width=56, font=('Consolas',10))
        self.v_mid_entry.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0,12))

        ttk.Button(frame, text='Validar', command=self._validate).grid(row=4, column=0, sticky='w')

        self.v_result = tk.Text(frame, height=5, width=56, font=('Consolas',10), wrap='word',
                                 relief='solid', borderwidth=1, bg='#fafafa')
        self.v_result.grid(row=5, column=0, columnspan=2, sticky='ew', pady=(12,0))

        frame.columnconfigure(0, weight=1)

    # ── HISTORICO ──
    def _build_historico_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=16)
        notebook.add(frame, text='  Historico  ')

        top = ttk.Frame(frame)
        top.pack(fill='x', pady=(0,8))
        ttk.Label(top, text='Buscar:', font=('',9)).pack(side='left')
        self.h_search = ttk.Entry(top, width=30, font=('',9))
        self.h_search.pack(side='left', padx=(6,0))
        self.h_search.bind('<KeyRelease>', lambda e: self._load_history())
        ttk.Button(top, text='↻', width=3, command=self._load_history).pack(side='left', padx=(4,0))
        ttk.Label(top, text='(clique duplo p/ reemitir)', font=('',8), foreground='gray').pack(side='right')

        cols = ('id','inst','mid','dias','valido','chave','criado')
        self.h_tree = ttk.Treeview(frame, columns=cols, show='headings', height=14)
        self.h_tree.heading('id', text='#')
        self.h_tree.heading('inst', text='Instituicao')
        self.h_tree.heading('mid', text='Machine ID')
        self.h_tree.heading('dias', text='Dias')
        self.h_tree.heading('valido', text='Valido ate')
        self.h_tree.heading('chave', text='Chave')
        self.h_tree.heading('criado', text='Criado em')
        self.h_tree.column('id', width=35, anchor='center')
        self.h_tree.column('inst', width=160)
        self.h_tree.column('mid', width=130)
        self.h_tree.column('dias', width=50, anchor='center')
        self.h_tree.column('valido', width=100, anchor='center')
        self.h_tree.column('chave', width=280)
        self.h_tree.column('criado', width=140, anchor='center')

        scroll_y = ttk.Scrollbar(frame, orient='vertical', command=self.h_tree.yview)
        scroll_x = ttk.Scrollbar(frame, orient='horizontal', command=self.h_tree.xview)
        self.h_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        btn_frame = ttk.Frame(frame)
        ttk.Button(btn_frame, text='Reemitir Licenca', command=self._reemitir).pack(side='left', padx=(0,8))
        ttk.Button(btn_frame, text='Excluir Selecionada', command=self._delete_license).pack(side='left', padx=(0,8))
        ttk.Button(btn_frame, text='Exportar CSV...', command=self._export_csv).pack(side='left')

        btn_frame.pack(side='bottom', fill='x', pady=(0,8))
        scroll_x.pack(side='bottom', fill='x')
        scroll_y.pack(side='right', fill='y')
        self.h_tree.pack(side='left', fill='both', expand=True)

        self.h_tree.bind('<Double-1>', self._reemitir)
        self.h_tree.bind('<Delete>', lambda e: self._delete_license())

        self._load_history()

    # ── AUTO-TESTE ──
    def _build_auto_tab(self, notebook):
        frame = ttk.Frame(notebook, padding=16)
        notebook.add(frame, text='  Auto-Teste  ')

        ttk.Label(frame, text='Testa o sistema de licencas localmente:', font=('',10)).pack(anchor='w')
        ttk.Button(frame, text='Executar Auto-Teste', command=self._self_test).pack(anchor='w', pady=(12,8))

        self.at_result = tk.Text(frame, height=12, width=72, font=('Consolas',10), wrap='word',
                                  relief='solid', borderwidth=1, bg='#fafafa')
        self.at_result.pack(fill='both', expand=True)

    # ── METODOS ──
    def _get_valid_days(self):
        v = self.valid_days.get()
        if v == '0':
            try: return max(1, int(self.custom_days_entry.get().strip() or '365'))
            except: return 365
        return int(v)

    def _generate(self):
        machine_id = self.mid_entry.get().strip().upper()
        if not machine_id:
            messagebox.showerror('Erro', 'Informe o ID da Maquina do cliente')
            return
        institution = self.inst_entry.get().strip() or 'Instituicao'
        valid_days = self._get_valid_days()

        key = generate_license_key(machine_id, institution, valid_days)
        self.key_display.delete('1.0', tk.END)
        self.key_display.insert('1.0', key)

        valid_until = (datetime.now() + timedelta(days=valid_days)).strftime('%d/%m/%Y')
        self.status_label.config(text=f'Chave gerada! Validade: {valid_days} dias (ate {valid_until})', foreground='green')

        try:
            db = _get_db()
            db.execute('INSERT INTO licenses (machine_id, institution, valid_days, valid_until, license_key) VALUES (?,?,?,?,?)',
                       (machine_id, institution, valid_days, valid_until, key))
            db.commit()
            db.close()
        except:
            pass

    def _copy_key(self):
        key = self.key_display.get('1.0', tk.END).strip()
        if not key:
            messagebox.showinfo('Aviso', 'Nenhuma chave para copiar')
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(key)
        self.status_label.config(text='Chave copiada para a area de transferencia!', foreground='blue')

    def _save_key(self):
        key = self.key_display.get('1.0', tk.END).strip()
        if not key:
            messagebox.showinfo('Aviso', 'Nenhuma chave para salvar')
            return
        f = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Arquivo de texto','*.txt')],
                                          title='Salvar chave de licenca')
        if f:
            with open(f, 'w', encoding='utf-8') as fh:
                fh.write(key)
            self.status_label.config(text=f'Chave salva em: {f}', foreground='blue')

    def _validate(self):
        key = self.v_key_entry.get().strip()
        machine_id = self.v_mid_entry.get().strip().upper()
        if not key or not machine_id:
            messagebox.showerror('Erro', 'Informe a chave e o ID da maquina')
            return
        result = validate_license_key(key, machine_id)
        self.v_result.delete('1.0', tk.END)
        if result['valid']:
            msg = f'LICENCA VALIDA\nValida ate: {result["valid_until"]}'
            self.v_result.config(bg='#f0fff0')
        else:
            msg = f'LICENCA INVALIDA\nErro: {result["error"]}'
            self.v_result.config(bg='#fff0f0')
        self.v_result.insert('1.0', msg)

    def _delete_license(self):
        sel = self.h_tree.selection()
        if not sel:
            messagebox.showinfo('Aviso', 'Selecione uma licenca no historico')
            return
        row = self.h_tree.item(sel[0], 'values')
        lid = row[0]
        inst = row[1]
        if not messagebox.askyesno('Confirmar Exclusao',
                                    f'Tem certeza que deseja excluir a licenca #{lid} de "{inst}"?\n\n'
                                    'Esta operacao nao pode ser desfeita.'):
            return
        try:
            db = _get_db()
            db.execute('DELETE FROM licenses WHERE id = ?', (lid,))
            db.commit()
            db.close()
            self._load_history()
        except Exception as e:
            messagebox.showerror('Erro', str(e))

    def _load_history(self):
        q = self.h_search.get().strip().lower()
        try:
            db = _get_db()
            if q:
                rows = db.execute('SELECT * FROM licenses WHERE LOWER(institution) LIKE ? ORDER BY id DESC',
                                  (f'%{q}%',)).fetchall()
            else:
                rows = db.execute('SELECT * FROM licenses ORDER BY id DESC').fetchall()
            db.close()
        except:
            rows = []
        for row in self.h_tree.get_children():
            self.h_tree.delete(row)
        for r in rows:
            vals = (r['id'], r['institution'], r['machine_id'], r['valid_days'],
                    r['valid_until'], r['license_key'], r['created_at'])
            self.h_tree.insert('', tk.END, values=vals)

    def _reemitir(self, event=None):
        sel = self.h_tree.selection()
        if not sel:
            messagebox.showinfo('Aviso', 'Selecione uma licenca no historico')
            return
        row = self.h_tree.item(sel[0], 'values')
        inst = row[1]
        dias = int(row[3])
        valid_until_old = row[4]
        mid_old = row[2]

        resp = messagebox.askyesnocancel('Reemitir Licenca',
            f'Instituicao: {inst}\n'
            f'Validade anterior: {dias} dias (ate {valid_until_old})\n'
            f'Machine ID anterior: {mid_old}\n\n'
            'Deseja usar o MESMO Machine ID? (Sim)\n'
            'Ou informar um NOVO Machine ID? (Nao)\n'
            'Cancelar para sair.')
        if resp is None:
            return
        if resp:
            new_mid = mid_old
        else:
            d = tk.Toplevel(self.root)
            d.title('Novo Machine ID')
            d.geometry('400x120')
            d.resizable(False, False)
            d.transient(self.root)
            d.grab_set()
            ttk.Label(d, text=f'Instituicao: {inst}\nValidade: {dias} dias').pack(pady=(10,6))
            entry = ttk.Entry(d, width=40, font=('Consolas',10))
            entry.pack(padx=20)
            entry.focus()
            result = {'mid': None}
            def confirm():
                result['mid'] = entry.get().strip().upper()
                d.destroy()
            ttk.Button(d, text='Confirmar', command=confirm).pack(pady=10)
            self.root.wait_window(d)
            if not result['mid']:
                return
            new_mid = result['mid']

        key = generate_license_key(new_mid, inst, dias)
        valid_until = (datetime.now() + timedelta(days=dias)).strftime('%d/%m/%Y')

        self.notebook.select(0)
        self.mid_entry.delete(0, tk.END)
        self.mid_entry.insert(0, new_mid)
        self.inst_entry.delete(0, tk.END)
        self.inst_entry.insert(0, inst)
        self.key_display.delete('1.0', tk.END)
        self.key_display.insert('1.0', key)
        self.status_label.config(
            text=f'Reemitido! Validade: {dias} dias (ate {valid_until})', foreground='blue')

        try:
            db = _get_db()
            db.execute('INSERT INTO licenses (machine_id, institution, valid_days, valid_until, license_key) VALUES (?,?,?,?,?)',
                       (new_mid, inst, dias, valid_until, key))
            db.commit()
            db.close()
        except:
            pass

    def _export_csv(self):
        f = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')],
                                          title='Exportar historico')
        if not f:
            return
        try:
            db = _get_db()
            rows = db.execute('SELECT * FROM licenses ORDER BY id').fetchall()
            db.close()
            with open(f, 'w', encoding='utf-8-sig') as fh:
                fh.write('ID;Instituicao;Machine ID;Dias;Valido ate;Chave;Criado em\n')
                for r in rows:
                    fh.write(f'{r["id"]};{r["institution"]};{r["machine_id"]};{r["valid_days"]};{r["valid_until"]};{r["license_key"]};{r["created_at"]}\n')
            messagebox.showinfo('OK', f'Exportado: {f}')
        except Exception as e:
            messagebox.showerror('Erro', str(e))

    def _self_test(self):
        self.at_result.delete('1.0', tk.END)
        self.at_result.insert('1.0', 'Executando auto-teste...\n\n')
        self.at_result.update()

        try:
            mid = get_machine_id()
            self.at_result.insert(tk.END, f'Machine ID local: {mid}\n')
            key = generate_license_key(mid, 'Teste Auto', 365)
            self.at_result.insert(tk.END, f'Chave gerada:     {key}\n')
            result = validate_license_key(key, mid)
            if result['valid']:
                self.at_result.insert(tk.END, f'Validacao:         VALIDA\n')
                self.at_result.insert(tk.END, f'Valida ate:        {result["valid_until"]}\n')
                self.at_result.insert(tk.END, '\nSUCESSO — Sistema de licencas funcionando corretamente.')
            else:
                self.at_result.insert(tk.END, f'Validacao:         FALHOU — {result["error"]}\n')
        except Exception as e:
            self.at_result.insert(tk.END, f'ERRO: {e}\n')

    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    LicenseApp().run()
