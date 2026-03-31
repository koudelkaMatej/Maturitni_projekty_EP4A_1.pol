# Alternativní kódy — rychlé úpravy pro maturitu

> **Jak používat:** Najdi úpravu, zkopíruj kód, vlož do souboru na uvedené cestě.
> Každý snippet obsahuje **aktuální stav** a **alternativy** — stačí nahradit.

---

## 1. Změna barev webu

Všechny barvy webu se řídí CSS proměnnými v jednom bloku. Změníš je na jednom místě a projeví se všude.

### 📁 `assets/css/style.css` — řádky 2–16 (`:root` blok)

**Aktuální nastavení:**

```css
:root {
    --primary-light: #A9ECFF;    /* Světle modrá — navbar pozadí, ikony, tlačítka "do košíku" */
    --primary-medium: #DBF6ED;   /* Světle zeleno-modrá — navbar, footer gradient */
    --primary-dark: #E2FBDE;     /* Světle zelená — akcentové prvky */
    --text-primary: #27445C;     /* Tmavě modrá — hlavní text, nadpisy, tlačítka */
    --text-secondary: #5A8DB9;   /* Středně modrá — podtexty, popisky */
    --background: #FFFFFF;       /* Pozadí stránky */
    --light-bg: #f8f9fa;         /* Světlé pozadí sekcí */
    --shadow: 0 4px 12px rgba(26, 60, 52, 0.1);
    --shadow-hover: 0 8px 24px rgba(26, 60, 52, 0.15);
    --transition: all 0.3s ease;
    --radius: 8px;
}
```

**Alternativa A — Teplé barvy (oranžovo-béžová):**

```css
:root {
    --primary-light: #FFD6A5;
    --primary-medium: #FFF1E0;
    --primary-dark: #FFECD2;
    --text-primary: #5C3D27;
    --text-secondary: #B9785A;
    --background: #FFFFFF;
    --light-bg: #fdf8f4;
    --shadow: 0 4px 12px rgba(92, 61, 39, 0.1);
    --shadow-hover: 0 8px 24px rgba(92, 61, 39, 0.15);
    --transition: all 0.3s ease;
    --radius: 8px;
}
```

**Alternativa B — Tmavý režim:**

```css
:root {
    --primary-light: #1e3a5f;
    --primary-medium: #0f1c2e;
    --primary-dark: #162840;
    --text-primary: #e2e8f0;
    --text-secondary: #94a3b8;
    --background: #0f172a;
    --light-bg: #1e293b;
    --shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    --shadow-hover: 0 8px 24px rgba(0, 0, 0, 0.4);
    --transition: all 0.3s ease;
    --radius: 8px;
}
```

**Alternativa C — Fialovo-růžová:**

```css
:root {
    --primary-light: #E8DAEF;
    --primary-medium: #F5EEF8;
    --primary-dark: #FADBD8;
    --text-primary: #4A235A;
    --text-secondary: #8E44AD;
    --background: #FFFFFF;
    --light-bg: #faf5ff;
    --shadow: 0 4px 12px rgba(74, 35, 90, 0.1);
    --shadow-hover: 0 8px 24px rgba(74, 35, 90, 0.15);
    --transition: all 0.3s ease;
    --radius: 8px;
}
```

> **⚠️ Pozor:** Některé barvy jsou hardcodované přímo v CSS (např. `#27445C` v account.css, products.css). Po změně palety prohledej i tyto soubory a nahraď ručně zapsané hodnoty za `var(--text-primary)` atd.

---

## 2. Grid produktů (Products stránka)

### 📁 `assets/css/products.css` — řádky 380–396

**Aktuální: 3 sloupce**

```css
.products-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2.5rem;
}

@media (max-width: 992px) {
    .products-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 576px) {
    .products-grid {
        grid-template-columns: 1fr;
    }
}
```

**Alternativa A — 4 sloupce:**

```css
.products-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 2rem;
}

@media (max-width: 1200px) {
    .products-grid {
        grid-template-columns: repeat(3, 1fr);
    }
}

@media (max-width: 992px) {
    .products-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 576px) {
    .products-grid {
        grid-template-columns: 1fr;
    }
}
```

