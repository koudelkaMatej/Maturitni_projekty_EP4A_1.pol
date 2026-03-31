# 💀 DASH! DIE! REPEAT!

> Top-down akční hra v Pygame propojená s Django webovým backendem a SQLite databází.

---

## O projektu

**Dash! Die! Repeat!** je fullscreen akční hra (1920×1080) ve které hráč ovládá postavu schopnou provádět útočný dash směrem ke kurzoru myši. Cílem je přežít co nejdéle vlnu neustále se množících nepřátel a dosáhnout co nejvyššího skóre — které se automaticky ukládá na server.

Projekt se skládá ze dvou propojených aplikací:
- **Pygame hra** — herní engine s animacemi, combat systémem a AI nepřátel
- **Django web** — uživatelské účty, profily, high-score databáze a dokumentační stránka

---

## Technologie

| Vrstva | Technologie | Verze |
|--------|-------------|-------|
| Herní engine | Pygame | 2.6.1 |
| Web framework | Django | 5.2.10 |
| Databáze | SQLite (Django ORM) | built-in |
| HTTP klient | requests | 2.32.5 |
| Asynchronní volání | threading | built-in |
| Matematika / fyzika | math | built-in |
| CORS | django-cors-headers | 4.9.0 |

---

## Instalace a spuštění

### 1. Klonování repozitáře

```bash
git clone https://github.com/koudelkaMatej/Maturitni_projekty_EP4A_1.pol.git
cd "Kodera Tomáš/databaze"
```

### 2. Instalace závislostí

```bash
pip install -r requirements.txt
```

### 3. Inicializace databáze a spuštění serveru

```bash
python manage.py migrate
python manage.py runserver
```

Web bude dostupný na: **http://127.0.0.1:8000**

### 4. Spuštění hry (v druhém terminálu)

```bash
cd ../projekt
python menu.py
```

---

## Ovládání

| Akce | Klávesa / tlačítko |
|------|--------------------|
| Pohyb | `W` `A` `S` `D` |
| Dash / Útok | Levé tlačítko myši (`LMB`) |
| Frenzy Mode | Aktivuje se automaticky |
| Restart po smrti | `Enter` |
| Návrat do menu | `Escape` |

---

## Herní mechaniky

### Dash systém
Kliknutím LMB se hráč vrhne směrem ke kurzoru o vzdálenost 250 px. Dash zanechává krvavou stopu (8 cákanců podél trasy) a ničí všechny nepřátele, které zasáhne.

### Combo & Frenzy Mode
- Dash, který zasáhne **5 nebo více nepřátel**, zvýší combo čítač o 1
- Po **3 combo-dasích** se aktivuje **Frenzy Mode** (5 sekund):
  - Hráč se pohybuje 1,5× rychleji
  - Nepřátelé zpomalí
  - Cooldown dashe se zkrátí na 600 ms

### Adaptivní obtížnost
- Skóre ≥ 50 → nepřátelé rychlost 3
- Skóre ≥ 100 → nepřátelé rychlost 4

---

## Struktura projektu

```
databaze/               ← Django projekt (settings, urls, wsgi)
myapp/                  ← Django aplikace
  ├─ models.py          ← Profile model (FK → auth_user)
  ├─ views.py           ← Views + REST API endpoint
  ├─ urls.py            ← URL routing
  ├─ admin.py           ← Admin panel
  └─ templates/main/    ← HTML šablony

projekt/                ← Pygame aplikace
  ├─ main.py            ← Herní smyčka, Player, Enemy, BloodSplat
  ├─ menu.py            ← Hlavní menu, výběr jména
  └─ assets/            ← Sprity, animace, fonty

manage.py
requirements.txt
db.sqlite3
```

---

## REST API

### `POST /api/update_score/`

Aktualizuje high-score hráče. Skóre se uloží pouze pokud je vyšší než dosavadní rekord.

**Request body:**
```json
{
  "username": "SlayerX",
  "score": 142
}
```

**Response:**
```json
{
  "status": "success",
  "new_highscore": true
}
```

Volání probíhá asynchronně přes `threading` — hra se při odesílání nezasekne.

---

## Databázový model

```
auth_user          myapp_profile
─────────────      ─────────────────
id (PK)      1──1  id (PK)
username           user_id (FK → auth_user)
password           score (DEFAULT 0)
email              email
is_active
date_joined
```

Vztah **1:1** — každý uživatel má právě jeden profil. Smazání uživatele automaticky smaže i jeho profil (`ON DELETE CASCADE`).

Databáze splňuje **BCNF normalizaci** — žádné redundance, každá funkční závislost je určena nadklíčem.

---

## Webová aplikace

- **Registrace / přihlášení** — Django Auth (`/register/`, `/login/`, `/logout/`)
- **Profil** — zobrazuje uložené high-score z databáze
- **Admin panel** — `python manage.py createsuperuser` → `/admin/`
- **Dokumentační stránka** — algoritmy, ER diagram, manuál, onboarding

---

## Časté problémy

**Hra neposílá skóre**
Zkontroluj, že Django server běží na portu 8000. Ověř URL v `main.py` → funkce `send_score_to_server()` a CORS nastavení v `settings.py`.

**Chyba migrace databáze**
Smaž `db.sqlite3` a složku `myapp/migrations/` (kromě `__init__.py`), poté spusť `makemigrations` a `migrate` znovu. Pozor — přijdeš o data.

**Pygame ImportError**
Ujisti se, že máš aktivní správné virtuální prostředí a nainstalované balíčky přes `pip install -r requirements.txt`. Pygame 2.6 vyžaduje Python 3.8+.
