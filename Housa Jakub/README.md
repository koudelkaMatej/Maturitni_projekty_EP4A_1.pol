# DRIVE. | E-shop s čistou energií (Maturitní projekt)

Tento repozitář obsahuje zdrojové kódy pro maturitní projekt. Jedná se o plně funkční e-shop s kofeinovou vodou "DRIVE.", který je postaven na moderních webových technologiích. Aplikace běží v prostředí Node.js a k ukládání dat využívá lokální databázi SQLite.

## Použité technologie
- **Koncept / Backend:** Node.js, Express.js
- **Databáze:** SQLite (balíček `better-sqlite3`)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Zpracování dat:** PDFKit (generování faktur), Nodemailer (odesílání e-mailů), bcryptjs (hashování hesla)

## Požadavky pro spuštění
K bezproblémovému spuštění projektu potřebujete mít na svém počítači nainstalované:
- **Node.js** (doporučená verze: `22.16.0`, případně jiná aktuální LTS)
- Příkazový řádek / Terminál (např. v aplikaci VS Code)

> Projekt je připraven pro **offline spuštění**. V repozitáři jsou zahrnuty i frontend knihovny v `node_modules` (Font Awesome, Quill, QRCode), takže po stažení z GitHubu není nutné nic dalšího stahovat z internetu.

## Jak projekt spustit

1. **Otevření repozitáře**
   Otevřete si hlavní složku projektu v terminálu.

2. **Instalace závislostí**
   Pro učitelský testovací počítač **není nutné spouštět** `npm install`, pokud je repozitář stažený kompletně včetně složky `node_modules`.

   Pokud by někdo měl repozitář bez `node_modules`, pak je možné závislosti doinstalovat příkazem:
   ```bash
   npm install
   ```

3. **Spuštění serveru**
   Uveďte lokální server do provozu příkazem:
   ```bash
   npm start
   ```

4. **Přístup do e-shopu**
   Po úspěšném spuštění se v terminálu zobrazí informace o běžícím portu (standardně to bývá `3000`). E-shop si následně projdete ve svém webovém prohlížeči na adrese: `http://localhost:3000`

## Offline režim (bez internetu)
- Externí CDN odkazy byly nahrazeny lokálními cestami (`/node_modules/...`), takže ikony a editor dokumentace fungují i bez internetu.
- QR platba používá lokální knihovnu `qrcodejs`.
- Google Pay a PayPal jsou v tomto školním projektu vedeny jako **testovací/simulační** scénáře; při offline provozu se objednávka dokončí lokální simulací.

## Učitelské přihlášení (Demo účet)
Pro přihlášení do předpřipraveného účtu pro hodnocení můžete využít tyto údaje:
- **E-mail:** `ucitel@spskladno.cz`
- **Heslo:** `ucitel`

*(Pozn.: Údaje byly vytvořeny předem pro usnadnění procházení aplikace a účet má již nasimulovanou fiktivní historii nákupů.)*

## Databáze
Aplikace k chodu používá souborovou databázi SQLite. Data se ukládají lokálně (primárně do souboru `site.db` v kořeni projektu). Při **prvním spuštění** projektu se databáze automaticky inicializuje, vytvoří strukturu tabulek a sama se naplní výchozími testovacími daty (kategorie, produkty aj.). Z hlediska chodu databáze tedy není nutný žádný manuální zásah.

## Upozornění pro práci z OneDrive
Pokud spouštíte projekt z cloudu, jako je OneDrive, ujistěte se prosím, že jsou veškeré soubory aplikace plně stažené uvnitř lokální paměti vašeho počítače (tzv. "Vždy zachovat na tomto zařízení"). Pokud se spouští aplikace, která má soubory s ikonou "online obláčku", mohla by se probíhající synchronizace souborů při zapisování údajů neshodnout se serverem a vyústilo by to v chybovost čtení/zápisu databáze.