**Alternativa B — 2 sloupce:**

```css
.products-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2.5rem;
}

@media (max-width: 576px) {
    .products-grid {
        grid-template-columns: 1fr;
    }
}
```

---

## 3. Zaoblení tlačítek

### 📁 `assets/css/style.css` — řádky 123–145

**Aktuální: pilulkový tvar (50px)**

```css
button, .btn {
    cursor: pointer;
    border: none;
    background: linear-gradient(135deg, #27445C 0%, #1a2e3f 100%);
    color: #ffffff;
    padding: 14px 28px;
    border-radius: 50px;
    font-weight: 600;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    font-size: 1rem;
    box-shadow: 0 4px 15px rgba(39, 68, 92, 0.3);
    letter-spacing: 0.5px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}
```

**Alternativa A — Mírně zaoblená (8px):**

```css
button, .btn {
    cursor: pointer;
    border: none;
    background: linear-gradient(135deg, #27445C 0%, #1a2e3f 100%);
    color: #ffffff;
    padding: 14px 28px;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    font-size: 1rem;
    box-shadow: 0 4px 15px rgba(39, 68, 92, 0.3);
    letter-spacing: 0.5px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}
```

**Alternativa B — Ostré hrany (0px):**

```css
button, .btn {
    cursor: pointer;
    border: none;
    background: linear-gradient(135deg, #27445C 0%, #1a2e3f 100%);
    color: #ffffff;
    padding: 14px 28px;
    border-radius: 0;
    font-weight: 600;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    font-size: 1rem;
    box-shadow: 0 4px 15px rgba(39, 68, 92, 0.3);
    letter-spacing: 0.5px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}
```

> **Pozor:** Navbar (`.navbar`) má vlastní `border-radius: 50px`. Pokud měníš zaoblení tlačítek, možná budeš chtít změnit i navbar (viz sekce 4).

---

## 4. Styl navbaru

### 📁 `assets/css/style.css` — řádky 184–199

**Aktuální: poloprůhledný, zaoblený, s blur efektem**

```css
.navbar {
    position: fixed;
    top: 20px;
    left: 0;
    right: 0;
    margin: 0 auto;
    transform: none;
    width: calc(100% - 2rem);
    max-width: calc(1320px - 2rem);
    background-color: rgba(219, 246, 237, 0.5);
    box-shadow: var(--shadow);
    z-index: 1000;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 50px;
}
```

**Alternativa A — Plně bílý navbar (klasický, přilepený nahoře):**

```css
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    margin: 0;
    transform: none;
    width: 100%;
    max-width: 100%;
    background-color: #ffffff;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
    z-index: 1000;
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    border-radius: 0;
}
```

**Alternativa B — Tmavý navbar:**

```css
.navbar {
    position: fixed;
    top: 20px;
    left: 0;
    right: 0;
    margin: 0 auto;
    transform: none;
    width: calc(100% - 2rem);
    max-width: calc(1320px - 2rem);
    background-color: rgba(15, 23, 42, 0.9);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    z-index: 1000;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 50px;
}
```

> **Pozor k tmavému navbaru:** Musíš také změnit barvu textu a odkazů v navbaru:
> `.nav-link { color: #e2e8f0; }` a `.logo span { color: #ffffff; }`

---

## 5. Velikosti nadpisů

### 📁 `assets/css/style.css` — řádky 73–90

**Aktuální:**

```css
h1, h2, h3, h4 {
    font-family: 'TelkaTRIAL', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin-bottom: 1rem;
    line-height: 1.2;
    font-weight: 700;
}

h1 { font-size: 2.5rem; }
h2 { font-size: 2rem; }
h3 { font-size: 1.5rem; }
```

**Alternativa A — Větší (výraznější):**

```css
h1 { font-size: 3.5rem; }
h2 { font-size: 2.5rem; }
h3 { font-size: 1.8rem; }
```

**Alternativa B — Menší (kompaktnější):**

```css
h1 { font-size: 2rem; }
h2 { font-size: 1.5rem; }
h3 { font-size: 1.25rem; }
```

---

