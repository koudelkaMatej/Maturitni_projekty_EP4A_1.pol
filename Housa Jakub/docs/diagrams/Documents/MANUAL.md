# DRIVE. E-shop — Komplexní manuál projektu

> **Autor:** Jakub Housa  
> **Škola:** SPŠ a VOŠ Kladno  
> **Třída:** EP4A  
> **Maturitní projekt — školní rok 2025/2026**

---

## Obsah

1. [Přehled projektu](#1-přehled-projektu)
2. [Architektura a technologie](#2-architektura-a-technologie)
3. [Instalace a spuštění](#3-instalace-a-spuštění)
4. [Databáze — schéma a tabulky](#4-databáze--schéma-a-tabulky)
5. [API endpointy](#5-api-endpointy)
6. [CSS proměnné a vzhled](#6-css-proměnné-a-vzhled)
7. [Správa produktů](#7-správa-produktů)
8. [Systém košíku](#8-systém-košíku)
9. [Objednávkový proces (checkout)](#9-objednávkový-proces-checkout)
10. [Autentizace a uživatelské účty](#10-autentizace-a-uživatelské-účty)
11. [E-maily a PDF faktury](#11-e-maily-a-pdf-faktury)
12. [Newsletter a slevové kódy](#12-newsletter-a-slevové-kódy)
13. [Admin / Dev mód](#13-admin--dev-mód)
14. [Cookie consent (GDPR)](#14-cookie-consent-gdpr)
15. [Nasazení (deployment)](#15-nasazení-deployment)
16. [Struktura souborů](#16-struktura-souborů)
17. [Časté úpravy — jak a kde](#17-časté-úpravy--jak-a-kde)

---

## 1. Přehled projektu

**DRIVE.** je e-shop pro energetické nápoje postavený jako **Multi-Page Application (MPA)** s vanilla JavaScriptem (bez frameworku). Server běží na **Node.js + Express 5**, data jsou uložena v **SQLite** databázi.

### Hlavní funkce

- Katalog produktů načítaný z databáze přes REST API
- Detail produktu s přepínáním příchutí bez reloadu stránky
- Košík s dual-mode úložištěm (localStorage + serverová synchronizace)
- 4-krokový checkout s validací, slevovými kódy a PDF fakturou
- Registrace / přihlášení / reset hesla s bcrypt hashováním
- Uživatelský účet s historií objednávek a správou předplatného
- Newsletter s automatickým slevovým kódem
- Admin rozhraní chráněné signed cookie
- GDPR cookie consent banner
- Responzivní design s vlastním fontem TelkaTRIAL

---

## 2. Architektura a technologie

### Backend

| Technologie | Verze | Účel |
|---|---|---|
| Node.js | 22.2.0 | Runtime |
| Express | 5.1.0 | Webový framework |
| better-sqlite3 | 12.4.1 | SQLite databáze |
| bcryptjs | 3.0.2 | Hashování hesel |
| nodemailer | 7.0.11 | Odesílání e-mailů |
| pdfkit | 0.17.2 | Generování PDF faktur |
| uuid | 13.0.0 | Generování tokenů |
| cookie-parser | 1.4.7 | Parsování cookies |
| compression | 1.8.1 | Gzip komprese |
| morgan | 1.10.1 | HTTP logování |
| dotenv | 17.2.3 | Proměnné prostředí |

### Frontend

- **HTML5** — statické stránky servírované Expressem
- **CSS3** — vlastní styly s CSS custom properties (žádný framework)
- **Vanilla JavaScript** — žádný React/Vue/Angular
- **Font Awesome 6.4** — ikony (CDN)
- **Font TelkaTRIAL** — vlastní písmo (Medium + Bold)

### Vzory

- Ceny v databázi jsou v **haléřích** (`price_cents`), na frontendu se dělí 100 → Kč
- Měna: **CZK**, formátování: `Intl.NumberFormat('cs-CZ')`
- Session: cookie-based, httpOnly, signed
- Autentizace: bcrypt (10 rounds), UUID v4 tokeny, 30denní platnost

---

## 3. Instalace a spuštění

### Požadavky

- Node.js ≥ 18 (doporučeno 22.x)
- npm

### Postup

```bash
# 1. Naklonovat repozitář
git clone <repo-url>
cd "Housa Jakub"

# 2. Nainstalovat závislosti
npm install

# 3. Spustit server
node server.js

# 4. Otevřít v prohlížeči
# http://localhost:3000
```

Při prvním spuštění se automaticky:
- vytvoří složka `data/` a soubor `data/site.db`
- vytvoří všechny tabulky (viz sekce 4)
- provedou migrace (přidání chybějících sloupců)
- zaseedují produkty, obrázky a slevový kód DRIVE10

### Proměnné prostředí

Vytvořte soubor `.env` v kořeni projektu (volitelné):

```env
PORT=3000
COOKIE_SECRET=secure-secret-key-123
SMTP_HOST=smtp.ethereal.email
SMTP_PORT=587
SMTP_SECURE=false
SMTP_USER=ethereal.user@example.com
SMTP_PASS=ethereal.pass
```

| Proměnná | Výchozí | Popis |
|---|---|---|
| `PORT` | `3000` | Port serveru |
| `COOKIE_SECRET` | `'secure-secret-key-123'` | Klíč pro podepisování cookies |
| `SMTP_HOST` | `'smtp.ethereal.email'` | SMTP server pro e-maily |
| `SMTP_PORT` | `587` | SMTP port |
| `SMTP_SECURE` | `false` | TLS (true pro port 465) |
| `SMTP_USER` | `'ethereal.user@example.com'` | SMTP přihlašovací jméno |
| `SMTP_PASS` | `'ethereal.pass'` | SMTP heslo |

> **Poznámka:** Pokud `SMTP_HOST` není nastaven, e-maily se nevyšlou a místo toho se logují do konzole jako `[MOCK EMAIL]`.

---

## 4. Databáze — schéma a tabulky

**Soubor:** `src/db.js` (269 řádků)  
**Engine:** SQLite s WAL módem (`journal_mode = WAL`)  
**Umístění DB:** `data/site.db`

### 4.1 Tabulka `products`

Řádky 15–25 v `src/db.js`:

| Sloupec | Typ | Omezení |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `slug` | TEXT | UNIQUE |
| `name` | TEXT | NOT NULL |
| `price_cents` | INTEGER | NOT NULL — cena v haléřích |
| `image` | TEXT | Hlavní obrázek produktu |
| `hover_image` | TEXT | Obrázek při hoveru |
| `description` | TEXT | Popis produktu |
| `features` | TEXT | JSON string — pole vlastností |
| `stock` | INTEGER | DEFAULT 100 |
| `color` | TEXT | DEFAULT '' — barevná třída (mango/citrus/berry) |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP |

**Příklad features:**
```json
["Přírodní kofein", "Bez cukru", "Vegan", "Recyklovatelná plechovka"]
```

### 4.2 Tabulka `product_images`

Řádky 134–143 v `src/db.js`:

| Sloupec | Typ | Omezení |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `product_id` | INTEGER | NOT NULL, FK→products(id) ON DELETE CASCADE |
| `url` | TEXT | NOT NULL — cesta k obrázku |
| `alt_text` | TEXT | Alternativní text |
| `sort_order` | INTEGER | DEFAULT 0 — pořadí řazení |
| `type` | TEXT | DEFAULT 'main' — typy: `main`, `thumb`, `mini` |

### 4.3 Tabulka `users`

Řádky 27–38 v `src/db.js`:

| Sloupec | Typ | Omezení |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `email` | TEXT | UNIQUE NOT NULL |
| `password_hash` | TEXT | NOT NULL — bcrypt hash |
| `first_name` | TEXT | |
| `last_name` | TEXT | |
| `phone` | TEXT | |
| `address` | TEXT | |
| `city` | TEXT | |
| `zip_code` | TEXT | |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP |

### 4.4 Tabulka `sessions`

| Sloupec | Typ | Omezení |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `user_id` | INTEGER | NOT NULL, FK→users(id) |
| `token` | TEXT | UNIQUE NOT NULL — UUID v4 |
| `expires_at` | DATETIME | NOT NULL |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP |

### 4.5 Tabulka `orders`

| Sloupec | Typ | Omezení |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `user_id` | INTEGER | FK→users(id), může být NULL (host) |
| `customer_email` | TEXT | NOT NULL |
| `customer_name` | TEXT | NOT NULL |
| `customer_address` | TEXT | NOT NULL |
| `customer_city` | TEXT | NOT NULL |
| `customer_zip` | TEXT | NOT NULL |
| `customer_phone` | TEXT | |
| `payment_method` | TEXT | DEFAULT 'card' |
| `total_cents` | INTEGER | NOT NULL |
| `discount_code` | TEXT | |
| `discount_amount` | INTEGER | DEFAULT 0 |
| `status` | TEXT | DEFAULT 'pending' |
| `created_at` | DATETIME | DEFAULT CURRENT_TIMESTAMP |

### 4.6 Tabulka `order_items`

| Sloupec | Typ | Omezení |
|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `order_id` | INTEGER | NOT NULL, FK→orders(id) ON DELETE CASCADE |
| `product_id` | INTEGER | NOT NULL, FK→products(id) |
| `quantity` | INTEGER | NOT NULL |
| `price_cents` | INTEGER | NOT NULL |
| `product_name` | TEXT | |

### 4.7 Další tabulky

- **`subscribers`** — newsletter odběratelé (email, subscribed_at)
- **`password_resets`** — tokeny pro reset hesla (email, token, expires_at)
- **`carts`** — serverové košíky (session_id, user_id)
- **`cart_items`** — položky košíku (cart_id, product_id, quantity, is_subscription)
- **`user_subscriptions`** — předplatné uživatelů (user_id, product_id, product_name, product_slug, price_cents, status, next_billing_date)
- **`discounts`** — slevové kódy (code, discount_percent, active)

### 4.8 Indexy

```sql
CREATE INDEX idx_products_slug ON products(slug);
CREATE INDEX idx_cart_items_cart ON cart_items(cart_id);
CREATE INDEX idx_cart_items_product ON cart_items(product_id);
CREATE INDEX idx_product_images_product ON product_images(product_id);
```

### 4.9 Automatické migrace

Při startu serveru se kontroluje existence sloupců a v případě potřeby se přidávají:

1. `user_subscriptions` — restrukturalizace (přidání product_id, product_name atd.)
2. `products.stock` — přidání sloupce
3. `orders.payment_method` — přidání sloupce
4. `orders.customer_phone` — přidání sloupce
5. `orders.discount_code` + `discount_amount` — přidání sloupců
6. `orders.user_id` — přidání sloupce
7. `cart_items.is_subscription` — přidání sloupce
8. `products.color` — přidání sloupce

---

## 5. API endpointy

Všechny endpointy jsou definovány v `server.js` (1305 řádků).

### 5.1 Produkty

| Metoda | Cesta | Popis | Auth |
|---|---|---|---|
| GET | `/api/products` | Seznam produktů (id, slug, name, price_cents, image, hover_image, color) | Ne |
| GET | `/api/products/:idOrSlug` | Detail produktu + pole `images` z tabulky `product_images` | Ne |

**Příklad odpovědi — detail:**
```json
{
  "id": 1,
  "slug": "cans-mango",
  "name": "CANS Mango — 24 × 330ml",
  "price_cents": 59900,
  "image": "/assets/img/products/test.png",
  "hover_image": "/assets/img/products/test2.jpg",
  "description": "Osvěžující mango příchuť...",
  "features": "[\"Přírodní kofein\",\"Bez cukru\",\"Vegan\",\"Recyklovatelná plechovka\"]",
  "stock": 100,
  "color": "mango",
  "images": [
    { "id": 1, "url": "/assets/img/products/test.png", "alt_text": "cans-mango - hlavní obrázek", "sort_order": 0, "type": "main" },
    { "id": 2, "url": "/assets/img/products/test.png", "alt_text": "cans-mango - náhled 1", "sort_order": 1, "type": "thumb" },
    { "id": 3, "url": "/assets/img/products/test2.jpg", "alt_text": "cans-mango - náhled 2", "sort_order": 2, "type": "thumb" },
    { "id": 4, "url": "/assets/img/products/test.png", "alt_text": "cans-mango - mini", "sort_order": 3, "type": "mini" }
  ]
}
```

### 5.2 Košík (session-based)

| Metoda | Cesta | Popis | Auth |
|---|---|---|---|
| GET | `/api/cart` | Načtení košíku pro aktuální session | Ne |
| POST | `/api/cart` | Přidání položky do košíku | Ne |
| PATCH | `/api/cart` | Aktualizace množství (0 = smazání) | Ne |
| DELETE | `/api/cart/:itemId` | Odebrání konkrétní položky | Ne |
| DELETE | `/api/cart` | Vymazání celého košíku | Ne |

### 5.3 Uživatelský košík (přihlášený uživatel)

| Metoda | Cesta | Popis | Auth |
|---|---|---|---|
| GET | `/api/user/cart` | Načtení košíku z DB | Ano |
| POST | `/api/user/cart/sync` | Synchronizace localStorage → DB | Ano |
| POST | `/api/user/cart/add` | Přidání položky do DB košíku | Ano |
| DELETE | `/api/user/cart` | Vymazání DB košíku | Ano |

### 5.4 Autentizace

| Metoda | Cesta | Popis | Auth |
|---|---|---|---|
| POST | `/api/auth/register` | Registrace uživatele | Ne |
| POST | `/api/auth/login` | Přihlášení (rate-limited: 5 pokusů / 15 min) | Ne |
| POST | `/api/auth/logout` | Odhlášení, smazání session | Ano |
| POST | `/api/auth/forgot-password` | Odeslání e-mailu pro reset hesla (token 1h) | Ne |
| POST | `/api/auth/reset-password` | Reset hesla pomocí tokenu | Ne |
| GET | `/api/auth/me` | Údaje přihlášeného uživatele + stav předplatného | Ano |

### 5.5 Uživatelský profil

| Metoda | Cesta | Popis | Auth |
|---|---|---|---|
| PUT | `/api/user/profile` | Aktualizace profilu (partial update) | Ano |
| DELETE | `/api/user/delete` | GDPR smazání účtu (anonymizace objednávek) | Ano |
| GET | `/api/user/orders` | Historie objednávek s položkami | Ano |

### 5.6 Předplatné

| Metoda | Cesta | Popis | Auth |
|---|---|---|---|
| GET | `/api/user/subscription` | Všechna předplatné uživatele | Ano |
| POST | `/api/user/subscription/cancel` | Zrušení předplatného | Ano |
| POST | `/api/user/subscription/reactivate` | Reaktivace předplatného | Ano |
| DELETE | `/api/user/subscription/:id` | Smazání zrušeného předplatného | Ano |

### 5.7 Checkout a slevy

| Metoda | Cesta | Popis | Auth |
|---|---|---|---|
| POST | `/api/validate-discount` | Ověření slevového kódu | Ne |
| POST | `/api/checkout` | Vytvoření objednávky (+ snížení skladu, e-mail, PDF) | Ne (host OK) |

### 5.8 Newsletter

| Metoda | Cesta | Popis | Auth |
|---|---|---|---|
| POST | `/api/newsletter` | Přihlášení k odběru, odešle uvítací e-mail s kódem DRIVE10 | Ne |

### 5.9 Admin endpointy

Vyžadují podepsaný cookie `dev_token = 'authorized'`.

| Metoda | Cesta | Popis |
|---|---|---|
| POST | `/api/admin/send-newsletter` | Hromadné rozeslání newsletteru |
| GET | `/api/admin/discounts` | Seznam slevových kódů |
| POST | `/api/admin/discounts` | Vytvoření nového slevového kódu |
| DELETE | `/api/admin/discounts/:id` | Smazání slevového kódu |

---

## 6. CSS proměnné a vzhled

### 6.1 Globální proměnné

Definováno v `:root` v souboru `assets/css/style.css` (řádky 2–16):

```css
:root {
    --primary-light: #A9ECFF;     /* Světle modrá — akcenty, hover */
    --primary-medium: #DBF6ED;    /* Zeleno-modrá — pozadí sekcí */
    --primary-dark: #E2FBDE;      /* Světle zelená — gradientové pozadí */
    --text-primary: #27445C;      /* Tmavě modrá — hlavní text */
    --text-secondary: #5A8DB9;    /* Střední modrá — sekundární text */
    --background: #FFFFFF;        /* Bílé pozadí */
    --light-bg: #f8f9fa;          /* Světle šedé pozadí */
    --shadow: 0 4px 12px rgba(26, 60, 52, 0.1);       /* Výchozí stín */
    --shadow-hover: 0 8px 24px rgba(26, 60, 52, 0.15); /* Stín při hoveru */
    --transition: all 0.3s ease;  /* Výchozí přechod */
    --radius: 8px;                /* Zaoblení rohů */
    --navbar-height: 72px;        /* Výška navigace */
    --navbar-offset: 20px;        /* Offset pod navigací */
}
```

### 6.2 Jak změnit barvy webu

1. Otevřete `assets/css/style.css`
2. Upravte hodnoty v `:root` bloku na řádcích 2–16
3. **Důležité:** Stejné proměnné se opakují i v dalších CSS souborech — pro konzistenci je změňte i tam:
   - `assets/css/products.css` (řádky 2–14)
   - `assets/css/about.css` (řádky 20–49)
   - `assets/css/product-detail.css`
   - `assets/css/cart.css`
   - `assets/css/account.css`

### 6.3 Fonty

Vlastní font **TelkaTRIAL** (soubory v `assets/fonts/`):

```css
@font-face {
    font-family: 'TelkaTRIAL';
    src: url('../fonts/TelkaTRIAL-Medium.otf') format('opentype');
    font-weight: 500;
}
@font-face {
    font-family: 'TelkaTRIALBold';
    src: url('../fonts/TelkaTRIAL-Bold.otf') format('opentype');
    font-weight: 700;
}
```

Změna fontu: nahraďte soubory `.otf` v `assets/fonts/` a upravte `@font-face` deklarace ve všech CSS souborech.

### 6.4 Barevné třídy příchutí (product detail)

V `assets/css/product-detail.css` jsou definovány barevné varianty:

- `.mango` — oranžové/žluté tóny
- `.citrus` — zelené/citrusové tóny
- `.berry` — fialové/červené tóny

Tyto třídy se přidávají na `.container.product-detail-page` dynamicky z JavaScriptu podle hodnoty `color` z databáze.

### 6.5 CSS soubory — přehled

| Soubor | Řádků | Účel |
|---|---|---|
| `assets/css/style.css` | 2235 | Globální styly, navbar, hero, sekce, footer, responsive |
| `assets/css/products.css` | 763 | Stránka produktů — grid, karty, filtry, animace |
| `assets/css/product-detail.css` | 807 | Detail produktu — galerie, příchutě, akordeon |
| `assets/css/about.css` | 1292 | O nás — hero, statistiky, timeline, tým |
| `assets/css/cart.css` | 1079 | Košík, checkout, shrnutí, poděkování |
| `assets/css/account.css` | 1356 | Dashboard, postranní panel, objednávky, profil |
| `assets/css/account-auth.css` | ~130 | Přihlášení/registrace — auth karta, formuláře |

---

## 7. Správa produktů

### 7.1 Kde jsou produkty definovány

Produkty se seedují ze souboru `src/seed.js`. Při startu serveru se kontroluje, zda produkty existují, a chybějící se doplní.

### 7.2 Přidání nového produktu

1. Otevřete `src/seed.js`
2. Přidejte slug do pole `mustHaveSlugs`:
   ```javascript
   const mustHaveSlugs = ['cans-mango', 'cans-citrus', 'cans-berry', 'mix', 'subscription', 'cans-peach', 'novy-produkt'];
   ```
3. Přidejte objekt produktu do pole `products`:
   ```javascript
   {
     slug: 'novy-produkt',
     name: 'CANS Nová Příchuť — 24 × 330ml',
     price_cents: 59900,          // 599 Kč v haléřích
     image: '/assets/img/products/novy.png',
     hover_image: '/assets/img/products/novy-hover.jpg',
     description: 'Popis nového produktu.',
     features: JSON.stringify(['Vlastnost 1', 'Vlastnost 2', 'Vlastnost 3']),
     stock: 100,
     color: 'mango'               // CSS třída: mango, citrus, nebo berry
   }
   ```
4. Přidejte barvu do `colorMap`:
   ```javascript
   'novy-produkt': 'citrus'
   ```
5. Přidejte obrázky do `assets/img/products/`
6. Smažte databázi a restartujte server:
   ```bash
   # Smazání DB (znovu se vytvoří při startu)
   del data\site.db
   node server.js
   ```

### 7.3 Změna ceny produktu

1. V `src/seed.js` změňte hodnotu `price_cents` (v **haléřích**)
   - 599 Kč = `59900`
   - 849 Kč = `84900`
2. Smažte DB a restartujte server

### 7.4 Změna obrázků produktu

**Základní obrázky** — v `src/seed.js` upravte `image` a `hover_image` cesty.

**Detailní obrázky** (galerie) — v tabulce `product_images`. Funkce `seedProductImages()` v `src/seed.js` (řádky 129–157) vytváří 4 obrázky pro každý produkt:

| Typ | Popis | Použití |
|---|---|---|
| `main` | Hlavní obrázek | Velký obrázek na detailu |
| `thumb` | Náhled 1 | Malý náhled v galerii |
| `thumb` | Náhled 2 (hover) | Druhý náhled v galerii |
| `mini` | Miniatura | Obrázek v košíku |

Pro vlastní obrázky upravte URL cesty v `seedProductImages()` nebo přidejte obrázky přímo do DB.

### 7.5 Barevné varianty (color)

Slouží pro CSS třídu na detail stránce. Dostupné hodnoty:

| Hodnota | Vizuální styl |
|---|---|
| `mango` | Oranžové/žluté tóny |
| `citrus` | Zelené/citrusové tóny |
| `berry` | Fialové/červené tóny |

Přidání nové barvy:
1. V `assets/css/product-detail.css` přidejte novou třídu (např. `.peach`)
2. V `src/seed.js` nastavte `color: 'peach'` pro daný produkt

---

## 8. Systém košíku

### 8.1 Architektura

**Soubor:** `assets/js/cart.js` (739 řádků)

Košík funguje v **dual-mode**:

1. **localStorage** (výchozí) — pro nepřihlášené uživatele
2. **Server DB** — synchronizace pro přihlášené uživatele přes API

### 8.2 Formát položky košíku (localStorage)

```json
{
  "id": "cans-mango",
  "name": "CANS Mango — 24 × 330ml",
  "price": 599,
  "quantity": 1,
  "variant": "Jednorázový nákup",
  "image": "/assets/img/products/test.png",
  "isSubscription": false,
  "addedAt": "2026-03-03T12:00:00.000Z"
}
```

### 8.3 Klíčové metody CartManager

| Metoda | Popis |
|---|---|
| `init()` | Inicializace — načtení z localStorage, navázání eventů |
| `addToCart(product, quantity, variant)` | Přidání/aktualizace položky |
| `removeFromCart(productId, variant)` | Odebrání položky |
| `updateQuantity(productId, variant, newQty)` | Změna množství (max 99) |
| `clearCart()` | Vymazání košíku |
| `getDiscount()` | Načtení slevy z localStorage |
| `checkAuthAndSyncCart()` | Kontrola přihlášení + synchronizace |
| `syncCartToServer()` | POST na `/api/user/cart/sync` |
| `loadCartFromServer()` | GET z `/api/user/cart` |
| `proceedToCheckout()` | Validace + přesměrování na checkout |

### 8.4 Mini-cart

Vysuvný panel (420px šířka) ukotvený vpravo, otevírá se kliknutím na ikonu košíku v navigaci. Zobrazuje:
- Seznam položek s obrázkem, názvem, cenou, množstvím
- Celkovou cenu
- Tlačítko pro přechod do košíku

---

## 9. Objednávkový proces (checkout)

### 4-krokový flow

```
Cart/cart.html → Cart/checkout.html → Cart/summary.html → Cart/thank-you.html
```

### Krok 1: Košík (`Cart/cart.html`)

- Zobrazení položek (renderuje `CartManager.updateCartPage()`)
- Přehled objednávky: mezisoučet, sleva, doprava, celkem
- Pole pro slevový kód → validace přes `POST /api/validate-discount`
- Tlačítko „Pokračovat k platbě"

### Krok 2: Checkout formulář (`Cart/checkout.html`)

- Kontrola přihlášení → předvyplnění údajů z profilu
- Pole: e-mail, telefon, jméno, příjmení, adresa, město, PSČ
- Výběr platby: karta, Apple Pay, Google Pay, QR platba, PayPal
- Validace:
  - E-mail: regex
  - Jméno: min 2 znaky
  - PSČ: `\d{3}\s?\d{2}`
  - Telefon: `^(\+420)?\s?\d{3}\s?\d{3}\s?\d{3}$`
- Uložení do `localStorage.checkoutData` → přesměrování na shrnutí

### Krok 3: Shrnutí (`Cart/summary.html`)

- Přehled: kontaktní údaje, adresa, platba, položky, ceny
- Tlačítko „Odeslat objednávku" → `POST /api/checkout`
- Payload obsahuje: košík, formulářová data, slevový kód
- Server: vytvoří objednávku, sníží sklad, odešle e-mail s PDF fakturou
- Při úspěchu: vymaže košík + přesměruje na poděkování

### Krok 4: Poděkování (`Cart/thank-you.html`)

- Zobrazí ID objednávky z URL parametru
- Zpráva: „Objednávka dokončena! Potvrzení jsme zaslali na váš e-mail."

---

## 10. Autentizace a uživatelské účty

### 10.1 Hashování hesel

- **Knihovna:** bcryptjs
- **Salt rounds:** 10 (řádek ~815 v `server.js`)
- **Hash funkce:** `bcrypt.hash(password, 10)`

### 10.2 Sessions

- **Délka platnosti:** 30 dní
- **Token:** UUID v4
- **Cookie:** `auth_token` — httpOnly, sameSite: 'lax', signed

### 10.3 Rate limiting přihlášení

- **Okno:** 15 minut
- **Max pokusů:** 5 na IP adresu
- **Odpověď při překročení:** HTTP 429

### 10.4 Stránky účtu

| Stránka | Cesta | Funkce |
|---|---|---|
| Přihlášení | `Account/login.html` | E-mail + heslo |
| Registrace | `Account/register.html` | Jméno, e-mail, heslo (min 6 znaků) |
| Reset hesla | `Account/forgot-password.html` | Odeslání tokenu na e-mail |
| Nové heslo | `Account/reset-password.html` | Zadání nového hesla s tokenem |
| Dashboard | `Account/index.html` | Přehled, objednávky, předplatné, profil |

### 10.5 GDPR smazání účtu

Endpoint `DELETE /api/user/delete`:
1. Smaže sessions
2. Smaže předplatné
3. Smaže data košíku
4. Odhlásí newsletter
5. Anonymizuje objednávky (`user_id = NULL`)
6. Smaže uživatele

---

## 11. E-maily a PDF faktury

### 11.1 E-mailový transport

**Soubor:** `server.js` řádky 80–88

- **Výchozí:** ethereal.email (vývojový mock server)
- **Produkce:** nastavit `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS` v .env
- Pokud není nastaven SMTP_HOST → e-maily se **logují do konzole** jako `[MOCK EMAIL]`

### 11.2 Typy odesílaných e-mailů

| E-mail | Příležitost | Odesílatel | Příloha |
|---|---|---|---|
| Potvrzení objednávky | Po úspěšném checkoutu | drivewater.bussines@gmail.com | PDF faktura |
| Reset hesla | Zapomenuté heslo | noreply@cans.cz | — |
| Newsletter uvítání | Přihlášení k odběru | drivewater.bussines@gmail.com | — |
| Hromadný newsletter | Admin akce | drivewater.bussines@gmail.com | — |

### 11.3 PDF faktura

**Generování:** `server.js` řádky 90–155 (funkce `generateInvoicePDF`)

Obsah faktury:
- Hlavička s logem „DRIVE."
- Číslo objednávky
- Dodavatel: „DRIVE Energy s.r.o., Václavské náměstí 1, 110 00 Praha 1, IČ: 12345678"
- Zákazník: jméno, adresa, PSČ + město
- Tabulka položek: Položka | Množství | Cena
- Celkem k úhradě

**Font:** TelkaTRIAL-Medium.otf a TelkaTRIAL-Bold.otf (s fallbackem na Helvetica)  
**Název souboru:** `faktura-{orderId}.pdf`

### 11.4 Změna údajů dodavatele na faktuře

V `server.js` na řádku ~115 upravte:

```javascript
doc.text('DRIVE Energy s.r.o.', { continued: false });
doc.text('Václavské náměstí 1', { continued: false });
doc.text('110 00 Praha 1', { continued: false });
doc.text('IČ: 12345678');
```

---

## 12. Newsletter a slevové kódy

### 12.1 Newsletter přihlášení

- Formuláře: na hlavní stránce a na stránce produktů
- Endpoint: `POST /api/newsletter`
- Uloží e-mail do tabulky `subscribers`
- Odešle uvítací e-mail s kódem **DRIVE10** (10% sleva)

### 12.2 Slevové kódy

**Výchozí kód:** `DRIVE10` — 10% sleva (seedováno automaticky)

Validace: `POST /api/validate-discount` → vrací `{ valid: true, discount_percent: 10 }`

### 12.3 Přidání nového slevového kódu

**Přes admin API:**
```bash
curl -X POST http://localhost:3000/api/admin/discounts \
  -H "Content-Type: application/json" \
  -d '{"code": "LETO20", "discount_percent": 20}'
```

**Přes seed data** — v `src/seed.js` přidejte další `INSERT`:
```javascript
db.prepare('INSERT INTO discounts (code, discount_percent) VALUES (?, ?)').run('LETO20', 20);
```

---

## 13. Admin / Dev mód

### 13.1 Aktivace

1. Přejděte na `http://localhost:3000/dev-enable`
2. Zadejte heslo (bcrypt hash je v `server.js` řádek ~1228)
3. Po úspěšném přihlášení se nastaví signed cookie `dev_token`
4. V navigaci se objeví odkaz „Vývoj" → `docs/index.html`

### 13.2 Admin funkce

- Rozesílání newsletterů
- Správa slevových kódů (CRUD)
- Přístup k dokumentaci a diagramům

### 13.3 Deaktivace

Přejděte na `http://localhost:3000/dev-disable` → smaže dev cookies.

---

## 14. Cookie consent (GDPR)

**Soubor:** `assets/js/cookie-consent.js` (82 řádků)

- Zobrazí fixní banner na spodku stránky
- Tlačítko „Souhlasím"
- Odkaz na `/Info/privacy.html`
- Po souhlasu uloží `drive_cookie_consent = 'true'` do localStorage
- Při dalším načtení stránky se banner nezobrazí

---

## 15. Nasazení (deployment)

### 15.1 Render.com

**Soubor:** `render.yaml`

```yaml
services:
  - type: web
    name: drive-eshop-app
    env: node
    plan: free
    buildCommand: npm install
    startCommand: node server.js
    envVars:
      - key: NODE_VERSION
        value: 22.2.0
```

- **Platforma:** Render.com
- **Plán:** Free tier
- **Build:** `npm install`
- **Start:** `node server.js`

> **Poznámka:** Na free tier je SQLite databáze **dočasná** — při restartu služby se DB znovu vytvoří a zaseeduje. Pro produkční nasazení zvažte PostgreSQL.

### 15.2 Proměnné prostředí na Render

V Render dashboardu nastavte:
- `COOKIE_SECRET` — unikátní tajný klíč
- `SMTP_HOST` — reálný SMTP server (např. smtp.gmail.com)
- `SMTP_USER` — e-mailová adresa
- `SMTP_PASS` — heslo / app password

---

## 16. Struktura souborů

```
├── server.js                # Express server, všechny API endpointy (1305 ř.)
├── package.json             # Závislosti a skripty
├── render.yaml              # Konfigurace nasazení na Render
├── 404.html                 # Stránka pro chybu 404
├── index.html               # Hlavní stránka (landing page)
│
├── src/
│   ├── db.js                # Schéma databáze, migrace (269 ř.)
│   └── seed.js              # Seedování produktů a dat (187 ř.)
│
├── data/
│   └── site.db              # SQLite databáze (generuje se automaticky)
│
├── assets/
│   ├── css/
│   │   ├── style.css        # Globální styly (2235 ř.)
│   │   ├── products.css     # Stránka produktů (763 ř.)
│   │   ├── product-detail.css  # Detail produktu (807 ř.)
│   │   ├── about.css        # O nás (1292 ř.)
│   │   ├── cart.css         # Košík a checkout (1079 ř.)
│   │   ├── account.css      # Uživatelský účet (1356 ř.)
│   │   └── account-auth.css # Přihlášení/registrace (~130 ř.)
│   ├── fonts/
│   │   ├── TelkaTRIAL-Medium.otf
│   │   └── TelkaTRIAL-Bold.otf
│   ├── img/
│   │   ├── products/        # Obrázky produktů
│   │   └── about/           # Obrázky pro sekci O nás
│   └── js/
│       ├── script.js        # Hlavní stránka (509 ř.)
│       ├── cart.js          # CartManager (739 ř.)
│       ├── products.js      # Výpis produktů (396 ř.)
│       ├── product-detail.js # Detail produktu (375 ř.)
│       ├── about.js         # Stránka O nás (45 ř.)
│       ├── cookie-consent.js # GDPR banner (82 ř.)
│       ├── dev-mode.js      # Dev mód (46 ř.)
│       └── scroll-snap.js   # Scroll snapping (57 ř.)
│
├── Products/
│   └── index.html           # Stránka produktů
├── Product-detail/
│   └── index.html           # Detail produktu
├── Cart/
│   ├── cart.html            # Krok 1: Košík
│   ├── checkout.html        # Krok 2: Formulář
│   ├── summary.html         # Krok 3: Shrnutí
│   └── thank-you.html       # Krok 4: Poděkování
├── Account/
│   ├── index.html           # Dashboard
│   ├── login.html           # Přihlášení
│   ├── register.html        # Registrace
│   ├── forgot-password.html # Zapomenuté heslo
│   └── reset-password.html  # Reset hesla
├── AboutUs/
│   └── index.html           # O nás
├── Info/
│   ├── terms.html           # Obchodní podmínky
│   ├── privacy.html         # Ochrana soukromí
│   └── shipping.html        # Doprava a platba
└── docs/
    ├── index.html           # Dokumentace (dev mód)
    ├── architecture.md      # Architektura
    └── diagrams/            # Mermaid diagramy
```

---

## 17. Časté úpravy — jak a kde

### Změna barev webu
- **Kde:** `assets/css/style.css` řádky 2–16 (`:root` blok)
- **Co:** Upravit hodnoty CSS custom properties
- **Pozor:** Změnit i v `products.css`, `about.css`, `product-detail.css`, `cart.css`, `account.css`

### Změna loga / názvu
- **Kde:** Navbar v každém HTML souboru — element `<a class="logo"><span>DRIVE.</span></a>`
- **Footer:** Každý HTML soubor — `<span>Drive.</span>` v patičce

### Přidání produktu
- **Kde:** `src/seed.js` — pole `products` + `mustHaveSlugs`
- **Potom:** Smazat `data/site.db` a restartovat server

### Změna ceny
- **Kde:** `src/seed.js` — atribut `price_cents` (v haléřích)
- **Potom:** Smazat DB a restartovat

### Změna obrázků produktu
- **Kam nahrát:** `assets/img/products/`
- **Kde nastavit cestu:** `src/seed.js` — `image`, `hover_image`
- **Pro galerii:** Upravit `seedProductImages()` v `src/seed.js`

### Změna údajů dodavatele na faktuře
- **Kde:** `server.js` řádky ~110–120 (funkce `generateInvoicePDF`)

### Změna doby platnosti session
- **Kde:** `server.js` řádek ~830 — `30 * DAY` → změnit číslo

### Změna rate limitingu
- **Kde:** `server.js` řádky 39–62 — `WINDOW_MS` a `MAX_ATTEMPTS`

### Přidání slevového kódu
- **Admin API:** `POST /api/admin/discounts` s body `{"code": "KOD", "discount_percent": 15}`
- **Seed:** Přidat do `src/seed.js`

### Změna SMTP pro produkci
- **Kde:** `.env` soubor — nastavit `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS`

### Změna textu cookie consent banneru
- **Kde:** `assets/js/cookie-consent.js` — řádky s `innerHTML`

### Změna validace formuláře (checkout)
- **Kde:** `Cart/checkout.html` — JavaScript sekce s `validateForm()`

### Přidání nové stránky
1. Vytvořte HTML soubor v nové složce (např. `NovaSekce/index.html`)
2. Přidejte odkaz do navigace a patičky ve všech HTML souborech
3. Volitelně: vytvořte CSS soubor v `assets/css/` a JS soubor v `assets/js/`

---

> **Tip:** Pro úplný reset databáze smažte soubor `data/site.db` a restartujte server příkazem `node server.js`. Všechna data se znovu zaseedují.
