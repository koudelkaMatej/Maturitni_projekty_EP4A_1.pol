# ER Diagram - Fitness App (AMP)

Tento diagram znázorňuje vztahy v databázi aplikace. Splňuje požadavky na vztahy 1:N a M:N.

```mermaid
erDiagram
    USERS ||--o{ WORKOUTS : "má (1:N)"
    USERS ||--o{ BODYWEIGHT_HISTORY : "zaznamenává (1:N)"
    WORKOUTS ||--o{ WORKOUT_ITEMS : "obsahuje (1:N)"
    EXERCISES ||--o{ WORKOUT_ITEMS : "je v (1:N)"
    
    USERS {
        int id PK
        string username UNIQUE
        string password
        string email
        string role
        int is_banned
        float bodyweight
    }

    EXERCISES {
        int id PK
        string name UNIQUE
        timestamp last_updated
    }

    WORKOUTS {
        int id PK
        int user_id FK
        timestamp date
        string note
    }

    WORKOUT_ITEMS {
        int id PK
        int workout_id FK
        int exercise_id FK
        int sets
        int reps
        float weight
    }

    BODYWEIGHT_HISTORY {
        int id PK
        int user_id FK
        float weight
        timestamp date
    }
```

### Popis vztahů:
1.  **USERS -> WORKOUTS (1:N)**: Jeden uživatel může mít mnoho tréninků.
2.  **USERS -> BODYWEIGHT_HISTORY (1:N)**: Jeden uživatel si může ukládat historii své váhy.
3.  **WORKOUTS <-> EXERCISES (M:N)**: Trénink obsahuje mnoho cviků a jeden cvik se může objevit v mnoha trénincích. Tento vztah je realizován přes spojovací tabulku **WORKOUT_ITEMS**.
