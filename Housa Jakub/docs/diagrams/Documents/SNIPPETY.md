# SNIPPETY — Kódové šablony pro maturitu

> **Účel:** Připravené copy-paste šablony. Každý snippet ukazuje kde ho vložit a co upravit.
> Viz také: [TAHAK.md](./TAHAK.md) | [MANUAL.md](./MANUAL.md) | [POJMY.md](./POJMY.md)

---

## Express — nový GET endpoint

Přidej **před řádek 1292** v `server.js` (před 404 handler):

```javascript
// Načtení všech položek z tabulky 'produkty'
// Endpoint: GET /api/moje-data
app.get('/api/moje-data', (req, res) => {
    try {
        const data = db.prepare('SELECT * FROM products').all();
        res.json(data);
    } catch (e) {
        logger.error('api', 'Chyba při načítání', { message: e.message });
        res.status(500).json({ error: 'Chyba serveru' });
    }
});
```

---

## Express — nový POST endpoint

```javascript
// Vytvoření nového záznamu
// Endpoint: POST /api/moje-data
app.post('/api/moje-data', (req, res) => {
    // Načtení dat z těla requestu
    const { nazev, cena } = req.body || {};

    // Validace vstupů
    if (!nazev) return res.status(400).json({ error: 'Chybí nazev' });
    if (!cena || isNaN(cena)) return res.status(400).json({ error: 'Chybí cena' });

    try {
        // Vložení do DB
        const result = db.prepare(
            'INSERT INTO products (name, price_cents) VALUES (?, ?)'
        ).run(nazev, Number(cena));

        res.status(201).json({ id: result.lastInsertRowid, nazev });
    } catch (e) {
        if (e.message.includes('UNIQUE')) {
            return res.status(409).json({ error: 'Název již existuje' });
        }
        logger.error('api', 'Chyba při vytváření', { message: e.message });
        res.status(500).json({ error: 'Chyba serveru' });
    }
});
```

---

## Express — endpoint s autentizací (jen pro přihlášené)

```javascript
// Endpoint dostupný jen pro přihlášené uživatele
// getCurrentUser() je helper funkce v server.js:288
app.get('/api/muj-profil', (req, res) => {
    const user = getCurrentUser(req);
    if (!user) return res.status(401).json({ error: 'Unauthorized' });

    // user.id a user.email jsou dostupné
    const profil = db.prepare('SELECT * FROM users WHERE id = ?').get(user.id);
    res.json(profil);
});
```

---

## Express — endpoint s admin ochranou

```javascript
// Endpoint dostupný jen pro admina (dev mód)
// requireAdmin middleware je v server.js:61
app.post('/api/admin/akce', requireAdmin, (req, res) => {
    const { data } = req.body || {};
    if (!data) return res.status(400).json({ error: 'Chybí data' });

    // admin logika zde
    res.json({ ok: true, message: 'Akce provedena' });
});
```

---

## Express — PUT endpoint (aktualizace záznamu)

```javascript
// Aktualizace záznamu — např. profil uživatele
app.put('/api/user/nazev', (req, res) => {
    const user = getCurrentUser(req);
    if (!user) return res.status(401).json({ error: 'Unauthorized' });

    const { jmeno, prijmeni } = req.body || {};

    // Partial update — aktualizuj jen co přišlo
    if (jmeno !== undefined) {
        db.prepare('UPDATE users SET first_name = ? WHERE id = ?').run(jmeno, user.id);
    }
    if (prijmeni !== undefined) {
        db.prepare('UPDATE users SET last_name = ? WHERE id = ?').run(prijmeni, user.id);
    }

    res.json({ ok: true });
});
```

---

## Express — DELETE endpoint

```javascript
// Smazání záznamu
app.delete('/api/moje-data/:id', (req, res) => {
    const user = getCurrentUser(req);
    if (!user) return res.status(401).json({ error: 'Unauthorized' });

    const { id } = req.params;

    const result = db.prepare('DELETE FROM cart_items WHERE id = ? AND cart_id IN (SELECT id FROM carts WHERE user_id = ?)').run(id, user.id);

    if (result.changes === 0) {
        return res.status(404).json({ error: 'Záznam nenalezen' });
    }

    res.json({ ok: true });
});
```

---

## SQLite — nová tabulka

Přidej do `src/db.js` do bloku `db.exec(...)`:

```javascript
// Nová tabulka pro recenze produktů
CREATE TABLE IF NOT EXISTS reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL,
  user_id INTEGER,
  rating INTEGER NOT NULL,          -- hodnocení 1-5
  comment TEXT,                     -- text recenze
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Index pro rychlé vyhledávání recenzí produktu
CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews(product_id);
```

---

## SQLite — přidání sloupce (migrace)

Přidej na konec migračního bloku v `src/db.js` (~řádek 260):

