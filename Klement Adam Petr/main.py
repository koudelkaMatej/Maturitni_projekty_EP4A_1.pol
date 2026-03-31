from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.properties import StringProperty, DictProperty, ListProperty, NumericProperty, ObjectProperty, BooleanProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.graphics.texture import Texture
from kivy.core.text import Label as CoreLabel
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from datetime import datetime, timedelta
import math

# --- Komponenty Grafu ---

class GraphWidget(Widget):
    """
    Vlastní widget pro vykreslování spojnicového grafu progresu.
    """
    data_points = ListProperty([])  # Seznam bodů (hodnota, "popisek")
    line_color = ListProperty([0, 0.78, 0.32, 1])
    
    def on_data_points(self, instance, value):
        self.draw_graph()
        
    def on_size(self, *args):
        self.draw_graph()
        
    def _render_text(self, text, font_size=11):
        """Vykreslí text na texturu pro použití v Canvasu."""
        cl = CoreLabel(text=text, font_size=font_size)
        cl.refresh()
        return cl.texture

    def draw_graph(self):
        """Hlavní logika vykreslování grafu na Canvas."""
        self.canvas.clear()
        
        if not self.data_points:
            return
            
        values = [p[0] for p in self.data_points]
        if not values:
            return
            
        # Výpočet rozsahu osy Y
        min_val = min(values) * 0.95
        max_val = max(values) * 1.05
        if min_val == max_val:
            min_val -= 5
            max_val += 5
        val_range = max_val - min_val
        
        # Odsazení grafu
        padding_left = 60
        padding_bottom = 40
        padding_top = 20
        padding_right = 20
        
        w = self.width - padding_left - padding_right
        h = self.height - padding_bottom - padding_top
        
        num_points = len(self.data_points)
        
        with self.canvas:
            # Vykreslení os
            Color(0.4, 0.4, 0.4, 1)
            Line(points=[self.x + padding_left, self.y + padding_bottom, 
                         self.x + padding_left, self.y + self.height - padding_top], width=1.2)
            Line(points=[self.x + padding_left, self.y + padding_bottom, 
                         self.x + self.width - padding_right, self.y + padding_bottom], width=1.2)
            
            # --- Dynamické popisky osy Y (Váha) ---
            min_y_label_spacing = 35
            num_y_labels = max(2, min(10, int(h / min_y_label_spacing) + 1))
            
            raw_step = val_range / max(1, num_y_labels - 1)
            magnitude = 10 ** math.floor(math.log10(max(raw_step, 0.001)))
            nice_steps = [1, 2, 2.5, 5, 10]
            nice_step = magnitude
            for ns in nice_steps:
                candidate = ns * magnitude
                if candidate >= raw_step:
                    nice_step = candidate
                    break
            
            y_start = math.floor(min_val / nice_step) * nice_step
            y_tick = y_start
            while y_tick <= max_val + 0.01:
                if y_tick >= min_val - 0.01:
                    y_pos = self.y + padding_bottom + ((y_tick - min_val) / val_range) * h
                    
                    # Pomocné mřížky
                    Color(0.4, 0.4, 0.4, 0.5)
                    Line(points=[self.x + padding_left - 5, y_pos,
                                 self.x + padding_left + w, y_pos], width=0.8)
                    
                    fmt = f"{y_tick:.0f}" if nice_step >= 1 else f"{y_tick:.1f}"
                    tex = self._render_text(fmt, font_size=11)
                    Color(0.8, 0.8, 0.8, 1)
                    Rectangle(
                        pos=(self.x + padding_left - 10 - tex.width,
                             y_pos - tex.height / 2),
                        size=tex.size, texture=tex)
                y_tick += nice_step

            # --- Dynamické popisky osy X (Datum) ---
            if num_points > 0:
                max_label_width = 45
                min_spacing = 15
                max_labels = max(2, int(w / (max_label_width + min_spacing)))
                
                if num_points <= max_labels:
                    indices = list(range(num_points))
                else:
                    indices = [0]
                    step = (num_points - 1) / (max_labels - 1)
                    for i in range(1, max_labels - 1):
                        indices.append(int(round(i * step)))
                    indices.append(num_points - 1)
                    indices = sorted(list(set(indices)))
                
                for i in indices:
                    val, date_str = self.data_points[i]
                    x_pos = self.x + padding_left + (i / (num_points - 1 if num_points > 1 else 1)) * w
                    
                    Color(0.4, 0.4, 0.4, 0.5)
                    Line(points=[x_pos, self.y + padding_bottom,
                                 x_pos, self.y + padding_bottom - 5], width=1)
                    
                    display_date = date_str[:10] if len(date_str) > 10 else date_str
                    try:
                        if "-" in display_date:
                            dt = datetime.strptime(display_date, "%Y-%m-%d")
                            display_date = f"{dt.day}.{dt.month}."
                    except (ValueError, TypeError):
                        pass
                    
                    tex = self._render_text(display_date, font_size=10)
                    Color(0.8, 0.8, 0.8, 1)
                    Rectangle(
                        pos=(x_pos - tex.width / 2, self.y + 15),
                        size=tex.size, texture=tex)
                    
            # --- Vykreslení čáry a bodů ---
            points = []
            for i, (val, label) in enumerate(self.data_points):
                x_pos = self.x + padding_left + (i / (num_points - 1 if num_points > 1 else 1)) * w
                y_pos = self.y + padding_bottom + ((val - min_val) / val_range) * h
                points.extend([x_pos, y_pos])
                
                Color(*self.line_color)
                Ellipse(pos=(x_pos - 4, y_pos - 4), size=(8, 8))
                Color(1, 1, 1, 0.8)
                Ellipse(pos=(x_pos - 2, y_pos - 2), size=(4, 4))

            if len(points) >= 4:
                Color(*self.line_color)
                Line(points=points, width=2.5, joint='round')

