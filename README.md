<<<<<<< HEAD
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
=======
📘 SPSKladno – Nastavení VS Code a GIT ve školním prostředí

Ve škole je Python, Git i VS Code nainstalováno jako portable verze na serveru.
Aby vše správně fungovalo, postupuj podle tohoto návodu.

🅰️ Část A – Jednorázové nastavení (stačí udělat jednou)
1️⃣ Nastavení VS Code (settings.json)

Otevři příkazovou paletu:

Ctrl + Shift + P → Open User Settings (JSON)

Vlož následující konfiguraci:

{
  "terminal.integrated.profiles.windows": {
    "Git Bash Portable": {
      "path": "G:/win32app/git_portable/bin/bash.exe",
      "args": ["--login", "-i"]
    }
  },
  "git.path": "G:/win32app/git_portable/cmd/git.exe",
  "git.enabled": true,
  "files.autoSave": "afterDelay",
  "git.enableSmartCommit": true,
  "git.autofetch": "all"
}

⚠️ Pokud už v souboru něco máš, přidej jen položky — neduplikuj vnější {}.

2️⃣ Nastavení Git identity

Otevři Git Bash Portable
(v liště terminálu klikni na šipku vedle +) a zadej:

git config --global user.email "tvuj@email.cz"
git config --global user.name "TvujNick"
git config --global credential.helper store

🔁 Nahraď údaje svými (např. z GitHubu).

3️⃣ Instalace rozšíření ve VS Code

Otevři Extensions:

Ctrl + Shift + X

Nainstaluj:

Python (ms-python.python)
Jupyter (ms-toolsai.jupyter)

💡 Stačí zadat „Python“ nebo „Jupyter“.

🅱️ Část B – Pro každý nový projekt (i po restartu PC)
4️⃣ Vytvoření a otevření složky projektu
VS Code → File → Open Folder…

Vyber nebo vytvoř složku projektu.

💡 Vždy pracuj v otevřené složce — VS Code pak správně rozpozná projekt, Git i venv.

5️⃣ Naklonování Git repozitáře

V terminálu (PowerShell nebo Git Bash):

git clone https://github.com/uzivatel/nazev-repozitare.git

Nebo do aktuální složky:

git clone https://github.com/uzivatel/nazev-repozitare.git .

Přes VS Code:

Ctrl + Shift + P → Git: Clone
6️⃣ Povolení spouštění skriptů (nutné po každém restartu PC)
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
7️⃣ Vytvoření virtuálního prostředí (venv)
& "G:/win32app/Portable Python-3.13.3 x64/python.exe" -m venv venv
8️⃣ Aktivace virtuálního prostředí
.\venv\Scripts\activate
9️⃣ Instalace balíčků
pip install nazev-balicku

Příklady:

pip install flask
pip install pandas matplotlib
pip install pygame

Pokud máš requirements.txt:

pip install -r requirements.txt
🔟 Uložení závislostí

Zobrazení balíčků:

pip freeze

Uložení do souboru:

pip freeze > requirements.txt

💡 Po každé instalaci nového balíčku aktualizuj requirements.txt.

📋 Shrnutí kroků
🅰️ Jednorázové nastavení
#	Co udělat	Kde
1	Nastavit settings.json	VS Code
2	Nastavit Git identitu	Git Bash
3	Instalovat Python + Jupyter	Extensions
🅱️ Každý projekt
#	Co udělat	Kde
4	Otevřít složku projektu	VS Code
5	Naklonovat repozitář	Terminál / Git Clone
6	Povolit skripty	PowerShell
7	Vytvořit venv	PowerShell
8	Aktivovat venv	PowerShell
<<<<<<< HEAD
9	Instalovat balíčky	PowerShell (s aktivním venv)
10	Uložit závislosti	
<<<<<<< HEAD
>>>>>>> fe6309f (odevzani znova)
=======



git : Romean972
>>>>>>> 6223a6c (gi)
=======
9	Instalovat balíčky	venv
10	Uložit závislosti	requirements.txt




git:Romean972
>>>>>>> 79a5136 (zas git)
