# POJMY — Slovníček technických pojmů

> **Účel:** Česká vysvětlení technických pojmů s vazbou na tento projekt. Pro rychlý lookup viz [TAHAK.md](./TAHAK.md).
> Viz také: [MANUAL.md](./MANUAL.md) | [SNIPPETY.md](./SNIPPETY.md) | [OTAZKY.md](./OTAZKY.md)

---

## Webová architektura

### MPA (Multi-Page Application)
Aplikace tvořená **více samostatnými HTML stránkami**. Každý klik na odkaz načte novou stránku ze serveru.

- **Náš projekt:** MPA — máme oddělené soubory `index.html`, `Products/index.html`, `Cart/cart.html` atd.
- **Výhody:** Jednodušší, bez buildovacího kroku, přátelské k SEO
- **Nevýhody:** Celá stránka se překreslí při každé navigaci

### SPA (Single-Page Application)
Aplikace v **jednom HTML souboru** — obsah se mění dynamicky JavaScriptem bez reloadu stránky (React, Vue, Angular).

- **Náš projekt:** Není SPA — my máme MPA s vanilla JS
- **Výhody:** Rychlejší navigace, lepší UX pro komplexní aplikace
- **Nevýhody:** Složitější build, SEO problémy, více JS frameworku

### REST API
**RE**presentational **S**tate **T**ransfer — způsob komunikace mezi frontendem a backendem přes HTTP.

- Každý endpoint má URL (např. `/api/products`) a HTTP metodu (GET, POST…)
- Server vrací JSON data
- **Náš projekt:** 40+ REST endpointů v `server.js`, všechny pod prefixem `/api/`

### CRUD
Zkratka pro základní databázové operace:
- **C**reate → POST + `INSERT INTO`
- **R**ead → GET + `SELECT`
- **U**pdate → PUT/PATCH + `UPDATE`
- **D**elete → DELETE + `DELETE FROM`

### Middleware
Funkce v Expressu, která **se spouští před samotným handlerem endpointu**. Zpracuje request a buď pokračuje dál (`next()`) nebo vrátí odpověď.

- **Náš projekt:** `rateLimiter` (server.js:40), `requireAdmin` (server.js:61), `cookieParser`, `compression`, `morgan`

```javascript
// Middleware — spustí se před každým POST /api/auth/login
app.post('/api/auth/login', rateLimiter, async (req, res) => { ... });
//                          ^^^^^^^^^^^  ← toto je middleware
```

---

## HTTP

### HTTP metody
| Metoda | Účel | Příklad v projektu |
|---|---|---|
| `GET` | Načtení dat | `GET /api/products` — seznam produktů |
| `POST` | Vytvoření nového záznamu | `POST /api/checkout` — nová objednávka |
| `PUT` | Nahrazení celého záznamu | `PUT /api/user/profile` — aktualizace profilu |
| `PATCH` | Částečná aktualizace | `PATCH /api/cart` — změna množství v košíku |
| `DELETE` | Smazání záznamu | `DELETE /api/cart/:itemId` — odebrání z košíku |

### HTTP stavové kódy
| Kód | Význam | Kdy v projektu |
|---|---|---|
| `200 OK` | Úspěch | Načtení produktů, přihlášení |
| `201 Created` | Vytvořeno | Nová objednávka, nový uživatel |
| `400 Bad Request` | Chybný vstup | Chybí email/heslo, neplatné PSČ |
| `401 Unauthorized` | Nepřihlášen | Přístup k profilu bez přihlášení |
| `403 Forbidden` | Zakázáno | Admin endpoint bez dev tokenu |
| `404 Not Found` | Nenalezeno | Neexistující produkt/stránka |
| `409 Conflict` | Konflikt | Email už existuje (`UNIQUE constraint`) |
| `429 Too Many Requests` | Rate limit | 5+ neúspěšných přihlášení za 15 min |
| `500 Internal Server Error` | Chyba serveru | Výjimka v kódu, DB chyba |

### Cookies
Malé soubory dat uložené v prohlížeči. Server je nastaví v hlavičce odpovědi.

- **`auth_token`** — přihlašovací token (httpOnly, sameSite: lax, 30 dní)
- **`drive_session`** — anonymní session pro košík (httpOnly)
- **`dev_token`** — admin přístup (signed = podepsaný serverem, httpOnly)
- **`dev_mode`** — zobrazení admin UI (není httpOnly — JS ho čte)

**`httpOnly`** = JavaScript v prohlížeči cookie nevidí → ochrana před XSS  
**`sameSite: lax`** = cookie se posílá jen ze stejné domény → ochrana před CSRF  
**`signed`** = obsah je podepsán serverovým klíčem → nelze falšovat

### Request Headers / Response Headers
HTTP hlavičky — metadata přenášená spolu s requestem/odpovědí.

- `Content-Type: application/json` — tělo je JSON
- `Cache-Control: no-store` — prohlížeč nemá cachovat obsah
- `Set-Cookie` — server nastavuje cookie

---

## Backend / Node.js

