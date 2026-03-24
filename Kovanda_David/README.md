# Snake projekt

## Požadavky
- Python 3.10+
- pip
- (doporučeno) virtuální prostředí

## Instalace závislostí
1. Aktivuj virtuální prostředí (např. `.venv\Scripts\Activate.ps1`).
2. Spusť:
```
pip install -r requirements.txt
```

## Backend (Flask)
```bash
cd backend
python app.py
```
Server běží na `http://localhost:5000`.

## Frontend (statické HTML)
- Otevři kořen projektu ve VS Code a spusť Live Server (typicky `http://127.0.0.1:5500`).
- Hlavní stránky: `Přihlášení.html`, `Registrace.html`, `O Projektu.html`, `Diagramy.html`, `Můj účet.html`.
- Dokumentace: `manual-pro-uzivatele.html`, `Prezentace-pro-investora.html`, `Prehled-pro-noveho-spolupracovnika.html`, `O-hre.html`.
- Vlastní CSS pro dokumentaci: `manual-pro-uzivatele.css`, `prezentace-pro-investora.css`, `prehled-pro-noveho-spolupracovnika.css`.

## Hra (snake_game.py)
```bash
python snake_game.py
```

## Poznámky
- Token se ukládá do `localStorage` (`snake_token`).
- API CORS je povolené přes `flask-cors`.
- Manuál pro uživatele je teď samostatná stránka `manual-pro-uzivatele.html`.
- Pro nasazení uprav konfiguraci (SECRET_KEY, CORS) v `backend/app.py`.
