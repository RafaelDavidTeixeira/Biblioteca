// ── STATE ──
let currentPage = window.CURRENT_PAGE;
let loanSelectedBookId = null;
let loanSelectedStudentId = null;
let loanSelectedDays = 14;
let institutionLoanDays = 14;
let currentReportType = '';
let returnLoanId = null;
let dtInterval;

// ── NAVIGATION ──
document.querySelectorAll('.nav-item[data-page]').forEach(el => {
  el.addEventListener('click', () => navigate(el.dataset.page));
});

function navigate(page) {
  document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
  document.querySelector(`.nav-item[data-page="${page}"]`)?.classList.add('active');
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('p-' + page)?.classList.add('active');
  currentPage = page;
  const urlMap = {
    'dashboard':'/dashboard','books':'/livros','students':'/alunos','loans':'/emprestimos',
    'reservations':'/reservas','charts':'/graficos','reports':'/relatorios','institution':'/instituicao',
    'categories':'/categorias','permissions':'/permissoes','users':'/usuarios','backup':'/backup','cleanup':'/limpeza',
    'barcodes':'/barcodes','activity':'/atividade','license_check':'/license-check'
  };
  history.pushState({}, '', urlMap[page] || '/' + page);
  loadPage(page);
}

function loadPage(page) {
  if (page === 'dashboard') loadDashboard();
  else if (page === 'books') loadBooks();
  else if (page === 'students') loadStudents();
  else if (page === 'loans') loadLoans();
  else if (page === 'reservations') loadReservationsPage();
  else if (page === 'charts') loadChartsPage();
  else if (page === 'reports') loadReportClasses();
  else if (page === 'barcodes') loadBarcodeBooks();
  else if (page === 'activity') loadActivity();
  else if (page === 'institution') loadInstitution();
  else if (page === 'categories') loadCategoriesPage();
  else if (page === 'permissions') loadPermissions();
  else if (page === 'users') loadUsers();
  else if (page === 'backup') { loadBackups(); checkCloudBackup(); }
  else if (page === 'cleanup') {} // no initial load needed
  else if (page === 'license_check') loadLicensePage();
}

async function loadReportClasses() {
  const [classes, cats] = await Promise.all([
    api('/api/reports/classes'), api('/api/reports/categories')
  ]);
  window._reportClasses = classes || [];
  window._reportCategories = cats || [];
}

// ── TOAST ──
function toast(msg, type='info') {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = `toast show ${type}`;
  clearTimeout(el._t);
  el._t = setTimeout(() => el.classList.remove('show'), 3200);
}

async function handleExit() {
  if (!confirm('Deseja sair do sistema?\nUm backup de segurança será criado automaticamente.')) return;
  
  const btn = document.querySelector('.btn-logout');
  btn.disabled = true;
  btn.style.opacity = '0.5';
  
  try {
    const r = await fetch('/api/system/shutdown', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'}
    });
    
    if (r.ok) {
      document.documentElement.style.margin = '0';
      document.documentElement.style.padding = '0';
      document.body.style.margin = '0';
      document.body.style.padding = '0';
      document.body.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:center;height:100vh;width:100vw;flex-direction:column;font-family:system-ui,sans-serif;text-align:center;background:#f5f5f5;margin:0;padding:0">
          <div style="background:#fff;border-radius:12px;padding:2.5rem 3rem;box-shadow:0 2px 20px rgba(0,0,0,.08);max-width:420px">
            <h1 style="margin:0 0 .8rem;font-size:1.4rem;color:#1a1a1a">Sistema Encerrado</h1>
            <p style="color:#666;margin:0 0 1rem;font-size:.9rem;line-height:1.5">O backup foi criado com sucesso.<br>Você já pode fechar esta janela.</p>
            <button onclick="window.open('','_self','');window.close()" style="padding:.7rem 1.5rem;cursor:pointer;background:#2d6a4f;color:white;border:none;border-radius:8px;font-size:.88rem;font-weight:500">Fechar Janela</button>
            <p style="color:#999;margin-top:.8rem;font-size:.75rem">Se o botão não funcionar, feche manualmente.</p>
          </div>
        </div>
      `;
    } else {
      toast('Erro ao sair do sistema', 'error');
      btn.disabled = false;
      btn.style.opacity = '1';
    }
  } catch(e) {
    document.documentElement.style.margin = '0';
    document.documentElement.style.padding = '0';
    document.body.style.margin = '0';
    document.body.style.padding = '0';
    document.body.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:center;height:100vh;width:100vw;flex-direction:column;font-family:system-ui,sans-serif;text-align:center;background:#f5f5f5;margin:0;padding:0">
        <div style="background:#fff;border-radius:12px;padding:2.5rem 3rem;box-shadow:0 2px 20px rgba(0,0,0,.08);max-width:420px">
          <h1 style="margin:0 0 .8rem;font-size:1.4rem;color:#1a1a1a">Sistema Encerrado</h1>
          <p style="color:#666;margin:0 0 1rem;font-size:.9rem;line-height:1.5">Você já pode fechar esta janela.</p>
          <button onclick="window.open('','_self','');window.close()" style="padding:.7rem 1.5rem;cursor:pointer;background:#2d6a4f;color:white;border:none;border-radius:8px;font-size:.88rem;font-weight:500">Fechar Janela</button>
          <p style="color:#999;margin-top:.8rem;font-size:.75rem">Se o botão não funcionar, feche manualmente.</p>
        </div>
      </div>
    `;
  }
}

// ── API HELPERS ──
async function api(url, opts={}) {
  try {
    const r = await fetch(url, {headers:{'Content-Type':'application/json'}, ...opts});
    // Se não for JSON, mostrar erro real do servidor
    const ct = r.headers.get('content-type') || '';
    if (!ct.includes('application/json')) {
      const txt = await r.text();
      const match = txt.match(/<pre[^>]*>([\s\S]*?)<\/pre>/i);
      const msg = match ? match[1].trim().slice(0,200) : `HTTP ${r.status}`;
      toast('Erro servidor: ' + msg, 'error');
      console.error('Server error:', txt.slice(0, 500));
      return null;
    }
    const d = await r.json();
    if (d?.license_inactive) {
      navigate('license_check');
      toast('Licenca inativa. Ative o sistema para continuar.', 'error');
      return null;
    }
    return d;
  } catch(e) {
    toast('Erro de comunicacao com o servidor', 'error');
    console.error('api() error:', e);
    return null;
  }
}

// ── DATETIME ──
function updateDT() {
  const now = new Date();
  const s = now.toLocaleDateString('pt-BR') + ' — ' + now.toLocaleTimeString('pt-BR');
  ['return-dt'].forEach(id => { const el=document.getElementById(id); if(el) el.textContent=s; });
  const dtInput = document.getElementById('loan-datetime');
  if (dtInput && !dtInput.dataset.userEdited) {
    const y = now.getFullYear();
    const m = String(now.getMonth()+1).padStart(2,'0');
    const d = String(now.getDate()).padStart(2,'0');
    const h = String(now.getHours()).padStart(2,'0');
    const min = String(now.getMinutes()).padStart(2,'0');
    dtInput.value = `${y}-${m}-${d}T${h}:${min}`;
    recalcDueDate();
  }
}


// ── MODALS ──
function openModal(id) {
  document.getElementById(id).classList.add('open');
  updateDT();
}
function closeModal(id) {
  document.getElementById(id).classList.remove('open');
  if (id === 'modal-loan') {
    clearLoanStudent();
  }
  if (id === 'modal-return') {
    document.getElementById('return-reservation-alert').style.display = 'none';
  }
}
document.querySelectorAll('.overlay').forEach(o => {
  // Apenas fecha clicando no botão X ou Cancelar — não mais no fundo
});

// ── DASHBOARD ──
async function loadDashboard() {
  const d = await api('/api/dashboard/stats');
  if (!d) return;
  document.getElementById('stat-books').textContent = d.total_books.toLocaleString('pt-BR');
  if (d.total_items !== d.total_books) {
    const itemsEl = document.getElementById('stat-items');
    itemsEl.textContent = `${d.total_items} itens (copias)`;
    itemsEl.style.display = '';
  }
  document.getElementById('stat-students').textContent = d.total_students.toLocaleString('pt-BR');
  document.getElementById('stat-loans').textContent = d.active_loans;
  document.getElementById('stat-overdue').textContent = d.overdue;
  const badge = document.getElementById('overdue-badge');
  if (d.overdue > 0) { badge.textContent = d.overdue; badge.style.display=''; document.getElementById('stat-overdue-msg').style.display=''; }
  else { badge.style.display='none'; document.getElementById('stat-overdue-msg').style.display='none'; }

  const resBadge = document.getElementById('reservation-badge');
  const reservations = await api('/api/reservations');
  if (reservations && reservations.length > 0) {
    resBadge.textContent = reservations.length;
    resBadge.style.display = '';
  } else {
    resBadge.style.display = 'none';
  }

  const tbody = document.getElementById('dash-loans-body');
  if (!d.recent_loans.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty"><p>Nenhum empréstimo ativo</p></td></tr>';
  } else {
    tbody.innerHTML = d.recent_loans.map(l => `
      <tr>
        <td>${l.student_name}</td>
        <td>${l.book_title}</td>
        <td><strong>${l.book_patrimony}</strong></td>
        <td>${l.borrowed_at}</td>
        <td>${l.due_date}</td>
        <td>${statusBadge(l)}</td>
      </tr>`).join('');
  }

  checkLicenseStatus();
  updateReservationBadge();
}

async function updateReservationBadge() {
  const reservations = await api('/api/reservations');
  const badge = document.getElementById('reservation-badge');
  if (reservations && reservations.length > 0) {
    badge.textContent = reservations.length;
    badge.style.display = '';
  } else {
    badge.style.display = 'none';
  }
}

let chartInstances = {};
async function loadChartsPage() {
  if (typeof Chart === 'undefined') return;
  const data = await api('/api/dashboard/charts');
  if (!data) return;

  // Estatísticas no topo
  const totalLoans = data.loans_per_day?.reduce((a, d) => a + d.count, 0) || 0;
  const avgPerDay = data.loans_per_day?.length ? Math.round(totalLoans / 30 * 10) / 10 : 0;
  document.getElementById('chart-stat-loans').textContent = totalLoans;
  document.getElementById('chart-stat-avg').textContent = avgPerDay;
  document.getElementById('chart-stat-top').textContent = data.top_books?.[0]?.title?.substring(0, 20) + '...' || '—';
  document.getElementById('chart-stat-cat').textContent = data.books_by_category?.[0]?.label || '—';

  // Destroy existing charts
  Object.values(chartInstances).forEach(c => c.destroy());
  chartInstances = {};

  const colors = {
    primary: '#3b82f6',
    secondary: '#6366f1',
    accent: '#8b5cf6',
    warning: '#f59e0b',
    success: '#10b981',
    danger: '#ef4444',
    palette: ['#3b82f6','#6366f1','#8b5cf6','#d946ef','#f43f5e','#f59e0b','#10b981','#06b6d4']
  };

  // 1. Loans per day (bar)
  if (data.loans_per_day.length) {
    chartInstances.loansPerDay = new Chart(document.getElementById('chart-loans-per-day'), {
      type: 'bar',
      data: {
        labels: data.loans_per_day.map(d => { const p = d.date.split('-'); return `${p[2]}/${p[1]}`; }),
        datasets: [{ label: 'Empréstimos', data: data.loans_per_day.map(d => d.count), backgroundColor: colors.primary, borderRadius: 3 }]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 1, font: { size: 8 } } }, x: { ticks: { maxRotation: 45, font: { size: 7 } } } } }
    });
  }

  // 2. Books by category (doughnut)
  if (data.books_by_category.length) {
    chartInstances.booksByCat = new Chart(document.getElementById('chart-books-by-cat'), {
      type: 'doughnut',
      data: {
        labels: data.books_by_category.map(c => c.label),
        datasets: [{ data: data.books_by_category.map(c => c.value), backgroundColor: colors.palette, borderWidth: 0 }]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { font: { size: 8 }, padding: 4, boxWidth: 10 } } } }
    });
  }

  // 3. Top borrowed books (horizontal bar)
  if (data.top_books.length) {
    chartInstances.topBooks = new Chart(document.getElementById('chart-top-books'), {
      type: 'bar',
      data: {
        labels: data.top_books.map(b => b.title.length > 20 ? b.title.substring(0, 20) + '...' : b.title),
        datasets: [{ label: 'Empréstimos', data: data.top_books.map(b => b.count), backgroundColor: colors.secondary, borderRadius: 3 }]
      },
      options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true, ticks: { stepSize: 1, font: { size: 8 } } }, y: { ticks: { font: { size: 7 } } } } }
    });
  }

  // 4. Loans by class (pie)
  if (data.loans_by_class.length) {
    chartInstances.loansByClass = new Chart(document.getElementById('chart-loans-by-class'), {
      type: 'pie',
      data: {
        labels: data.loans_by_class.map(c => c.label),
        datasets: [{ data: data.loans_by_class.map(c => c.value), backgroundColor: colors.palette, borderWidth: 0 }]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { font: { size: 8 }, padding: 4, boxWidth: 10 } } } }
    });
  }
}

