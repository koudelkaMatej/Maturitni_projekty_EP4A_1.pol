
Tento repozitář obsahuje zdrojové kódy pro maturitní projekt. Jedná se o plně funkční e-shop s kofeinovou vodou "DRIVE.", který je postaven na moderních webových technologiích. Aplikace běží v prostředí Node.js a k ukládání dat využívá lokální databázi SQLite.

## Použité technologie
- **Koncept / Backend:** Node.js, Express.js
- **Databáze:** SQLite (balíček `better-sqlite3`)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Zpracování dat:** PDFKit (generování faktur), Nodemailer (odesílání e-mailů), bcryptjs (hashování hesla)

## Požadavky pro spuštění
K bezproblémovému spuštění projektu potřebujete mít na svém počítači nainstalované:
- **Node.js v20 LTS** (doporučená verze: `20.x.x` — aktuální LTS)
- Příkazový řádek / Terminál (např. v aplikaci VS Code)

## Instalace Node.js

1. Přejděte na [https://nodejs.org](https://nodejs.org) a stáhněte verzi **20 LTS**
2. Spusťte instalátor a projděte průvodcem (vše ponechte výchozí)
3. Po instalaci restartujte terminál
4. Ověřte instalaci:
   ```bash
   node --version
   npm --version
   ```

## Povolení spouštění skriptů v PowerShell

Pokud se při spuštění `npm` zobrazí chyba `running scripts is disabled on this system`, je nutné povolit spouštění skriptů. Otevřete PowerShell **jako správce** a zadejte:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Potvrďte volbou `A` (Ano). Poté zavřete a znovu otevřete terminál.

> Alternativně lze místo PowerShell použít klasický **příkazový řádek (cmd)**, kde toto omezení neplatí.

## Jak projekt spustit

1. **Otevření repozitáře**
   Otevřete si hlavní složku projektu v terminálu.

2. **Instalace závislostí**
   Nainstalujte potřebné balíčky příkazem:
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

## Vývojářský režim (Dev Mode)

Dev mód zpřístupňuje vývojářskou dokumentaci, správu slevových kódů a hromadný newsletter.

**Jak vstoupit:**

1. Otevřete jakoukoliv stránku e-shopu
2. 5× rychle stiskněte klávesu `d` (do 2 sekund)
3. Zadejte heslo: `kO2N37Ac`
4. Po přihlášení se v navigaci objeví odkaz „Vývoj" a v pravém dolním rohu plovoucí badge DEV

Alternativně: přistupte přímo na `/dev-enable`

## Databáze
Aplikace k chodu používá souborovou databázi SQLite. Data se ukládají lokálně (primárně do souboru `site.db` v kořeni projektu). Při **prvním spuštění** projektu se databáze automaticky inicializuje, vytvoří strukturu tabulek a sama se naplní výchozími testovacími daty (kategorie, produkty aj.). Z hlediska chodu databáze tedy není nutný žádný manuální zásah.

## Upozornění pro práci z OneDrive
Pokud spouštíte projekt z cloudu, jako je OneDrive, ujistěte se prosím, že jsou veškeré soubory aplikace plně stažené uvnitř lokální paměti vašeho počítače (tzv. "Vždy zachovat na tomto zařízení"). Pokud se spouští aplikace, která má soubory s ikonou "online obláčku", mohla by se probíhající synchronizace souborů při zapisování údajů neshodnout se serverem a vyústilo by to v chybovost čtení/zápisu databáze.
