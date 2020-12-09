from Player import Player
from Asteroid import Asteroid
from Enemy import Enemy
from math import sqrt
import tkinter as tk
from random import random
import json

# The game resolution is 1080 x 1080, therefore the screen resolution of 1920x1080 is recommended

class Match:
    def __init__(self, canvas, app, level=0, lives=3, points=0):
        self.level = level
        self.canvas = canvas
        self.app = app
        self.mainframe = app.mainframe

        # Lives
        self.lives = lives
        self.life_models = []

        # Scoring
        self.duration = 0
        self.points = points
        self.points_var = tk.IntVar()
        self.points_var.set(self.points)
        self.level_var = tk.StringVar()
        self.level_var.set(f"Level {self.level}")
        self.gui_elements()

        # Level Design
        self.asteroid_formation = [1]  # Starting asteroids
        self.enemy_spawn_rate = 0.00005

        # Entities
        self.player = Player(0, self.canvas, self)
        self.asteroid_id = 0
        self.active_asteroids = []
        self.enemy_id = 0
        self.enemies = []

        # Events
        self.lives_given = 1
        self.extra_life_score_trigger = 5000  # Extra life given every 5k points

        # Game states
        self.paused = False
        self.end = False
        self.perma_death = False

        # Menus
        self.boss_key_active = False
        self.esc_menu_active = False

        # Key Bindings
        self.mainframe.bind("<Escape>", self.esc_menu)  # Unchangeable

        for setting in self.app.settings['keymap']:
            self.mainframe.unbind("<" + self.app.settings['keymap'][setting] + ">")
        self.mainframe.bind("<" + self.app.settings['keymap']['Thruster'] + ">", self.player.boost)
        self.mainframe.bind("<" + self.app.settings['keymap']['Turn Left'] + ">", self.player.rotate_left)
        self.mainframe.bind("<" + self.app.settings['keymap']['Turn Right'] + ">", self.player.rotate_right)
        self.mainframe.bind("<" + self.app.settings['keymap']['Jump'] + ">", self.player.jump)
        self.mainframe.bind("<" + self.app.settings['keymap']['Shoot'] + ">", self.player.shoot)
        self.mainframe.bind("<" + self.app.settings['keymap']['Boss Key'] + ">", self.boss_key)

        # self.mainframe.bind("<Key>", self.print_key)  # Testing purposes

        # Saving
        self.potential_save = dict()
        if self.level != 0:
            self.calculate_level()

        # Game start
        self.next_level()

        self.mainframe.after(10, self.update_lives)
        self.game_loop()

    # def print_key(self, event):
    #     print(event.keycode)
    #     print(event.keysym)

    def update_lives(self, change=0):
        self.lives += change
        self.update_lives_meter()

    def update_lives_meter(self):
        for life in self.life_models:
            self.canvas.delete(life)
        self.life_models = []
        life_model = [0.0, 20.0, 6.0, 0.0, 12.0, 20.0, 11.0, 16.666666666666668, 1.0, 16.666666666666668]
        x_offset = self.app.win_w * 0.025
        y_offset = self.app.win_h * 0.1
        for l in range(self.lives):
            points = life_model.copy()
            for i in range(len(points)):
                if i % 2 == 0:
                    points[i] = x_offset + life_model[i] + 15 * l
                else:
                    points[i] = y_offset + life_model[i]
            self.life_models.append(self.canvas.create_polygon(points, outline="white", width=1))

    def gui_elements(self):
        self.points_label = tk.Label(self.mainframe, bd=0, font=("Arial", 24),
                                     fg="white", bg="black", textvariable=self.points_var)
        self.points_label.place(relx=0.02, rely=0.02, anchor="nw")

        self.level_label = tk.Label(self.mainframe, bd=0, font=("Arial", 24),
                                     fg="white", bg="black", textvariable=self.level_var)
        self.level_label.place(relx=0.44, rely=0.02, anchor="nw")

        self.boss_key_image = tk.PhotoImage(file="images/excel.png")

        self.save_n_quit_button = tk.Button(self.mainframe, text="Save & Quit", bd=0, font=("Arial", 24),
                                            fg="white", bg="black", cursor="hand2", command=self.save_n_quit)
        self.continue_button = tk.Button(self.mainframe, text="Continue", bd=0, font=("Arial", 24),
                                         fg="white", bg="black", cursor="hand2", command=self.esc_menu)
        self.quit_button = tk.Button(self.mainframe, text="Quit", bd=0, font=("Arial", 24),
                                            fg="white", bg="black", cursor="hand2", command=self.exit_match)
        self.cheat_code_entry = tk.Entry(self.mainframe, text="Back", font=("Arial", 24), width=12,
                                   fg="white", bg="black", highlightthickness=1, highlightcolor="green")
        self.cheat_code_button = tk.Button(self.mainframe, text="Enter", bd=0, font=("Arial", 24),
                                         fg="white", bg="black", cursor="hand2", command=self.enter_cheat_code)

        self.app.add_elements([self.points_label, self.level_label])

    def event_checker(self):
        if self.points // self.extra_life_score_trigger >= self.lives_given:
            self.lives_given += 1
            self.update_lives(1)

    def enter_cheat_code(self):
        cheat_code = self.cheat_code_entry.get()
        self.cheat_code_entry.delete(0, 'end')
        if cheat_code == "anotha lyf":
            self.update_lives(1)
        elif cheat_code == "clear skies":
            for asteroid in self.active_asteroids:
                self.canvas.delete(asteroid)
                self.active_asteroids[asteroid.id] = None
                self.canvas.delete(asteroid.model)
            for enemy in self.enemies:
                self.canvas.delete(enemy)
                self.enemies[enemy.id] = None
                self.canvas.delete(enemy.model)
            self.test_level_clear()
        elif cheat_code == "makin it rain":
            self.points += 5000
            self.points_var.set(self.points)
            self.event_checker()

    def boss_key(self, event=None):
        if not self.esc_menu_active:
            if self.boss_key_active:
                self.boss_key_active = False
                self.paused = False
                self.canvas.delete(self.image)
            else:
                self.image = self.canvas.create_image(self.app.win_w // 2, self.app.win_h // 2, anchor="center",
                                                      image=self.boss_key_image)
                self.boss_key_active = True
                self.paused = True

    def esc_menu(self, event=None):
        if not self.boss_key_active:
            if self.esc_menu_active:
                self.esc_menu_active = False
                self.paused = False

                self.save_n_quit_button.place_forget()
                self.quit_button.place_forget()
                self.continue_button.place_forget()

                self.cheat_code_entry.place_forget()
                self.cheat_code_button.place_forget()
            else:
                self.esc_menu_active = True
                self.paused = True

                self.save_n_quit_button.place(relx=0.5, rely=0.5, anchor="center")
                self.continue_button.place(relx=0.5, rely=0.6, anchor="center")
                self.quit_button.place(relx=0.5, rely=0.7, anchor="center")

                self.cheat_code_entry.place(relx=0.5, rely=0.9, anchor="center")
                self.cheat_code_button.place(relx=0.7, rely=0.9, anchor="center")


    # def toggle_pause(self):
    #     if self.paused:
    #         self.paused = False
    #     else:
    #         self.paused = True

    def save_n_quit(self):
        if True:    # Add criteria for saving
            name = self.app.active_profile_name
            with open(f"saves/{name}_save.json", "w") as outfile:
                json.dump(self.potential_save, outfile)
            self.exit_match()

    def center_is_clear(self):
        for asteroid in self.active_asteroids:
            if asteroid is not None:
                if self.distance(asteroid.center_x, asteroid.center_y, self.app.win_w // 2, self.app.win_h // 2) < (
                        asteroid.size + 100):
                    return False
        for enemy in self.enemies:
            if enemy is not None:
                if self.distance(enemy.center_x, enemy.center_y, self.app.win_w // 2, self.app.win_h // 2) < (
                        enemy.size + 100):
                    return False
        return True

    def add_asteroids(self, layout):
        self.asteroid_id = 0
        for size in range(len(layout)):
            for i in range(layout[size]):
                if size == 0:
                    self.active_asteroids.append(Asteroid(0, self.canvas, 1, self.asteroid_id))
                else:
                    self.active_asteroids.append(Asteroid(0, self.canvas, 2 * size, self.asteroid_id))
                self.asteroid_id += 1

    def add_enemies(self, n):
        for i in range(n):
            self.enemies.append(Enemy(0, self.canvas, 3, self.enemy_id))
            self.enemy_id += 1

    @staticmethod
    def distance(x1, y1, x2, y2):
        return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def collision_detection(self):
        for asteroid in self.active_asteroids:
            if asteroid is not None:
                for bullet in self.player.bullets:
                    if bullet is not None:  # Asteroid - Bullet
                        if self.distance(asteroid.center_x, asteroid.center_y, bullet.center_x,
                                         bullet.center_y) <= asteroid.size * 0.9:
                            bullet.remove()
                            self.asteroid_explosion(asteroid)
                for enemy in self.enemies:  # Asteroid - Enemy
                    if enemy is not None:
                        if self.distance(enemy.center_x, enemy.center_y, asteroid.center_x,
                                         asteroid.center_y) <= (asteroid.size + enemy.size) * 0.9:
                            self.enemy_explosion(enemy)
                            self.asteroid_explosion(asteroid)
                        for bullet in enemy.bullets:
                            if bullet is not None:
                                if self.distance(asteroid.center_x, asteroid.center_y, bullet.center_x,
                                                 bullet.center_y) <= asteroid.size * 0.9:
                                    bullet.remove()
                                    self.asteroid_explosion(asteroid)

                # Asteroid - Player collision
                if self.player.alive:  # If not invisible
                    for i in range(0, len(self.player.points), 2):
                        x, y = self.player.points[i], self.player.points[i + 1]
                        if self.distance(asteroid.center_x, asteroid.center_y, x,
                                         y) <= asteroid.size * 0.9:  # Player - Asteroid
                            self.asteroid_explosion(asteroid)
                            self.player.destroy()
                            self.update_lives(-1)
                            if self.lives == 0:
                                self.exit_match()
                            break
        for enemy in self.enemies:
            if enemy is not None:
                for bullet in self.player.bullets:  # Player bullet - Enemy
                    if bullet is not None:
                        if self.distance(enemy.center_x, enemy.center_y, bullet.center_x,
                                         bullet.center_y) <= enemy.size * 0.9:
                            self.enemy_explosion(enemy)
                            bullet.remove()
                if self.player.alive:
                    for i in range(0, len(self.player.points), 2):  # Player - Enemy
                        x, y = self.player.points[i], self.player.points[i + 1]
                        if self.distance(enemy.center_x, enemy.center_y, x, y) <= enemy.size * 1.2:
                            self.enemy_explosion(enemy)
                            self.player.destroy()
                            self.update_lives(-1)
                            if self.lives == 0:
                                self.exit_match()
                            break

    def asteroid_explosion(self, asteroid):
        self.points += asteroid.bounty
        self.event_checker()
        self.points_var.set(self.points)
        new_asteroids, self.asteroid_id = asteroid.explode(self.asteroid_id)
        self.active_asteroids[asteroid.id] = None
        for new_asteroid in new_asteroids:
            self.active_asteroids.append(new_asteroid)
        self.test_level_clear()

    def enemy_explosion(self, enemy):
        enemy.explode()
        self.points += enemy.bounty
        self.event_checker()
        self.points_var.set(self.points)
        self.enemies[enemy.id] = None
        self.test_level_clear()

    def test_level_clear(self):
        for asteroid in self.active_asteroids:
            if asteroid is not None:
                return False
        for enemy in self.enemies:
            if enemy is not None:
                return False
        self.next_level()

    def next_level(self):
        self.active_asteroids.clear()
        self.asteroid_id = 0
        self.enemies.clear()
        self.enemy_id = 0
        self.level += 1
        self.level_var.set(f"Level {self.level}")

        self.potential_save['lives'] = self.lives
        self.potential_save['level'] = self.level - 1  # Because lvl gets added in next lvl
        self.potential_save['points'] = self.points

        self.asteroid_formation[-1] += 1
        if self.asteroid_formation[-1] >= 4:
            self.asteroid_formation.append(0)
        self.add_asteroids(self.asteroid_formation)

    def calculate_level(self):
        current_level = 0
        while current_level < self.level - 1:
            current_level += 1
            self.asteroid_formation[-1] += 1
            if self.asteroid_formation[-1] >= 4:
                self.asteroid_formation.append(0)

    def exit_match(self):
        self.perma_death = True
        self.app.end_match_screen(self.points)

        self.quit_button.place_forget()
        self.save_n_quit_button.place_forget()
        self.continue_button.place_forget()

        self.cheat_code_entry.place_forget()
        self.cheat_code_button.place_forget()

    def spawn_enemies(self):
        if random() < self.enemy_spawn_rate:
            n = 1 + int(1.5 * random())
            self.add_enemies(n)

    def game_loop(self):
        if not self.paused:
            self.player.update()
            for enemy in self.enemies:
                if enemy is not None:
                    enemy.update()
                    for i in range(len(enemy.bullets)):
                        bullet = enemy.bullets[i]
                        if bullet is not None:
                            bullet.move()

            for asteroid in self.active_asteroids:
                if asteroid is not None:
                    asteroid.move()
            for i in range(len(self.player.bullets)):
                bullet = self.player.bullets[i]
                if bullet is not None:
                    bullet.move()

            self.collision_detection()
            self.spawn_enemies()
        if not self.end:
            self.mainframe.after(10, self.game_loop)
        else:
            self.canvas.delete("all")  # Happens only on the end
        self.mainframe.update()
