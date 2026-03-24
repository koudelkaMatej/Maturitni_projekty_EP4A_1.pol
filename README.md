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
9	Instalovat balíčky	venv
10	Uložit závislosti	requirements.txt




git:Romean972