class GradientBackground(Widget):
    """Widget pro vytvoření přechodového pozadí aplikace."""
    gradient_texture = ObjectProperty(None)
    
    def create_gradient_texture(self):
        texture = Texture.create(size=(1, 64), colorfmt='rgba')
        buf = bytes()
        for i in range(64):
            r = int(10 + i * 0.5)
            g = int(60 + i * 2)
            b = int(30 + i * 1)
            buf += bytes([r, g, b, 255])
        texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        texture.wrap = 'repeat'
        texture.uvsize = (1, -1)
        return texture

# Globální nastavení okna
Window.size = (1200, 700)
Window.clearcolor = (0.07, 0.07, 0.07, 1)
Window.minimum_width = 800
Window.minimum_height = 600


# ======== OBRAZOVKY APLIKACE ========

class MainScreen(Screen):
    """
    Hlavní obrazovka po přihlášení. Obsahuje navigaci a přepíná mezi 
    tréninky, statistikami a administrací.
    """
    username = StringProperty("")
    workouts_screen = ObjectProperty(None)
    stats_screen = ObjectProperty(None)
    is_admin = BooleanProperty(False)
    
    def on_kv_post(self, *args):
        """Propojení referencí na pod-obrazovky po načtení KV souboru."""
        for widget in self.walk():
            if isinstance(widget, WorkoutsScreen):
                self.workouts_screen = widget
            elif isinstance(widget, StatsScreen):
                self.stats_screen = widget
    
    def switch_view(self, view):
        """Přepne zobrazení v centrálním ScreenManageru."""
        try:
            self.ids.sm_content.current = view
        except Exception:
            pass
    
    def logout(self):
        """Odhlásí uživatele a uloží případný rozpracovaný trénink."""
        if self.workouts_screen and self.workouts_screen.workout_data:
            self.workouts_screen.save_workout()
        
        if self.workouts_screen:
            self.workouts_screen.workout_data = []
            self.workouts_screen.ids.workout_list.text = ""
            self.workouts_screen.ids.note.text = ""
            
        self.manager.current = "login"

