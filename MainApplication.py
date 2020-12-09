import tkinter as tk
from Profile import Profile
from Player import Player
from Match import Match
from datetime import datetime
import json
import os


def now():
    return datetime.today().strftime('%Y-%m-%d %H:%M:%S')


class MainApplication(tk.Frame):
    def __init__(self, mainframe):
        self.mainframe = mainframe
        tk.Frame.__init__(self, self.mainframe)
        self.mainframe.title("Asteroid Game")

        self.win_w = 1000
        self.win_h = 1000

        self.mainframe.width = self.win_w
        self.mainframe.height = self.win_h
        self.mainframe.resizable(False, False)

        self.canvas = tk.Canvas(mainframe, width=self.win_w, height=self.win_h, bg="black",
                                highlightthickness=0)  ##, highlightthickness=1, highlightbackground="red"
        self.canvas.pack()
        self.active_elements = []
        self.active_profile_name = []

        # Load existing profiles
        if os.path.exists("profiles.json"):
            self.profiles = self.load_profiles()
        else:
            self.profiles = {}

        # Load settings
        self.new_map = None
        self.settings = self.load_settings()
        self.temp_settings = self.settings.copy()

        # Creating elememts
        self.main_menu_elements()
        self.new_game_elements()
        self.pre_game_elements()
        self.load_profile_elements()
        self.end_match_elements()
        self.main_menu_screen()
        self.settings_elements()

        # Game testing
        # self.match = Match(1, self.canvas, self.mainframe)
        # self.canvas.bind("<Button 1>", self.getorigin) # TESTING ONLY

    # def getorigin(self, eventorigin): # USED FOR TESTING
    #     # self.canvas.delete("all")
    #     global x0, y0
    #     x0 = eventorigin.x
    #     y0 = eventorigin.y
    #     print(x0, y0)

    def save_settings(self):
        with open("settings.json", "w") as outfile:
            json.dump(self.settings, outfile)

    def load_settings(self):
        with open("settings.json", "r") as infile:
            return json.load(infile)

    def save_profiles(self):
        with open("profiles.json", "w") as outfile:
            json.dump(self.profiles, outfile)

    @staticmethod
    def load_profiles():
        with open("profiles.json", "r") as infile:
            return json.load(infile)

    def add_elements(self, new_elements):
        """Adds new buttons to active buttons list"""
        for element in new_elements:
            self.active_elements.append(element)

    def clear_screen(self):
        """Clears screen of buttons"""
        for element in self.active_elements:
            element.place_forget()

        if self.title_object is not None:
            self.canvas.delete(self.title_object)

    def main_menu_elements(self):
        self.title_object = None
        self.game_title = tk.PhotoImage(file="images/Asteroids_title.png")
        self.new_profile_button = tk.Button(self.mainframe, text="New Profile", bd=0, font=("Arial", 24),
                                            fg="white", bg="black", cursor="hand2", command=self.new_game_screen)
        self.load_game_button = tk.Button(self.mainframe, text="Load Profile", bd=0, font=("Arial", 24),
                                          fg="white", bg="black", cursor="hand2", command=self.load_profile_screen)
        self.high_score_button = tk.Button(self.mainframe, text="High Score", bd=0, font=("Arial", 24),
                                           fg="white", bg="black", cursor="hand2", command=self.high_score_screen)
        self.settings_button = tk.Button(self.mainframe, text="Settings", bd=0, font=("Arial", 24),
                                         fg="white", bg="black", cursor="hand2", command=self.settings_screen)
        self.exit_button = tk.Button(self.mainframe, text="Exit", bd=0, font=("Arial", 24),
                                     fg="white", bg="black", cursor="hand2", command=mainframe.destroy)

    def new_game_elements(self):
        self.enter_name_label = tk.Label(self.mainframe, text="Name: ", bd=0, font=("Arial", 24),
                                         fg="white", bg="black")
        self.create_profile_button = tk.Button(self.mainframe, text="Create Profile", bd=0, font=("Arial", 24),
                                               fg="white", bg="black", cursor="hand2", command=self.create_profile)
        self.new_game_back_button = tk.Button(self.mainframe, text="Back", bd=0, font=("Arial", 24),
                                              fg="white", bg="black", cursor="hand2", command=self.main_menu_screen)
        self.name_entry = tk.Entry(self.mainframe, text="Back", font=("Arial", 24),
                                   fg="white", bg="black", highlightthickness=1, highlightcolor="green")

    def pre_game_elements(self):
        self.name_variable = tk.StringVar()
        self.name_label = tk.Label(self.mainframe, text="Name: ", bd=0, font=("Arial", 16),
                                   fg="white", bg="black", textvariable=self.name_variable)
        self.start_new_game_button = tk.Button(self.mainframe, text="New Game", bd=0, font=("Arial", 24),
                                               fg="white", bg="black", cursor="hand2", command=self.start_game)
        self.continue_button = tk.Button(self.mainframe, text="Continue", bd=0, font=("Arial", 24),
                                         fg="white", bg="black", cursor="hand2", command=self.continue_game)
        self.main_menu_button = tk.Button(self.mainframe, text="Main Menu", bd=0, font=("Arial", 24),
                                          fg="white", bg="black", cursor="hand2", command=self.main_menu_screen)

    def set_potential_profile(self, name):
        self.potential_profile = name
        for i in range(len(self.load_profile_buttons)):
            if list(self.profiles.keys())[i] == name:
                self.load_profile_buttons[i].config(fg="green")
            else:
                self.load_profile_buttons[i].config(fg="white")

    def high_score_profile_labels(self):
        "Creates all profile labels for the load_game screen"
        self.high_score_labels = []
        high_scores_temp = []
        for i in range(len(self.profiles)):
            name = list(self.profiles.keys())[i]
            score = self.profiles[name]['score']
            high_scores_temp.append([score, name])

        high_scores_temp.sort(reverse=True)
        for i in range(len(high_scores_temp)):
            rank = i+1
            score = high_scores_temp[i][0]
            name = high_scores_temp[i][1]
            self.high_score_labels.append(
                    tk.Button(self.mainframe, text=f"{rank}.   -   {name}   -   {score}", bd=0, font=("Arial", 24),
                    fg="white", bg="black"))

    def high_score_screen(self):
        self.clear_screen()

        self.high_score_profile_labels()

        for i, profile in enumerate(self.high_score_labels):
            profile.place(relx=0.5, rely=0.3 + i * 0.08, anchor="center")
            self.add_elements([profile])

        self.new_game_back_button.place(relx=0.02, rely=0.98, anchor="sw")

        self.add_elements([self.new_game_back_button])

    def load_into_settings_labels(self):
        "Creates all profile labels for the load_game screen"
        self.change_settings_labels = []
        self.change_settings_mappings = []
        self.change_settings_buttons = []
        for i in range(len(self.settings['keymap'])):
            name = list(self.settings['keymap'].keys())[i]
            keymap = self.settings['keymap'][name]
            self.change_settings_labels.append(
                tk.Label(self.mainframe, text=name, font=("Arial", 16), fg="white", bg="black"))
            self.change_settings_mappings.append(
                tk.Label(self.mainframe, text=keymap, borderwidth=2, relief="raised", font=("Arial", 16), fg="white", bg="black"))
            self.change_settings_buttons.append(
                tk.Button(self.mainframe, text="Change", bd=2, font=("Arial", 16),
                          cursor="hand2",
                          fg="white", bg="black", command=lambda i = i: self.change_setting(i)))

    def settings_elements(self):
        self.settings_label = tk.Label(
            self.mainframe, text="Settings", bd=0, font=("Arial", 28), fg="white", bg="black")
        self.enter_keymap_notification = tk.Label(
            self.mainframe, text="Press desired key", bd=0, font=("Arial", 24), fg="green", bg="black")
        self.save_settings_button = tk.Button(self.mainframe, text="Save Settings", bd=0, font=("Arial", 24),
                                               fg="white", bg="black", cursor="hand2", command=self.pre_save_settings)

    def change_setting(self, i):
        self.potential_change_index = i
        self.potential_change_name = list(self.settings['keymap'].keys())[i]
        self.enter_keymap_notification.place(relx=0.5, rely=0.8, anchor="center")
        self.mainframe.bind("<Key>", self.assign_new_keymap)

    def pre_save_settings(self):
        self.settings = self.temp_settings.copy()
        for element in self.change_settings_mappings:
            element.config(fg="white")
        self.save_settings()

    def assign_new_keymap(self, event):
        self.temp_settings['keymap'][self.potential_change_name] = event.keysym
        self.mainframe.unbind("<Key>")
        self.change_settings_mappings[self.potential_change_index].config(
            text=self.temp_settings['keymap'][self.potential_change_name], fg="green")
        self.enter_keymap_notification.place_forget()

    def settings_screen(self):
        self.clear_screen()

        self.settings_label.place(relx=0.5, rely=0.2, anchor="center")
        self.temp_settings = self.settings.copy()

        self.load_into_settings_labels()
        for i in range(len(self.change_settings_labels)):
            setting_label = self.change_settings_labels[i]
            keymap_label = self.change_settings_mappings[i]
            change_button = self.change_settings_buttons[i]
            setting_label.place(relx=0.3, rely=0.3 + i * 0.08, anchor="n")
            keymap_label.place(relx=0.5, rely=0.3 + i * 0.08, anchor="n")
            change_button.place(relx=0.7, rely=0.3 + i * 0.08, anchor="n")
            self.add_elements([setting_label, keymap_label, change_button])

        self.save_settings_button.place(relx=0.78, rely=0.98, anchor="sw")
        self.new_game_back_button.place(relx=0.02, rely=0.98, anchor="sw")

        self.add_elements([self.settings_label, self.new_game_back_button, self.save_settings_button])

    def load_into_profile_labels(self):
        "Creates all profile labels for the load_game screen"
        self.load_profile_buttons = []
        for i in range(len(self.profiles)):
            name = list(self.profiles.keys())[i]
            last_played = self.profiles[name]['last_played']
            self.load_profile_buttons.append(
                tk.Button(self.mainframe, text=f"{name}    -    {last_played}", bd=0, font=("Arial", 24),
                          cursor="hand2",
                          fg="white", bg="black", command=lambda name=name: self.set_potential_profile(name)))

    def load_profile_elements(self):
        self.potential_profile = None
        self.load_profile_button = tk.Button(self.mainframe, text="Load Profile", bd=0, font=("Arial", 24),
                                             fg="white", bg="black", cursor="hand2", command=self.load_profile)

        self.delete_profile_button = tk.Button(self.mainframe, text="Delete Profile", bd=0, font=("Arial", 24),
                                               fg="white", bg="black", cursor="hand2", command=self.delete_profile)
        # new game button already exists
        # back button reused from new profile screen

    def main_menu_screen(self):
        self.clear_screen()
        self.title_object = self.canvas.create_image(self.win_w // 2, self.win_h*0.3, anchor="center", image=self.game_title)
        self.new_profile_button.place(relx=0.5, rely=0.45, anchor="center")
        self.load_game_button.place(relx=0.5, rely=0.55, anchor="center")
        self.high_score_button.place(relx=0.5, rely=0.65, anchor="center")
        self.settings_button.place(relx=0.5, rely=0.75, anchor="center")
        self.exit_button.place(relx=0.5, rely=0.85, anchor="center")

        self.add_elements([self.new_profile_button, self.load_game_button, self.high_score_button, self.settings_button,
                           self.exit_button])

    def new_game_screen(self):
        self.clear_screen()

        self.enter_name_label.place(relx=0.2, rely=0.4, anchor="center")
        self.name_entry.place(relx=0.6, rely=0.4, anchor="center")
        self.name_entry.delete(0, "end")
        self.create_profile_button.place(relx=0.5, rely=0.6, anchor="center")
        self.new_game_back_button.place(relx=0.02, rely=0.98, anchor="sw")

        self.add_elements(
            [self.create_profile_button, self.new_game_back_button, self.enter_name_label, self.name_entry])

    def pre_game_screen(self):
        self.clear_screen()

        if os.path.isfile(f"saves/{self.active_profile_name}_save.json"):  # Delete all profile saves
            with open(f"saves/{self.active_profile_name}_save.json") as infile:
                self.save = json.load(infile)
                self.continue_button.place(relx=0.5, rely=0.6, anchor="center")

        self.name_label.place(relx=0.02, rely=0.02, anchor="nw")
        self.start_new_game_button.place(relx=0.5, rely=0.5, anchor="center")
        self.main_menu_button.place(relx=0.02, rely=0.98, anchor="sw")

        self.add_elements([self.name_label, self.start_new_game_button, self.continue_button, self.main_menu_button])

    def load_profile_screen(self):
        self.clear_screen()

        self.load_into_profile_labels()

        for i, profile in enumerate(self.load_profile_buttons):
            profile.place(relx=0.5, rely=0.3 + i * 0.08, anchor="center")
            self.add_elements([profile])

        self.load_profile_button.place(relx=0.5, rely=0.68, anchor="center")
        self.delete_profile_button.place(relx=0.5, rely=0.76, anchor="center")
        self.new_profile_button.place(relx=0.5, rely=0.84, anchor="center")
        self.new_game_back_button.place(relx=0.02, rely=0.98, anchor="sw")

        self.add_elements([self.load_profile_button, self.new_game_back_button, self.new_game_back_button,
                           self.delete_profile_button])

    def end_match_elements(self):
        self.retry_button = tk.Button(self.mainframe, text="Retry", bd=0, font=("Arial", 24),
                                               fg="white", bg="black", cursor="hand2", command=self.end_match_retry)
        self.back_to_hangar_button = tk.Button(self.mainframe, text="Back to Hangar", bd=0, font=("Arial", 24),
                                              fg="white", bg="black", cursor="hand2", command=self.end_match_hangar)

    def end_match_retry(self):
        self.match.end = True
        self.start_game()

    def end_match_hangar(self):
        self.match.end = True
        self.pre_game_screen()

    def end_match_screen(self, points):
        self.retry_button.place(relx=0.5, rely=0.68, anchor="center")
        self.back_to_hangar_button.place(relx=0.5, rely=0.76, anchor="center")

        self.add_elements([self.retry_button, self.back_to_hangar_button])
        self.profiles[self.active_profile_name]['last_played'] = now()
        self.profiles[self.active_profile_name]['score'] = max(self.profiles[self.active_profile_name]['score'], points)
        self.save_profiles()

    def create_profile(self):
        name, last_played, progress, score = self.name_entry.get(), now(), "1", 0
        if name not in list(self.profiles.keys()):
            self.profile = Profile(name, last_played, progress, score)
            self.profiles[name] = {"last_played": last_played, "progress": progress, "score": score}
            self.save_profiles()
            self.profile = Profile(name, last_played, progress, score)
            self.name_variable.set(f"Name: {self.profile.name}")

            self.pre_game_screen()
        else:
            print("Name already exists, try a different one.")

    def load_profile(self):
        if self.potential_profile is not None:
            name = self.potential_profile
            last_played, progress, score = self.profiles[name]['last_played'], self.profiles[name]['progress'], \
                                           self.profiles[name]['score']
            self.profile = Profile(name, last_played, progress, score)
            self.name_variable.set(f"Name: {self.profile.name}")
            self.active_profile_name = name
            self.profiles[name]['last_played'] = now()

            self.pre_game_screen()

    def delete_profile(self):
        if self.potential_profile is not None:
            name = self.potential_profile
            self.potential_profile = None
            self.profiles.pop(name, None)
            if os.path.isfile(f"saves/{name}_save.json"):  # Delete all profile saves
                os.remove(f"saves/{name}_save.json")
            self.load_into_profile_labels()  # Reset labels
            self.load_profile_screen()

            self.save_profiles()

    def continue_game(self):
        level = self.save['level']
        lives = self.save['lives']
        points = self.save['points']
        if os.path.isfile(f"saves/{self.active_profile_name}_save.json"):  # Delete all profile saves
            os.remove(f"saves/{self.active_profile_name}_save.json")
        self.clear_screen()
        self.match = Match(self.canvas, self, level, lives, points)

    def start_game(self):
        if os.path.isfile(f"saves/{self.active_profile_name}_save.json"):  # Delete all profile saves
            os.remove(f"saves/{self.active_profile_name}_save.json")
        self.clear_screen()
        self.match = Match(self.canvas, self, 0)
        # self.pre_game_screen()


if __name__ == "__main__":
    mainframe = tk.Tk()
    MainApplication(mainframe)
    mainframe.mainloop()