```javascript
// Přidání sloupce 'nova_vlastnost' do tabulky products
// Pattern z db.js:188 — bezpečná migrace bez ztráty dat
const colsProducts = db.pragma("table_info(products)").map(c => c.name);
if (!colsProducts.includes('nova_vlastnost')) {
    db.exec("ALTER TABLE products ADD COLUMN nova_vlastnost TEXT DEFAULT ''");
}

// Přidání INTEGER sloupce do orders
const colsOrders = db.pragma("table_info(orders)").map(c => c.name);
if (!colsOrders.includes('priority')) {
    db.exec("ALTER TABLE orders ADD COLUMN priority INTEGER DEFAULT 0");
}
```

---

## SQLite — CRUD operace

```javascript
// READ — jeden záznam
const produkt = db.prepare('SELECT * FROM products WHERE id = ?').get(123);
// produkt je objekt nebo undefined (pokud nenalezen)

// READ — více záznamů
const produkty = db.prepare('SELECT * FROM products WHERE stock > ?').all(0);
// produkty je pole objektů

// READ — s JOIN
const polozky = db.prepare(`
    SELECT oi.quantity, oi.price_cents, p.name
    FROM order_items oi
    JOIN products p ON p.id = oi.product_id
    WHERE oi.order_id = ?
`).all(orderId);

// CREATE
const result = db.prepare(
    'INSERT INTO reviews (product_id, user_id, rating, comment) VALUES (?, ?, ?, ?)'
).run(productId, userId, 5, 'Skvělý produkt!');
const newId = result.lastInsertRowid;

// UPDATE
db.prepare('UPDATE products SET stock = ? WHERE id = ?').run(newStock, productId);

// DELETE
const del = db.prepare('DELETE FROM reviews WHERE id = ? AND user_id = ?').run(id, userId);
if (del.changes === 0) { /* nenalezeno nebo není tvoje */ }
```

---

## SQLite — transakce

Použij pro operace, které musí proběhnout celé nebo vůbec (např. objednávka):

```javascript
// Vzor z server.js:717 (createOrderTransaction)
const vytvorObjednavku = db.transaction((userId, items) => {
    // 1. Ověř sklad
    for (const item of items) {
        const produkt = db.prepare('SELECT stock FROM products WHERE id = ?').get(item.id);
        if (!produkt || produkt.stock < item.qty) {
            throw new Error(`NEDOSTATEK_SKLADU:${item.id}`);
        }
    }

    // 2. Vlož objednávku
    const orderResult = db.prepare(
        'INSERT INTO orders (user_id, total_cents) VALUES (?, ?)'
    ).run(userId, totalCents);

    // 3. Vlož položky a sniž sklad
    for (const item of items) {
        db.prepare('INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)').run(orderResult.lastInsertRowid, item.id, item.qty);
        db.prepare('UPDATE products SET stock = stock - ? WHERE id = ?').run(item.qty, item.id);
    }

    return orderResult.lastInsertRowid;
});

try {
    const orderId = vytvorObjednavku(userId, items);
    res.json({ orderId });
} catch (e) {
    if (e.message.startsWith('NEDOSTATEK_SKLADU')) {
        res.status(409).json({ error: 'Nedostatek zboží na skladě' });
    } else {
        res.status(500).json({ error: 'Chyba serveru' });
    }
}
```

---

## JavaScript — fetch GET

Vzor z `assets/js/products.js`:

```javascript
// Načtení produktů z API a zobrazení
async function nactiProdukty() {
    try {
        const response = await fetch('/api/products');

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const produkty = await response.json();

        // Zpracování dat
        produkty.forEach(produkt => {
            console.log(produkt.name, produkt.price_cents / 100, 'Kč');
        });
    } catch (err) {
        console.error('Chyba při načítání produktů:', err);
    }
}

// Zavolej při načtení stránky
document.addEventListener('DOMContentLoaded', nactiProdukty);
```

---

## JavaScript — fetch POST s JSON

Vzor z checkout procesu:

```javascript
// Odeslání formuláře na server
async function odesliObjednavku(data) {
    try {
        const response = await fetch('/api/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            // Server vrátil chybu
            alert('Chyba: ' + (result.error || 'Neznámá chyba'));
            return;
        }

        // Úspěch
        window.location.href = `/Cart/thank-you.html?orderId=${result.orderId}`;
    } catch (err) {
        console.error('Chyba sítě:', err);
        alert('Nepodařilo se odeslat objednávku. Zkuste to znovu.');
    }
}
```

---

## JavaScript — DOM manipulace