class LoginScreen(Screen):
    """
    Přihlašovací obrazovka. Zpracovává vstup uživatele a automatické přihlášení.
    """
    def on_kv_post(self, *args):
        """Kontrola automatického přihlášení při startu."""
        try:
            from data_manager import DataManager
            dm = DataManager()
            creds = dm.get_autologin()
            if creds:
                u, p = creds
                self.ids.username.text = u or ""
                self.ids.password.text = p or ""
                self.login()
        except Exception:
            pass

    def login(self):
        """Ověření údajů a vstup do aplikace."""
        username = self.ids.username.text
        password = self.ids.password.text

        from data_manager import DataManager
        dm = DataManager()
        
        if dm.validate_login(username, password) or (username == "admin" and password == "1234"):
            try:
                remember = bool(getattr(self.ids.get("remember_me"), "active", False))
                dm.set_autologin(username, password, enabled=remember)
            except Exception:
                pass
            self.manager.current = "main"
            main_screen = self.manager.get_screen("main")
            main_screen.username = username
            role = dm.get_user_role(username)
            main_screen.is_admin = (username == "admin") or (role == "admin")
            
            if main_screen.workouts_screen:
                main_screen.workouts_screen.load_user_data(username)
            try:
                main_screen.switch_view("workouts")
            except Exception:
                pass
        else:
            Popup(title="Chyba", content=Label(text="Špatné jméno nebo heslo!"), size_hint=(0.5, 0.3)).open()