## 6. Styl produktových karet

### 📁 `assets/css/products.css` — řádky 486–489

**Aktuální: bez borderu, bez stínu (čistý vzhled)**

```css
.product-card {
    display: flex;
    flex-direction: column;
}
```

**Alternativa A — S borderem a stínem:**

```css
.product-card {
    display: flex;
    flex-direction: column;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1rem;
    background: white;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    transition: all 0.3s ease;
}

.product-card:hover {
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
    transform: translateY(-4px);
    border-color: transparent;
}
```

**Alternativa B — Výrazný stín (bez borderu):**

```css
.product-card {
    display: flex;
    flex-direction: column;
    border-radius: 20px;
    padding: 1rem;
    background: white;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
    transition: all 0.3s ease;
}

.product-card:hover {
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.12);
    transform: translateY(-6px);
}
```

---

## 7. Hover efekt na obrázcích produktů

### 📁 `assets/css/products.css` — řádky 514–526

**Aktuální: při hoveru se obrázek vymění za druhý**

```css
.product-img-hover {
    position: absolute;
    top: 0;
    left: 0;
    opacity: 0;
}

.product-image-link:hover .product-img-hover {
    opacity: 1;
}

.product-image-link:hover .product-img-main {
    opacity: 0;
}
```

**Alternativa A — Vypnout swap (žádná výměna obrázku):**

```css
.product-img-hover {
    display: none;
}

.product-image-link:hover .product-img-hover {
    display: none;
}

.product-image-link:hover .product-img-main {
    opacity: 1;
}
```

**Alternativa B — Zoom efekt místo swapu:**

```css
.product-img-hover {
    display: none;
}

.product-image-link:hover .product-img-main {
    opacity: 1;
    transform: scale(1.08);
    transition: transform 0.4s ease;
}
```

---

## 8. Benefits grid (homepage)

### 📁 `assets/css/style.css` — řádky 746–750

**Aktuální: 4 sloupce**

```css
.benefits-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 2rem;
}
```

**Alternativa A — 3 sloupce:**

```css
.benefits-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
}
```

**Alternativa B — 2 sloupce:**

```css
.benefits-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2rem;
}
```

> **Pozor:** Na řádku 816 je ještě `.fresh-benefits .benefits-grid` s `repeat(4, 1fr)`. Změň obě místa.

---

## 9. Footer barvy

### 📁 `assets/css/style.css` — řádky 1002–1009

**Aktuální: zeleno-modrý gradient**

```css
footer {
    background: linear-gradient(135deg, var(--primary-medium) 0%, var(--primary-light) 100%);
    color: var(--text-primary);
    padding: 4rem 1rem 2rem;
    font-size: 0.95rem;
    box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.05);
    text-align: left;
}
```

**Alternativa A — Tmavý footer:**

```css
footer {
    background: #0f172a;
    color: #e2e8f0;
    padding: 4rem 1rem 2rem;
    font-size: 0.95rem;
    box-shadow: none;
    text-align: left;
}
```

> K tmavému footeru přidej: `.footer-link { color: #94a3b8; }` a `.footer-link:hover { color: #ffffff; }`

**Alternativa B — Bílý footer s horním borderem:**

```css
footer {
    background: #ffffff;
    color: var(--text-primary);
    padding: 4rem 1rem 2rem;
    font-size: 0.95rem;
    box-shadow: none;
    border-top: 1px solid #e2e8f0;
    text-align: left;
}
```

---

## 10. Gap (mezera) mezi produkty

### 📁 `assets/css/products.css` — řádek 383

**Aktuální:**

```css
gap: 2.5rem;
```

**Alternativa A — Menší mezera (těsněji u sebe):**

```css
gap: 1.25rem;
```

**Alternativa B — Větší mezera (vzdušnější):**

```css
gap: 3.5rem;
```

---

## 11. Tlačítko "Do košíku" na produktových kartách

### 📁 `assets/css/products.css` — řádky 567–587

**Aktuální: modro-tyrkysový gradient, zaoblení 6px**

