# Dokumentace datového schématu

Aplikace používá hierarchický datový model v JSON.

## Entita: User (uživatel)
Kořenové klíče v `users.json` představují unikátní uživatelská jména.

### Atributy:
- **workouts** (List[Object]): Historie tréninkových jednotek.
- **personal_records** (Object): Nejvyšší zvednutá váha podle cviku.
- **progress_data** (Object): Historie výkonu podle cviku.
- **bodyweight** (Number): Aktuální tělesná váha v kg.
- **bodyweight_history** (List[Object]): Historie tělesné váhy.

## Entita: Workout (trénink)
Představuje jednu tréninkovou jednotku.

### Atributy:
- **date** (String): Časový údaj (YYYY-MM-DD HH:MM:SS).
- **note** (String): Poznámka uživatele.
- **summary** (String): Textový souhrn tréninku.
- **exercises** (List[Tuple]): Seznam provedených cviků.
  - Formát: `[NázevCvičení, Série, Opakování, Váha]`

## Entita: Progress Entry (záznam progresu)
Reprezentuje výkon pro konkrétní cvik v konkrétní den.

### Atributy:
- **date** (String): Datum tréninku (YYYY-MM-DD).
- **sets** (Integer): Počet sérií.
- **reps** (Integer): Počet opakování.
- **weight** (Integer): Váha v kg.
- **volume** (Integer): Celkový objem (sets * reps * weight).

## Entita: Bodyweight Entry (záznam váhy)
Záznam o tělesné váze.

### Atributy:
- **date** (String): Datum záznamu (YYYY-MM-DD).
- **weight** (Number): Váha v kg.

## Vztahy
- Jeden **User** má mnoho **Workouts**.
- Jeden **User** má mnoho **Personal Records** (jeden pro každý typ cviku).
- Jeden **User** má mnoho **Progress Entries** (sdružených podle typu cviku).
- Jeden **User** má mnoho **Bodyweight Entries** (historie tělesné váhy).