### Node.js
JavaScript runtime pro server. Umožňuje spouštět JS mimo prohlížeč.

- **Verze v projektu:** 22.2.0 (LTS)
- **Spuštění:** `node server.js`
- **Event loop** — Node.js je jednovláknový, ale asynchronní operace (I/O, síť, DB) zpracovává neblokujícím způsobem

### Express
Webový framework pro Node.js. Zjednodušuje tvorbu HTTP serveru a routování.

```javascript
const app = express();
app.get('/url', handler);     // registrace route
app.use(middleware);          // globální middleware
app.listen(3000, callback);   // spuštění na portu
```

- **Verze v projektu:** Express 5.1.0

### npm (Node Package Manager)
Správce balíčků pro Node.js.

- `npm install` — nainstaluje závislosti z `package.json` do `node_modules/`
- `package.json` — seznam závislostí, skripty (`npm start`)
- `node_modules/` — složka s knihovnami (necommituje se do Gitu)

### Moduly (CommonJS)
Systém importu/exportu souborů v Node.js.

```javascript
// Export (src/db.js)
module.exports = { db };

// Import (server.js)
const { db } = require('./src/db');
```

---

## Databáze

### SQLite
Jednoduchá relační databáze uložená v **jednom souboru** (`data/site.db`). Nevyžaduje samostatný databázový server.

- **Knihovna:** `better-sqlite3` (synchronní API)
- **Soubor DB:** `data/site.db`
- Ideální pro projekty s nižším provozem a jednoduchou správou

### WAL mód (Write-Ahead Logging)
Mód SQLite pro **souběžné čtení** — čtenáři neblokují zapisovatele.

```javascript
db.pragma('journal_mode = WAL');  // src/db.js řádek 12
```

### SQL příkazy
```sql
SELECT * FROM products;                     -- načtení všech produktů
SELECT * FROM products WHERE slug = ?;      -- načtení jednoho produktu
INSERT INTO orders (email, total) VALUES (?, ?);  -- nová objednávka
UPDATE products SET stock = stock - 1 WHERE id = ?;  -- snížení skladu
DELETE FROM sessions WHERE token = ?;       -- smazání session
```

### JOIN
Spojení dat ze dvou tabulek přes cizí klíč.

```sql
-- Načtení položek košíku s detaily produktu
SELECT ci.quantity, p.name, p.price_cents
FROM cart_items ci
JOIN products p ON p.id = ci.product_id
WHERE ci.cart_id = ?
```

Používá se v projektu pro košík (`getCartItems` — server.js:310), historii objednávek, předplatné.

### Foreign Key (Cizí klíč)
Odkaz z jedné tabulky do druhé. Zajišťuje **referenční integritu**.

```sql
order_id INTEGER NOT NULL,
FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
-- ON DELETE CASCADE = při smazání objednávky se smažou i položky
```

### Index
Datová struktura pro **rychlé vyhledávání** v tabulce.

```sql
CREATE INDEX idx_products_slug ON products(slug);
-- Zrychluje: SELECT * FROM products WHERE slug = 'cans-mango'
```

### Migrace
Úprava existujícího databázového schématu bez ztráty dat.

```javascript
// Pattern v src/db.js:188
const cols = db.pragma("table_info(products)").map(c => c.name);
if (!cols.includes('color')) {
    db.exec("ALTER TABLE products ADD COLUMN color TEXT DEFAULT ''");
}
```

### Transakce
Skupina SQL operací, které **buď proběhnou všechny, nebo žádná** (atomicita).

```javascript
// Pattern v server.js:717
const createOrder = db.transaction(() => {
    // INSERT orders
    // INSERT order_items  
    // UPDATE products SET stock = stock - 1
    // Pokud cokoli selže → vše se vrátí zpět (rollback)
});
createOrder(); // spuštění transakce
```

---

## Bezpečnost

### Hashování vs šifrování
| | Hashování | Šifrování |
|---|---|---|
| **Směr** | Jednosměrné (nelze zpětně) | Obousměrné (lze dešifrovat) |
| **Účel** | Ověření hesla | Přenos tajných dat |
| **Příklad** | bcrypt, SHA-256 | AES, RSA |
| **V projektu** | bcrypt pro hesla | — |

### bcrypt
Hashovací algoritmus speciálně navržený pro hesla. Záměrně pomalý (odolný vůči brute-force).

- **Salt** = náhodná data přidaná k heslu před hashováním → stejné heslo = různý hash
- **Rounds (cost factor)** = počet iterací → čím více, tím pomalejší a bezpečnější
- **Projekt:** 10 rounds (`bcrypt.hash(password, 10)` — server.js:821)

```javascript
// Hashování (při registraci)
const hash = await bcrypt.hash(password, 10);

// Ověření (při přihlášení)
const ok = await bcrypt.compare(password, user.password_hash);
```

### Rate Limiting
Omezení počtu requestů z jedné IP adresy za časové okno. Ochrana před brute-force útoky.

- **Projekt:** Max 5 pokusů o přihlášení za 15 minut (server.js:39–59)
- Při překročení → HTTP 429

