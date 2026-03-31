# TAHAK — Rychlá reference pro maturitu

> **Účel:** Najdi odpověď za 30 sekund. Pro podrobnosti viz [MANUAL.md](./MANUAL.md).
> Viz také: [ALTERNATIVY.md](./ALTERNATIVY.md) | [SNIPPETY.md](./SNIPPETY.md) | [POJMY.md](./POJMY.md) | [OTAZKY.md](./OTAZKY.md)

---

## Spuštění projektu

```bash
cd "Housa Jakub"        # správná složka!
npm install             # jen pokud chybí node_modules
node server.js          # spuštění serveru
# → http://localhost:3000
```

| Co | Hodnota |
|---|---|
| **Port** | `3000` → `http://localhost:3000` |
| **Demo účet** | `ucitel@spskladno.cz` / heslo: `ucitel` |
| **Dev mód heslo** | `kO2N37Ac` (přejít na `/dev-enable`) |
| **Slevový kód** | `DRIVE10` (10 % sleva) |
| **Reset databáze** | smazat `data/site.db` → restartovat server |
| **Logy** | `logs/combined.log`, `logs/error.log`, `logs/orders.log` |

---

## Kde co najdu — rychlý lookup

| Chci změnit... | Soubor | Kde přibližně |
|---|---|---|
| **Barvy webu** | `assets/css/style.css` | řádky 2–16 (`:root`) |
| **Barvy — ostatní CSS** | `products.css`, `about.css`, `product-detail.css`, `cart.css`, `account.css` | řádky 2–16 každý |
| **Produkty (přidat/upravit)** | `src/seed.js` | pole `products` |
| **Ceny produktů** | `src/seed.js` | atribut `price_cents` (v haléřích!) |
| **Obrázky produktů** | `src/seed.js` | `image`, `hover_image`, `seedProductImages()` |
| **API endpoint** | `server.js` | před řádek 1292 (před 404 handler) |
| **Checkout formulář validace** | `Cart/checkout.html` | JavaScript sekce, funkce `validateForm()` |
| **Navbar styl** | `assets/css/style.css` | řádky 184–199 |
| **Footer barvy** | `assets/css/style.css` | řádky 1002–1009 |
| **Název/Logo webu** | všechny HTML soubory | `<a class="logo"><span>DRIVE.</span></a>` |
| **Font** | všechny CSS soubory | `@font-face` + `assets/fonts/` |
| **Faktura — dodavatel** | `server.js` | řádky ~110–120 (fce `generateInvoicePDF`) |
| **E-mail odesílatel** | `.env` soubor | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS` |
| **Cookie consent text** | `assets/js/cookie-consent.js` | řádky s `innerHTML` |
| **Délka session** | `server.js` | řádek ~840 (konstanta `30 * DAY`) |
| **Rate limiting** | `server.js` | řádky 39–59 (`windowMs`, `count >= 5`) |
| **Slevový kód (nový)** | admin API nebo `src/seed.js` | viz sekce níže |
| **Dev mód heslo** | `server.js` | řádek 1242 (bcrypt hash) |
| **DB schéma** | `src/db.js` | řádky 14–145 |
| **DB migrace** | `src/db.js` | řádky 147–264 |

---

## Přidání produktu (5 kroků)

```
1. Otevři src/seed.js
2. Přidej slug do mustHaveSlugs:
   ['cans-mango', ..., 'novy-produkt']

3. Přidej objekt do pole products:
   {
     slug: 'novy-produkt',
     name: 'CANS Nová Příchuť — 24 × 330ml',
     price_cents: 59900,           // 599 Kč = 59900 haléřů
     image: '/assets/img/products/novy.png',
     hover_image: '/assets/img/products/novy-hover.jpg',
     description: 'Popis produktu.',
     features: JSON.stringify(['Vlastnost 1', 'Vlastnost 2']),
     stock: 100,
     color: 'mango'                // mango / citrus / berry
   }

4. Přidej obrázky do assets/img/products/

5. Smaž DB a restartuj:
   del data\site.db   (Windows)
   node server.js
```

---

## Přidání nového API endpointu

Přidej **před řádek 1292** v `server.js` (před `app.use` 404 handler):

```javascript
// GET endpoint — načtení dat
app.get('/api/nova-vec', (req, res) => {
    const data = db.prepare('SELECT * FROM products').all();
    res.json(data);
});

// POST endpoint — vytvoření / uložení
app.post('/api/nova-vec', (req, res) => {
    const { nazev, hodnota } = req.body || {};
    if (!nazev) return res.status(400).json({ error: 'Chybí nazev' });
    
    const result = db.prepare('INSERT INTO tabulka (nazev) VALUES (?)').run(nazev);
    res.status(201).json({ id: result.lastInsertRowid });
});
```

**S autentizací** (jen pro přihlášené):
```javascript
app.get('/api/moje-data', (req, res) => {
    const user = getCurrentUser(req);     // helper funkce v server.js:288
    if (!user) return res.status(401).json({ error: 'Unauthorized' });
    
    const data = db.prepare('SELECT * FROM orders WHERE user_id = ?').all(user.id);
    res.json(data);
});
```

**S admin ochranou**:
```javascript
app.post('/api/admin/akce', requireAdmin, (req, res) => {  // requireAdmin middleware: server.js:61
    // sem se dostanou jen přihlášení admini
    res.json({ ok: true });
});
```

---

## Přidání nové stránky (3 kroky)

```
1. Vytvoř složku a soubor:
   NovaSekce/index.html
   (zkopíruj strukturu z jiné stránky, např. AboutUs/index.html)

