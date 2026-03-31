# OTÁZKY — Příprava na maturitu

> **Účel:** Předpokládané otázky s připravenými odpověďmi. Pro pojmy viz [POJMY.md](./POJMY.md), pro rychlý lookup [TAHAK.md](./TAHAK.md).
> Viz také: [MANUAL.md](./MANUAL.md) | [SNIPPETY.md](./SNIPPETY.md) | [architecture.md](./architecture.md)

---

## Architektura aplikace

### "Popište architekturu vaší aplikace."

Projekt je **Multi-Page Application (MPA)** s klasickým client-server modelem.

- **Frontend:** Statické HTML stránky (`index.html`, `Products/index.html`, `Cart/cart.html` atd.) s vanilla JavaScriptem a CSS. Žádný JavaScript framework — čistý DOM a Fetch API.
- **Backend:** Node.js server s Express 5 frameworkem (`server.js`). Obsluhuje jak statické soubory, tak REST API endpointy (cesta `/api/...`).
- **Databáze:** SQLite uložená v souboru `data/site.db`. Přístup přes knihovnu `better-sqlite3`.
- **Komunikace:** Frontend volá backend přes HTTP (JSON REST API). Např. `fetch('/api/products')` vrátí JSON seznam produktů.

Architektura je záměrně jednoduchá — vhodná pro školní projekt, bez buildovacích nástrojů.

---

### "Proč jste zvolil tuto architekturu? Proč ne React nebo Vue?"

MPA s vanilla JS jsem zvolil, protože:
1. **Žádný build krok** — stačí `node server.js`, není potřeba Webpack/Vite
2. **Výuka základů** — DOM manipulace, Fetch API, asynchronní JS bez abstrakcí frameworku
3. **Přehlednost** — každá stránka je samostatný HTML soubor, jasná struktura
4. **Rychlost vývoje** — bez konfigurace, okamžitý start

Nevýhoda: složitější sdílení stavu mezi stránkami (řeším localStorage).

---

### "Co je MPA vs SPA? Jaký je rozdíl?"

| | MPA (Multi-Page Application) | SPA (Single-Page Application) |
|---|---|---|
| **Stránky** | Více HTML souborů | Jeden HTML soubor |
| **Navigace** | Browser načte novou stránku | JS přepíše obsah bez reloadu |
| **Framework** | Žádný nutný | React, Vue, Angular |
| **Build** | Není potřeba | Webpack/Vite nutný |
| **SEO** | Jednoduché | Složitější |
| **Příklad** | Náš projekt | Gmail, Facebook |

---

### "Co je REST API a jak ho používáte?"

**REST API** je způsob komunikace mezi frontendem a backendem přes HTTP. Každý zdroj (produkt, objednávka) má svou URL a operace se provádí HTTP metodami.

V projektu máme **40+ endpointů** pod prefixem `/api/`:
- `GET /api/products` — seznam všech produktů
- `GET /api/products/:slug` — detail jednoho produktu
- `POST /api/checkout` — vytvoření objednávky
- `POST /api/auth/login` — přihlášení
- `PUT /api/user/profile` — aktualizace profilu

Frontend volá API pomocí `fetch()`:
```javascript
const response = await fetch('/api/products');
const produkty = await response.json();
```

---

## Databáze

### "Popište databázové schéma vašeho projektu."

Databáze má **11 tabulek** v SQLite souboru `data/site.db`:

**Jádro e-shopu:**
- `products` — produkty (slug, name, price_cents, image, stock, color, features jako JSON)
- `orders` — objednávky (user_id, email, adresa, payment_method, total_cents, discount_code, status)
- `order_items` — položky objednávek (order_id, product_id, quantity, price_cents)

**Uživatelé a přihlášení:**
- `users` — uživatelé (email, password_hash, jméno, adresa)
- `sessions` — přihlašovací tokeny (user_id, token UUID, expires_at)
- `password_resets` — tokeny pro reset hesla (email, token, expires_at)

**Košík:**
- `carts` — košíky (session_id, user_id)
- `cart_items` — položky v košíku (cart_id, product_id, quantity, is_subscription)