```javascript
// Najít element
const btn = document.querySelector('.btn-pridat');
const container = document.getElementById('produkty-seznam');

// Změna textu / HTML
btn.textContent = 'Přidáno!';
container.innerHTML = '<p>Žádné produkty</p>';

// Přidání / odebrání CSS třídy
btn.classList.add('aktivni');
btn.classList.remove('aktivni');
btn.classList.toggle('aktivni');      // přidá pokud není, odebere pokud je

// Atributy
btn.setAttribute('disabled', 'true');
btn.removeAttribute('disabled');
const hodnota = btn.getAttribute('data-id');

// Dynamické vytvoření elementu
const karta = document.createElement('div');
karta.classList.add('product-card');
karta.innerHTML = `<h3>${produkt.name}</h3><p>${produkt.price_cents / 100} Kč</p>`;
container.appendChild(karta);

// Přístup k hodnotám formuláře
const email = document.getElementById('email-input').value.trim();
```

---

## JavaScript — event listenery

```javascript
// DOMContentLoaded — spustí se po načtení HTML (bez obrázků)
document.addEventListener('DOMContentLoaded', () => {
    console.log('Stránka načtena, JS inicializován');
    nactiProdukty();
});

// Click na tlačítko
document.querySelector('#btn-koupit').addEventListener('click', (event) => {
    event.preventDefault();          // zabrání výchozí akci (submit, redirect)
    pridatDoKosiku();
});

// Submit formuláře
document.querySelector('#checkout-form').addEventListener('submit', async (event) => {
    event.preventDefault();          // zabrání odeslání formuláře
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData);
    await odesliObjednavku(data);
});

// Delegování — jeden listener pro dynamicky přidané elementy
document.querySelector('.products-grid').addEventListener('click', (event) => {
    const btn = event.target.closest('.btn-quick-add');
    if (!btn) return;
    const productId = btn.dataset.id;
    pridatDoKosiku(productId);
});
```

---

## HTML — nová stránka (šablona)

Zkopíruj do `NovaSekce/index.html`:

```html
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Název stránky — DRIVE.</title>

    <!-- Globální styly -->
    <link rel="stylesheet" href="../assets/css/style.css">
    <!-- Styly specifické pro tuto stránku (volitelné) -->
    <link rel="stylesheet" href="../assets/css/nova-sekce.css">

    <!-- Font Awesome ikony -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>

<!-- Navigace (zkopíruj z jiné stránky a uprav aktivní odkaz) -->
<nav class="navbar">
    <div class="nav-container">
        <a href="/" class="logo"><span>DRIVE.</span></a>
        <ul class="nav-links">
            <li><a href="/" class="nav-link">Domů</a></li>
            <li><a href="/Products" class="nav-link">Produkty</a></li>
            <li><a href="/AboutUs" class="nav-link">O nás</a></li>
            <li><a href="/NovaSekce" class="nav-link active">Název sekce</a></li>
        </ul>
        <div class="nav-actions">
            <a href="#" class="cart-icon" id="cart-btn">
                <i class="fas fa-shopping-cart"></i>
                <span class="cart-badge" id="cart-count">0</span>
            </a>
        </div>
        <button class="hamburger" id="hamburger-btn">
            <span></span><span></span><span></span>
        </button>
    </div>
</nav>

<!-- Hlavní obsah stránky -->
<main>
    <section class="hero-section">
        <div class="container">
            <h1>Název stránky</h1>
            <p>Popis obsahu stránky.</p>
        </div>
    </section>

    <!-- Obsah stránky -->
    <section class="section">
        <div class="container">
            <h2>Sekce</h2>
            <p>Obsah sekce.</p>
        </div>
    </section>
</main>

<!-- Patička (zkopíruj z jiné stránky) -->
<footer>
    <div class="footer-container">
        <div class="footer-brand">
            <span>Drive.</span>
            <p>Energetické nápoje pro každý den.</p>
        </div>
        <div class="footer-links">
            <h4>Navigace</h4>
            <ul>
                <li><a href="/" class="footer-link">Domů</a></li>
                <li><a href="/Products" class="footer-link">Produkty</a></li>
                <li><a href="/AboutUs" class="footer-link">O nás</a></li>
            </ul>
        </div>
    </div>
    <div class="footer-bottom">
        <p>&copy; 2026 DRIVE. Energy. Všechna práva vyhrazena.</p>
    </div>
</footer>

<!-- Skripty -->
<script src="../assets/js/script.js"></script>
<script src="../assets/js/cookie-consent.js"></script>
<!-- Vlastní skript stránky (volitelné) -->
<script src="../assets/js/nova-sekce.js"></script>

</body>
</html>
```

---

## CSS — nová komponenta

Přidej do příslušného CSS souboru nebo nového `assets/css/nova-sekce.css`:

