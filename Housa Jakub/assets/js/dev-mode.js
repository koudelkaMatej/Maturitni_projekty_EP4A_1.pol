document.addEventListener('DOMContentLoaded', () => {
    const navMenu = document.getElementById('navMenu');
    if (!navMenu) return;

    // Helper to get cookie
    const getCookie = (name) => {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    };

    const isDevMode = getCookie('dev_mode') === 'true';
    const existingDevLink = Array.from(navMenu.querySelectorAll('a')).find(a => a.textContent === 'Vývoj');

    if (isDevMode) {
        // Add if not exists
        if (!existingDevLink) {
            const devLi = document.createElement('li');
            const devLink = document.createElement('a');
            devLink.href = '/docs/index.html';
            devLink.className = 'nav-link';
            devLink.textContent = 'Vývoj';
            
            // Check if we are currently on the docs page to set active class
            if (window.location.pathname.includes('/docs/')) {
                devLink.classList.add('active');
            }

            devLi.appendChild(devLink);
            
            // Insert before the last item (usually Contact) or append
            // Assuming Contact is last, we want it before Contact? Or at the end?
            // Original code appended it. Let's append it.
            // But wait, usually "Contact" is last.
            // Let's just append it for now to match previous behavior.
            navMenu.appendChild(devLi);
        }
    } else {
        // Remove if exists (cleanup hardcoded or cached links)
        if (existingDevLink) {
            existingDevLink.parentElement.remove();
        }
    }
});
