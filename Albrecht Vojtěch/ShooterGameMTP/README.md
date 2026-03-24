1. Stažení projektu
Rozbal ZIP soubor projektu, nebo klonuj repozitář:
bashgit clone <url-repozitare>
cd <nazev-slozky>
2. Vytvoření virtuálního prostředí (doporučeno)
bashpython -m venv venv
Aktivace:

Windows: venv\Scripts\activate
macOS / Linux: source venv/bin/activate

3. Instalace závislostí
bashpip install flask werkzeug pygame requests pyvidplayer2 static-ffmpeg
```

---

## 🗂️ Struktura projektu
```
projekt/
├── main.py                  # Flask backend + REST API
├── ShooterGameMTP.py        # Herní engine (Pygame)
├── database.db              # SQLite databáze (vytvoří se automaticky)
├── Audiowide-Regular.ttf    # Herní font
│
├── templates/               # HTML šablony pro Flask
│   ├── MTP.html
│   ├── ActiveUsers.html
│   ├── ScoreBoard.html
│   ├── admin.html
│   ├── prezentace.html
│   ├── prezentace-investor.html
│   ├── prezentace-kolega.html
│   └── prezentace-novyuzivatel.html
│
├── static/                  # Obrázky, video, fonty pro web
│   ├── background.png
│   ├── background_video.mp4
│   └── ...
│
└── sprites/                 # Herní sprity
    ├── hrac.png
    ├── enemy1.png / enemy2.png
    ├── strela.png / enemystrela.png
    └── heart.png

⚠️ Složky sprites/ a static/ musí obsahovat všechny soubory. Bez nich hra poběží, ale bez grafiky.


▶️ Spuštění
Hra vyžaduje dva spuštěné terminály zároveň.
Terminál 1 – Flask server (backend)
bashpython main.py
Server poběží na http://127.0.0.1:5000. Databáze se vytvoří automaticky při prvním spuštění.
Terminál 2 – Hra
bashpython ShooterGameMTP.py
Pokud server neběží, hra tě automaticky přihlásí jako hosta (skóre se neukládá).

🌐 Webové rozhraní
StránkaURLHlavní stránkahttp://127.0.0.1:5000/Registracehttp://127.0.0.1:5000/signupPřihlášeníhttp://127.0.0.1:5000/signinŽebříčekhttp://127.0.0.1:5000/scoreboardPrezentacehttp://127.0.0.1:5000/prezentaceAdmin panel http://127.0.0.1:5000/admin

🎮 Ovládání hry
KlávesaAkce↑Pohyb nahoru↓Pohyb dolůSPACEStřelbaSSlow Motion (5 s aktivní, cooldown 15 s)

👾 Nepřátelé a bodování
TypPopisBody🔴 Typ 1Rychlý, letí přímo na hráče+1 bod🟣 Typ 2Pomalejší, ale střílí projektily+2 body
Každých 10 bodů se nepřátelé zrychlí. Hráč má 3 životy.

🔌 REST API přehled
MetodaEndpointPopisPOST/api/signupRegistrace nového uživatelePOST/api/loginPřihlášení, vrací user_idPOST/api/submit_scoreUloží skóre po konci hryGET/api/scoreboardVrátí top 10 hráčů jako JSON

❓ Časté problémy
ModuleNotFoundError
bashpip install flask werkzeug pygame requests pyvidplayer2 static-ffmpeg
Chybí grafika / sprity
Zkontroluj obsah složek sprites/ a static/.
Chyba při přihlašování v hře
main.py musí běžet před spuštěním ShooterGameMTP.py.
Video se nezobrazuje
Soubor static/background_video.mp4 musí existovat – jinak hra automaticky použije statické pozadí.
Port 5000 je obsazený
V main.py změň: app.run(debug=True, threaded=True, port=5001)
V ShooterGameMTP.py uprav: BASE_URL = "http://127.0.0.1:5001/api"