```css
/* ===================================
   Nova komponenta — popis k čemu slouží
   =================================== */

/* Kontejner komponenty */
.nova-komponenta {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 2rem;
    background: var(--light-bg);        /* CSS proměnná z :root */
    border-radius: var(--radius);       /* CSS proměnná z :root */
    box-shadow: var(--shadow);          /* CSS proměnná z :root */
    transition: var(--transition);      /* CSS proměnná z :root */
}

/* Hover stav */
.nova-komponenta:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-2px);
}

/* Nadpis v komponentě */
.nova-komponenta h3 {
    color: var(--text-primary);
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
}

/* Text v komponentě */
.nova-komponenta p {
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.6;
}

/* Tlačítko */
.nova-komponenta .btn-akce {
    background: var(--text-primary);
    color: #ffffff;
    padding: 10px 20px;
    border-radius: 6px;
    border: none;
    cursor: pointer;
    transition: var(--transition);
}

.nova-komponenta .btn-akce:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}

/* Responzivní — tablet */
@media (max-width: 992px) {
    .nova-komponenta {
        padding: 1.5rem;
    }
}

/* Responzivní — mobil */
@media (max-width: 576px) {
    .nova-komponenta {
        padding: 1rem;
    }
}
```

---

## Odeslání e-mailu z nového endpointu

Vzor ze `sendConfirmationEmail` v `server.js`:

```javascript
// Odeslání vlastního e-mailu z nového endpointu
// transporter je nakonfigurovaný v server.js:78

async function posliEmail(komu, predmet, htmlObsah) {
    // Pokud není nastaven SMTP, loguj mock
    if (!process.env.SMTP_HOST) {
        logger.info('email', '[MOCK EMAIL]', { to: komu, subject: predmet });
        return;
    }

    try {
        await transporter.sendMail({
            from: '"DRIVE. Energy" <drivewater.bussines@gmail.com>',
            to: komu,
            subject: predmet,
            html: htmlObsah
        });
        logger.info('email', 'Email odeslán', { to: komu });
    } catch (err) {
        logger.error('email', 'Chyba odesílání', { to: komu, message: err.message });
    }
}

// Použití v endpointu:
app.post('/api/kontakt', async (req, res) => {
    const { email, zprava } = req.body || {};
    if (!email || !zprava) return res.status(400).json({ error: 'Chybí data' });

    await posliEmail(
        'admin@drive.cz',
        'Nová zpráva od zákazníka',
        `<h2>Nová zpráva</h2><p>Od: ${email}</p><p>${zprava}</p>`
    );

    res.json({ ok: true });
});
```

---

## Validace formuláře (regex vzory)

Vzory z `Cart/checkout.html` a `server.js`:

```javascript
// E-mail
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
if (!emailRegex.test(email)) {
    return res.status(400).json({ error: 'Neplatný formát e-mailu' });
}

// České PSČ (12345 nebo 123 45)
const pscRegex = /^\d{3}\s?\d{2}$/;
if (!pscRegex.test(psc)) {
    chyby.push('Neplatné PSČ (formát: 123 45)');
}

// České telefonní číslo
const telefonRegex = /^(\+420)?\s?\d{3}\s?\d{3}\s?\d{3}$/;
if (telefon && !telefonRegex.test(telefon)) {
    chyby.push('Neplatné telefonní číslo');
}

// Jméno (min 2 znaky)
if (!jmeno || jmeno.trim().length < 2) {
    chyby.push('Jméno musí mít alespoň 2 znaky');
}

// Heslo (min 6 znaků)
if (!heslo || heslo.length < 6) {
    chyby.push('Heslo musí mít alespoň 6 znaků');
}

// Příklad kompletní validace
function validateForm(data) {
    const chyby = [];
    if (!data.email || !emailRegex.test(data.email)) chyby.push('Neplatný e-mail');
    if (!data.jmeno || data.jmeno.trim().length < 2) chyby.push('Neplatné jméno');
    if (!pscRegex.test(data.psc)) chyby.push('Neplatné PSČ');
    return chyby;  // prázdné pole = vše OK
}
```

---

## Přidání nového pole k produktu (end-to-end)

**Krok 1: Migrace v `src/db.js`** (~řádek 260):
```javascript
const cols = db.pragma("table_info(products)").map(c => c.name);
if (!cols.includes('kalorie')) {
    db.exec("ALTER TABLE products ADD COLUMN kalorie INTEGER DEFAULT 0");
}
```

**Krok 2: Seed data v `src/seed.js`** (přidej do každého produktového objektu):
```javascript
{ slug: 'cans-mango', ..., kalorie: 15 }
```

**Krok 3: Zahrnutí do API odpovědi v `server.js`** — automaticky (SELECT * vrátí všechny sloupce).

**Krok 4: Zobrazení na frontendu** v `assets/js/product-detail.js`:
```javascript
// V renderProduct funkci přidej:
if (produkt.kalorie) {
    const kalorieEl = document.createElement('p');
    kalorieEl.textContent = `Kalorická hodnota: ${produkt.kalorie} kcal / 100ml`;
    infoContainer.appendChild(kalorieEl);
}
```