### XSS (Cross-Site Scripting)
Útok vložením škodlivého JavaScriptu do stránky. Může ukrást cookies/data.

- **Ochrana:** httpOnly cookies (JS je nevidí), escapování uživatelského vstupu
- **Projekt:** httpOnly cookie na `auth_token`

### CSRF (Cross-Site Request Forgery)
Útok, kdy cizí stránka odešle request jménem přihlášeného uživatele.

- **Ochrana:** `sameSite: lax` cookies → cookie se neposílá z cizích stránek
- **Projekt:** nastaveno na `auth_token` a `drive_session`

### SQL Injection
Útok vložením SQL kódu do vstupního pole.

- **Ochrana:** parametrizované dotazy (nikdy nekonkatenovat SQL string)
- **Projekt:** `db.prepare('SELECT * FROM users WHERE email = ?').get(email)` — `?` = parametr

### GDPR
Nařízení EU o ochraně osobních dat. Uživatel má právo na výmaz svých dat.

- **Projekt:** Endpoint `DELETE /api/user/delete` — smaže sessions, předplatné, data košíku, odhlásí newsletter, anonymizuje objednávky, smaže uživatele (server.js:~1040)

---

## Frontend

### DOM (Document Object Model)
Objektová reprezentace HTML stránky v paměti prohlížeče. JavaScript ho může číst a měnit.

```javascript
document.querySelector('.btn')          // najde první .btn
document.getElementById('cart-count')   // najde #cart-count
element.innerHTML = '<p>Ahoj</p>';      // změna obsahu
element.classList.add('active');        // přidání třídy
```

### CSS Custom Properties (proměnné)
Proměnné definované v CSS, sdílené napříč soubory.

```css
:root {
    --primary-light: #A9ECFF;   /* definice proměnné */
}
.button {
    background: var(--primary-light);  /* použití */
}
```

- **Projekt:** Definovány v `:root` v každém CSS souboru (řádky 2–16)

### Responzivní design
Web přizpůsobující se různým velikostem obrazovky pomocí **media queries**.

```css
/* Desktop: výchozí styl */
.products-grid { grid-template-columns: repeat(3, 1fr); }

/* Tablet */
@media (max-width: 992px) {
    .products-grid { grid-template-columns: repeat(2, 1fr); }
}

/* Mobil */
@media (max-width: 576px) {
    .products-grid { grid-template-columns: 1fr; }
}
```

### localStorage
Úložiště v prohlížeči — data přetrvají i po zavření záložky (na rozdíl od `sessionStorage`).

```javascript
localStorage.setItem('cart', JSON.stringify(cartData));   // uložení
const cart = JSON.parse(localStorage.getItem('cart'));    // načtení
localStorage.removeItem('cart');                          // smazání
```

- **Projekt:** Košík (`cart`), checkout data (`checkoutData`), cookie consent

### Fetch API
Moderní způsob HTTP requestů z JavaScriptu (asynchronní, vrací Promise).

```javascript
// GET
const response = await fetch('/api/products');
const products = await response.json();

// POST
const response = await fetch('/api/checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items, email })
});
```

---

## Nástroje a knihovny

### Git
Systém pro správu verzí kódu. Sleduje změny souborů.

```bash
git status              # co se změnilo
git add soubor.js       # připravit k commitu
git commit -m "popis"   # uložit změnu
git push                # nahrát na GitHub
git pull                # stáhnout změny
```

### SMTP (Simple Mail Transfer Protocol)
Protokol pro odesílání e-mailů.

- **Projekt:** Nodemailer knihovna, konfigurace v `.env` (`SMTP_HOST`, `SMTP_USER`, `SMTP_PASS`)
- **Vývojový mock:** `smtp.ethereal.email` — e-maily se neposílají, jen logují
- Bez nastavení SMTP → výpis `[MOCK EMAIL]` v konzoli

### PDFKit
Node.js knihovna pro generování PDF souborů.

- **Projekt:** Generování faktur při checkoutu (`generateInvoicePDF` — server.js:88)
- Faktura se odesílá jako příloha e-mailu

### Nodemailer
Node.js knihovna pro odesílání e-mailů přes SMTP.

- **Projekt:** Konfigurován v server.js:78–86, funkce `sendEmail` a `sendConfirmationEmail`

### Morgan
HTTP request logger pro Express. Loguje každý příchozí request.

- **Projekt:** `app.use(morgan('combined', { stream: logger.morganStream }))` — server.js:34
- Výstup: `logs/combined.log`

### UUID (Universally Unique Identifier)
Náhodný unikátní identifikátor (128 bitů, formát `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`).

- **Projekt:** Session tokeny, reset tokeny → `const token = uuidv4()` (knihovna `uuid`)

### better-sqlite3
Synchronní Node.js driver pro SQLite. Na rozdíl od jiných driverů nepotřebuje `async/await`.

```javascript
const db = new Database('data/site.db');
db.prepare('SELECT * FROM products').all();  // synchronní
```
