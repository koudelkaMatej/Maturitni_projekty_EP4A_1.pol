document.addEventListener('DOMContentLoaded', () => {
    const cookieConsentKey = 'drive_cookie_consent';
    
    if (!localStorage.getItem(cookieConsentKey)) {
        showCookieBanner();
    }

    function showCookieBanner() {
        const banner = document.createElement('div');
        banner.id = 'cookie-consent-banner';
        banner.innerHTML = `
            <div class="cookie-content">
                <p>
                    Tento web používá soubory cookie k zajištění funkčnosti a vylepšení uživatelského zážitku. 
                    Používáním webu s tím souhlasíte. 
                    <a href="/Info/privacy.html" style="color: inherit; text-decoration: underline;">Více informací</a>.
                </p>
                <div class="cookie-buttons">
                    <button id="cookie-accept" class="btn btn-sm">Souhlasím</button>
                </div>
            </div>
        `;

        // Styles
        Object.assign(banner.style, {
            position: 'fixed',
            bottom: '0',
            left: '0',
            width: '100%',
            backgroundColor: '#27445C', // Brand dark blue
            color: '#fff',
            padding: '1rem',
            zIndex: '9999',
            boxShadow: '0 -2px 10px rgba(0,0,0,0.1)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center'
        });

        // Inner content styles
        const content = banner.querySelector('.cookie-content');
        Object.assign(content.style, {
            maxWidth: '1200px',
            width: '100%',
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: '1rem'
        });

        // Button styles
        const btn = banner.querySelector('#cookie-accept');
        Object.assign(btn.style, {
            backgroundColor: '#fff',
            color: '#27445C',
            border: 'none',
            padding: '0.5rem 1.5rem',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '0.9rem'
        });

        document.body.appendChild(banner);

        document.getElementById('cookie-accept').addEventListener('click', () => {
            localStorage.setItem(cookieConsentKey, 'true');
            banner.remove();
        });
    }
});