**Ostatní:**
- `user_subscriptions` — předplatné (user_id, product_id, status, next_billing_date)
- `subscribers` — newsletter odběratelé
- `discounts` — slevové kódy (code, discount_percent, active)

---

### "Co je normalizace databáze? Jak ji vidíte ve vašem projektu?"

Normalizace = rozdělení dat do tabulek tak, aby se data **neduplikovala**. Každá informace je na jednom místě.

**Příklad v projektu:**
- ❌ Bez normalizace: `orders` by obsahoval přímo `product_name, product_price` → při změně ceny by historické objednávky měly špatnou cenu
- ✅ S normalizací: `order_items` ukládá `price_cents` v době nákupu → historické ceny jsou zachovány

Tabulky `orders` a `order_items` jsou v **3. normální formě** — každá informace je na jednom místě.

---

### "Jak fungují migrace ve vašem projektu?"

Migrace = bezpečná změna struktury DB bez ztráty dat.

Při každém startu serveru `src/db.js` zkontroluje, zda existují všechny potřebné sloupce:

```javascript
// Zkontroluj existující sloupce
const cols = db.pragma("table_info(products)").map(c => c.name);
// Pokud sloupec chybí, přidej ho
if (!cols.includes('color')) {
    db.exec("ALTER TABLE products ADD COLUMN color TEXT DEFAULT ''");
}
```

Tím je zajištěno, že **starší databáze** (bez nového sloupce) bude automaticky aktualizována.

---

### "Proč SQLite? Jaká jsou omezení?"

**Výhody:**
- Zero-config — jeden soubor, žádný server
- Synchronní API (bez async/await) — jednodušší kód
- Ideální pro malé projekty

**Omezení:**
- Špatná souběžnost při mnoha zápisech najednou
- Na Render.com free tier je DB dočasná (při restartu se smaže)
- Pro produkci s tisíci uživateli → PostgreSQL/MySQL

---

## Autentizace a bezpečnost

### "Jak funguje přihlašování ve vašem projektu?"

1. Uživatel vyplní e-mail a heslo, klikne "Přihlásit"
2. Frontend odešle `POST /api/auth/login` s `{ email, password }`
3. Server najde uživatele v DB: `SELECT * FROM users WHERE email = ?`
4. Porovná heslo s bcrypt hashem: `bcrypt.compare(password, user.password_hash)`
5. Při úspěchu vytvoří **session token** (UUID v4) a uloží ho do DB s expirací za 30 dní
6. Token se pošle zpět jako **httpOnly cookie** `auth_token`
7. Při každém dalším requestu server přečte cookie a ověří token v DB

---

### "Co je bcrypt? Proč ho používáte pro hesla?"

**bcrypt** je hashovací algoritmus speciálně navržený pro hesla. Záměrně je **pomalý** — odolný vůči brute-force útokům.

Klíčové vlastnosti:
- **Jednosměrné** — z hashe nelze získat původní heslo
- **Salt** — každé heslo dostane náhodná data → stejné heslo = různý hash
- **Cost factor (rounds)** — čím více iterací, tím bezpečnější

V projektu: `bcrypt.hash(password, 10)` — 10 rounds (server.js:821).

```javascript
// Hashování při registraci
const hash = await bcrypt.hash('mojeHeslo123', 10);
// hash = '$2b$10$...'  (60 znaků, nelze zpětně dekódovat)

// Ověření při přihlášení
const ok = await bcrypt.compare('mojeHeslo123', hash);  // true
```

---

### "Jaká bezpečnostní opatření jste implementoval?"

1. **Hashování hesel** — bcrypt s 10 rounds (server.js:821)
2. **Rate limiting** — max 5 pokusů o přihlášení za 15 minut per IP → ochrana před brute-force (server.js:39-59)
3. **httpOnly cookies** — JavaScript v prohlížeči nemůže číst `auth_token` → ochrana před XSS
4. **SameSite cookies** — cookie se neposílá z cizích domén → ochrana před CSRF
5. **Signed cookies** — `dev_token` je podepsán serverovým klíčem → nelze falšovat
6. **Parametrizované SQL dotazy** — `db.prepare('... WHERE email = ?').get(email)` → ochrana před SQL injection
7. **GDPR smazání** — endpoint DELETE /api/user/delete smaže všechna data uživatele
8. **Reset token expiry** — tokeny pro reset hesla expirují za 1 hodinu

