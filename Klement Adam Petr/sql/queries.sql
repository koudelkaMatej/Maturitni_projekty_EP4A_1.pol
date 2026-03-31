-- Vzorové SQL dotazy pro Fitness App (SELECT, JOIN, GROUP BY, FILTERING)

-- 1. Získání všech tréninků konkrétního uživatele včetně názvů cviků (Vztah 1:N a M:N přes JOIN)
SELECT u.username, w.date, e.name as exercise_name, wi.sets, wi.reps, wi.weight
FROM users u
JOIN workouts w ON u.id = w.user_id
JOIN workout_items wi ON w.id = wi.workout_id
JOIN exercises e ON wi.exercise_id = e.id
WHERE u.username = 'alex'
ORDER BY w.date DESC;

-- 2. Získání osobních rekordů (PR) pro každé cvičení u konkrétního uživatele (Filtrování a Seskupování)
SELECT e.name, MAX(wi.weight) as personal_record
FROM users u
JOIN workouts w ON u.id = w.user_id
JOIN workout_items wi ON w.id = wi.workout_id
JOIN exercises e ON wi.exercise_id = e.id
WHERE u.username = 'admin'
GROUP BY e.name
ORDER BY personal_record DESC;

-- 3. Seznam uživatelů a celkového počtu jejich tréninků (JOIN a COUNT)
SELECT u.username, COUNT(w.id) as total_workouts
FROM users u
LEFT JOIN workouts w ON u.id = w.user_id
GROUP BY u.id
ORDER BY total_workouts DESC;

-- 4. Vyhledávání cviků podle názvu (Filtrování)
SELECT * FROM exercises 
WHERE name LIKE '%press%' 
ORDER BY name ASC;

-- 5. Výpočet celkového objemu práce (volume) u všech tréninků uživatele (Seskupování)
SELECT w.date, SUM(wi.sets * wi.reps * wi.weight) as total_volume
FROM users u
JOIN workouts w ON u.id = w.user_id
JOIN workout_items wi ON w.id = wi.workout_id
WHERE u.username = 'alex'
GROUP BY w.id
ORDER BY w.date ASC;
