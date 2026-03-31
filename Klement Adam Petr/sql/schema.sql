-- Schéma databáze pro Fitness App
-- Splňuje požadavky na 1:N a M:N vztahy a BCNF normalizaci

-- Tabulka uživatelů (PK: id)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT,
    role TEXT DEFAULT 'user',
    is_banned INTEGER DEFAULT 0,
    bodyweight REAL DEFAULT 0
);

-- Tabulka cvičení (PK: id)
CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabulka tréninků (PK: id, FK: user_id -> users.id)
-- Vztah 1:N (Jeden uživatel má více tréninků)
CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Tabulka položek tréninku (PK: id, FK: workout_id, exercise_id)
-- Vztah M:N (Jeden trénink má více cvičení, jedno cvičení může být v mnoha trénincích)
CREATE TABLE IF NOT EXISTS workout_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    sets INTEGER NOT NULL,
    reps INTEGER NOT NULL,
    weight REAL NOT NULL,
    FOREIGN KEY (workout_id) REFERENCES workouts (id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises (id) ON DELETE CASCADE
);

-- Tabulka historie váhy (PK: id, FK: user_id -> users.id)
-- Vztah 1:N (Jeden uživatel má více záznamů o váze)
CREATE TABLE IF NOT EXISTS bodyweight_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    weight REAL NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
