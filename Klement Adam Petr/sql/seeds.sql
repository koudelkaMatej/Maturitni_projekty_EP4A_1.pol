-- Vzorová data pro Fitness App (INSERT skripty)

-- 1. Uživatelé
INSERT INTO users (username, password, email, role) VALUES ('admin', '1234', 'admin@fitness.cz', 'admin');
INSERT INTO users (username, password, email, role) VALUES ('alex', '5412', 'alex@seznam.cz', 'user');
INSERT INTO users (username, password, email, role) VALUES ('test_user', 'heslo123', 'test@example.com', 'user');

-- 2. Cvičení (Globální seznam)
INSERT INTO exercises (name) VALUES ('Bench press');
INSERT INTO exercises (name) VALUES ('Dřepy');
INSERT INTO exercises (name) VALUES ('Mrtvý tah');
INSERT INTO exercises (name) VALUES ('Pull-ups');
INSERT INTO exercises (name) VALUES ('Kliky');

-- 3. Tréninky (Vztah 1:N s uživatelem)
INSERT INTO workouts (user_id, note) VALUES (1, 'První trénink po pauze');
INSERT INTO workouts (user_id, note) VALUES (2, 'Nohy a hýždě');
INSERT INTO workouts (user_id, note) VALUES (3, 'Lehký kardio trénink');

-- 4. Položky tréninku (Vztah M:N přes propojovací tabulku)
-- Trénink 1 (Admin)
INSERT INTO workout_items (workout_id, exercise_id, sets, reps, weight) VALUES (1, 1, 3, 10, 60); -- Bench press
INSERT INTO workout_items (workout_id, exercise_id, sets, reps, weight) VALUES (1, 2, 3, 12, 80); -- Dřepy

-- Trénink 2 (Alex)
INSERT INTO workout_items (workout_id, exercise_id, sets, reps, weight) VALUES (2, 2, 4, 8, 100); -- Dřepy
INSERT INTO workout_items (workout_id, exercise_id, sets, reps, weight) VALUES (2, 3, 3, 5, 120); -- Mrtvý tah

-- 5. Historie váhy
INSERT INTO bodyweight_history (user_id, weight) VALUES (1, 85.5);
INSERT INTO bodyweight_history (user_id, weight) VALUES (2, 72.0);
INSERT INTO bodyweight_history (user_id, weight) VALUES (2, 71.8);