```css
.btn-quick-add {
    margin-top: 0.8rem;
    width: 100%;
    padding: 10px;
    font-size: 0.9rem;
    background: linear-gradient(135deg, var(--primary-light) 0%, #80d8ff 100%);
    color: var(--text-primary);
    border-radius: 6px;
}
```

**Alternativa A — Plná tmavá barva:**

```css
.btn-quick-add {
    margin-top: 0.8rem;
    width: 100%;
    padding: 10px;
    font-size: 0.9rem;
    background: var(--text-primary);
    color: #ffffff;
    border-radius: 6px;
}
```

**Alternativa B — Obrysové tlačítko (outline):**

```css
.btn-quick-add {
    margin-top: 0.8rem;
    width: 100%;
    padding: 10px;
    font-size: 0.9rem;
    background: transparent;
    color: var(--text-primary);
    border: 2px solid var(--text-primary);
    border-radius: 6px;
}

.btn-quick-add:hover {
    background: var(--text-primary);
    color: #ffffff;
    transform: none;
    box-shadow: none;
}
```

---

---

## 12. Checkout formulář — styl inputů

### 📁 `assets/css/cart.css` — řádky 568–585

**Aktuální: zaoblené inputy se světlým pozadím**

```css
.form-input {
    width: 100%;
    height: 52px;
    padding: 0 1.2rem;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    font-size: 1rem;
    background: #f9fafb;
    transition: all 0.3s;
    font-family: inherit;
}

.form-input:focus {
    border-color: var(--text-primary);
    background: #fff;
    outline: none;
    box-shadow: 0 0 0 4px rgba(39, 68, 92, 0.05);
}
```

**Alternativa A — Minimální underline styl:**

```css
.form-input {
    width: 100%;
    height: 52px;
    padding: 0 0.25rem;
    border: none;
    border-bottom: 2px solid #e5e7eb;
    border-radius: 0;
    font-size: 1rem;
    background: transparent;
    transition: all 0.3s;
    font-family: inherit;
}

.form-input:focus {
    border-bottom-color: var(--text-primary);
    background: transparent;
    outline: none;
    box-shadow: none;
}
```

**Alternativa B — Výrazný focus s barevným rámečkem:**

```css
.form-input {
    width: 100%;
    height: 52px;
    padding: 0 1.2rem;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 1rem;
    background: #ffffff;
    transition: all 0.3s;
    font-family: inherit;
}

.form-input:focus {
    border-color: var(--primary-light);
    background: #fff;
    outline: none;
    box-shadow: 0 0 0 3px rgba(169, 236, 255, 0.4);
}
```

---

## 13. Platební metody — styl karet

### 📁 `assets/css/cart.css` — řádky 588–637

**Aktuální: svislé karty s ikonou a textem**

```css
.payment-methods {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 1rem;
}

.payment-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.8rem;
    padding: 1.5rem;
    border: 2px solid #e5e7eb;
    border-radius: 16px;
    transition: all 0.3s;
    background: #f9fafb;
}
```

**Alternativa A — Vodorovné tlačítko (ikona + text vedle sebe):**

```css
.payment-methods {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.payment-content {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 1rem;
    padding: 1rem 1.5rem;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    transition: all 0.3s;
    background: #f9fafb;
}
```

**Alternativa B — Kompaktní mřížka (jen ikona, text pod):**

```css
.payment-methods {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.5rem;
}

.payment-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
    padding: 0.8rem 0.5rem;
    border: 2px solid #e5e7eb;
    border-radius: 10px;
    transition: all 0.3s;
    background: #f9fafb;
    font-size: 0.75rem;
}

.payment-content i {
    font-size: 1.5rem;
}
```

---

## 14. Hero sekce — pozadí a rozložení

### 📁 `assets/css/style.css` — řádky 548–566

**Aktuální: gradient z CSS proměnných**

```css
.hero {
    background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary-medium) 100%);
}

.hero-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 1.5rem;
}
```

**Alternativa A — Tmavý gradient:**

```css
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
}

.hero-title { color: #ffffff; }
.hero-subtitle { color: #94a3b8; }
```

**Alternativa B — Rozdělené rozložení (text vlevo, prostor vpravo):**