// ── RESERVATIONS ──
async function loadReservationsPage() {
  const status = document.getElementById('res-filter-status')?.value || 'active';
  const reservations = await api('/api/reports/reservations?status=' + status);
  if (!reservations) return;

  // Update stats BEFORE early return for empty table
  const stats = await api('/api/reports/reservation-stats');
  if (stats) {
    document.getElementById('res-stat-active').textContent = stats.total_active || 0;
    document.getElementById('res-stat-fulfilled').textContent = stats.total_fulfilled || 0;
    document.getElementById('res-stat-cancelled').textContent = stats.total_cancelled || 0;
  }

  const tbody = document.getElementById('reservations-body');
  if (!reservations.length) {
    tbody.innerHTML = '<tr><td colspan="10" class="empty"><p>Nenhuma reserva encontrada</p></td></tr>';
    return;
  }

  const statusColors = {'Ativa':'#10b981','Atendida':'#3b82f6','Cancelada':'#ef4444'};
  tbody.innerHTML = reservations.map((r, i) => `
    <tr>
      <td><strong>${i + 1}</strong></td>
      <td><strong>${r.student_name}</strong></td>
      <td>${r.student_enrollment}</td>
      <td>${r.student_class || '—'}</td>
      <td>${r.book_title}</td>
      <td><strong>${r.book_patrimony}</strong></td>
      <td>${r.reserved_at}</td>
      <td><span style="color:${statusColors[r.status_label] || '#666'};font-weight:600">${r.status_label}</span></td>
      <td>${r.operator_name || '—'}</td>
      <td>${r.status === 'active' ? `<div style="display:flex;gap:4px"><button class="btn btn-primary btn-sm" onclick="fulfillReservation(${r.id})">Emprestar</button><button class="btn btn-danger btn-sm" onclick="cancelReservationFromPage(${r.id}, '${r.book_title.replace(/'/g, "\\'")}')">Cancelar</button></div>` : '—'}</td>
    </tr>`).join('');
}

async function cancelReservationFromPage(resId, bookTitle) {
  if (!confirm(`Cancelar reserva de "${bookTitle}"?`)) return;
  const r = await api(`/api/reservations/${resId}`, { method: 'DELETE' });
  if (r?.ok) {
    toast('Reserva cancelada', 'success');
    loadReservationsPage();
    loadDashboard();
    updateReservationBadge();
  } else {
    toast(r?.error || 'Erro', 'error');
  }
}

async function fulfillReservation(rid) {
  if (!confirm('Confirmar empréstimo a partir desta reserva?')) return;
  const r = await api(`/api/reservations/${rid}/fulfill`, {method:'POST'});
  if (r?.ok) {
    toast('Empréstimo realizado com sucesso!', 'success');
    loadReservationsPage();
    loadDashboard();
    updateReservationBadge();
  } else {
    toast(r?.error || 'Erro ao realizar empréstimo', 'error');
  }
}

// ── BOOKS ──
async function openNewBook() {
  document.getElementById('book-modal-title').textContent = 'Cadastrar Novo Livro';
  document.getElementById('book-edit-id').value = '';
  ['book-patrimony','book-title','book-author','book-isbn','book-publisher','book-notes','book-location'].forEach(f => document.getElementById(f).value = '');
  document.getElementById('book-year').value = '';
  document.getElementById('book-patrimony').disabled = false;
  loadBookCategories();
  // Sugerir próximo patrimônio
  const d = await api('/api/books?sort_by=patrimony&sort_order=desc&q=&per_page=1');
  const books = d?.books || d || [];
  if (books.length > 0) {
    const last = parseInt(books[0].patrimony, 10);
    if (!isNaN(last)) document.getElementById('book-patrimony').value = last + 1;
  }
  openModal('modal-book');
}

let booksSearchQuery = '';

async function loadBooks(q='') {
  if (q !== undefined) booksSearchQuery = q;
  const parts = (document.getElementById('books-sort')?.value || 'title_asc').split('_');
  const sortOrder = parts.pop();
  const sortBy = parts.join('_');
  const d = await api(`/api/books?q=${encodeURIComponent(booksSearchQuery)}&sort_by=${sortBy}&sort_order=${sortOrder}`);
  if (!d) return;
  const isAdmin = window.USER_ROLE === 'admin';
  const canDelete = isAdmin || opPerms.can_delete_books;
  const tbody = document.getElementById('books-body');
  const books = d.books || d;
  if (!books.length) { tbody.innerHTML = '<tr><td colspan="7" class="empty"><p>Nenhum livro encontrado</p></td></tr>'; return; }
  tbody.innerHTML = books.map(b => `
    <tr>
      <td><strong>${b.patrimony}</strong></td>
      <td>${b.title}</td>
      <td>${b.author}</td>
      <td>${b.category || '—'}</td>
      <td>${b.location ? `<span style="font-size:.8rem;color:var(--muted)">📍 ${b.location}</span>` : '—'}</td>
      <td><span class="badge ${b.available ? 'available' : 'unavailable'}">${b.available ? 'Disponível' : 'Emprestado'}</span></td>
      <td style="white-space:nowrap">
        <button class="btn btn-secondary btn-sm" onclick='editBook(${b.id})'>Editar</button>
        <button class="btn btn-secondary btn-sm" onclick="printBarcode(${b.id},'${b.patrimony}','${b.title.replace(/'/g,"\\'")}')" title="Imprimir etiqueta" style="padding:5px 8px">🏷️</button>
        ${canDelete ? `<button class="btn btn-danger btn-sm" onclick='deleteBook(${b.id},"${b.title.replace(/'/g,"\\'")}")'>Excluir</button>` : ''}
      </td>
    </tr>`).join('');
  document.getElementById('books-pagination').style.display = 'none';
}

async function deleteBook(id, title) {
  if (!confirm(`Excluir "${title}"? Esta ação não pode ser desfeita.`)) return;
  const r = await api(`/api/books/${id}`, {method: 'DELETE'});
  if (r?.ok) { toast('Livro excluído!', 'success'); loadBooks(booksSearchQuery); }
  else toast(r?.error || 'Erro', 'error');
}

function printBarcode(id, patrimony, title) {
  const win = window.open('', '_blank', 'width=400,height=300');
  win.document.write(`
    <html><head><title>Etiqueta - ${patrimony}</title>
    <style>body{font-family:monospace;text-align:center;padding:20px}img{max-width:100%}p{margin:4px 0;font-size:12px}</style></head>
    <body>
    <img src="/api/books/${id}/barcode" onload="window.print()" onerror="document.body.innerHTML='Erro ao carregar código de barras'">
    <p><strong>${title}</strong></p>
    <p>${patrimony}</p>
    </body></html>
  `);
}

document.getElementById('books-search').addEventListener('input', debounce(e => loadBooks(e.target.value), 300));
document.getElementById('books-sort')?.addEventListener('change', e => { localStorage.setItem('books-sort', e.target.value); });
document.getElementById('barcode-search')?.addEventListener('input', debounce(e => loadBarcodeBooks(e.target.value), 300));
document.getElementById('barcode-sort')?.addEventListener('change', e => loadBarcodeBooks());
document.getElementById('loans-search')?.addEventListener('input', debounce(e => loadLoans(), 300));

async function saveBook() {
  const id = document.getElementById('book-edit-id').value;
  const data = {
    patrimony: document.getElementById('book-patrimony').value.trim().toUpperCase(),
    title: document.getElementById('book-title').value.trim(),
    author: document.getElementById('book-author').value.trim(),
    isbn: document.getElementById('book-isbn').value.trim(),
    category: document.getElementById('book-category').value,
    publisher: document.getElementById('book-publisher').value.trim(),
    year: document.getElementById('book-year').value || null,
    location: document.getElementById('book-location').value.trim(),
    notes: document.getElementById('book-notes').value.trim()
  };
  if (!data.patrimony || !data.title) { toast('Patrimônio e título são obrigatórios', 'error'); return; }
  const url = id ? `/api/books/${id}` : '/api/books';
  const method = id ? 'PUT' : 'POST';
  const r = await api(url, {method: method, body: JSON.stringify(data)});
  if (r?.ok) {
    document.getElementById('book-edit-id').value = '';
    closeModal('modal-book');
    toast(id ? 'Livro atualizado!' : 'Livro cadastrado!', 'success');
    loadBooks(booksSearchQuery);
  } else {
    toast(r?.error || 'Erro ao salvar', 'error');
  }
}

async function editBook(id) {
  const b = await api('/api/books/' + id);
  if (!b) {
    toast('Erro ao carregar dados do livro', 'error');
    return;
  }
  document.getElementById('book-modal-title').textContent = 'Editar Livro';
  document.getElementById('book-edit-id').value = b.id || id;
  document.getElementById('book-patrimony').value = b.patrimony || '';
  document.getElementById('book-patrimony').disabled = false; // Permite editar
  document.getElementById('book-title').value = b.title || '';
  document.getElementById('book-author').value = b.author || '';
  document.getElementById('book-isbn').value = b.isbn || '';
  document.getElementById('book-publisher').value = b.publisher || '';
  document.getElementById('book-year').value = b.year || '';
  document.getElementById('book-location').value = b.location || '';
  document.getElementById('book-notes').value = b.notes || '';
  loadBookCategories(() => {
    const catSel = document.getElementById('book-category');
    if (catSel && b.category) catSel.value = b.category;
  });
  openModal('modal-book');
}

async function loadBookCategories(cb) {
  const cats = await api('/api/categories');
  const sel = document.getElementById('book-category');
  if (!cats) return;
  sel.innerHTML = '<option value="">Selecione...</option>' + cats.map(c => `<option value="${c.name}">${c.name}</option>`).join('');
  if (cb) cb();
}

document.getElementById('modal-book').addEventListener('click', e => {
  if (e.target === document.getElementById('modal-book')) return;
});

// Reset student modal on open
const origOpenModal = window.openModal;
window.openModal = function(id) {
  if (id === 'modal-loan') {
    loanCart = [];
    loanSelectedBookId = null; loanSelectedStudentId = null;
    document.getElementById('loan-scan-input').value = '';
    document.getElementById('loan-book-search').value = '';
    document.getElementById('loan-student-search').value = '';
    document.getElementById('loan-student-results').style.display = 'none';
    document.getElementById('loan-book-results').style.display = 'none';
    document.getElementById('loan-student-selected').style.display = 'none';
    document.getElementById('loan-student-id').value = '';
    document.getElementById('loan-books-section').style.display = 'none';
    document.getElementById('loan-student-loans-section').style.display = 'none';
    document.getElementById('loan-student-active-loans').innerHTML = '<div style="text-align:center;padding:16px;color:var(--muted);font-size:.85rem">Nenhum empréstimo ativo</div>';
    setLoanDaysDefault();
    renderCart();
    // Reset datetime to current when opening (userEdited is cleared in updateDT)
    const dtInput = document.getElementById('loan-datetime');
    if (dtInput) delete dtInput.dataset.userEdited;
  }
  if (id === 'modal-return') {
    returnLoanId = null;
    document.getElementById('return-scan-input').value = '';
    document.getElementById('return-patrimony') && (document.getElementById('return-patrimony').value = '');
    document.getElementById('return-preview').style.display = 'none';
    document.getElementById('return-reservation-alert').style.display = 'none';
    document.getElementById('return-loan-id').value = '';
    document.getElementById('btn-confirm-return').disabled = true;
  }
  if (id === 'modal-user') {
    document.getElementById('user-modal-title').textContent = 'Novo Usuário';
    document.getElementById('user-edit-id').value = '';
    ['user-name','user-email','user-password'].forEach(f => document.getElementById(f).value = '');
    document.getElementById('user-role').value = 'operator';
    document.getElementById('user-email').disabled = false;
  }
  document.getElementById(id).classList.add('open');
  updateDT();
};

// ── STUDENTS ──
async function loadStudents(q='') {
  const activeFilter = document.getElementById('students-active-filter')?.value || 'active';
  const parts = (document.getElementById('students-sort')?.value || 'name_asc').split('_');
  const sortOrder = parts.pop();
  const sortBy = parts.join('_');
  const d = await api('/api/students?q=' + encodeURIComponent(q) + '&active=' + activeFilter + '&sort_by=' + sortBy + '&sort_order=' + sortOrder);
  if (!d) return;
  const isAdmin = window.USER_ROLE === 'admin';
  const canEdit = isAdmin || opPerms.can_edit_students;
  const tbody = document.getElementById('students-body');
  if (!d.length) { tbody.innerHTML = '<tr><td colspan="7" class="empty"><p>Nenhum aluno encontrado</p></td></tr>'; return; }
  tbody.innerHTML = d.map(s => {
    const sit = !s.active ? '<span class="badge" style="background:#e5e7eb;color:#6b7280">Inativo</span>' : (s.has_overdue ? '<span class="badge late"><span class="badge-dot"></span>Pendencia</span>' : '<span class="badge active"><span class="badge-dot"></span>Regular</span>');
    const loans = s.active_loans > 0 ? `<strong>${s.active_loans}</strong> ativo${s.active_loans>1?'s':''}` : '0';
    const toggleBtn = canEdit ? `<button class="btn btn-secondary btn-sm" onclick="toggleStudentActive(${s.id},${!s.active})">${s.active ? 'Desativar' : 'Reativar'}</button>` : '';
    return `<tr>
      <td>${s.name}</td><td>${s.enrollment}</td><td>${s.class_name||'—'}</td>
      <td>${loans}</td><td>${sit}</td>
      <td><button class="btn btn-secondary btn-sm" onclick='editStudent(${JSON.stringify(s)})'>Editar</button>${toggleBtn}</td>
    </tr>`;
  }).join('');
}

async function toggleStudentActive(id, newActive) {
  const status = newActive ? 'reativar' : 'desativar';
  if (!confirm(`Tem certeza que deseja ${status} este aluno?`)) return;
  const r = await api(`/api/students/${id}/toggle-active`, {method: 'POST'});
  if (r?.ok) { toast('Aluno ' + status + 'do!', 'success'); loadStudents(document.getElementById('students-search').value); }
  else toast(r?.error || 'Erro', 'error');
}

async function deleteStudent(id, name) {
  if (!confirm(`Excluir "${name}"? Esta ação não pode ser desfeita.`)) return;
  const r = await api(`/api/students/${id}`, {method: 'DELETE'});
  if (r?.ok) { toast('Aluno excluído!', 'success'); loadStudents(); }
  else toast(r?.error || 'Erro', 'error');
}

document.getElementById('students-search').addEventListener('input', debounce(e => loadStudents(e.target.value), 300));
document.getElementById('students-sort')?.addEventListener('change', e => { localStorage.setItem('students-sort', e.target.value); });

async function saveStudent() {
  const id = document.getElementById('student-edit-id').value;
  const data = {
    name: document.getElementById('student-name').value.trim(),
    enrollment: document.getElementById('student-enrollment').value.trim(),
    class_name: document.getElementById('student-class').value.trim(),
    phone: document.getElementById('student-phone').value.trim(),
    email: document.getElementById('student-email').value.trim(),
    notes: document.getElementById('student-notes').value.trim()
  };
  if (!data.name || !data.enrollment) { toast('Nome e matrícula são obrigatórios', 'error'); return; }
  const url = id ? `/api/students/${id}` : '/api/students';
  const method = id ? 'PUT' : 'POST';
  const r = await api(url, {method, body: JSON.stringify(data)});
  if (r?.ok) {
    document.getElementById('student-edit-id').value = '';
    closeModal('modal-student');
    toast(id ? 'Aluno atualizado!' : 'Aluno cadastrado!', 'success');
    loadStudents();
  } else {
    toast(r?.error || 'Erro ao salvar', 'error');
  }
}

function openNewStudent() {
  document.getElementById('student-modal-title').textContent = 'Cadastrar Novo Aluno';
  document.getElementById('student-edit-id').value = '';
  ['student-name','student-enrollment','student-class','student-phone','student-email','student-notes'].forEach(f => document.getElementById(f).value = '');
  document.getElementById('student-enrollment').disabled = false;
  openModal('modal-student');
}

async function openDeactivateClass() {
  const res = await api('/api/reports/classes');
  if (!res || !res.length) { toast('Nenhuma turma encontrada', 'error'); return; }
  const sel = document.getElementById('deactivate-class-select');
  sel.innerHTML = res.map(c => '<option value="' + c + '">' + c + '</option>').join('');
  openModal('modal-deactivate-class');
}

async function openBatchEditClass() {
  const res = await api('/api/reports/classes');
  if (!res || !res.length) { toast('Nenhuma turma encontrada', 'error'); return; }
  const sel = document.getElementById('batch-edit-class-select');
  sel.innerHTML = '<option value="">— Selecione —</option>' + res.map(c => '<option value="' + c + '">' + c + '</option>').join('');
  document.getElementById('batch-edit-students-wrap').style.display = 'none';
  openModal('modal-batch-edit-class');
}

async function loadBatchEditStudents() {
  const cls = document.getElementById('batch-edit-class-select').value;
  const wrap = document.getElementById('batch-edit-students-wrap');
  const tbody = document.getElementById('batch-edit-students-body');
  if (!cls) { wrap.style.display = 'none'; return; }
  const students = await api('/api/students/by-class/' + encodeURIComponent(cls));
  if (!students || !students.length) {
    tbody.innerHTML = '<tr><td colspan="5" style="padding:16px;text-align:center;color:var(--muted)">Nenhum aluno ativo nesta turma</td></tr>';
  } else {
    tbody.innerHTML = students.map(s =>
      '<tr class="batch-edit-row"><td style="padding:6px 8px;border-bottom:1px solid var(--border)">' + s.name + '</td>' +
      '<td style="padding:6px 8px;border-bottom:1px solid var(--border)">' + s.enrollment + '</td>' +
      '<td style="padding:6px 8px;border-bottom:1px solid var(--border)">' + s.class_name + '</td>' +
      '<td style="padding:6px 8px;border-bottom:1px solid var(--border)"><input type="text" class="batch-new-class" data-id="' + s.id + '" style="width:120px;padding:4px 6px;border-radius:4px;border:1px solid var(--border);font-size:.85rem" placeholder="' + s.class_name + '"></td>' +
      '<td style="padding:6px 8px;border-bottom:1px solid var(--border);text-align:center"><input type="checkbox" class="batch-inactive" style="width:18px;height:18px;cursor:pointer"></td></tr>'
    ).join('');
  }
  wrap.style.display = 'block';
}

async function saveBatchEditClass() {
  const changes = [];
  document.querySelectorAll('.batch-edit-row').forEach(row => {
    const inp = row.querySelector('.batch-new-class');
    const chk = row.querySelector('.batch-inactive');
    const newClass = inp.value.trim();
    const inactive = chk.checked;
    if (newClass || inactive) changes.push({id: parseInt(inp.dataset.id), class_name: newClass, inactive});
  });
  if (!changes.length) { toast('Nenhuma alteracao para salvar', 'error'); return; }
  closeModal('modal-batch-edit-class');
  const r = await api('/api/students/batch-update-class', {method:'POST', body:JSON.stringify({changes})});
  if (r?.ok) {
    toast(r.count + ' alunos atualizados!', 'success');
    loadStudents(document.getElementById('students-search').value);
  }
}

async function confirmDeactivateClass() {
  const cls = document.getElementById('deactivate-class-select').value;
  if (!cls) return;
  closeModal('modal-deactivate-class');
  if (!confirm('Tem certeza que deseja desativar TODOS os alunos da turma ' + cls + '?\n\nIsso não exclui os alunos, apenas os marca como inativos.\nEles continuarão no histórico de empréstimos.')) return;
  const r = await api('/api/students/deactivate-class', {method:'POST', body:JSON.stringify({class_name: cls})});
  if (r?.ok) {
    toast(r.count + ' alunos da turma ' + cls + ' foram desativados!', 'success');
    loadStudents(document.getElementById('students-search').value);
  }
}

function editStudent(s) {
  document.getElementById('student-modal-title').textContent = 'Editar Aluno';
  document.getElementById('student-edit-id').value = s.id;
  document.getElementById('student-name').value = s.name;
  document.getElementById('student-enrollment').value = s.enrollment;
  document.getElementById('student-enrollment').disabled = false;
  document.getElementById('student-class').value = s.class_name;
  document.getElementById('student-phone').value = s.phone;
  document.getElementById('student-email').value = s.email;
  document.getElementById('student-notes').value = s.notes;
  openModal('modal-student');
}

// ── LOANS ──
let loanCart = []; // Carrinho de empréstimos: [{id, title, patrimony}]

async function loadLoans() {
  const status = document.getElementById('loans-filter').value;
  const q = document.getElementById('loans-search')?.value?.trim() || '';
  const params = new URLSearchParams({status});
  if (q) params.set('q', q);
  const d = await api('/api/loans?' + params.toString());
  if (!d) return;
  const tbody = document.getElementById('loans-body');
  if (!d.length) { tbody.innerHTML = '<tr><td colspan="9" class="empty"><p>Nenhum empréstimo encontrado</p></td></tr>'; return; }
  tbody.innerHTML = d.map(l => `
    <tr>
      <td>${l.student_name}</td>
      <td>${l.student_class||'—'}</td>
      <td>${l.book_title}</td>
      <td><strong>${l.book_patrimony}</strong></td>
      <td>${l.borrowed_at}</td>
      <td>${l.due_date}${l.is_overdue ? ` <span style="color:var(--danger);font-size:.72rem">(${l.days_overdue}d atraso)</span>` : ''}${l.renewed > 0 ? ` <span style="color:var(--muted);font-size:.72rem">(${l.renewed}x renovado)</span>` : ''}</td>
      <td>${statusBadge(l)}</td>
      <td>${l.reservation_count > 0 ? '<span style="color:var(--warning);font-weight:600;font-size:.78rem">📌 ' + l.reservation_count + '</span>' : '<span style="color:var(--muted);font-size:.78rem">—</span>'}</td>
      <td style="display:flex;gap:4px;flex-wrap:wrap">
        ${!l.returned ? `<button class="btn btn-secondary btn-sm" onclick="quickReturn(${l.id})">Devolver</button>` : ''}
        ${!l.returned ? `<button class="btn btn-sm" style="background:var(--warning);color:#000" onclick="renewLoan(${l.id})">Renovar</button>` : ''}
      </td>
    </tr>`).join('');
}

async function quickReturn(loanId) {
  const r = await api(`/api/loans/${loanId}/return`, {method:'POST'});
  if (r?.ok) {
    if (r.has_reservation && r.reservation) {
      toast(`✅ Devolução! 📌 Reservado por ${r.reservation.student_name}`, 'success');
    } else {
      toast('Devolução registrada!', 'success');
    }
    loadLoans(); loadDashboard(); loadActiveReservations();
  }
  else toast(r?.error || 'Erro', 'error');
}

async function renewLoan(loanId) {
  if (!confirm('Renovar este empréstimo?')) return;
  const r = await api(`/api/loans/${loanId}/renew`, {method:'POST'});
  if (r?.ok) { toast(`Renovado! Nova devolução: ${r.loan.due_date}`, 'success'); loadLoans(); loadDashboard(); }
  else toast(r?.error || 'Erro', 'error');
}

// ── CARRINHO DE EMPRÉSTIMOS ──
function addToCart(bookId, title, patrimony) {
  if (loanCart.find(b => b.id === bookId)) { toast('Livro já adicionado!', 'error'); return; }
  loanCart.push({id: bookId, title, patrimony});
  renderCart();
  // Limpar busca
  document.getElementById('loan-book-search').value = '';
  document.getElementById('loan-book-results').style.display = 'none';
  document.getElementById('loan-scan-input').value = '';
  toast(`"${title}" adicionado ao carrinho`, 'success');
}

function removeFromCart(bookId) {
  loanCart = loanCart.filter(b => b.id !== bookId);
  renderCart();
}

function renderCart() {
  const list = document.getElementById('loan-cart-list');
  const count = document.getElementById('loan-cart-count');
  const btn = document.getElementById('btn-finalize-loans');
  count.textContent = loanCart.length;
  btn.disabled = loanCart.length === 0;
  
  if (loanCart.length === 0) {
    list.innerHTML = '<div style="text-align:center;padding:20px;color:var(--muted);font-size:.85rem">Nenhum livro adicionado</div>';
    return;
  }
  
  list.innerHTML = loanCart.map(b => `
    <div style="display:flex;justify-content:space-between;align-items:center;padding:6px 8px;border-bottom:1px solid #eee;font-size:.9rem">
      <div><strong>${b.title}</strong> <span style="color:var(--muted)">(${b.patrimony})</span></div>
      <button onclick="removeFromCart(${b.id})" style="background:none;border:none;color:var(--danger);cursor:pointer;font-size:1.2rem;padding:0 4px">×</button>
    </div>`).join('');
}

// Scanner adiciona direto ao carrinho
document.getElementById('loan-scan-input').addEventListener('change', async function() {
  const val = this.value.trim().toUpperCase();
  if (!val || !loanSelectedStudentId) { toast('Selecione um aluno primeiro!', 'error'); this.value = ''; return; }
  const d = await api('/api/books/by-patrimony/' + encodeURIComponent(val));
  if (d?.error) { toast(d.error, 'error'); }
  else if (d) {
    if (!d.available) { toast(`Livro "${d.title}" já está emprestado`, 'error'); }
    else { addToCart(d.id, d.title, d.patrimony); }
  }
  this.value = '';
});

// Busca manual de livros no carrinho
let bookSearchTimeout;
document.getElementById('loan-book-search').addEventListener('input', function() {
  clearTimeout(bookSearchTimeout);
  bookSearchTimeout = setTimeout(async () => {
    const q = this.value.trim();
    if (q.length < 2) { document.getElementById('loan-book-results').style.display='none'; return; }
    const books = await api('/api/books/search?q=' + encodeURIComponent(q) + '&limit=30');
    const res = document.getElementById('loan-book-results');
    if (!books?.length) { res.style.display='none'; return; }
    res.innerHTML = books.filter(b => !loanCart.find(c => c.id === b.id)).map(b => {
      if (b.available) {
        return `<div class="search-result-item" onclick="addToCart(${b.id},'${b.title.replace(/'/g,"\\'")}','${b.patrimony}')">
          <strong>${b.title}</strong><span>${b.patrimony} · ${b.author} <span style="color:var(--accent)">+ Adicionar</span></span>
        </div>`;
      } else {
        return `<div class="search-result-item" onclick="reserveBook(${b.id},'${b.title.replace(/'/g,"\\'")}','${b.patrimony}')">
          <strong>${b.title}</strong><span>${b.patrimony} · Emprestado <span style="color:var(--warning)">📌 Reservar</span></span>
        </div>`;
      }
    }).join('') || '<div style="padding:10px 14px;font-size:.82rem;color:var(--muted)">Nenhum livro encontrado</div>';
    res.style.display = 'block';
  }, 250);
});

async function reserveBook(bookId, title, patrimony) {
  if (!loanSelectedStudentId) { toast('Selecione um aluno primeiro!', 'error'); return; }
  const r = await api('/api/reservations', {method:'POST', body: JSON.stringify({book_id: bookId, student_id: loanSelectedStudentId})});
  if (r?.ok) {
    toast(`Reserva criada para "${title}"`, 'success');
    loadActiveReservations();
    updateReservationBadge();
  }
  else toast(r?.error || 'Erro', 'error');
}

// Busca de aluno no carrinho
let studentSearchTimeout;
document.getElementById('loan-student-search').addEventListener('input', function() {
  clearTimeout(studentSearchTimeout);
  studentSearchTimeout = setTimeout(async () => {
    const q = this.value.trim();
    if (q.length < 2) { document.getElementById('loan-student-results').style.display='none'; return; }
    const d = await api('/api/students?q=' + encodeURIComponent(q));
    const students = d || [];
    const res = document.getElementById('loan-student-results');
    if (!students?.length) { res.style.display='none'; return; }
    res.innerHTML = students.map(s =>
      `<div class="search-result-item" onclick="selectLoanStudent(${s.id},'${s.name.replace(/'/g,"\\'")}','${s.enrollment}',${s.has_overdue})">
        <strong>${s.name}</strong><span>${s.enrollment} · ${s.class_name||''} ${s.has_overdue ? '⚠ Pendência' : ''}</span>
      </div>`).join('');
    res.style.display = 'block';
  }, 250);
});

function selectLoanStudent(id, name, enrollment, hasOverdue) {
  loanSelectedStudentId = id;
  document.getElementById('loan-student-id').value = id;
  document.getElementById('loan-student-search').value = `${name} (${enrollment})`;
  document.getElementById('loan-student-results').style.display = 'none';
  document.getElementById('loan-student-selected').style.display = 'block';
  document.getElementById('loan-student-selected-name').textContent = `${name} (${enrollment})`;
  document.getElementById('loan-books-section').style.display = 'block';
  document.getElementById('loan-student-loans-section').style.display = 'block';
  if (hasOverdue) toast(`⚠ Aluno "${name}" tem pendência em aberto!`, 'error');
  loadStudentActiveLoans(id);
  document.getElementById('loan-scan-input').focus();
}

async function loadStudentActiveLoans(studentId) {
  const allLoans = await api('/api/loans?status=active');
  const studentLoans = (allLoans || []).filter(l => l.student_id === studentId && !l.returned);
  const container = document.getElementById('loan-student-active-loans');
  if (studentLoans.length === 0) {
    container.innerHTML = '<div style="text-align:center;padding:16px;color:var(--muted);font-size:.85rem">Nenhum empréstimo ativo</div>';
    return;
  }
  container.innerHTML = studentLoans.map(l => `
    <div style="display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid #eee;font-size:.85rem">
      <input type="checkbox" id="loan-check-${l.id}" data-loan-id="${l.id}" style="width:16px;height:16px;cursor:pointer">
      <div style="flex:1">
        <strong>${l.book_title}</strong> <span style="color:var(--muted)">(${l.book_patrimony})</span>
        <div style="color:var(--muted);font-size:.78rem">Devolução: ${l.due_date}${l.renewed > 0 ? ` — ${l.renewed}x renovado` : ''}</div>
      </div>
    </div>`).join('');
}

async function loadActiveReservations() {
  const reservations = await api('/api/reservations');
  const resBadge = document.getElementById('reservation-badge');
  if (reservations && reservations.length > 0) {
    resBadge.textContent = reservations.length;
    resBadge.style.display = '';
  } else {
    resBadge.style.display = 'none';
  }
}

async function cancelReservation(resId, bookTitle) {
  if (!confirm(`Cancelar reserva de "${bookTitle}"?`)) return;
  const r = await api(`/api/reservations/${resId}`, {method:'DELETE'});
  if (r?.ok) {
    toast('Reserva cancelada', 'success');
    loadActiveReservations();
    loadDashboard();
    updateReservationBadge();
  }
  else toast(r?.error || 'Erro', 'error');
}

async function batchReturnSelected() {
  const checks = document.querySelectorAll('#loan-student-active-loans input[type="checkbox"]:checked');
  if (checks.length === 0) { toast('Selecione pelo menos um livro!', 'error'); return; }
  let successCount = 0;
  let reservedBooks = [];
  for (const check of checks) {
    const loanId = check.dataset.loanId;
    const r = await api(`/api/loans/${loanId}/return`, {method:'POST'});
    if (r?.ok) {
      successCount++;
      if (r.has_reservation && r.reservation) {
        reservedBooks.push(`${r.reservation.student_name}`);
      }
    }
  }
  if (successCount > 0) {
    let msg = `${successCount} livro(s) devolvido(s)!`;
    if (reservedBooks.length > 0) {
      msg += ` 📌 Reservas: ${reservedBooks.join(', ')}`;
    }
    toast(msg, 'success');
    loadStudentActiveLoans(loanSelectedStudentId);
    loadDashboard();
    loadLoans();
    loadActiveReservations();
  }
}

async function batchRenewSelected() {
  const checks = document.querySelectorAll('#loan-student-active-loans input[type="checkbox"]:checked');
  if (checks.length === 0) { toast('Selecione pelo menos um livro!', 'error'); return; }
  const loanIds = Array.from(checks).map(c => parseInt(c.dataset.loanId));
  const r = await api('/api/loans/batch-renew', {method:'POST', body: JSON.stringify({loan_ids: loanIds})});
  if (r?.ok) {
    const renewed = r.success?.length || 0;
    const errs = r.errors?.length || 0;
    toast(`${renewed} renovado(s)${errs > 0 ? `, ${errs} erro(s)` : ''}`, renewed > 0 ? 'success' : 'error');
    loadStudentActiveLoans(loanSelectedStudentId);
    loadDashboard();
    loadLoans();
  } else {
    toast(r?.error || 'Erro', 'error');
  }
}

function clearLoanStudent() {
  loanSelectedStudentId = null;
  document.getElementById('loan-student-id').value = '';
  document.getElementById('loan-student-search').value = '';
  document.getElementById('loan-student-selected').style.display = 'none';
  document.getElementById('loan-books-section').style.display = 'none';
  document.getElementById('loan-student-loans-section').style.display = 'none';
  loanCart = [];
  renderCart();
}

function setLoanMode(mode, btn) {
  btn.parentElement.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('loan-scanner-div').style.display = mode==='scanner' ? '' : 'none';
  document.getElementById('loan-manual-div').style.display = mode==='manual' ? '' : 'none';
  if (mode==='scanner') setTimeout(() => document.getElementById('loan-scan-input').focus(), 100);
}

function getBorrowedDate() {
  const dt = document.getElementById('loan-datetime')?.value;
  if (dt) {
    const parts = dt.split('T');
    const d = parts[0].split('-');
    const t = (parts[1] || '00:00').split(':');
    return new Date(+d[0], +d[1] - 1, +d[2], +t[0], +t[1]);
  }
  return new Date();
}

function recalcDueDate() {
  const days = loanSelectedDays || institutionLoanDays || 14;
  const base = getBorrowedDate();
  const due = new Date(base); due.setDate(due.getDate() + days);
  document.getElementById('loan-due-date').value = due.toISOString().split('T')[0];
}

function setLoanDays(days, btn) {
  loanSelectedDays = days;
  btn.closest('.days-toggle').querySelectorAll('.day-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  recalcDueDate();
}

function setLoanDaysDefault() {
  loanSelectedDays = institutionLoanDays;
  document.querySelectorAll('#loan-days-toggle .day-btn').forEach(b => {
    const days = parseInt(b.textContent);
    b.classList.toggle('active', days === institutionLoanDays);
  });
  recalcDueDate();
}

// Recalcular data de devolução quando usuario alterar data do emprestimo
document.addEventListener('input', function(e) {
  if (e.target.id === 'loan-datetime') {
    e.target.dataset.userEdited = 'true';
    recalcDueDate();
  }
});

async function fetchLoanDaysDefault() {
  const d = await api('/api/institution/loan-days');
  if (d) {
    institutionLoanDays = d.loan_days_default || 14;
  }
}

async function saveBatchLoans() {
  if (!loanSelectedStudentId || loanCart.length === 0) { toast('Selecione aluno e livros', 'error'); return; }
  const dueDate = document.getElementById('loan-due-date').value;
  const btn = document.getElementById('btn-finalize-loans');
  btn.disabled = true; btn.textContent = 'Registrando...';
  
  const dtInput = document.getElementById('loan-datetime');
  const borrowedAt = dtInput ? dtInput.value.replace('T', ' ') + ':00' : '';

  const r = await api('/api/loans/batch', {
    method: 'POST',
    body: JSON.stringify({
      student_id: loanSelectedStudentId,
      book_ids: loanCart.map(b => b.id),
      due_date: dueDate,
      borrowed_at: borrowedAt
    })
  });
  
  if (r?.ok) {
    const res = r.result;
    toast(`✅ ${res.total} empréstimo(s) registrado(s)!`, 'success');
    if (res.errors.length) { toast(`Erros: ${res.errors.join('; ')}`, 'error'); }
    loanCart = [];
    renderCart();
    clearLoanStudent();
    closeModal('modal-loan');
    loadLoans(); loadDashboard();
  } else {
    toast(r?.error || 'Erro ao registrar empréstimos', 'error');
  }
  btn.disabled = false; btn.textContent = '✅ Finalizar Empréstimos';
}

// ── RETURN MODAL ──
document.getElementById('return-scan-input').addEventListener('change', async function() {
  const patrimony = this.value.trim().toUpperCase();
  if (!patrimony) return;
  const d = await api('/api/loans/lookup-patrimony/' + encodeURIComponent(patrimony));
  if (d?.error) {
    toast(d.error, 'error');
  } else if (d) {
    const r = await api(`/api/loans/${d.id}/return`, {method:'POST'});
    if (r?.ok) {
      if (r.has_reservation && r.reservation) {
        toast(`✅ Devolução! 📌 Reservado por ${r.reservation.student_name}`, 'success');
      } else {
        toast('Devolução registrada!', 'success');
      }
      loadLoans(); loadDashboard(); loadActiveReservations();
    } else {
      toast(r?.error || 'Erro', 'error');
    }
  }
  this.value = '';
});

async function lookupReturn() {
  const val = document.getElementById('return-patrimony').value.trim().toUpperCase();
  await lookupReturnByPatrimony(val);
}

async function lookupReturnByPatrimony(patrimony) {
  if (!patrimony) return;
  const d = await api('/api/loans/lookup-patrimony/' + encodeURIComponent(patrimony));
  const preview = document.getElementById('return-preview');
  const alertDiv = document.getElementById('return-reservation-alert');
  if (d?.error) {
    preview.innerHTML = `<span style="color:var(--danger)">âš  ${d.error}</span>`;
    preview.style.display = 'block';
    alertDiv.style.display = 'none';
    document.getElementById('btn-confirm-return').disabled = true;
    returnLoanId = null;
  } else if (d) {
    returnLoanId = d.id;
    document.getElementById('return-loan-id').value = d.id;
    const overdueTxt = d.is_overdue ? `<span style="color:var(--danger)">âš  ${d.days_overdue} dia(s) em atraso</span>` : '<span style="color:var(--success)">No prazo</span>';
    preview.innerHTML = `<table>
      <tr><td>Livro:</td><td>${d.book_title} (${d.book_patrimony})</td></tr>
      <tr><td>Aluno:</td><td>${d.student_name} · ${d.student_class||''}</td></tr>
      <tr><td>Retirada:</td><td>${d.borrowed_at}</td></tr>
      <tr><td>Previsto:</td><td>${d.due_date}</td></tr>
      <tr><td>Situação:</td><td>${overdueTxt}</td></tr>
    </table>`;
    preview.style.display = 'block';
    document.getElementById('btn-confirm-return').disabled = false;
    
    const reservations = await api('/api/reservations?book_id=' + d.book_id);
    if (reservations && reservations.length > 0) {
      const first = reservations[0];
      alertDiv.innerHTML = `<strong>📌 ATENÇÃO:</strong> Este livro está reservado por <strong>${first.student_name}</strong> (${first.student_enrollment}).<br>Após a devolução, o aluno deverá ser notificado.`;
      alertDiv.style.display = 'block';
    } else {
      alertDiv.style.display = 'none';
    }
  }
}

function setReturnMode(mode, btn) {
  btn.parentElement.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('return-scanner-div').style.display = mode==='scanner' ? '' : 'none';
  document.getElementById('return-manual-div').style.display = mode==='manual' ? '' : 'none';
  if (mode==='scanner') setTimeout(() => document.getElementById('return-scan-input').focus(), 100);
}

async function confirmReturn() {
  if (!returnLoanId) return;
  const r = await api(`/api/loans/${returnLoanId}/return`, {method:'POST'});
  if (r?.ok) {
    closeModal('modal-return');
    if (r.has_reservation && r.reservation) {
      toast(`✅ Devolução! 📌 Reservado por ${r.reservation.student_name}`, 'success');
    } else {
      toast('Devolução registrada!', 'success');
    }
    loadLoans(); loadDashboard(); loadActiveReservations();
  } else toast(r?.error || 'Erro', 'error');
}

// ── GLOBAL SEARCH ──
let searchTimeout;
document.getElementById('global-search').addEventListener('input', function() {
  clearTimeout(searchTimeout);
  const q = this.value.trim();
  const res = document.getElementById('search-results');
  if (q.length < 2) { res.classList.remove('open'); return; }
  searchTimeout = setTimeout(async () => {
    const d = await api('/api/search?q=' + encodeURIComponent(q));
    if (!d) return;
    let html = '';
    if (d.books?.length) {
      html += '<div class="search-group-title">Livros</div>';
      html += d.books.map(b => `<div class="search-result-item" onclick="navigate('books')"><strong>${b.title}</strong><span>${b.patrimony} · ${b.author}</span></div>`).join('');
    }
    if (d.students?.length) {
      html += '<div class="search-group-title">Alunos</div>';
      html += d.students.map(s => `<div class="search-result-item" onclick="navigate('students')"><strong>${s.name}</strong><span>${s.enrollment} · ${s.class_name}</span></div>`).join('');
    }
    if (!html) html = '<div style="padding:12px 14px;font-size:.82rem;color:var(--muted)">Nenhum resultado</div>';
    res.innerHTML = html;
    res.classList.add('open');
  }, 250);
});
document.addEventListener('click', e => {
  if (!e.target.closest('.search-bar')) document.getElementById('search-results').classList.remove('open');
});

// ── REPORTS ──
async function showReportFilters(type) {
  currentReportType = type;
  const titles = {
    'active-loans':'Empréstimos Ativos','overdue':'Livros em Atraso',
    'student-history':'Histórico por Aluno','movement':'Movimentação por Período',
    'inventory':'Acervo Completo','most-borrowed':'Mais Emprestados',
    'student-ranking':'Ranking de Alunos (Premiação)','class-ranking':'Ranking de Turmas',
    'reservations':'Reservas de Livros'
  };
  document.getElementById('report-filter-title').textContent = titles[type];

  const [classes, cats, students] = await Promise.all([
    api('/api/reports/classes'), api('/api/reports/categories'), api('/api/students?active=all')
  ]);

  let html = '';
  if (['active-loans','overdue','student-history'].includes(type)) {
    html += `<div class="filter-group"><label>Turma</label><select id="rf-class"><option value="">Todas</option>${(classes||[]).map(c=>`<option>${c}</option>`).join('')}</select></div>`;
  }
  if (type === 'student-history') {
    html += `<div class="filter-group"><label>Aluno</label><select id="rf-student"><option value="">Selecione...</option>${(students||[]).map(s=>`<option value="${s.id}">${s.name} (${s.enrollment})</option>`).join('')}</select></div>`;
  }
  if (['student-history','movement','most-borrowed'].includes(type)) {
    html += `<div class="filter-group"><label>Data Inicio</label><input type="date" id="rf-from"></div>`;
    html += `<div class="filter-group"><label>Data Fim</label><input type="date" id="rf-to"></div>`;
  }
  if (type === 'movement') {
    html += `<div class="filter-group"><label>Tipo</label><select id="rf-type"><option value="all">Todos</option><option value="borrows">Empréstimos</option><option value="returns">Devoluções</option></select></div>`;
  }
  if (['inventory','most-borrowed'].includes(type)) {
    html += `<div class="filter-group"><label>Categoria</label><select id="rf-cat"><option value="">Todas</option>${(cats||[]).map(c=>`<option>${c}</option>`).join('')}</select></div>`;
  }
  if (type === 'inventory') {
    html += `<div class="filter-group"><label>Status</label><select id="rf-status"><option value="">Todos</option><option value="available">Disponivel</option><option value="borrowed">Emprestado</option></select></div>`;
  }
  // Ranking de alunos — filtros independentes
  if (type === 'student-ranking') {
    html += `<div class="filter-group"><label>Aluno (opcional)</label><select id="rf-student-rank"><option value="">Todos os alunos</option>${(students||[]).map(s=>`<option value="${s.id}">${s.name} (${s.enrollment})</option>`).join('')}</select></div>`;
    html += `<div class="filter-group"><label>Turma (opcional)</label><select id="rf-class-rank"><option value="">Todas as turmas</option>${(classes||[]).map(c=>`<option>${c}</option>`).join('')}</select></div>`;
    html += `<div class="filter-group"><label>Período — Início</label><input type="date" id="rf-from"></div>`;
    html += `<div class="filter-group"><label>Período — Fim</label><input type="date" id="rf-to"></div>`;
    html += `<div class="filter-group"><label title="Mostrar apenas alunos com pelo menos X livros emprestados no período. Use 0 para mostrar todos.">Mín. livros lidos ⓘ</label><input type="number" id="rf-min-loans" min="0" value="0" style="width:80px" title="Filtro para premiação: ex: 5 = mostrar apenas alunos que leram 5 ou mais livros"></div>`;
  }
  // Ranking de turmas
  if (type === 'class-ranking') {
    html += `<div class="filter-group"><label>Data Inicio</label><input type="date" id="rf-from"></div>`;
    html += `<div class="filter-group"><label>Data Fim</label><input type="date" id="rf-to"></div>`;
  }
  if (type === 'reservations') {
    html += `<div class="filter-group"><label>Status</label><select id="rf-res-status"><option value="active">Ativas</option><option value="fulfilled">Atendidas</option><option value="cancelled">Canceladas</option><option value="all">Todas</option></select></div>`;
  }

  document.getElementById('report-filter-row').innerHTML = html;
  document.getElementById('report-filter-panel').style.display = '';
  document.getElementById('report-print-panel').style.display = 'none';
  document.getElementById('report-filter-panel').scrollIntoView({behavior:'smooth'});
}

async function runReport() {
  const g = id => document.getElementById(id)?.value || '';
  const params = new URLSearchParams();
  if (g('rf-class')) params.set('class_name', g('rf-class'));
  if (g('rf-class-rank')) params.set('class_name', g('rf-class-rank'));
  if (g('rf-student')) params.set('student_id', g('rf-student'));
  if (g('rf-student-rank')) params.set('student_id', g('rf-student-rank'));
  if (g('rf-from')) params.set('date_from', g('rf-from'));
  if (g('rf-to')) params.set('date_to', g('rf-to'));
  if (g('rf-type')) params.set('type', g('rf-type'));
  if (g('rf-cat')) params.set('category', g('rf-cat'));
  if (g('rf-status')) params.set('status', g('rf-status'));
  if (g('rf-res-status')) params.set('status', g('rf-res-status'));
  if (g('rf-min-loans')) params.set('min_loans', g('rf-min-loans'));

  const urlMap = {
    'active-loans': '/api/reports/active-loans',
    'overdue': '/api/reports/overdue',
    'student-history': '/api/reports/student-history',
    'movement': '/api/reports/movement',
    'inventory': '/api/reports/inventory',
    'most-borrowed': '/api/reports/most-borrowed',
    'student-ranking': '/api/reports/student-ranking',
    'class-ranking': '/api/reports/class-ranking',
    'reservations': '/api/reports/reservations'
  };

  const url = `${urlMap[currentReportType]}?${params}`;

  try {
    const d = await api(url);
    if (!d) return; // api() já mostra toast de erro e trata license_inactive

    if (d?.error) { toast(d.error, 'error'); return; }

    const inst = await api('/api/institution');

    const subtitles = {
    'active-loans':'Empréstimos Ativos','overdue':'Livros em Atraso',
    'student-history':'Histórico por Aluno','movement':'Movimentação por Período',
    'inventory':'Acervo Completo','most-borrowed':'Livros Mais Emprestados',
      'student-ranking':'Ranking de Alunos','class-ranking':'Ranking de Turmas',
      'reservations':'Reservas de Livros'
    };

    const g2 = id => document.getElementById(id)?.value || '';
    const reportTitle = subtitles[currentReportType];
    const generatedAt = `Gerado em ${new Date().toLocaleDateString('pt-BR')} ${new Date().toLocaleTimeString('pt-BR')}`;

    const logoUrl = inst?.logo_path ? `/api/institution/logo-file?t=${Date.now()}` : '';
    
    const details = [];
    if (inst?.cnpj) details.push(`CNPJ: ${inst.cnpj}`);
    if (inst?.address) details.push(inst.address);
    
    const contacts = [];
    if (inst?.phone) contacts.push(`Tel: ${inst.phone}`);
    if (inst?.email) contacts.push(`Email: ${inst.email}`);
    
    const headerHtml = `
    <div class="header-box">
      ${logoUrl ? `<img src="${logoUrl}" style="max-height:35px;max-width:70px;object-fit:contain;flex-shrink:0">` : ''}
      <div class="info">
        <h2 style="margin:0 0 1px 0;">${inst?.name || 'Biblioteca'}</h2>
        ${details.length ? `<p style="margin:0 0 1px 0;font-size:10px">${details.join(' | ')}</p>` : ''}
        ${contacts.length ? `<p style="margin:0;font-size:10px">${contacts.join(' | ')}</p>` : ''}
      </div>
    </div>`;

    const periodText = g2('rf-from') && g2('rf-to') ? `Período: ${g2('rf-from')} a ${g2('rf-to')}` : 'Todos os períodos';

    const printStyle = `<style>
      #print-content { font-family: Arial, sans-serif; }
      #print-content table { width:100%; border-collapse:collapse; font-size:9px; margin-top:4px; }
      #print-content th { padding:2px 5px; text-align:left; font-size:9px; white-space:normal; border-bottom:1px solid #333; font-weight:bold; color:#333; }
      #print-content td { padding:2px 5px; font-size:9px; white-space:normal; word-wrap:break-word; overflow-wrap:break-word; }
      #print-content p { margin:2px 0; font-size:9px; }
      #print-content h2 { font-size:11px; margin:0; }
      #print-content h3 { font-size:9px; margin:2px 0 1px; }
      #print-content img { max-height:35px; max-width:70px; object-fit:contain; }
      #print-content .header-box { display:flex; align-items:center; gap:10px; margin-bottom:4px; padding-bottom:3px; border-bottom:1px solid #333; }
      #print-content .header-box .info { flex:1; }
    </style>`;
    
    document.getElementById('print-content').innerHTML = printStyle + `<div>${headerHtml}${buildReportTable(currentReportType, d, periodText)}</div>`;
    document.getElementById('report-print-panel').style.display = '';
    document.getElementById('report-print-panel').scrollIntoView({behavior:'smooth'});
  } catch(e) {
    toast('Erro ao gerar relatorio: ' + e.message, 'error');
  }
}


function buildReportTable(type, data, periodText) {
  const reportNames = {
    'active-loans':'Empréstimos Ativos','overdue':'Livros em Atraso',
    'student-history':'Histórico por Aluno','movement':'Movimentação por Período',
    'inventory':'Acervo Completo','most-borrowed':'Livros Mais Emprestados',
    'student-ranking':'Ranking de Alunos','class-ranking':'Ranking de Turmas',
    'reservations':'Reservas de Livros'
  };
  const titleLine = `<p style="font-size:10px;margin-bottom:6px"><strong>${reportNames[type]||type}</strong>${periodText !== 'Todos os períodos' ? ` | ${periodText}` : ''}</p>`;

  if (!data || (Array.isArray(data) && !data.length) || (data.loans && !data.loans.length)) {
    return titleLine + '<p style="color:var(--muted);font-size:9px;margin-top:6px">Nenhum resultado encontrado.</p>';
  }
  if (type === 'student-history') {
    const s = data.student;
    let activeTag = !s.active ? ' <span style="color:#ef4444;font-weight:600">(Inativo)</span>' : '';
    let html = titleLine;
    html += `<p style="font-size:9px;margin-bottom:6px"><strong>Aluno:</strong> <strong>${s.name}</strong>${activeTag} | Matrícula: ${s.enrollment} | Turma: ${s.class_name||'—'}</p>`;
    html += loanTable(data.loans);
    html += `<p style="margin-top:6px;font-size:9px;color:var(--muted)">Total: ${data.total} | Ativos: ${data.active} | Devolvidos: ${data.returned}</p>`;
    return html;
  }
  if (type === 'inventory') {
    return titleLine + `<table><thead><tr><th>Patrimônio</th><th>Título</th><th>Autor</th><th>Categoria</th><th>Localização</th><th>Status</th></tr></thead><tbody>
      ${data.map(b=>`<tr><td>${b.patrimony}</td><td>${b.title}</td><td>${b.author}</td><td>${b.category||'—'}</td><td>${b.location||'—'}</td><td>${b.available?'Disponível':'Emprestado'}</td></tr>`).join('')}
    </tbody></table><p style="font-size:9px;color:var(--muted);margin-top:4px">Total: ${data.length} livros</p>`;
  }
  if (type === 'most-borrowed') {
    return titleLine + `<table><thead><tr><th>#</th><th>Patrimônio</th><th>Título</th><th>Autor</th><th>Categoria</th><th>Empréstimos</th></tr></thead><tbody>
      ${data.map((b,i)=>`<tr><td>${i+1}</td><td>${b.patrimony||'—'}</td><td>${b.title}</td><td>${b.author}</td><td>${b.category||'—'}</td><td><strong>${b.total_loans}</strong></td></tr>`).join('')}
    </tbody></table><p style="font-size:9px;color:var(--muted);margin-top:4px">Total: ${data.length} livro(s) — ${data.reduce((a,b)=>a+b.total_loans,0)} empréstimo(s)</p>`;
  }
  if (type === 'movement') {
    return titleLine + `<table><thead><tr><th>Tipo</th><th>Aluno</th><th>Livro</th><th>Patrimônio</th><th>Data/Hora</th></tr></thead><tbody>
      ${data.map(l=>`<tr><td>${l.event}</td><td>${l.student_name}</td><td>${l.book_title}</td><td>${l.book_patrimony}</td><td>${l.event_at}</td></tr>`).join('')}
    </tbody></table><p style="font-size:9px;color:var(--muted);margin-top:4px">Total: ${data.length} registros</p>`;
  }
  if (type === 'student-ranking') {
    if (!data.length) return titleLine + '<p style="color:var(--muted);font-size:9px;margin-top:6px">Nenhum aluno encontrado.</p>';
    return titleLine + `
      <table><thead><tr><th>#</th><th>Aluno</th><th>Matrícula</th><th>Turma</th><th>Livros Lidos</th><th>Primeiro</th><th>Último</th></tr></thead><tbody>
        ${data.map((s,i)=>`<tr>
          <td><strong>${i+1}</strong></td>
          <td><strong>${s.name}</strong></td>
          <td>${s.enrollment}</td>
          <td>${s.class_name||'—'}</td>
          <td><strong style="color:var(--accent)">${s.total_loans}</strong></td>
          <td>${s.first_loan ? s.first_loan.split(' ')[0] : '—'}</td>
          <td>${s.last_loan ? s.last_loan.split(' ')[0] : '—'}</td>
        </tr>`).join('')}
      </tbody></table>
      <p style="font-size:9px;color:var(--muted);margin-top:4px">Total: ${data.length} aluno(s) — ${data.reduce((a,s)=>a+s.total_loans,0)} empréstimo(s) no período</p>`;
  }
  if (type === 'class-ranking') {
    if (!data.length) return titleLine + '<p style="color:var(--muted);font-size:9px;margin-top:6px">Nenhuma turma encontrada.</p>';
    return titleLine + `
      <p style="font-size:10px;color:var(--muted);margin-bottom:4px">Programa de Premiação — Ranking de Turmas</p>
      <table><thead><tr><th>#</th><th>Turma</th><th>Alunos</th><th>Total de Livros</th><th>Média/Aluno</th></tr></thead><tbody>
        ${data.map((c,i)=>`<tr>
          <td><strong>${i+1}</strong></td>
          <td><strong>${c.class_name}</strong></td>
          <td>${c.total_students}</td>
          <td><strong style="color:var(--accent)">${c.total_loans}</strong></td>
          <td>${c.avg_per_student}</td>
        </tr>`).join('')}
      </tbody></table>
      <p style="font-size:9px;color:var(--muted);margin-top:4px">Total: ${data.length} turma(s) — ${data.reduce((a,c)=>a+c.total_loans,0)} empréstimo(s) no período</p>`;
  }
  if (type === 'reservations') {
    if (!data.length) return titleLine + '<p style="color:var(--muted);font-size:9px;margin-top:6px">Nenhuma reserva encontrada.</p>';
    const statusColors = {'Ativa':'#10b981','Atendida':'#3b82f6','Cancelada':'#ef4444'};
    return titleLine + `
      <table><thead><tr><th>#</th><th>Aluno</th><th>Matrícula</th><th>Turma</th><th>Livro</th><th>Patrimônio</th><th>Reservado em</th><th>Status</th><th>Operador</th></tr></thead><tbody>
        ${data.map((r,i)=>`<tr>
          <td><strong>${i+1}</strong></td>
          <td><strong>${r.student_name}</strong></td>
          <td>${r.student_enrollment}</td>
          <td>${r.student_class||'—'}</td>
          <td>${r.book_title}</td>
          <td>${r.book_patrimony}</td>
          <td>${r.reserved_at}</td>
          <td><span style="color:${statusColors[r.status_label]||'#666'};font-weight:600">${r.status_label}</span></td>
          <td>${r.operator_name||'—'}</td>
        </tr>`).join('')}
      </tbody></table>
      <p style="font-size:9px;color:var(--muted);margin-top:4px">Total: ${data.length} reserva(s)</p>`;
  }
  // active-loans, overdue
  return titleLine + loanTable(data) + `<p style="font-size:9px;color:var(--muted);margin-top:4px">Total: ${data.length} registro(s)</p>`;
}

function loanTable(loans) {
  return `<table><thead><tr><th>Aluno</th><th>Turma</th><th>Livro</th><th>Patrimônio</th><th>Retirada</th><th>Devolução</th><th>Status</th></tr></thead><tbody>
    ${loans.map(l=>`<tr><td>${l.student_name}</td><td>${l.student_class||'—'}</td><td>${l.book_title}</td><td>${l.book_patrimony}</td><td>${l.borrowed_at}</td><td>${l.returned ? l.returned_at : l.due_date}</td><td>${l.returned?'Devolvido':l.is_overdue?`Atraso (${l.days_overdue}d)`:'Ativo'}</td></tr>`).join('')}
  </tbody></table>`;
}

// ── ACTIVITY ──
async function loadActivity() {
  const d = await api('/api/activity');
  if (!d) return;
  const icons = {borrow:'borrow',return:'return',register_book:'register',register_student:'register',login:'login',backup:'register'};
  document.getElementById('activity-list').innerHTML = d.map(a => `
    <div class="activity-item">
      <div class="act-dot ${icons[a.type]||'register'}"></div>
      <div><div class="act-text">${a.description}</div><div class="act-time">${a.created_at} · ${a.user}</div></div>
    </div>`).join('') || '<div class="empty"><p>Sem atividade registrada</p></div>';
}

// ── INSTITUTION ──
async function loadInstitution() {
  const d = await api('/api/institution');
  if (!d) return;
  document.getElementById('inst-name').value = d.name || '';
  document.getElementById('inst-cnpj').value = d.cnpj || '';
  document.getElementById('inst-address').value = d.address || '';
  document.getElementById('inst-phone').value = d.phone || '';
  document.getElementById('inst-email').value = d.email || '';
  if (d.logo_path) {
    document.getElementById('inst-logo-preview').innerHTML = `<img src="/api/institution/logo-file" style="width:100%;height:100%;object-fit:cover">`;
    loadLogo();
  }
}

async function loadLogo() {
  try {
    const r = await fetch('/api/institution');
    const d = await r.json();
    if (d?.logo_path) {
      document.getElementById('brand-icon').innerHTML = `<img src="/api/institution/logo-file" style="width:100%;height:100%;object-fit:cover;border-radius:6px">`;
    }
  } catch(e) {}
}

async function loadCategories() {
  const cats = await api('/api/categories');
  const list = document.getElementById('categories-list');
  if (!cats || !cats.length) { list.innerHTML = '<p style="color:var(--muted);font-size:.82rem">Nenhuma categoria</p>'; return; }
  list.innerHTML = cats.map(c => `
    <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border)">
      <span style="font-size:.88rem">${c.name}</span>
      ${window.USER_ROLE === 'admin' ? `<button class="btn btn-danger btn-sm" onclick="deleteCategory(${c.id},'${c.name.replace(/'/g,"\\'")}')" style="padding:3px 8px;font-size:.7rem">Excluir</button>` : ''}
    </div>`).join('');
}

async function loadCategoriesPage() {
  loadCategories();
  const d = await api('/api/institution');
  if (!d) return;
  document.getElementById('cat-inst-days').value = d.loan_days_default || 14;
  document.querySelectorAll('#p-categories .day-btn').forEach(b => b.classList.remove('active'));
  const daysMap = {7:0,14:1,21:2,30:3};
  const idx = daysMap[d.loan_days_default];
  if (idx !== undefined) document.querySelectorAll('#p-categories .day-btn')[idx]?.classList.add('active');
}

async function saveCategoryLoanDays() {
  const days = parseInt(document.getElementById('cat-inst-days').value) || 14;
  const d = await api('/api/institution');
  const data = {
    name: d?.name || '',
    cnpj: d?.cnpj || '',
    address: d?.address || '',
    phone: d?.phone || '',
    email: d?.email || '',
    loan_days_default: days
  };
  const r = await api('/api/institution', {method:'PUT', body: JSON.stringify(data)});
  if (r?.ok) { toast('Prazo salvo!', 'success'); }
  else toast('Erro ao salvar', 'error');
}

async function saveCategory() {
  const name = document.getElementById('cat-name').value.trim();
  if (!name) { toast('Nome é obrigatório', 'error'); return; }
  const r = await api('/api/categories', {method:'POST', body:JSON.stringify({name})});
  if (r?.ok) { closeModal('modal-category'); toast('Categoria criada!', 'success'); loadCategories(); loadBookCategories(); }
  else toast(r?.error || 'Erro', 'error');
}

async function deleteCategory(id, name) {
  if (!confirm(`Excluir "${name}"?`)) return;
  const r = await api(`/api/categories/${id}`, {method:'DELETE'});
  if (r?.ok) { toast('Categoria excluída!', 'success'); loadCategories(); loadBookCategories(); }
  else toast(r?.error || 'Erro', 'error');
}

async function uploadLogo(input) {
  if (!input.files[0]) return;
  const fd = new FormData();
  fd.append('logo', input.files[0]);
  try {
    const r = await fetch('/api/institution/logo', {method:'POST', body:fd});
    const d = await r.json();
    if (d.ok) {
      toast('Logo atualizado!', 'success');
      const ts = Date.now();
      document.getElementById('inst-logo-preview').innerHTML = `<img src="/api/institution/logo-file?t=${ts}" style="width:100%;height:100%;object-fit:cover">`;
      document.getElementById('brand-icon').innerHTML = `<img src="/api/institution/logo-file?t=${ts}" style="width:100%;height:100%;object-fit:cover;border-radius:6px">`;
    } else toast(d.error || 'Erro', 'error');
  } catch(e) { toast('Erro de conexão', 'error'); }
}

function downloadTemplate(type) {
  window.location.href = `/api/${type}/import-template`;
}

async function saveInstitution() {
  const data = {
    name: document.getElementById('inst-name').value.trim(),
    cnpj: document.getElementById('inst-cnpj').value.trim(),
    address: document.getElementById('inst-address').value.trim(),
    phone: document.getElementById('inst-phone').value.trim(),
    email: document.getElementById('inst-email').value.trim()
  };
  const r = await api('/api/institution', {method:'PUT', body: JSON.stringify(data)});
  if (r?.ok) { toast('Dados salvos!', 'success'); document.getElementById('inst-name-sidebar').textContent = data.name; }
  else toast('Erro ao salvar', 'error');
}

function setDefaultDays(days, btn) {
  const page = btn.closest('.page');
  if (page) page.querySelectorAll('.day-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const input = page?.querySelector('input[type="number"]') || document.getElementById('cat-inst-days');
  if (input) input.value = days;
}

async function openSobre() {
  openModal('modal-sobre');
  const d = await api('/api/version');
  if (!d) return;
  document.getElementById('sobre-versao').textContent = d.version;
  document.getElementById('sobre-instituicao').textContent = d.institution || '—';
  document.getElementById('sobre-desenvolvido').textContent = d.desenvolvido_por || '—';
  const lic = d.license_active ? 'Ativa' : 'Inativa';
  document.getElementById('sobre-licenca').textContent = lic + (d.license_valid_until ? ' (válida até ' + d.license_valid_until + ')' : '');
  const year = new Date().getFullYear();
  document.getElementById('sobre-copyright').textContent = '© ' + year + ' Biblioteca — Todos os direitos reservados.';
}

// ── USERS ──
async function loadUsers() {
  const d = await api('/api/users');
  if (!d) return;
  const isAdmin = window.USER_ROLE === 'admin';
  document.getElementById('users-body').innerHTML = d.map(u => `
    <tr>
      <td>${u.name}</td><td>${u.email}</td>
      <td>${u.role === 'admin' ? 'Administrador' : 'Operador'}</td>
      <td>${u.last_login}</td>
      <td><span class="badge ${u.active?'active':'returned'}">${u.active?'Ativo':'Inativo'}</span></td>
      ${isAdmin ? `<td><button class="btn btn-secondary btn-sm" onclick='editUser(${JSON.stringify(u)})'>Editar</button><button class="btn btn-danger btn-sm" onclick='deleteUser(${u.id},"${u.name.replace(/'/g,"\\'")}")'>Excluir</button></td>` : ''}
    </tr>`).join('');
}

async function deleteUser(id, name) {
  if (!confirm(`Excluir "${name}"?`)) return;
  const r = await api(`/api/users/${id}`, {method: 'DELETE'});
  if (r?.ok) { toast('Usuário excluído!', 'success'); loadUsers(); }
  else toast(r?.error || 'Erro', 'error');
}

async function saveUser() {
  const id = document.getElementById('user-edit-id').value;
  const data = {
    name: document.getElementById('user-name').value.trim(),
    email: document.getElementById('user-email').value.trim(),
    password: document.getElementById('user-password').value,
    role: document.getElementById('user-role').value
  };
  if (!data.name || !data.email) { toast('Nome e e-mail são obrigatórios', 'error'); return; }
  const url = id ? `/api/users/${id}` : '/api/users';
  const method = id ? 'PUT' : 'POST';
  const r = await api(url, {method, body: JSON.stringify(data)});
  if (r?.ok) { closeModal('modal-user'); toast('Usuário salvo!', 'success'); loadUsers(); }
  else toast(r?.error || 'Erro', 'error');
}

function editUser(u) {
  document.getElementById('user-modal-title').textContent = 'Editar Usuário';
  document.getElementById('user-edit-id').value = u.id;
  document.getElementById('user-name').value = u.name;
  document.getElementById('user-email').value = u.email;
  document.getElementById('user-email').disabled = true;
  document.getElementById('user-password').value = '';
  document.getElementById('user-role').value = u.role;
  document.getElementById('modal-user').classList.add('open');
}

async function changePassword() {
  const cur = document.getElementById('pw-current').value;
  const nw = document.getElementById('pw-new').value;
  const conf = document.getElementById('pw-confirm').value;
  if (nw !== conf) { toast('As senhas não coincidem', 'error'); return; }
  const r = await api('/api/users/change-password', {method:'POST', body: JSON.stringify({current_password:cur, new_password:nw})});
  if (r?.ok) { closeModal('modal-change-pw'); toast('Senha alterada!', 'success'); }
  else toast(r?.error || 'Erro', 'error');
}

// ── BACKUP ──
async function loadBackups() {
  const d = await api('/api/backup/list');
  if (!d) return;
  const dirEl = document.getElementById('backup-dir-path');
  if (dirEl && d.dir) dirEl.textContent = d.dir;
  const tbody = document.getElementById('backups-body');
  const files = d.files || d;
  if (!files.length) { tbody.innerHTML = '<tr><td colspan="4" class="empty"><p>Nenhum backup local</p></td></tr>'; return; }
  tbody.innerHTML = files.map(f => `<tr><td>📄 ${f.name}</td><td>${f.size_kb} KB</td><td>${f.date}</td><td><button class="btn btn-sm btn-secondary" onclick="restoreBackupByName(\'${f.name}\')">Restaurar</button></td></tr>`).join('');
}

async function restoreBackup(input) {
  if (!input.files[0]) return;
  if (!confirm('⚠️ Tem certeza? O banco atual será substituído. Um backup de segurança será criado automaticamente.')) return;
  const fd = new FormData();
  fd.append('file', input.files[0]);
  try {
    const r = await fetch('/api/backup/restore', {method:'POST', body:fd});
    const d = await r.json();
    if (d.ok) toast('Banco restaurado! Recarregando...', 'success'), setTimeout(() => location.reload(), 2000);
    else toast(d.error || 'Erro', 'error');
  } catch(e) { toast('Erro de conexão', 'error'); }
}

async function restoreBackupByName(name) {
  if (!confirm('⚠️ Restaurar ' + name + '? O banco atual será substituído.')) return;
  const r = await api('/api/backup/restore-by-name', {method:'POST', body:JSON.stringify({name})});
  if (r?.ok) toast('Banco restaurado! Recarregando...', 'success'), setTimeout(() => location.reload(), 2000);
  else toast(r?.error || 'Erro', 'error');
}

async function checkCloudBackup() {
  const el = document.getElementById('cloud-backup-status');
  if (!el) return;
  try {
    const d = await api('/api/backup/cloud-status');
    if (!d) { el.innerHTML = '<p style="color:var(--muted)">Não foi possível verificar</p>'; return; }
    if (d.available) {
      const remotes = (d.remotes || []).map(r => `<option value="${r}">${r}</option>`).join('');
      el.innerHTML = `
        <p style="color:var(--success);margin-bottom:12px">✅ rclone disponível</p>
        <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap">
          <select id="cloud-remote" style="padding:8px 12px;border:1px solid var(--border);border-radius:6px;background:var(--bg);color:var(--text)">${remotes}</select>
          <button class="btn btn-primary" onclick="cloudUpload()">☁️ Enviar para Nuvem</button>
        </div>
        <p style="font-size:.78rem;color:var(--muted);margin-top:8px">O backup será salvo em <code>${d.remotes[0] || '?'}:Biblioteca/backups/</code></p>`;
    } else if (d.reason === 'not_installed') {
      el.innerHTML = `<p style="color:var(--muted)">☁️ Backup na nuvem disponível. <a href="https://rclone.org" target="_blank">Instale o rclone</a> e configure um remote.</p>`;
    } else if (d.reason === 'not_configured') {
      el.innerHTML = `<p style="color:var(--muted)">☁️ rclone instalado. Execute <code>rclone config</code> no terminal para configurar um remote (Google Drive, etc).</p>`;
    } else {
      el.innerHTML = `<p style="color:var(--muted)">☁️ ${d.message || 'Indisponível'}</p>`;
    }
  } catch(e) {
    el.innerHTML = '<p style="color:var(--muted)">☁️ Backup na nuvem indisponível</p>';
  }
}

async function cloudUpload() {
  const btn = document.querySelector('#cloud-backup-status .btn-primary');
  const remote = document.getElementById('cloud-remote')?.value;
  if (!remote) return toast('Selecione um remote', 'error');
  btn.disabled = true;
  btn.textContent = '⏳ Enviando...';
  try {
    const r = await fetch('/api/backup/cloud-upload', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({remote})});
    const d = await r.json();
    if (d.ok) toast(d.message, 'success');
    else toast(d.error || 'Erro', 'error');
  } catch(e) { toast('Erro de conexão', 'error'); }
  finally { btn.disabled = false; btn.textContent = '☁️ Enviar para Nuvem'; }
}

// ── CSV IMPORT ──
async function importCSV(type, input) {
  if (!input.files[0]) return;
  const fd = new FormData();
  fd.append('file', input.files[0]);
  try {
    const r = await fetch(`/api/${type}/import-csv`, {method:'POST', body:fd});
    const d = await r.json();
    if (d.ok) {
      toast(`✓ ${d.imported} importados, ${d.skipped} ignorados`, d.skipped > 0 ? 'info' : 'success');
      if (type === 'books') loadBooks();
      else loadStudents();
    } else toast(d.error || 'Erro', 'error');
  } catch(e) { toast('Erro de conexão', 'error'); }
  input.value = '';
}

// ── HELPERS ──
function statusBadge(l) {
  if (l.returned) return '<span class="badge returned"><span class="badge-dot"></span>Devolvido</span>';
  if (l.is_overdue) return `<span class="badge late"><span class="badge-dot"></span>Atrasado</span>`;
  return '<span class="badge active"><span class="badge-dot"></span>Ativo</span>';
}

function debounce(fn, ms) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

// ── LICENSE CHECK PAGE ──
async function checkLicenseStatus() {
  try {
    const lic = await api('/api/license/status');
    if (!lic) return; // erro de rede — não redirecionar
    const widget = document.getElementById('lic-widget');
    const widgetText = document.getElementById('lic-widget-text');
    const widgetSub = document.getElementById('lic-widget-sub');
    if (!widget) return;

    if (lic.active) {
      const days = lic.days_left;
      if (days !== null && days !== undefined) {
        if (days <= 5) {
          // Alerta: faltam 5 dias ou menos
          widget.className = 'lic-widget warn';
          widgetText.textContent = `⚠ Licença expira em ${days} dia(s)!`;
          widgetSub.textContent = `Válida até: ${lic.valid_until || '—'}`;
          widget.style.display = '';
          if (!window._licenseWarnShown) {
            toast(`⚠ Sua licença expira em ${days} dia(s)! Renove em breve.`, 'error');
            window._licenseWarnShown = true;
          }
        } else {
          // Licença ok — mostrar dias restantes discretamente
          widget.className = 'lic-widget ok';
          widgetText.textContent = `✓ Licença ativa`;
          widgetSub.textContent = `${days} dia(s) restantes`;
          widget.style.display = '';
        }
      }
    } else {
      // Licença inativa ou expirada — bloquear e redirecionar
      widget.className = 'lic-widget err';
      widgetText.textContent = lic.expired ? '✗ Licença expirada' : '✗ Não ativada';
      widgetSub.textContent = 'Acesso bloqueado';
      widget.style.display = '';
      if (!window._licenseExpiredShown) {
        toast(lic.expired ? '⚠ Licença expirada! Sistema bloqueado.' : '⚠ Sistema não ativado.', 'error');
        window._licenseExpiredShown = true;
      }
      setTimeout(() => navigate('license_check'), 2000);
    }
  } catch(e) {
    console.warn('Erro ao verificar licença:', e);
  }
}

async function loadLicensePage() {
  const lic = await api('/api/license/status');
  if (lic?.active) {
    toast('Licença ativa! Redirecionando...', 'success');
    setTimeout(() => navigate('dashboard'), 1500);
  }
}

async function activateLicenseFromPage() {
  const key = document.getElementById('lic-key').value.trim();
  const msg = document.getElementById('lic-msg-page');
  if (key.length < 10) { msg.className='lic-msg err'; msg.style.color='var(--danger)'; msg.textContent='Chave muito curta.'; return; }
  msg.textContent='Verificando...'; msg.style.color='var(--muted)';
  try {
    const r = await fetch('/api/license/activate', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({key})
    });
    const d = await r.json();
    if (d.ok) {
      msg.style.color='var(--success)';
      msg.textContent=`✓ Ativada! Instituição: ${d.institution} | Válida até: ${d.valid_until}`;
      toast('Licença ativada com sucesso!', 'success');
      setTimeout(() => navigate('dashboard'), 2000);
    } else {
      msg.style.color='var(--danger)';
      msg.textContent='✗ ' + d.error;
    }
  } catch(e) {
    msg.style.color='var(--danger)'; msg.textContent='Erro de conexão';
  }
}

document.getElementById('lic-key')?.addEventListener('input', function(e) {
  let val = e.target.value.replace(/[^A-Za-z0-9]/g,'').toUpperCase();
  let parts = val.match(/.{1,5}/g) || [];
  e.target.value = parts.join('-').substring(0,29);
});

// ── PERMISSIONS ──
const PERM_LABELS = {
  can_create_books: 'Cadastrar livros',
  can_edit_books: 'Editar livros',
  can_delete_books: 'Excluir livros',
  can_create_students: 'Cadastrar alunos',
  can_edit_students: 'Editar alunos',
  can_delete_students: 'Excluir alunos',
  can_create_loans: 'Registrar empréstimos',
  can_return_books: 'Registrar devolucoes',
  can_renew_loans: 'Renovar empréstimos',
  can_manage_reservations: 'Gerenciar reservas',
  can_view_reports: 'Visualizar relatórios',
  can_print_barcodes: 'Imprimir etiquetas',
  can_manage_categories: 'Gerenciar categorias',
  can_backup: 'Fazer backup',
  can_view_activity: 'Visualizar atividades'
};

async function loadPermissions() {
  const perms = await api('/api/operator-permissions');
  if (!perms) return;
  const list = document.getElementById('perms-list');
  let html = '';
  for (const [key, label] of Object.entries(PERM_LABELS)) {
    const checked = perms[key] ? 'checked' : '';
    html += `<label class="perm-item" style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid var(--border);cursor:pointer">
      <input type="checkbox" data-perm="${key}" ${checked} style="width:18px;height:18px;accent-color:var(--accent)">
      <span style="font-size:.9rem">${label}</span>
    </label>`;
  }
  list.innerHTML = html;
}

async function savePermissions() {
  const perms = {};
  document.querySelectorAll('[data-perm]').forEach(cb => { perms[cb.dataset.perm] = cb.checked; });
  const r = await api('/api/operator-permissions', {method:'POST', body:JSON.stringify(perms)});
  if (r?.ok) toast('Permissões salvas!', 'success');
  else toast(r?.error || 'Erro ao salvar', 'error');
}

// ── BARCODES ──
let barcodeBooks = [];
let barcodeSearchQuery = '';
async function loadBarcodeBooks(q) {
  if (q !== undefined) barcodeSearchQuery = q;
  const parts = (document.getElementById('barcode-sort')?.value || 'patrimony_asc').split('_');
  const sortOrder = parts.pop();
  const sortBy = parts.join('_');
  const d = await api(`/api/books?q=${encodeURIComponent(barcodeSearchQuery)}&sort_by=${sortBy}&sort_order=${sortOrder}&per_page=10000`);
  if (!d) {
    toast('Erro ao carregar livros', 'error');
    return;
  }
  barcodeBooks = d.books || d || [];
  renderBarcodeBooks();
}

function renderBarcodeBooks() {
  const tbody = document.getElementById('barcode-books-body');
  if (!barcodeBooks.length) { tbody.innerHTML = '<tr><td colspan="5" class="empty">Nenhum livro encontrado</td></tr>'; return; }
  tbody.innerHTML = barcodeBooks.map(b => `
    <tr>
      <td><input type="checkbox" class="bc-check" data-id="${b.id}" onchange="updateBarcodeCount()"></td>
      <td><strong>${b.patrimony}</strong></td>
      <td>${b.title}</td>
      <td>${b.author || '—'}</td>
      <td><span class="badge ${b.available ? 'available' : 'unavailable'}">${b.available ? 'Disponível' : 'Emprestado'}</span></td>
    </tr>
  `).join('');
  updateBarcodeCount();
}

function toggleAllBarcodes(checked) {
  document.querySelectorAll('.bc-check').forEach(cb => cb.checked = checked);
  updateBarcodeCount();
}

function updateBarcodeCount() {
  const count = document.querySelectorAll('.bc-check:checked').length;
  document.getElementById('bc-selected-count').textContent = count;
}

async function printSelectedBarcodes() {
  const ids = Array.from(document.querySelectorAll('.bc-check:checked')).map(cb => parseInt(cb.dataset.id));
  if (!ids.length) { toast('Selecione ao menos um livro', 'error'); return; }
  const preset = document.getElementById('bc-preset').value;
  const books = barcodeBooks.filter(b => ids.includes(b.id));
  
  const presets = {
    'a4-3col':  {w:63.5, h:38.1, fs:9,  cols:3, gap:2, margin:5, label:'A4 - 3 colunas (padrao)'},
    'a4-2col':  {w:105,  h:74,   fs:11, cols:2, gap:4, margin:5, label:'A4 - 2 colunas (grande)'},
    'a4-4col':  {w:48,   h:25,   fs:7,  cols:4, gap:1, margin:3, label:'A4 - 4 colunas (pequeno)'},
    'terminal-1col': {w:302,  h:151,  fs:12, cols:1, gap:4, margin:10,label:'Terminal - 1 coluna (grande)'}
  };
  const p = presets[preset] || presets['a4-3col'];
  const colWidth = 'calc(' + (100/p.cols) + '% - ' + (p.gap*(p.cols-1)/p.cols) + 'px)';

  let html = '<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Etiquetas - ' + p.label + '</title>\
<style>\
@page{margin:' + p.margin + 'mm;size:A4}\
body{margin:0;padding:0;font-family:Arial,sans-serif;font-size:' + p.fs + 'px}\
.grid{display:flex;flex-wrap:wrap;gap:' + p.gap + 'px;justify-content:center}\
.label{border:1px dashed #999;display:flex;flex-direction:column;align-items:center;justify-content:center;\
  width:' + colWidth + ';height:' + p.h + 'mm;page-break-inside:avoid;padding:3px;box-sizing:border-box;overflow:hidden}\
.label .pat{font-weight:bold;font-size:' + p.fs + 'px;margin-bottom:1px;line-height:1.1}\
.label .tit{font-size:' + (p.fs-1) + 'px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:95%;line-height:1.1}\
.label img{max-width:90%;max-height:' + (p.h*0.45) + 'mm;width:auto;height:auto}\
@media print{.no-print{display:none}}\
</style></head><body>\
<div class="no-print" style="padding:10px;text-align:center;position:fixed;top:0;left:0;right:0;background:#fff;z-index:999;border-bottom:1px solid #ccc">\
  <button onclick="window.print()" style="padding:8px 20px;font-size:14px;cursor:pointer">🖨️ Imprimir</button>\
  <button onclick="window.close()" style="padding:8px 20px;font-size:14px;cursor:pointer;margin-left:8px">Fechar</button>\
  <p style="font-size:12px;color:#666;margin:5px 0 0">' + books.length + ' etiquetas selecionadas | ' + p.label + '</p>\
</div>\
<div style="height:60px"></div>\
<div class="grid">';
  for (const b of books) {
    html += '<div class="label"><div class="pat">' + b.patrimony + '</div><div class="tit">' + b.title + '</div><img src="/api/books/' + b.id + '/barcode" alt="' + b.patrimony + '"></div>';
  }
  html += '</div></body></html>';

  const win = window.open('', '_blank');
  if (win) {
    win.document.write(html);
    win.document.close();
  } else {
    toast('Permita pop-ups para imprimir etiquetas', 'error');
  }
}

// ── INIT ──
let opPerms = {};
async function loadOperatorPermissions() {
  const p = await api('/api/operator-permissions');
  if (p) {
    opPerms = p;
    applyPermissions();
  }
}

// ── CLEANUP ──
async function runCleanup() {
  const tables = [];
  if (document.getElementById('clean-books')?.checked) tables.push('books');
  if (document.getElementById('clean-students')?.checked) tables.push('students');
  if (document.getElementById('clean-loans')?.checked) tables.push('loans');
  if (document.getElementById('clean-logs')?.checked) tables.push('activity_log');
  if (document.getElementById('clean-categories')?.checked) tables.push('categories');
  if (!tables.length) { toast('Nenhum dado selecionado', 'error'); return; }
  if (!confirm('Tem certeza? Esta acao ira APAGAR os dados selecionados.\nUm backup sera criado automaticamente.')) return;
  const btn = document.getElementById('btn-cleanup');
  const status = document.getElementById('cleanup-status');
  btn.disabled = true;
  btn.textContent = 'Limpando...';
  status.textContent = 'Criando backup e limpando dados...';
  const r = await fetch('/api/cleanup', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({tables})
  }).then(r => r.json()).catch(() => null);
  btn.disabled = false;
  btn.textContent = '🗑️ Limpar Dados Selecionados';
  if (r?.ok) {
    status.textContent = `Limpeza concluida! Backup: ${r.backup}`;
    toast('Dados apagados com sucesso!', 'success');
  } else {
    status.textContent = 'Erro: ' + (r?.error || 'falha na comunicacao');
    toast(r?.error || 'Erro ao limpar dados', 'error');
  }
}

function applyPermissions() {
  const isAdmin = window.USER_ROLE === 'admin';
  if (isAdmin) return;
  if (!opPerms.can_create_books) document.querySelector('.perm-create-books')?.remove();
  if (!opPerms.can_create_students) document.querySelector('.perm-create-students')?.remove();
  if (!opPerms.can_create_loans) document.querySelector('.perm-create-loans')?.remove();
  if (!opPerms.can_return_books) document.querySelector('.perm-return-books')?.remove();
  if (!opPerms.can_view_reports) document.querySelector('[data-page="reports"]')?.remove();
  if (!opPerms.can_manage_reservations) document.querySelector('[data-page="reservations"]')?.remove();
  if (!opPerms.can_print_barcodes) document.querySelector('[data-page="barcodes"]')?.remove();
  if (!opPerms.can_manage_categories) { document.querySelector('.perm-manage-cats')?.remove(); document.getElementById('nav-categories')?.remove(); }
  if (!opPerms.can_backup) document.querySelector('[data-page="backup"]')?.remove();
  if (!opPerms.can_view_activity) document.querySelector('[data-page="activity"]')?.remove();
  document.querySelector('.perm-save-inst')?.remove();
}

setInterval(updateDT, 1000);
updateDT();
fetchLoanDaysDefault();
loadOperatorPermissions();
loadLogo();
// Restore sort preferences
const bs = document.getElementById('books-sort');
if (bs) bs.value = localStorage.getItem('books-sort') || 'title_asc';
const ss = document.getElementById('students-sort');
if (ss) ss.value = localStorage.getItem('students-sort') || 'name_asc';
loadPage(currentPage);