---

### "Co je rate limiting a proč ho máte?"

**Rate limiting** = omezení počtu requestů z jedné IP adresy za časové okno.

V projektu (server.js:39-59):
- **Okno:** 15 minut
- **Limit:** 5 pokusů
- **Cíl:** Ochrana před brute-force útoky na přihlašování

Při překročení server vrátí **HTTP 429 Too Many Requests**.

```javascript
if (data.count >= 5) {
    return res.status(429).json({ error: 'Too many login attempts' });
}
```

---

### "Jak funguje reset hesla?"

1. Uživatel zadá e-mail na `/Account/forgot-password.html`
2. `POST /api/auth/forgot-password` → server vygeneruje **UUID token** s expirací za 1 hodinu
3. Token se uloží do tabulky `password_resets`
4. Na e-mail přijde odkaz: `http://localhost:3000/Account/reset-password.html?token=...`
5. Uživatel zadá nové heslo, odešle `POST /api/auth/reset-password`
6. Server ověří token (existence + nepropadalost), aktualizuje bcrypt hash, smaže token

> **Bezpečnost:** Na nezaregistrovaný e-mail server vrátí stejnou odpověď — neodhaluje existenci účtu.

---

## Košík a checkout

### "Jak funguje košík v projektu?"

Košík funguje ve **dvou módech** (dual-mode):

**1. localStorage (nepřihlášení uživatelé):**
- Data uložena v prohlížeči: `localStorage.setItem('drive_cart', JSON.stringify(data))`
- Přetrvávají i po zavření záložky
- Formát: `{ "cans-mango": { quantity: 2, price: 599, name: "CANS Mango", ... } }`

**2. Serverový DB košík (přihlášení uživatelé):**
- Po přihlášení se localStorage košík synchronizuje na server: `POST /api/user/cart/sync`
- Košík uložen v tabulkách `carts` a `cart_items`
- Dostupný na více zařízeních

Při odhlášení se server košík odpojí od uživatele (ochrana před "ghost" předplatnými).

---

### "Popište objednávkový proces (checkout)."

Checkout je **4-krokový flow**:

```
Krok 1: Cart/cart.html     → zobrazení košíku, slevový kód
Krok 2: Cart/checkout.html → formulář (kontakty, adresa, platba)
Krok 3: Cart/summary.html  → shrnutí před odesláním
Krok 4: Cart/thank-you.html → potvrzení s ID objednávky
```

**Na serveru při `POST /api/checkout`:**
1. Validace vstupů (email, jméno, adresa, PSČ)
2. Načtení produktů z DB (aktuální ceny, ne z requestu!)
3. Validace a aplikace slevového kódu
4. Databázová **transakce**: kontrola skladu → INSERT orders → INSERT order_items → UPDATE stock
5. Generování **PDF faktury** (PDFKit)
6. Odeslání **potvrzovacího e-mailu** s PDF přílohou
7. Vrácení `{ orderId }` frontendu

---

### "Jak funguje synchronizace košíku?"

Problém: uživatel dá zboží do košíku bez přihlášení (localStorage), pak se přihlásí.

Řešení:
1. Při přihlášení frontend zavolá `POST /api/user/cart/sync` s obsahem localStorage košíku
2. Server uloží položky do tabulky `cart_items` vázané na `user_id`
3. Při příštím přihlášení (jiné zařízení) frontend zavolá `GET /api/user/cart` a načte serverový košík

Implementace v `assets/js/cart.js` — metody `syncCartToServer()` a `loadCartFromServer()`.

---

## Frontend

### "Proč jste použil vanilla JavaScript a ne React?"

1. **Školní projekt** — cílem bylo ukázat znalost fundamentů
2. **Žádný build krok** — jednodušší nasazení
3. **Menší overhead** — žádný JS framework ke stažení
4. **Přímá práce s DOM** — lepší pochopení jak browser funguje

