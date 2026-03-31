// Helper to get cookie value
const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
};

// ─── Keyboard shortcut: press 'd' 5× within 2s → /dev-enable ───
(function () {
    let presses = 0;
    let timer = null;

    document.addEventListener('keydown', (e) => {
        // Ignore when typing in inputs/textareas
        const tag = document.activeElement?.tagName;
        if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;

        if (e.key === 'd' || e.key === 'D') {
            presses++;
            clearTimeout(timer);

            if (presses >= 5) {
                presses = 0;
                window.location.href = '/dev-enable';
                return;
            }

            timer = setTimeout(() => { presses = 0; }, 2000);
        } else {
            presses = 0;
            clearTimeout(timer);
        }
    });
})();

// ─── On DOM ready: nav link + floating badge ───
document.addEventListener('DOMContentLoaded', () => {
    const isDevMode = getCookie('dev_mode') === 'true';

    // 1. Nav menu link "Vývoj"
    const navMenu = document.getElementById('navMenu');
    if (navMenu) {
        const existingDevLink = Array.from(navMenu.querySelectorAll('a')).find(a => a.textContent.trim() === 'Vývoj');

        if (isDevMode) {
            if (!existingDevLink) {
                const devLi = document.createElement('li');
                const devLink = document.createElement('a');
                devLink.href = '/docs/index.html';
                devLink.className = 'nav-link';
                devLink.textContent = 'Vývoj';
                if (window.location.pathname.includes('/docs/')) {
                    devLink.classList.add('active');
                }
                devLi.appendChild(devLink);
                navMenu.appendChild(devLi);
            }
        } else {
            if (existingDevLink) {
                existingDevLink.parentElement.remove();
            }
        }
    }

    // 2. Floating DEV badge (visible on all pages when in dev mode)
    if (isDevMode) {
        const badge = document.createElement('a');
        badge.href = '/docs/index.html';
        badge.title = 'Otevřít vývojářskou konzoli';
        badge.style.cssText = [
            'position:fixed',
            'bottom:20px',
            'right:20px',
            'z-index:99999',
            'background:#27445C',
            'color:#A9ECFF',
            'font-family:monospace',
            'font-size:11px',
            'font-weight:700',
            'letter-spacing:1px',
            'padding:6px 10px',
            'border-radius:6px',
            'text-decoration:none',
            'box-shadow:0 2px 8px rgba(0,0,0,0.3)',
            'opacity:0.85',
            'transition:opacity 0.2s',
            'user-select:none',
        ].join(';');
        badge.textContent = 'DEV';
        badge.addEventListener('mouseenter', () => { badge.style.opacity = '1'; });
        badge.addEventListener('mouseleave', () => { badge.style.opacity = '0.85'; });
        document.body.appendChild(badge);
    }
});
