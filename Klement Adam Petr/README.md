# Fitness App — projekt

Tento projekt obsahuje desktopovou aplikaci (Kivy), webové rozhraní (Flask) a sdílený datový systém (JSON).

## Struktura projektu

- `main.py` & `fitness.kv` — Desktop aplikace (Kivy)
- `web_app.py` — Webová aplikace (Flask)
- `data_manager.py` — Sdílená logika práce s daty
- `data/` — Úložiště databáze (JSON)
- `tests/` — Automatické testy

## Instalace

1. Nainstaluj Python (doporučeno 3.10–3.12 kvůli Kivy).
   - Poznámka: Python 3.14 může dělat problémy s Kivy. Pokud narazíš na chybu, použij Python 3.12.
2. Nainstaluj závislosti:
   ```bash
   pip install -r requirements.txt
   ```
   nebo použij `install_dependencies.bat`.

## Spuštění

### 1) Desktop aplikace (Kivy)
Spuštění:
```bash
python main.py
```
nebo dvojklikem `start_game.bat`.
- Přihlášení: `admin` / `1234`
- Funkce: přidávání tréninků, PR, graf pokroku, váha.

### 2) Webová aplikace (Flask)
Spuštění:
```bash
python web_app.py
```
nebo `start_website.bat`.
- Otevři `http://localhost:5000` v prohlížeči.
- Dashboard, nastavení účtu, historie tréninků, detail tréninku.

### 3) Testy
Spuštění testů:
```bash
python -m unittest tests/test_data_manager.py
```

## Dokumentace

### Milníky
- **Listopad**: nápad, design, datový model.
- **Leden**: jádro aplikace + databáze + propojení s webem. (splněno)
- **Březen**: ladění, doplnění funkcí, úpravy UI.

### Datový systém
Data jsou v JSON (`data/users.json`). Přístup je přes třídu `DataManager`, díky čemuž používá stejná data jak hra, tak web.

### Funkce
- **Tréninky**: cviky, série, opakování, váha, poznámky.
- **Progres**: automatické PR, objem, grafy.
- **Přístup**: desktop i web, sdílená databáze.