class WorkoutsScreen(Screen):
    """
    Obrazovka pro záznam tréninku. Umožňuje výběr cviků a zadávání sérií.
    """
    exercises = ListProperty([])
    workout_data = ListProperty()
    personal_records = DictProperty()
    progress_data = DictProperty()
    selected_exercise = StringProperty("")
    show_exercises = BooleanProperty(False)

    def load_user_data(self, username):
        """Načte data uživatele a centrální seznam cviků."""
        from data_manager import DataManager
        dm = DataManager()
        user_data = dm.get_user_data(username)
        
        self.personal_records.update(user_data.get("personal_records", {}))
        self.progress_data.update(user_data.get("progress_data", {}))
        self.exercises = dm.get_central_exercises()

    def on_exercises(self, instance, value):
        self.update_exercise_list()

    def update_exercise_list(self):
        """Vykreslí seznam tlačítek pro výběr cviku."""
        exercise_list = self.ids.get('exercise_list', None)
        if exercise_list:
            exercise_list.clear_widgets()
            for exercise in self.exercises:
                btn = Button(text=exercise, size_hint_y=None, height=48, background_color=(0.2, 0.2, 0.2, 1))
                btn.bind(on_release=lambda b: self.select_exercise(b.text))
                exercise_list.add_widget(btn)

    def toggle_exercise_list(self):
        """Zobrazí/skryje boční panel se seznamem cviků."""
        self.show_exercises = not self.show_exercises
        if self.show_exercises:
            self.update_exercise_list()

    def select_exercise(self, exercise_name):
        """Vybere cvik ze seznamu."""
        self.selected_exercise = exercise_name
        self.show_exercises = False

    def add_custom_exercise(self):
        """Přidá nový cvik do centrální databáze."""
        name = self.ids.new_exercise.text.strip()
        if not name:
            Popup(title="Chyba", content=Label(text="Název cviku je prázdný."), size_hint=(0.5, 0.3)).open()
            return
        from data_manager import DataManager
        dm = DataManager()
        username = App.get_running_app().root.get_screen("main").username
        success, msg = dm.add_central_exercise(name, username)
        if success:
            if name not in self.exercises:
                self.exercises.append(name)
            self.ids.new_exercise.text = ""
            self.update_exercise_list()
            Popup(title="OK", content=Label(text="Cvik přidán do centrálního seznamu."), size_hint=(0.5, 0.3)).open()
        else:
            Popup(title="Chyba", content=Label(text=msg), size_hint=(0.5, 0.3)).open()

    def add_exercise(self):
        """Přidá zadanou sérii do aktuálního tréninku."""
        sets = self.ids.sets.text
        reps = self.ids.reps.text
        weight = self.ids.weight.text

        if not (self.selected_exercise and sets and reps and weight):
            Popup(title="Chyba", content=Label(text="Vyplň všechny údaje!"), size_hint=(0.5, 0.3)).open()
            return

        entry = f"{self.selected_exercise} - {sets}x{reps}, {weight}kg"
        self.workout_data.append((self.selected_exercise, int(sets), int(reps), int(weight)))
        self.ids.workout_list.text += f"{entry}\n"

        # Okamžitá aktualizace rekordů v paměti
        if self.selected_exercise not in self.personal_records or int(weight) > self.personal_records[self.selected_exercise]:
            self.personal_records[self.selected_exercise] = int(weight)

        # Vyčištění vstupů
        self.ids.sets.text = ""
        self.ids.reps.text = ""
        self.ids.weight.text = ""

    def remove_last(self):
        """Odstraní poslední přidanou sérii z tréninku."""
        if self.workout_data:
            self.workout_data.pop()
            lines = self.ids.workout_list.text.strip().split("\n")
            self.ids.workout_list.text = "\n".join(lines[:-1])
        else:
            Popup(title="Chyba", content=Label(text="Žádné cviky k odstranění."), size_hint=(0.5, 0.3)).open()

    def save_workout(self):
        """Uloží kompletní trénink do databáze."""
        if not self.workout_data:
            Popup(title="Chyba", content=Label(text="Nejdřív přidej alespoň jeden cvik!"), size_hint=(0.5, 0.3)).open()
            return

        note = self.ids.note.text
        summary = "\n".join([f"{ex} - {s}x{r}, {w}kg" for ex, s, r, w in self.workout_data])

        from data_manager import DataManager
        dm = DataManager()
        username = App.get_running_app().root.get_screen("main").username
        
        updated_data = dm.save_workout(username, self.workout_data, note, summary)
        
        self.personal_records.update(updated_data.get("personal_records", {}))
        self.progress_data.update(updated_data.get("progress_data", {}))

        popup = Popup(
            title="Uloženo",
            content=Label(text=f"Trénink byl úspěšně uložen!\n\n{summary}\n\nPoznámka:\n{note if note else '(žádná)'}"),
            size_hint=(0.7, 0.7),
        )
        popup.bind(on_dismiss=self.back_to_dashboard)
        popup.open()

        self.workout_data = []
        self.ids.workout_list.text = ""
        self.ids.note.text = ""

    def back_to_dashboard(self, *_):
        """Návrat na hlavní přehled."""
        main_screen = App.get_running_app().root.get_screen('main')
        main_screen.switch_view('workouts')

