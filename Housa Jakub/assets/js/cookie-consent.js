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
                <p style="margin: 0; line-height: 1.5; font-size: 0.95rem;">
                    Tento web používá soubory cookie k zajištění funkčnosti a vylepšení uživatelského zážitku. 
                    Používáním webu s tím souhlasíte. 
                    <a href="/Info/privacy.html" style="color: #A9ECFF; text-decoration: underline; font-weight: 600;">Více informací</a>.
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
            padding: '1.5rem',
            zIndex: '9999',
            boxShadow: '0 -4px 20px rgba(0,0,0,0.15)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            borderTop: '1px solid rgba(255,255,255,0.1)'
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
            backgroundColor: '#ffffff',
            backgroundImage: 'none', // Override CSS gradient
            color: '#27445C',
            border: 'none',
            padding: '0.75rem 2rem',
            borderRadius: '50px',
            cursor: 'pointer',
            fontWeight: '700',
            fontSize: '1rem',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            transition: 'transform 0.2s ease'
        });

        // Add hover effect via event listeners since we can't do pseudo-classes in inline styles
        btn.addEventListener('mouseenter', () => {
            btn.style.transform = 'scale(1.05)';
            btn.style.boxShadow = '0 6px 12px rgba(0,0,0,0.15)';
        });
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = 'scale(1)';
            btn.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
        });

        document.body.appendChild(banner);

        document.getElementById('cookie-accept').addEventListener('click', () => {
            localStorage.setItem(cookieConsentKey, 'true');
            banner.remove();
        });
    }
});