```css
.hero {
    background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary-medium) 100%);
}

.hero-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    align-items: center;
    text-align: left;
    gap: 2rem;
}

@media (max-width: 768px) {
    .hero-content {
        grid-template-columns: 1fr;
        text-align: center;
    }
}
```

**Alternativa C — Bílé pozadí s výrazným textem:**

```css
.hero {
    background: #ffffff;
    border-bottom: 1px solid #e5e7eb;
}

.hero-title { color: var(--text-primary); }
```

---

## 15. Hamburger menu — animace

### 📁 `assets/css/style.css` — řádky 447–472

**Aktuální: střední čárka zmizí, krajní se zkříží (X)**

```css
.hamburger.active span:nth-child(1) {
    transform: rotate(45deg) translate(5px, 5px);
}

.hamburger.active span:nth-child(2) {
    opacity: 0;
}

.hamburger.active span:nth-child(3) {
    transform: rotate(-45deg) translate(5px, -5px);
}
```

**Alternativa A — Všechny čárky tvoří X (různé osy):**

```css
.hamburger.active span:nth-child(1) {
    transform: translateY(7px) rotate(45deg);
}

.hamburger.active span:nth-child(2) {
    transform: scaleX(0);
    opacity: 0;
}

.hamburger.active span:nth-child(3) {
    transform: translateY(-7px) rotate(-45deg);
}
```

**Alternativa B — Střední čárka se rozšíří na celou šířku (≡ → —):**

```css
.hamburger.active span:nth-child(1) {
    opacity: 0;
    transform: translateY(-6px);
}

.hamburger.active span:nth-child(2) {
    width: 25px;
    transform: none;
}

.hamburger.active span:nth-child(3) {
    opacity: 0;
    transform: translateY(6px);
}
```

---

## 16. Animace a přechody

### 📁 `assets/css/style.css` — řádky 537–546 (`@keyframes fadeIn`)

**Aktuální: fadeIn (zespoda nahoru + zprůhledňování)**

```css
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
```

**Alternativa A — Slide z leva:**

```css
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateX(-30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}
```

**Alternativa B — Scale-in (zvětšení z malého):**

```css
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: scale(0.85);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}
```

**Alternativa C — Bez animací (přístupnost / preference):**

```css
/* Vypnout animace pro uživatele, kteří preferují no-motion */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.001ms !important;
        transition-duration: 0.001ms !important;
    }
}

/* Nebo úplně vypnout fadeIn pro hero */
.hero-content h1,
.hero-content p,
.hero-content .btn {
    animation: none;
    opacity: 1;
}
```

---

## 17. Loading / prázdný stav

### 📁 `assets/css/cart.css` — řádky 639–650 (`.empty-cart-message`)

**Aktuální: centrovaný text s ikonou**

```css
.empty-cart-message {
    text-align: center;
    padding: 4rem 2rem;
}
```

**Alternativa A — Prázdný stav s výraznou ikonou a CTA:**

```css
.empty-cart-message {
    text-align: center;
    padding: 5rem 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
}

.empty-cart-message::before {
    content: '🛒';
    font-size: 4rem;
    opacity: 0.3;
}

.empty-cart-message h3 {
    color: var(--text-primary);
    font-size: 1.5rem;
}

.empty-cart-message p {
    color: var(--text-secondary);
    max-width: 300px;
}
```

**Alternativa B — Skeleton loading placeholder (pro produkty):**

```css
/* Přidej třídu .skeleton na element, dokud se data nenačtou */
.skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
    border-radius: 8px;
    color: transparent;
    pointer-events: none;
}

@keyframes skeleton-loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* Použití v produktovém gridu */
.product-card.skeleton .product-img { height: 220px; }
.product-card.skeleton .product-title { height: 1.2rem; margin-bottom: 0.5rem; }
.product-card.skeleton .product-price { height: 1rem; width: 60%; }
```

---

## 18. Kombinace — celkový redesign

Kombinuj více sekcí pro konzistentní nový vzhled. **Vždy změň `:root` jako první.**

### Kombinace A — Dark Mode (tmavý celkový styl)