Pokud by projekt rostl (desítky stránek, komplexní interakce), přechod na React by byl rozumný.

---

### "Co jsou CSS custom properties (proměnné) a jak je používáte?"

CSS custom properties = proměnné definované v `:root` (globální scope), dostupné v celém souboru.

```css
/* Definice v :root (assets/css/style.css:2-16) */
:root {
    --primary-light: #A9ECFF;
    --text-primary: #27445C;
}

/* Použití */
.navbar { background: var(--primary-light); }
.button { color: var(--text-primary); }
```

**Výhoda:** Změna barvy na jednom místě → projeví se všude. Základem pro themování.

---

### "Jak jste implementoval responzivní design?"

Responzivita je řešena přes **CSS media queries** na dvou breakpointech:

```css
/* Tablet: 992px */
@media (max-width: 992px) {
    .products-grid { grid-template-columns: repeat(2, 1fr); }
    .navbar { /* mobilní nav */ }
}

/* Mobil: 576px */
@media (max-width: 576px) {
    .products-grid { grid-template-columns: 1fr; }
    .hero-title { font-size: 2rem; }
}
```

Používám **CSS Grid** a **Flexbox** — přirozeně se přizpůsobují dostupné šířce.

---

## E-maily a PDF

### "Jak generujete faktury?"

Faktury se generují pomocí knihovny **PDFKit** přímo v Node.js.

Funkce `generateInvoicePDF()` v `server.js:88`:
1. Vytvoří nový PDF dokument
2. Nastaví font TelkaTRIAL (vlastní OTF font)
3. Vypíše hlavičku "DRIVE.", číslo objednávky
4. Dodavatel: "DRIVE Energy s.r.o., Václavské náměstí 1, Praha 1"
5. Zákazník: jméno, adresa z objednávky
6. Tabulka položek: název, množství, cena
7. Celková cena
8. Vrátí Buffer s PDF → odešle jako příloha e-mailu

---

### "Jak odesíláte e-maily?"

Pomocí knihovny **Nodemailer** s SMTP protokolem.

Konfigurace v `server.js:78-86`:
```javascript
const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,  // ze .env souboru
    port: 587,
    auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS }
});
```

Typy e-mailů v projektu:
- **Potvrzení objednávky** — s PDF fakturou jako příloha
- **Reset hesla** — odkaz s jednorázovým tokenem (platnost 1h)
- **Newsletter uvítání** — se slevovým kódem DRIVE10
- **Hromadný newsletter** — admin funkce

Pokud `SMTP_HOST` není nastaven → e-maily se logují jako `[MOCK EMAIL]` do konzole.

---

## Praktické otázky

### "Jak byste přidal nový produkt do e-shopu?"

1. Otevři `src/seed.js`
2. Přidej slug do `mustHaveSlugs`: `['cans-mango', ..., 'novy-produkt']`
3. Přidej objekt produktu do pole `products`:
   ```javascript
   {
     slug: 'novy-produkt',
     name: 'CANS Nová Příchuť — 24 × 330ml',
     price_cents: 59900,        // 599 Kč
     image: '/assets/img/products/novy.png',
     hover_image: '/assets/img/products/novy-hover.jpg',
     description: 'Popis.',
     features: JSON.stringify(['Vlastnost 1', 'Vlastnost 2']),
     stock: 100,
     color: 'mango'
   }
   ```
4. Nahraj obrázky do `assets/img/products/`
5. Smaž `data/site.db` a restartuj server → produkt se automaticky seeduje

---

### "Jak byste přidal novou stránku na web?"

1. Vytvoř složku a `index.html` (zkopíruj strukturu z jiné stránky)
2. Uprav navigaci (navbar) ve **všech HTML souborech** — přidej odkaz na novou stránku
3. Volitelně vytvoř CSS soubor `assets/css/nova-sekce.css` a JS soubor `assets/js/nova-sekce.js`
4. Prolinkuj CSS a JS v HTML souboru nové stránky

> Express automaticky servíruje nový soubor přes `express.static()` — není potřeba přidávat route do `server.js`.

---

### "Jak byste změnil barevné schéma webu?"

