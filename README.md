📘 SPSKladno – Nastavení VS Code a GIT ve školním prostředí
Ve škole je Python, Git i VS Code nainstalováno jako portable verze na serveru.
Aby vše správně fungovalo, postupuj podle tohoto návodu.

🅰️ Část A – Jednorázové nastavení (stačí udělat jednou)
1️⃣ Nastavení VS Code (settings.json)
Otevři příkazovou paletu:

Ctrl + Shift + P → „Open User Settings (JSON)”

Vlož následující konfiguraci:

json
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
Otevři Git Bash Portable (v liště terminálu klikni na šipku vedle +) a zadej:

bash
git config --global user.email "tvuj@email.cz"
git config --global user.name "TvujNick"
git config --global credential.helper store
🔁 Nahraď údaje svými (např. z GitHubu).

3️⃣ Instalace rozšíření ve VS Code
Otevři Extensions (Ctrl + Shift + X) a nainstaluj:

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

bash
git clone https://github.com/uzivatel/nazev-repozitare.git
Nebo klonování do aktuální složky:

bash
git clone https://github.com/uzivatel/nazev-repozitare.git .
Přes VS Code:

Ctrl + Shift + P

„Git: Clone“

vlož URL repozitáře

6️⃣ Povolení spouštění skriptů (nutné po každém restartu PC)
powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
7️⃣ Vytvoření virtuálního prostředí (venv)
powershell
& "G:/win32app/Portable Python-3.13.3 x64/python.exe" -m venv venv
8️⃣ Aktivace virtuálního prostředí
powershell
.\venv\Scripts\activate
9️⃣ Instalace balíčků (pip install)
bash
pip install nazev-balicku
Příklady:

bash
pip install flask
pip install pandas matplotlib
pip install pygame
Pokud máš requirements.txt:

bash
pip install -r requirements.txt
🔟 Uložení závislostí (pip freeze)
Zobrazení balíčků:

bash
pip freeze
Uložení do souboru:

bash
pip freeze > requirements.txt
💡 Po každé instalaci nového balíčku aktualizuj requirements.txt.

📋 Shrnutí kroků
🅰️ Část A – Jednorázové nastavení
#	Co udělat	Kde
1	Nastavit settings.json	VS Code – User Settings (JSON)
2	Nastavit Git identitu	Git Bash Portable
3	Instalovat Python + Jupyter	VS Code – Extensions


🅱️ Část B – Pro každý nový projekt
#	Co udělat	Kde
4	Otevřít složku projektu	VS Code – File → Open Folder
5	Naklonovat repozitář	Terminál / Git: Clone
6	Povolit skripty	PowerShell
7	Vytvořit venv	PowerShell
8	Aktivovat venv	PowerShell
9	Instalovat balíčky	PowerShell (s aktivním venv)
10	Uložit závislosti	



git : Romean972