1. **Barvy** (sekce 1, Alternativa B):
   ```css
   :root {
       --primary-light: #1e3a5f;
       --primary-medium: #0f1c2e;
       --text-primary: #e2e8f0;
       --text-secondary: #94a3b8;
       --background: #0f172a;
       --light-bg: #1e293b;
   }
   ```

2. **Navbar** (sekce 4, Alternativa B) — tmavý navbar

3. **Footer** (sekce 9, Alternativa A) — tmavý footer:
   ```css
   footer { background: #0a0f1a; color: #e2e8f0; }
   ```

4. **Hero** (sekce 14, Alternativa A) — tmavý gradient

5. **Produktové karty** (sekce 6, Alternativa B) — tmavé pozadí:
   ```css
   .product-card { background: #1e293b; }
   ```

> **Pozor:** U dark mode zkontroluj kontrast textu. Hardcodované barvy `#27445C` v `account.css` a `products.css` nahraď `var(--text-primary)`.

---

### Kombinace B — Warm / Cozy (teplý béžový styl)

1. **Barvy** (sekce 1, Alternativa A):
   ```css
   :root {
       --primary-light: #FFD6A5;
       --primary-medium: #FFF1E0;
       --text-primary: #5C3D27;
       --text-secondary: #B9785A;
       --background: #FFFAF5;
   }
   ```

2. **Tlačítka** (sekce 3, Alternativa A) — mírné zaoblení (8px)

3. **Navbar** (sekce 4, Aktuální) — zaoblený s blur efektem (ponech beze změny)

4. **Produktové karty** (sekce 6, Alternativa A) — s borderem a shadow:
   ```css
   .product-card { border: 1px solid #e8d5c4; border-radius: 16px; }
   ```

5. **Hero** (sekce 14, Alternativa C) — bílé pozadí

---

## 19. Responzivní breakpointy

### 📁 `assets/css/products.css`, `style.css` — media queries

**Aktuální: 2 breakpointy (992px, 576px)**

```css
@media (max-width: 992px) { /* tablet */ }
@media (max-width: 576px) { /* mobil */ }
```

**Alternativa A — Přidání 1200px breakpointu (large desktop):**

```css
/* Přidej před stávající media queries v každém souboru */
@media (max-width: 1200px) {
    .products-grid { grid-template-columns: repeat(3, 1fr); }
    .container { max-width: 960px; }
}

@media (max-width: 992px) {
    .products-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 576px) {
    .products-grid { grid-template-columns: 1fr; }
}
```

**Alternativa B — Zjednodušení na jeden breakpoint (768px):**

```css
/* Smaž breakpoint na 992px, ponech jen jeden */
@media (max-width: 768px) {
    .products-grid { grid-template-columns: 1fr; }
    .navbar .nav-links { display: none; }
    .hamburger { display: flex; }
}
```

---

## Rychlý přehled souborů

| Co měníš | Soubor | Řádky (přibližně) |
|----------|--------|-----|
| Barvy celého webu | `assets/css/style.css` | 2–16 |
| Grid produktů | `assets/css/products.css` | 380–396 |
| Zaoblení tlačítek | `assets/css/style.css` | 123–145 |
| Navbar | `assets/css/style.css` | 184–199 |
| Nadpisy | `assets/css/style.css` | 73–90 |
| Produktové karty | `assets/css/products.css` | 486–489 |
| Hover obrázků | `assets/css/products.css` | 514–526 |
| Benefits grid | `assets/css/style.css` | 746–750 |
| Footer | `assets/css/style.css` | 1002–1009 |
| Mezera v gridu | `assets/css/products.css` | 383 |
| Tlačítko do košíku | `assets/css/products.css` | 567–587 |
| Checkout formulář inputy | `assets/css/cart.css` | 568–585 |
| Platební metody | `assets/css/cart.css` | 588–637 |
| Hero sekce | `assets/css/style.css` | 548–566 |
| Hamburger animace | `assets/css/style.css` | 447–472 |
| Animace fadeIn | `assets/css/style.css` | 537–546 |
| Prázdný stav košíku | `assets/css/cart.css` | 639–650 |
| Responzivní breakpointy | všechny CSS soubory | media queries |
