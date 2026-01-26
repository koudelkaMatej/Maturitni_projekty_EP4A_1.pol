from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, DictProperty, ListProperty, NumericProperty, ObjectProperty, BooleanProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.graphics.texture import Texture
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from datetime import datetime, timedelta

class GraphWidget(Widget):
    data_points = ListProperty([])  # List of (value, "label")
    line_color = ListProperty([0, 0.78, 0.32, 1])
    
    def on_data_points(self, instance, value):
        self.draw_graph()
        
    def on_size(self, *args):
        self.draw_graph()
        
    def draw_graph(self):
        self.canvas.clear()
        if not self.data_points or len(self.data_points) < 2:
            return
            
        values = [p[0] for p in self.data_points]
        min_val = min(values) * 0.9
        max_val = max(values) * 1.1
        val_range = max_val - min_val if max_val != min_val else 1
        
        # Dimensions with padding
        x_pad = 50
        y_pad = 50
        w = self.width - 2 * x_pad
        h = self.height - 2 * y_pad
        
        points = []
        step_x = w / (len(self.data_points) - 1)
        
        with self.canvas:
            # Draw Axis
            Color(0.3, 0.3, 0.3, 1)
            Line(points=[x_pad, y_pad, x_pad, self.height - y_pad], width=1.5) # Y axis
            Line(points=[x_pad, y_pad, self.width - x_pad, y_pad], width=1.5)  # X axis
            
            # Draw Line
            Color(*self.line_color)
            for i, (val, label) in enumerate(self.data_points):
                x = x_pad + i * step_x
                y = y_pad + ((val - min_val) / val_range) * h
                points.extend([x, y])
                
                # Draw point
                Color(*self.line_color)
                Ellipse(pos=(x-3, y-3), size=(6, 6))
                
                # Draw label (simplified)
                if len(self.data_points) < 10 or i % (len(self.data_points)//5) == 0:
                    # Draw text label logic would go here, simplified to lines for now
                    Color(0.5, 0.5, 0.5, 0.5)
                    Line(points=[x, y_pad, x, y_pad-5], width=1)

            Line(points=points, width=2)

class GradientBackground(Widget):
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

# Nastavení velikosti a základní barvy okna
Window.size = (1200, 700)
Window.clearcolor = (0.07, 0.07, 0.07, 1)
Window.minimum_width = 800
Window.minimum_height = 600


# ======== OBRAZOVKY ========

class MainScreen(Screen):
    username = StringProperty("")
    current_view = StringProperty("workouts")
    workouts_screen = ObjectProperty(None)
    stats_screen = ObjectProperty(None)
    
    def on_kv_post(self, *args):
        """Called after kv file is loaded"""
        # Store references to our child screens
        for widget in self.walk():
            if isinstance(widget, WorkoutsScreen):
                self.workouts_screen = widget
            elif isinstance(widget, StatsScreen):
                self.stats_screen = widget
    
    def switch_view(self, view):
        self.current_view = view
        
        if view == "stats" and self.stats_screen:
            self.stats_screen.on_enter()
    
    def logout(self):
        if self.workouts_screen:
            # Save any remaining data before logout
            self.workouts_screen.save_to_file(
                "\n".join([f"{ex} - {s}x{r}, {w}kg" for ex, s, r, w in self.workouts_screen.workout_data]),
                self.workouts_screen.ids.note.text
            )
            # Reset workout data
            self.workouts_screen.workout_data = []
            self.workouts_screen.ids.workout_list.text = ""
            self.workouts_screen.ids.note.text = ""
            
        self.manager.current = "login"

class LoginScreen(Screen):
    def login(self):
        username = self.ids.username.text
        password = self.ids.password.text

        if username == "admin" and password == "1234":
            self.manager.current = "main"
            main_screen = self.manager.get_screen("main")
            main_screen.username = username
            
            # Load saved data for the user
            workouts_screen = None
            for widget in main_screen.walk():
                if isinstance(widget, WorkoutsScreen):
                    workouts_screen = widget
                    break
            
            if workouts_screen:
                workouts_screen.load_user_data(username)
        else:
            popup = Popup(title="Chyba",
                          content=Label(text="Špatné jméno nebo heslo!"),
                          size_hint=(0.5, 0.3))
            popup.open()





class WorkoutsScreen(Screen):
    exercises = ListProperty(["Bench press", "Dřepy", "Mrtvý tah", "Biceps curl", "Kliky"])
    workout_data = ListProperty()
    personal_records = DictProperty()
    progress_data = DictProperty()  # New: Track progress over time
    selected_exercise = StringProperty("")
    show_exercises = BooleanProperty(False)

    def load_user_data(self, username):
        """Load saved data for the user from JSON file."""
        from data_manager import DataManager
        dm = DataManager()
        user_data = dm.get_user_data(username)
        
        self.personal_records.update(user_data.get("personal_records", {}))
        self.progress_data.update(user_data.get("progress_data", {}))
        
        # Update exercises list with any custom exercises
        custom_exercises = set()
        for workout in user_data.get("workouts", []):
            for ex, _, _, _ in workout["exercises"]:
                custom_exercises.add(ex)
        
        # Add any new exercises to the list
        for exercise in custom_exercises:
            if exercise not in self.exercises:
                self.exercises.append(exercise)

    def on_exercises(self, instance, value):
        self.update_exercise_list()

    def update_exercise_list(self):
        exercise_list = self.ids.get('exercise_list', None)
        if exercise_list:
            exercise_list.clear_widgets()
            for exercise in self.exercises:
                btn = Button(
                    text=exercise,
                    size_hint_y=None,
                    height=48,
                    background_color=(0.2, 0.2, 0.2, 1)
                )
                btn.bind(on_release=lambda b: self.select_exercise(b.text))
                exercise_list.add_widget(btn)

    def toggle_exercise_list(self):
        """Show or hide the right-side exercise panel."""
        # Toggle flag; kv bindings handle visibility/disabled state
        self.show_exercises = not self.show_exercises
        if self.show_exercises:
            # populate list when opening
            self.update_exercise_list()

    def select_exercise(self, exercise_name):
        self.selected_exercise = exercise_name
        self.show_exercises = False

    def add_custom_exercise(self):
        name = self.ids.new_exercise.text.strip()
        if name and name not in self.exercises:
            self.exercises.append(name)
            self.ids.new_exercise.text = ""
        else:
            popup = Popup(title="Chyba",
                          content=Label(text="Cvik už existuje nebo je prázdný."),
                          size_hint=(0.5, 0.3))
            popup.open()

    def add_exercise(self):
        sets = self.ids.sets.text
        reps = self.ids.reps.text
        weight = self.ids.weight.text

        if not (self.selected_exercise and sets and reps and weight):
            popup = Popup(title="Chyba",
                          content=Label(text="Vyplň všechny údaje!"),
                          size_hint=(0.5, 0.3))
            popup.open()
            return

        entry = f"{self.selected_exercise} - {sets}x{reps}, {weight}kg"
        self.workout_data.append((self.selected_exercise, int(sets), int(reps), int(weight)))
        self.ids.workout_list.text += f"{entry}\n"

        # aktualizace osobních rekordů
        if self.selected_exercise not in self.personal_records or int(weight) > self.personal_records[self.selected_exercise]:
            self.personal_records[self.selected_exercise] = int(weight)

        # vyčištění polí
        self.ids.sets.text = ""
        self.ids.reps.text = ""
        self.ids.weight.text = ""



    def remove_last(self):
        if self.workout_data:
            self.workout_data.pop()
            lines = self.ids.workout_list.text.strip().split("\n")
            self.ids.workout_list.text = "\n".join(lines[:-1])
        else:
            popup = Popup(title="Chyba",
                          content=Label(text="Žádné cviky k odstranění."),
                          size_hint=(0.5, 0.3))
            popup.open()

    def save_workout(self):
        if not self.workout_data:
            popup = Popup(title="Chyba",
                          content=Label(text="Nejdřív přidej alespoň jeden cvik!"),
                          size_hint=(0.5, 0.3))
            popup.open()
            return

        note = self.ids.note.text
        summary = "\n".join([f"{ex} - {s}x{r}, {w}kg" for ex, s, r, w in self.workout_data])

        # Save via DataManager
        from data_manager import DataManager
        dm = DataManager()
        username = App.get_running_app().root.get_screen("main").username
        
        updated_data = dm.save_workout(username, self.workout_data, note, summary)
        
        # Update local state
        self.personal_records.update(updated_data.get("personal_records", {}))
        self.progress_data.update(updated_data.get("progress_data", {}))

        popup = Popup(
            title="Uloženo",
            content=Label(text=f"Trénink byl úspěšně uložen!\n\n{summary}\n\nPoznámka:\n{note if note else '(žádná)'}"),
            size_hint=(0.7, 0.7),
        )
        popup.bind(on_dismiss=self.back_to_dashboard)
        popup.open()

        # reset polí
        self.workout_data = []
        self.ids.workout_list.text = ""
        self.ids.note.text = ""

    def save_to_file(self, summary, note):
        """Saves workout data via DataManager. Used by logout."""
        if not self.workout_data:
            return

        from data_manager import DataManager
        dm = DataManager()
        username = App.get_running_app().root.get_screen("main").username
        
        dm.save_workout(username, self.workout_data, note, summary)

    def back_to_dashboard(self, *_):
        """Vrátí uživatele zpět na hlavní obrazovku."""
        # Find the MainScreen instance and switch to workouts view
        main_screen = App.get_running_app().root.get_screen('main')
        main_screen.switch_view('workouts')



class StatsScreen(Screen):
    user_weight = NumericProperty(0)
    personal_records = DictProperty()
    progress_data = DictProperty()
    bodyweight_history = ListProperty()
    show_stat_exercises = BooleanProperty(False)
    
    # Stats Display
    stat_mode = StringProperty("exercise") # or "bodyweight"
    selected_stat_item = StringProperty("Vyber cvik")
    stat_exercises = ListProperty([])
    
    # Metrics
    metric_pr = StringProperty("-")
    metric_avg = StringProperty("-")
    metric_peak = StringProperty("-")
    metric_low = StringProperty("-")
    
    def on_enter(self):
        self.reload_data()

    def reload_data(self):
        main_screen = App.get_running_app().root.get_screen('main')
        username = main_screen.username
        
        from data_manager import DataManager
        dm = DataManager()
        user_data = dm.get_user_data(username)
        
        self.personal_records = user_data.get("personal_records", {})
        self.progress_data = user_data.get("progress_data", {})
        self.user_weight = user_data.get("bodyweight", 0)
        self.bodyweight_history = user_data.get("bodyweight_history", [])
        
        # Populate exercise list
        exercises = set()
        for workout in user_data.get("workouts", []):
            for ex, _, _, _ in workout.get("exercises", []):
                exercises.add(ex)
        self.stat_exercises = sorted(list(exercises))

    def on_stat_exercises(self, instance, value):
        container = self.ids.get('stat_exercise_list', None)
        if not container:
            return
        container.clear_widgets()
        for exercise in value:
            btn = Button(text=exercise, size_hint_y=None, height=44, background_color=(0.2, 0.2, 0.2, 1))
            btn.bind(on_release=lambda b: self.show_exercise_stats(b.text))
            container.add_widget(btn)

    def toggle_stat_exercise_list(self):
        self.show_stat_exercises = not self.show_stat_exercises
        if self.show_stat_exercises:
            # Ensure list is populated when opened
            self.on_stat_exercises(None, self.stat_exercises)
            self.selected_stat_item = "Vyber cvik"

    def update_weight(self):
        try:
            new_weight = float(self.ids.weight_input.text)
            
            # Save via DataManager
            from data_manager import DataManager
            dm = DataManager()
            username = App.get_running_app().root.get_screen('main').username
            
            dm.log_bodyweight(username, new_weight)
            
            self.user_weight = new_weight
            self.ids.weight_label.text = f"Aktuální váha: {self.user_weight} kg"
            self.ids.weight_input.text = ""
            
            # Reload to update history/graphs
            self.reload_data()
            if self.stat_mode == "bodyweight":
                self.show_bodyweight_stats()
                
        except ValueError:
            popup = Popup(title="Chyba", content=Label(text="Zadej číslo!"), size_hint=(0.5, 0.3))
            popup.open()

    def show_exercise_stats(self, exercise_name):
        self.stat_mode = "exercise"
        self.selected_stat_item = exercise_name
        
        # 1. Prepare Graph Data
        # Filter progress data for this exercise
        history = self.progress_data.get(exercise_name, [])
        graph_points = []
        for entry in history:
            # entry: {'date': '...', 'weight': 100, ...}
            # Simplified: just plotting weight sequence
            graph_points.append((entry['weight'], entry['date']))
            
        self.ids.graph.data_points = graph_points
        self.ids.graph.line_color = [0, 0.78, 0.32, 1] # Green
        
        # 2. Metrics
        # PR
        pr = self.personal_records.get(exercise_name, 0)
        self.metric_pr = f"{pr} kg"
        
        # Avg Last Month
        now = datetime.now()
        month_ago = now - timedelta(days=30)
        recent_weights = []
        
        for entry in history:
            try:
                d = datetime.strptime(entry['date'], "%Y-%m-%d")
                if d >= month_ago:
                    recent_weights.append(entry['weight'])
            except: pass
            
        if recent_weights:
            avg = sum(recent_weights) / len(recent_weights)
            self.metric_avg = f"{avg:.1f} kg"
        else:
            self.metric_avg = "-"
            
        # Hide BW metrics
        self.metric_peak = "-"
        self.metric_low = "-"

    def show_bodyweight_stats(self):
        self.stat_mode = "bodyweight"
        self.selected_stat_item = "Tělesná váha"
        self.show_stat_exercises = False
        
        history = self.bodyweight_history
        if not history:
            self.ids.graph.data_points = []
            return
            
        # Graph Data
        graph_points = []
        weights = []
        for entry in history:
            w = entry.get('weight', 0)
            graph_points.append((w, entry.get('date', '')))
            weights.append(w)
            
        self.ids.graph.data_points = graph_points
        self.ids.graph.line_color = [0.2, 0.6, 1, 1] # Blue
        
        # Metrics
        if weights:
            self.metric_peak = f"{max(weights)} kg"
            self.metric_low = f"{min(weights)} kg"
            
            # Month Avg
            now = datetime.now()
            month_ago = now - timedelta(days=30)
            recent = []
            for entry in history:
                try:
                    d = datetime.strptime(entry['date'], "%Y-%m-%d")
                    if d >= month_ago:
                        recent.append(entry['weight'])
                except: pass
            
            if recent:
                avg = sum(recent) / len(recent)
                self.metric_avg = f"{avg:.1f} kg"
            else:
                self.metric_avg = "-"
        
        self.metric_pr = "-" # Not relevant for BW usually (or could be target)

class FitnessApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(MainScreen(name="main"))
        return sm


if __name__ == "__main__":
    FitnessApp().run()
