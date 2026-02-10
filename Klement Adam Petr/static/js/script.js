// Web teď používá skutečné API (Flask na 5000) pro registraci/přihlášení a uloží JWT do localStorage.

const API_URL = 'http://localhost:5000';

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const modalOverlay = id('modal-overlay');
  const modalReg = id('modal-register');
  const modalLogin = id('modal-login');
  const regForm = id('form-register');
  const loginForm = id('form-login');
  const btnGet = id('btn-get-access');
  const heroGet = id('hero-get');
  const purchaseStart = id('purchase-start');
  const downloadArea = id('download-area');
  const btnLoginOpen = id('btn-login-open');
  const btnLogout = id('btn-logout');
  const userBadge = id('user-badge');
  const userNameEl = id('user-name');
  const dashboard = id('dashboard');
  const workoutsList = id('workouts-list');
  const workoutsEmpty = id('workouts-empty');

  // Wire UI actions
  [btnGet, heroGet, purchaseStart].forEach(b => b && b.addEventListener('click', openRegister));
  btnLoginOpen && btnLoginOpen.addEventListener('click', openLogin);
  id('reg-cancel').addEventListener('click', closeModals);
  id('login-cancel').addEventListener('click', closeModals);
  btnLogout && btnLogout.addEventListener('click', logout);

  // Register submit
  regForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = id('reg-username').value.trim();
    const email = id('reg-email').value.trim();
    const password = id('reg-password').value;
    if (!username || !password) {
      return showMsg('reg-msg', 'Vyplň uživatelské jméno a heslo.');
    }

    try {
      const res = await fetch(`${API_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
      });
      const data = await res.json();
      if (res.status === 201) {
        showMsg('reg-msg', 'Registrace úspěšná. Přihlašuji...');
        // auto-login
        const err = await loginInternal(username, password);
        if (!err) {
          closeModals();
          showDownload(username);
        } else {
          showMsg('reg-msg', err);
        }
      } else {
        showMsg('reg-msg', data.error || 'Registrace selhala');
      }
    } catch (e) {
      const hint = (location.protocol === 'file:')
        ? ' (Otevři stránku přes http://localhost:5000 — spusť run_web.ps1)'
        : '';
      showMsg('reg-msg', `Chyba připojení k serveru: ${e}${hint}`);
    }
  });

  // Login submit
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = id('login-username').value.trim();
    const password = id('login-password').value;
    const err = await loginInternal(username, password);
    if (!err) {
      showMsg('login-msg', 'Přihlášení úspěšné.');
      closeModals();
      showDownload(username);
    } else {
      showMsg('login-msg', err);
    }
  });

  // Initialize UI based on saved token
  // nejdřív ověř API
  checkApi().then((ok) => {
    toggleApiBanner(!ok);
  });

  const savedUser = localStorage.getItem('amp_username');
  const savedToken = localStorage.getItem('amp_token');
  if (savedUser && savedToken) {
    setLoggedInUI(savedUser);
    downloadArea.classList.remove('hidden');
    fetchAndRenderWorkouts();
    updateHeroStats(); // New: update phone mockup
  } else {
    setLoggedOutUI();
  }

  // Helpers
  function id(name){ return document.getElementById(name); }
  function showMsg(elId, text){ const el = id(elId); if (el) el.innerText = text || ''; }

  function openRegister(){
    modalOverlay.classList.remove('hidden');
    modalReg.classList.remove('hidden');
    showMsg('reg-msg', '');
    id('reg-username').focus();
  }
  function openLogin(){
    modalOverlay.classList.remove('hidden');
    modalLogin.classList.remove('hidden');
    showMsg('login-msg', '');
    id('login-username').focus();
  }
  function closeModals(){
    modalOverlay.classList.add('hidden');
    modalReg.classList.add('hidden');
    modalLogin.classList.add('hidden');
  }

  function setLoggedInUI(username){
    userNameEl.textContent = username;
    userBadge.classList.remove('hidden');
    btnLogout.classList.remove('hidden');
    const btnSettings = id('btn-settings');
    if (btnSettings) btnSettings.classList.remove('hidden');
    
    if (btnLoginOpen) btnLoginOpen.classList.add('hidden');
    const btnGet = id('btn-get-access');
    if (btnGet) btnGet.classList.add('hidden');
    if (dashboard) dashboard.classList.remove('hidden');
  }
  function setLoggedOutUI(){
    userNameEl.textContent = '';
    userBadge.classList.add('hidden');
    btnLogout.classList.add('hidden');
    const btnSettings = id('btn-settings');
    if (btnSettings) btnSettings.classList.add('hidden');

    if (btnLoginOpen) btnLoginOpen.classList.remove('hidden');
    const btnGet = id('btn-get-access');
    if (btnGet) btnGet.classList.remove('hidden');
    downloadArea.classList.add('hidden');
    if (dashboard) dashboard.classList.add('hidden');
    if (workoutsList) workoutsList.innerHTML = '';
  }

  async function loginInternal(username, password){
    try {
      const res = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      if (res.status === 200 && data.token){
        localStorage.setItem('amp_token', data.token);
        localStorage.setItem('amp_username', username);
        setLoggedInUI(username);
        return null;
      } else {
        return data.error || 'Přihlášení selhalo';
      }
    } catch (e) {
      const hint = (location.protocol === 'file:')
        ? ' (Otevři stránku přes http://localhost:5000 — spusť run_web.ps1)'
        : '';
      return `Chyba připojení k serveru: ${e}${hint}`;
    }
  }

  function logout(){
    localStorage.removeItem('amp_token');
    localStorage.removeItem('amp_username');
    setLoggedOutUI();
  }

  function showDownload(username){
    downloadArea.classList.remove('hidden');
    const h3 = downloadArea.querySelector('h3');
    if (h3) h3.innerText = `Děkujeme, ${username} — přístup aktivní`;
  }

  async function fetchAndRenderWorkouts(){
    const token = localStorage.getItem('amp_token');
    if (!token) return;
    try {
      // rychlý ping (volitelně)
      // await fetch(`${API_URL}/ping`);
      const res = await fetch(`${API_URL}/get_workouts`, {
        method: 'GET',
        headers: { 'Authorization': token }
      });
      if (res.status === 401){
        // token neplatný/expirace
        logout();
        alert('Relace vypršela. Přihlas se znovu.');
        return;
      }
      const data = await res.json();
      const workouts = Array.isArray(data.workouts) ? data.workouts : [];
      renderWorkouts(workouts);
    } catch(e){
      const hint = (location.protocol === 'file:')
        ? ' (Otevři stránku přes http://localhost:5000 — spusť run_web.ps1)'
        : '';
      console.warn('Chyba při načítání tréninků:', e, hint);
    }
  }

  function renderWorkouts(workouts){
    if (!workoutsList) return;
    workoutsList.innerHTML = '';
    if (!workouts || workouts.length === 0){
      workoutsEmpty && workoutsEmpty.classList.remove('hidden');
      return;
    }
    workoutsEmpty && workoutsEmpty.classList.add('hidden');
    
    // LIMIT TO 5 on Dashboard
    const limitedWorkouts = workouts.slice(0, 5);
    
    limitedWorkouts.forEach(w => {
      const item = document.createElement('div');
      item.className = 'workout-item';
      
      const head = document.createElement('div');
      head.className = 'workout-head';
      
      // Date and main info
      const infoDiv = document.createElement('div');
      const dateEl = document.createElement('div');
      dateEl.className = 'workout-date';
      dateEl.textContent = w.date ? new Date(w.date).toLocaleString() : 'Neznámé datum';
      
      const summaryEl = document.createElement('div');
      summaryEl.className = 'workout-ex';
      summaryEl.textContent = w.summary_text || 'Trénink';

      infoDiv.appendChild(summaryEl);
      infoDiv.appendChild(dateEl);
      
      // Note
      if (w.note) {
        const noteEl = document.createElement('div');
        noteEl.className = 'workout-meta';
        noteEl.textContent = `Poznámka: ${w.note}`;
        infoDiv.appendChild(noteEl);
      }
      
      // Detail button
      const btnDiv = document.createElement('div');
      const btn = document.createElement('button');
      btn.className = 'btn ghost small';
      btn.textContent = 'Detail';
      btn.onclick = () => {
        window.location.href = `/workout_detail?id=${w.id}`;
      };
      btnDiv.appendChild(btn);

      head.appendChild(infoDiv);
      head.appendChild(btnDiv);
      item.appendChild(head);
      
      workoutsList.appendChild(item);
    });
  }

  async function checkApi(){
    try {
      const res = await fetch(`${API_URL}/ping`, { method: 'GET' });
      return res.ok;
    } catch(e) {
      return false;
    }
  }
  function toggleApiBanner(show){
    const bar = id('api-status');
    if (!bar) return;
    bar.classList[show ? 'remove' : 'add']('hidden');
  }

  async function updateHeroStats() {
    const token = localStorage.getItem('amp_token');
    if (!token) return;
    
    try {
      const res = await fetch(`${API_URL}/get_user_stats`, {
        headers: { 'Authorization': token }
      });
      if (res.ok) {
        const data = await res.json();
        
        // Update Phone Mockup
        const wk = data.latest_workout;
        const stats = data.stats;
        
        const titleEl = id('hero-wk-title');
        const descEl = id('hero-wk-desc');
        const noteEl = id('hero-note');
        const statsEl = id('hero-stats');
        
        if (titleEl) titleEl.textContent = wk.title;
        if (descEl) descEl.textContent = wk.desc;
        if (noteEl) noteEl.textContent = `Poznámka: ${wk.note}`;
        
        if (statsEl) {
          // Combine BW and PR
          statsEl.textContent = `${stats.bw_text} · ${stats.pr_text}`;
        }
        
        // Update Dashboard Counter
        const countEl = id('days-active-count');
        if (countEl && stats.days_active !== undefined) {
          countEl.textContent = stats.days_active;
        }
      }
    } catch (e) {
      console.warn("Failed to fetch user stats for hero", e);
    }
  }
});