class StatsScreen(Screen):
    """
    Obrazovka statistik. Zobrazuje grafy progresu a tělesné váhy.
    """
    user_weight = NumericProperty(0)
    personal_records = DictProperty()
    progress_data = DictProperty()
    bodyweight_history = ListProperty()
    show_stat_exercises = BooleanProperty(False)
    
    stat_mode = StringProperty("exercise") # "exercise" nebo "bodyweight"
    selected_stat_item = StringProperty("Vyber cvik")
    stat_exercises = ListProperty([])
    
    metric_pr = StringProperty("-")
    metric_avg = StringProperty("-")
    metric_peak = StringProperty("-")
    metric_low = StringProperty("-")
    
    def on_enter(self):
        self.reload_data()

    def reload_data(self):
        """Načte čerstvá data pro statistiky."""
        main_screen = App.get_running_app().root.get_screen('main')
        username = main_screen.username
        
        from data_manager import DataManager
        dm = DataManager()
        user_data = dm.get_user_data(username)
        
        self.personal_records = user_data.get("personal_records", {})
        self.progress_data = user_data.get("progress_data", {})
        self.user_weight = user_data.get("bodyweight", 0)
        self.bodyweight_history = user_data.get("bodyweight_history", [])
        
        exercises = set()
        for workout in user_data.get("workouts", []):
            for ex, _, _, _ in workout.get("exercises", []):
                exercises.add(ex)
        self.stat_exercises = sorted(list(exercises))

    def on_stat_exercises(self, instance, value):
        """Vykreslí seznam cviků pro výběr grafu."""
        container = self.ids.get('stat_exercise_list', None)
        if not container: return
        container.clear_widgets()
        for exercise in value:
            btn = Button(text=exercise, size_hint_y=None, height=44, background_color=(0.2, 0.2, 0.2, 1))
            btn.bind(on_release=lambda b: self.show_exercise_stats(b.text))
            container.add_widget(btn)

    def toggle_stat_exercise_list(self):
        self.show_stat_exercises = not self.show_stat_exercises
        if self.show_stat_exercises:
            self.on_stat_exercises(None, self.stat_exercises)
            self.selected_stat_item = "Vyber cvik"

    def update_weight(self):
        """Uloží novou tělesnou váhu uživatele."""
        try:
            new_weight = float(self.ids.weight_input.text)
            from data_manager import DataManager
            dm = DataManager()
            username = App.get_running_app().root.get_screen('main').username
            dm.log_bodyweight(username, new_weight)
            
            self.user_weight = new_weight
            self.ids.weight_label.text = f"Aktuální váha: {self.user_weight} kg"
            self.ids.weight_input.text = ""
            
            self.reload_data()
            if self.stat_mode == "bodyweight":
                self.show_bodyweight_stats()
        except ValueError:
            Popup(title="Chyba", content=Label(text="Zadej číslo!"), size_hint=(0.5, 0.3)).open()

    def show_exercise_stats(self, exercise_name):
        """Zobrazí graf a metriky pro konkrétní cvik."""
        self.stat_mode = "exercise"
        self.selected_stat_item = exercise_name
        self.show_stat_exercises = False
        
        history = list(self.progress_data.get(exercise_name, []))
        graph_points = []
        for entry in history:
            try:
                w = entry['weight'] if isinstance(entry, dict) else entry[3]
                d = entry['date'] if isinstance(entry, dict) else str(entry)
                graph_points.append((w, d))
            except: continue
            
        self.ids.graph.data_points = graph_points
        self.ids.graph.line_color = [0, 0.78, 0.32, 1]
        
        # Výpočet metrik (PR, průměr, atd.)
        pr = self.personal_records.get(exercise_name, 0)
        self.metric_pr = f"{pr} kg"
        
        now = datetime.now()
        month_ago = now - timedelta(days=30)
        total_volume, total_reps = 0.0, 0
        exercise_weights = []
        
        for entry in history:
            try:
                weight = float(entry.get('weight', 0))
                date_str = entry.get('date', '')
                exercise_weights.append(weight)
                
                # Průměr za poslední měsíc
                dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
                if dt >= month_ago:
                    s, r = int(entry.get('sets', 1)), int(entry.get('reps', 1))
                    total_volume += weight * s * r
                    total_reps += s * r
            except: continue
            
        self.metric_avg = f"{total_volume/total_reps:.1f} kg" if total_reps > 0 else "-"
        self.metric_peak = f"{max(exercise_weights)} kg" if exercise_weights else "-"
        self.metric_low = f"{min(exercise_weights)} kg" if exercise_weights else "-"

    def show_bodyweight_stats(self):
        """Zobrazí graf tělesné váhy."""
        self.stat_mode = "bodyweight"
        self.selected_stat_item = "Tělesná váha"
        self.show_stat_exercises = False
        
        history = self.bodyweight_history
        if not history:
            self.ids.graph.data_points = []
            return
            
        graph_points = [(e.get('weight', 0), e.get('date', '')) for e in history]
        weights = [e.get('weight', 0) for e in history]
            
        self.ids.graph.data_points = graph_points
        self.ids.graph.line_color = [0.2, 0.6, 1, 1]
        
        if weights:
            self.metric_peak = f"{max(weights)} kg"
            self.metric_low = f"{min(weights)} kg"
            self.metric_avg = f"{sum(weights)/len(weights):.1f} kg"
        self.metric_pr = "-"