1. Otevři `assets/css/style.css`
2. Najdi `:root` blok (řádky 2–16)
3. Uprav hodnoty CSS proměnných:
   ```css
   :root {
       --primary-light: #NOVÁ_BARVA;
       --text-primary: #NOVÁ_BARVA;
   }
   ```
4. Udělej totéž v dalších CSS souborech (každý má vlastní `:root`):
   `products.css`, `about.css`, `product-detail.css`, `cart.css`, `account.css`

Hotové alternativy jsou v [ALTERNATIVY.md](./ALTERNATIVY.md).

---

### "Jak byste přidal nový API endpoint?"

1. Otevři `server.js`
2. Před řádek 1292 (404 handler) přidej:
   ```javascript
   app.get('/api/nova-funkce', (req, res) => {
       const data = db.prepare('SELECT * FROM products').all();
       res.json(data);
   });
   ```
3. Restartuj server (`node server.js`)
4. Otestuj: `http://localhost:3000/api/nova-funkce`

Podrobné šablony viz [SNIPPETY.md](./SNIPPETY.md).

---

### "Jak byste přidal slevový kód?"

**Přes admin rozhraní** (aktivuj dev mód na `/dev-enable`, heslo: `kO2N37Ac`):
- Na hlavní stránce se zobrazí admin panel pro správu slevových kódů

**Přes API** (curl nebo Postman):
```bash
curl -X POST http://localhost:3000/api/admin/discounts \
  -H "Content-Type: application/json" \
  -d '{"code": "LETO2026", "discount_percent": 15}'
```

**Přes seed data** v `src/seed.js` — přidej INSERT příkaz.

---

### "Co byste udělal jinak, kdybystě projekt dělali znovu?"

*(Ukázkové odpovědi — přizpůsob svému skutečnému názoru)*

1. **TypeScript** místo plain JavaScript — typová bezpečnost, lepší autocomplete
2. **PostgreSQL** místo SQLite — pro produkci s více uživateli
3. **React nebo Next.js** pro frontend — složitý stav košíku by byl přehlednější
4. **JWT tokeny** místo session DB — stateless autentizace
5. **Testy** (Jest/Vitest) — automatické ověření že API funguje správně

---

## Obecné technické otázky

### "Vysvětlete HTTP metody a jak je používáte."

| Metoda | Účel | Příklad v projektu |
|---|---|---|
| `GET` | Načtení dat, bez vedlejších efektů | `GET /api/products` → seznam produktů |
| `POST` | Vytvoření nového záznamu | `POST /api/checkout` → nová objednávka |
| `PUT` | Nahrazení celého záznamu | `PUT /api/user/profile` → aktualizace profilu |
| `PATCH` | Částečná aktualizace | `PATCH /api/cart` → změna množství |
| `DELETE` | Smazání záznamu | `DELETE /api/cart/:id` → odebrání z košíku |

---

### "Co jsou HTTP stavové kódy? Uveďte příklady z projektu."

- `200 OK` — úspěch (načtení produktů)
- `201 Created` — vytvořeno (nová objednávka, registrace)
- `400 Bad Request` — neplatný vstup (chybí email)
- `401 Unauthorized` — nepřihlášen (přístup k profilu)
- `403 Forbidden` — zakázáno (admin endpoint bez oprávnění)
- `404 Not Found` — nenalezeno (neexistující URL)
- `409 Conflict` — konflikt (email již existuje)
- `429 Too Many Requests` — rate limit překročen
- `500 Internal Server Error` — chyba serveru

---

### "Co je middleware v Expressu?"

Middleware je funkce, která **se spustí před handlerem endpointu**. Dostane `req`, `res` a `next`.

```javascript
// Příklad middleware z projektu — rate limiter
const rateLimiter = (req, res, next) => {
    // Zkontroluj počet pokusů...
    if (data.count >= 5) {
        return res.status(429).json({ error: 'Too many requests' });
    }
    next();  // Pokračuj na handler
};

// Použití — middleware se spustí před handlerem
app.post('/api/auth/login', rateLimiter, async (req, res) => { ... });
```

Globální middleware (pro každý request): `app.use(compression())`, `app.use(cookieParser())`.