2. Přidej odkaz do navigace ve VŠECH HTML souborech:
   <a href="/NovaSekce" class="nav-link">Název</a>

3. Volitelně přidej:
   assets/css/nova-sekce.css
   assets/js/nova-sekce.js
   (a nalinkuj je v HTML souboru)
```

---

## Přidání sloupce do databáze

V `src/db.js` na konec migračního bloku (~řádek 260) přidej:

```javascript
// Přidání sloupce nova_vlastnost do products
const colsProducts = db.pragma("table_info(products)").map(c => c.name);
if (!colsProducts.includes('nova_vlastnost')) {
    db.exec("ALTER TABLE products ADD COLUMN nova_vlastnost TEXT DEFAULT ''");
}
```

Poté restartuj server — migrace proběhne automaticky.

---

## Přidání nového slevového kódu

**Přes admin API** (musíš mít aktivní dev mód):
```bash
curl -X POST http://localhost:3000/api/admin/discounts \
  -H "Content-Type: application/json" \
  -d '{"code": "LETO20", "discount_percent": 20}'
```

**Přes seed data** — v `src/seed.js` přidej:
```javascript
db.prepare("INSERT OR IGNORE INTO discounts (code, discount_percent) VALUES (?, ?)").run('LETO20', 20);
```

---

## Změna barev webu

Otevři `assets/css/style.css`, najdi `:root` (řádky 2–16) a změň hodnoty:

```css
:root {
    --primary-light: #A9ECFF;    /* světlé pozadí, hover efekty */
    --primary-medium: #DBF6ED;   /* navbar, footer gradient */
    --primary-dark: #E2FBDE;     /* akcenty */
    --text-primary: #27445C;     /* hlavní text a tlačítka */
    --text-secondary: #5A8DB9;   /* sekundární text */
    --background: #FFFFFF;       /* pozadí stránky */
}
```

> **Pozor:** Stejné hodnoty změň i v: `products.css`, `about.css`, `product-detail.css`, `cart.css`, `account.css` (každý soubor má vlastní `:root` blok)

Hotové alternativy ke zkopírování → viz [ALTERNATIVY.md](./ALTERNATIVY.md)

---

## Rychlé debugování

| Problém | Příčina | Řešení |
|---|---|---|
| Server se nespouští | Chybí závislosti | `npm install` |
| `EADDRINUSE :3000` | Port je obsazený | Ukonči jiný proces nebo změň PORT v `.env` |
| API vrací 500 | Chyba v kódu | Podívej se do `logs/error.log` |
| API vrací 401 | Nejsi přihlášen | Přihlas se nebo použij demo účet |
| API vrací 429 | Rate limit | Počkej 15 minut (nebo restartuj server) |
| Styly se nezobrazují | Cache prohlížeče | Ctrl+Shift+R (hard refresh) |
| JavaScript nefunguje | Chyba v JS | F12 → Console → hledej červené chyby |
| Obrázky chybí | Špatná cesta | Zkontroluj cestu v `src/seed.js`, soubory v `assets/img/products/` |
| Data zmizela | DB smazána / restart | Znovu seeduj: smaž DB → `node server.js` |
| Email se neposílá | SMTP nenastaven | Nastav `.env` nebo hledej `[MOCK EMAIL]` v konzoli |
| `UNIQUE constraint failed` | Duplicitní email/slug | Použij jiný email nebo slug |

---

## Všechny URL stránky

| Stránka | URL |
|---|---|
| Domů | `http://localhost:3000/` |
| Produkty | `http://localhost:3000/Products` |
| Detail produktu | `http://localhost:3000/Product-detail?slug=cans-mango` |
| Košík | `http://localhost:3000/Cart/cart.html` |
| Checkout | `http://localhost:3000/Cart/checkout.html` |
| Shrnutí objednávky | `http://localhost:3000/Cart/summary.html` |
| O nás | `http://localhost:3000/AboutUs` |
| Přihlášení | `http://localhost:3000/Account/login.html` |
| Registrace | `http://localhost:3000/Account/register.html` |
| Dashboard | `http://localhost:3000/Account` |
| Dev mód přihlášení | `http://localhost:3000/dev-enable` |
| Dev mód odhlášení | `http://localhost:3000/dev-disable` |
| Test e-mail | `http://localhost:3000/test-email` |

---

## Testovací data (pro demo u maturity)

| Co | Hodnota |
|---|---|
| Demo účet e-mail | `ucitel@spskladno.cz` |
| Demo účet heslo | `ucitel` |
| Slevový kód | `DRIVE10` (10 % sleva) |
| Dev mód heslo | `kO2N37Ac` |
| Testovací e-mail | `http://localhost:3000/test-email` |

> **Ceny produktů:** 599 Kč (CANS Mango/Citrus/Berry), 799 Kč (Broskev), 849 Kč (MIX BOX), 749 Kč (Předplatné)  
> **Předplatné sleva:** 20 % automaticky při výběru "předplatné"