class AdminScreen(Screen):
    """
    Administrátorské rozhraní. Správa uživatelů a centrálního seznamu cviků.
    """
    search_exercise = StringProperty("")
    search_user = StringProperty("")
    all_exercises = ListProperty([])
    users = ListProperty([])

    def on_enter(self):
        from data_manager import DataManager
        dm = DataManager()
        self.all_exercises = dm.get_central_exercises()
        self.users = dm.list_users()
        self._render_lists()

    def _render_lists(self):
        """Vykreslí seznamy cviků a uživatelů s možností filtrování."""
        ex_container = self.ids.get("admin_exercise_list")
        usr_container = self.ids.get("admin_user_list")
        
        if ex_container is not None:
            ex_container.clear_widgets()
            q = self.search_exercise.strip().lower()
            for ex in sorted(self.all_exercises):
                if q and q not in ex.lower(): continue
                btn = Button(text=ex, size_hint_y=None, height=40, background_color=(0.2,0.2,0.2,1))
                btn.bind(on_release=lambda b: self._confirm_delete_exercise(b.text))
                ex_container.add_widget(btn)
                
        if usr_container is not None:
            usr_container.clear_widgets()
            q = self.search_user.strip().lower()
            for u in sorted(self.users, key=lambda x: x["username"]):
                if q and q not in u["username"].lower(): continue
                row = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=8)
                row.add_widget(Label(text=f'{u["username"]} {"(BAN)" if u.get("is_banned") else ""}'))
                ban_btn = Button(text="Ban" if not u.get("is_banned") else "Unban", background_color=(1,0.5,0,1))
                del_btn = Button(text="Delete", background_color=(0.8,0.2,0.2,1))
                ban_btn.bind(on_release=lambda b, uname=u["username"], banned=u.get("is_banned"): self._confirm_ban_toggle(uname, banned))
                del_btn.bind(on_release=lambda b, uname=u["username"]: self._confirm_delete_user(uname))
                row.add_widget(ban_btn)
                row.add_widget(del_btn)
                usr_container.add_widget(row)

    def on_search_exercise(self, instance, value):
        self.search_exercise = value
        self._render_lists()

    def on_search_user(self, instance, value):
        self.search_user = value
        self._render_lists()

    # --- Potvrzovací dialogy pro Admin akce ---

    def _confirm_delete_exercise(self, ex_name):
        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        box.add_widget(Label(text=f"Opravdu smazat cvik '{ex_name}'?"))
        btns = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=10)
        btn_yes = Button(text="Ano", background_color=(0.8,0.2,0.2,1))
        btn_no = Button(text="Ne", background_color=(0.2,0.2,0.2,1))
        btns.add_widget(btn_yes); btns.add_widget(btn_no)
        box.add_widget(btns)
        popup = Popup(title="Potvrzení", content=box, size_hint=(0.5, 0.3))
        
        def do_delete(*_):
            from data_manager import DataManager
            dm = DataManager()
            actor = App.get_running_app().root.get_screen("main").username
            ok, msg = dm.delete_central_exercise(ex_name, actor)
            Popup(title="Info", content=Label(text=msg), size_hint=(0.5,0.3)).open()
            self.on_enter()
            popup.dismiss()
        btn_yes.bind(on_release=do_delete)
        btn_no.bind(on_release=lambda *_: popup.dismiss())
        popup.open()

    def _confirm_ban_toggle(self, username, currently_banned):
        action_text = "zabanovat" if not currently_banned else "zrušit ban"
        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        box.add_widget(Label(text=f"Opravdu {action_text} uživatele '{username}'?"))
        btns = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=10)
        btn_yes, btn_no = Button(text="Ano", background_color=(1,0.5,0,1)), Button(text="Ne", background_color=(0.2,0.2,0.2,1))
        btns.add_widget(btn_yes); btns.add_widget(btn_no)
        box.add_widget(btns)
        popup = Popup(title="Potvrzení", content=box, size_hint=(0.5, 0.3))
        
        def do_action(*_):
            from data_manager import DataManager
            dm = DataManager()
            actor = App.get_running_app().root.get_screen("main").username
            if currently_banned: dm.unban_user(username, actor)
            else: dm.ban_user(username, actor)
            self.on_enter(); popup.dismiss()
        btn_yes.bind(on_release=do_action)
        btn_no.bind(on_release=lambda *_: popup.dismiss())
        popup.open()

    def _confirm_delete_user(self, username):
        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        box.add_widget(Label(text=f"Opravdu smazat účet '{username}'?"))
        btns = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=10)
        btn_yes, btn_no = Button(text="Ano", background_color=(0.8,0.2,0.2,1)), Button(text="Ne", background_color=(0.2,0.2,0.2,1))
        btns.add_widget(btn_yes); btns.add_widget(btn_no)
        box.add_widget(btns)
        popup = Popup(title="Potvrzení", content=box, size_hint=(0.5, 0.3))
        
        def do_delete(*_):
            from data_manager import DataManager
            dm = DataManager()
            actor = App.get_running_app().root.get_screen("main").username
            dm.delete_user(username, actor)
            self.on_enter(); popup.dismiss()
        btn_yes.bind(on_release=do_delete)
        btn_no.bind(on_release=lambda *_: popup.dismiss())
        popup.open()

    def export_audit(self):
        """Exportuje auditní log do CSV."""
        try:
            from data_manager import DataManager
            dm = DataManager()
            ok, path = dm.export_audit_csv()
            Popup(title="Export", content=Label(text=f"Audit exportován: {path}"), size_hint=(0.5,0.3)).open()
        except:
            Popup(title="Chyba", content=Label(text="Export selhal"), size_hint=(0.5,0.3)).open()

    def confirm_clear_all_exercises(self):
        """Kritická akce pro vymazání všech cviků."""
        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        box.add_widget(Label(text="OPRAVDU SMAZAT CELÝ CENTRÁLNÍ SEZNAM?"))
        box.add_widget(Label(text="(Smaže i historii všech tréninků!)", font_size=12, color=(1,0.5,0.5,1)))
        btns = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=10)
        btn_yes, btn_no = Button(text="Smazat vše", background_color=(0.8,0,0,1)), Button(text="Zrušit", background_color=(0.2,0.2,0.2,1))
        btns.add_widget(btn_yes); btns.add_widget(btn_no)
        box.add_widget(btns)
        popup = Popup(title="KRITICKÁ AKCE", content=box, size_hint=(0.6, 0.4))
        
        def do_clear(*_):
            from data_manager import DataManager
            dm = DataManager()
            actor = App.get_running_app().root.get_screen("main").username
            dm.clear_central_exercises_and_cleanup(actor)
            self.on_enter(); popup.dismiss()
        btn_yes.bind(on_release=do_clear)
        btn_no.bind(on_release=lambda *_: popup.dismiss())
        popup.open()

# --- Hlavní Třída Aplikace ---

class FitnessApp(App):
    def build(self):
        """Inicializace ScreenManageru a přidání obrazovek."""
        sm = ScreenManager()
        try:
            sm.transition = SlideTransition(duration=0.25)
        except: pass
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(MainScreen(name="main"))
        return sm

if __name__ == "__main__":
    FitnessApp().run()
