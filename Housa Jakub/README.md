# E-shop s kofeinovou vodou

Tohle je školní projekt e-shop. Běží na Node.js a používá lokální databázi SQLite.

## Co je potřeba
K tomu, aby to běželo, potřebujete mít v počítači nainstalovaný Node.js.

## Jak to rozchodit

1. Otevřete si tuhle složku v příkazovém řádku (nebo v terminálu ve VS Code).

2. Nainstalujte potřebné balíčky příkazem:
   npm ci
   (pokud to nepůjde, zkuste npm install)

3. Spusťte server příkazem:
   npm start

4. V terminálu by se mělo vypsat, na jakém portu to běží (obvykle 3000).

5. Otevřete prohlížeč a jděte na adresu:
   http://localhost:3000

## Databáze
Projekt používá souborovou databázi SQLite. Data se ukládají lokálně do souboru (třeba site.db nebo ve složce data/). Při prvním spuštění by se měla databáze sama připravit a naplnit testovacími daty (produkty atd.), takže nemusíte nic nastavovat ručně.

## Poznámka k OneDrive
Pokud máte projekt na OneDrive, dejte si pozor, aby byly soubory stažené v počítači (v režimu "Vždy zachovat na tomto zařízení"). Jinak může databáze blbnout, když se ji OneDrive bude snažit synchronizovat ve chvíli, kdy do ní server zapisuje.
