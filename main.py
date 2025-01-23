import tkinter as tk
from tkinter import messagebox
import random
import math
import os
import json

class NumberWarrior:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Number Warrior")
        
        self.languages = {}
        self.load_languages()
        
        self.current_lang = tk.StringVar(value="en")
        self.create_language_menu()

        self.player_power = 100
        self.enemy_power = 50
        self.coins = 0
        self.round = 0
        self.health = 3
        self.crit_chance = 15
        self.temp_bonus = 1.0
        self.boss_defeated = False
        self.purchased_items = set()
        
        self.bosses = [
            {
                "name": "Vampire",
                "effect": self.boss_vampire,
                "message": "vampire_effect",
                "reward_multiplier": 2,
                "color": "#FF0000"
            },
            {
                "name": "Tank",
                "effect": self.boss_shield,
                "message": "shield_effect",
                "reward_multiplier": 1.5,
                "color": "#0000FF"
            },
            {
                "name": "Cursed",
                "effect": self.boss_curse,
                "message": "curse_effect",
                "reward_multiplier": 3,
                "color": "#800080"
            }
        ]
        
        self.shop_items = [
            {"name": "+30 Power", "cost": 50, "effect": lambda: self.add_power(30)},
            {"name": "x1.5 Power", "cost": 100, "effect": lambda: self.multiply_power(1.5)},
            {"name": "+10% Crit", "cost": 120, "effect": lambda: self.add_crit_chance(10)},
            {"name": "Temp Boost x2", "cost": 100, "effect": lambda: self.apply_temp_boost(2)},
            {"name": "Heal (+1 ❤)", "cost": 250, "effect": lambda: self.heal(1)},
            {"name": "❄️ Freeze Enemy", "cost": 300, "effect": self.freeze_enemy, "consumable": False},
            {"name": "⚡ Lucky Duel", "cost": 250, "effect": self.duel_challenge, "consumable": False},
            {"name": "🔮 Random Boost", "cost": 150, "effect": self.random_boost, "consumable": True},
            {"name": "👥 Power Clones", "cost": 400, "effect": self.clone_power, "consumable": True},
            {"name": "💀 Blood Sacrifice", "cost": 0, "effect": self.blood_sacrifice, "consumable": True},
            {"name": "⏳ Rewind Time", "cost": 600, "effect": self.rewind_time, "consumable": True},
            {"name": "🎲 Crit Roulette", "cost": 200, "effect": self.crit_roulette, "consumable": True},
        ]

        self.mods = []
        self.load_mods()
        self.create_widgets()
        self.next_round()

    def load_languages(self):
        lang_dir = "lang"
        if not os.path.exists(lang_dir):
            os.makedirs(lang_dir)
        
        for filename in os.listdir(lang_dir):
            if filename.endswith(".json"):
                lang_code = filename[:2]
                with open(os.path.join(lang_dir, filename), 'r', encoding='utf-8') as file:
                    self.languages[lang_code] = json.load(file)

    def create_language_menu(self):
        lang_menu = tk.OptionMenu(self.root, self.current_lang, *self.languages.keys(), command=self.update_language)
        lang_menu.config(font=('Arial', 10))
        lang_menu.pack(anchor="ne", padx=10, pady=5)

    def update_language(self, selected_lang):
        self.root.title(self.languages[selected_lang]["title"])
        self.fight_btn.config(text=self.languages[selected_lang]["attack"])
        self.shop_btn.config(text=self.languages[selected_lang]["shop"])
        self.mods_btn.config(text=self.languages[selected_lang]["mods"])
        self.update_stats()


    def load_mods(self):
        mods_dir = "mods"
        if not os.path.exists(mods_dir):
            os.makedirs(mods_dir)
        
        for filename in os.listdir(mods_dir):
            if filename.endswith(".json"):
                with open(os.path.join(mods_dir, filename), 'r', encoding='utf-8') as file:
                    mod_data = json.load(file)
                    self.mods.append(mod_data)
                    if "boss" in mod_data:
                        self.bosses.append(mod_data["boss"])
                    if "shop_item" in mod_data:
                        self.shop_items.append(mod_data["shop_item"])

    def create_widgets(self):
        self.stats_label = tk.Label(self.root, font=('Arial', 12), justify='left')
        self.stats_label.pack(pady=10)
        
        self.enemy_label = tk.Label(self.root, font=('Arial', 14, 'bold'))
        self.enemy_label.pack(pady=15)
        
        self.fight_btn = tk.Button(self.root, command=self.fight, font=('Arial', 14), bg='#FF4500', fg='white')
        self.fight_btn.pack(pady=10, ipadx=20)
        
        self.shop_btn = tk.Button(self.root, command=self.open_shop, font=('Arial', 12), bg='#32CD32')
        self.shop_btn.pack(pady=5)
        
        self.mods_btn = tk.Button(self.root, command=self.open_mods_manager, font=('Arial', 12), bg='#6495ED')
        self.mods_btn.pack(pady=5)
        
        self.update_language(self.current_lang.get())

    def open_mods_manager(self):
        mods_window = tk.Toplevel(self.root)
        mods_window.title(self.languages[self.current_lang.get()]["mods_title"])
        
        for mod in self.mods:
            frame = tk.Frame(mods_window, padx=10, pady=5)
            frame.pack(fill='x')
            
            mod_name = mod.get("name", "Unnamed Mod")
            tk.Label(frame, text=mod_name, font=('Arial', 12)).pack(side='left')
            
            btn_state = tk.NORMAL if mod.get("enabled", False) else tk.DISABLED
            btn_text = self.languages[self.current_lang.get()]["mod_disable"] if mod.get("enabled", False) else self.languages[self.current_lang.get()]["mod_enable"]
            btn = tk.Button(frame, text=btn_text, 
                          command=lambda m=mod: self.toggle_mod(m),
                          state=btn_state,
                          bg='#FFD700' if mod.get("enabled", False) else '#808080')
            btn.pack(side='right')

    def toggle_mod(self, mod):
        mod["enabled"] = not mod.get("enabled", False)
        status = self.languages[self.current_lang.get()]["mod_enable"].lower() if not mod["enabled"] else self.languages[self.current_lang.get()]["mod_disable"].lower()
        messagebox.showinfo("Success", self.languages[self.current_lang.get()]["mod_toggle"].format(name=mod.get('name', 'Unnamed Mod'), status=status))
        self.open_mods_manager()

    def update_stats(self):
        lang = self.current_lang.get()
        stats_text = self.languages[lang]["stats"].format(
            round=self.round,
            power=self.player_power,
            bonus=self.temp_bonus,
            coins=self.coins,
            health='❤' * self.health,
            crit=self.crit_chance
        )
        self.stats_label.config(text=stats_text)
    
    def next_round(self):
        self.round += 1
        self.temp_bonus = 1.0
        
        base_enemy = math.floor(
            math.pow(self.round, 1.3) * 10 + 
            5 * self.round + 
            random.randint(-10, 30)
        )
        
        if self.round % 3 == 0:
            self.current_boss = random.choice(self.bosses)
            self.enemy_power = int(base_enemy * 1.8)
            self.apply_boss_effect()
            self.enemy_label.config(
                text=self.languages[self.current_lang.get()]["boss_template"].format(
                    name=self.current_boss["name"], 
                    power=self.enemy_power
                ),
                fg=self.current_boss['color']
            )
            self.boss_defeated = False
        else:
            self.enemy_power = base_enemy
            self.enemy_label.config(
                text=self.languages[self.current_lang.get()]["enemy_template"].format(power=self.enemy_power), 
                fg='black'
            )
        
        self.update_stats()
        
    def apply_boss_effect(self):
        self.current_boss['effect']()
        messagebox.showwarning("Boss Effect!", self.languages[self.current_lang.get()][self.current_boss['message']])
        
    def boss_vampire(self):
        self.player_power = int(self.player_power * 0.7)
        
    def boss_shield(self):
        self.enemy_power = int(self.enemy_power * 1.5)
        
    def boss_curse(self):
        self.player_power = int(self.player_power * 0.9)
        
    def fight(self):
        effective_power = int(self.player_power * self.temp_bonus)
        lang = self.current_lang.get()
        
        is_critical = random.randint(1, 100) <= self.crit_chance
        if is_critical:
            effective_power *= 2
            messagebox.showinfo(self.languages[lang]["crit_hit"], self.languages[lang]["crit_message"])
            
        if effective_power > self.enemy_power:
            reward = random.randint(25, 60) + self.round * 6
            if self.round % 3 == 0 and not self.boss_defeated:
                reward *= self.current_boss['reward_multiplier']
                self.boss_defeated = True
                messagebox.showinfo("Victory!", self.languages[lang]["boss_defeated"].format(reward=reward))
            self.coins += reward
            self.next_round()
        else:
            self.health -= 1
            if self.health <= 0:
                messagebox.showerror(self.languages[lang]["game_over"], self.languages[lang]["game_over_message"])
                self.root.destroy()
            else:
                messagebox.showwarning("Defeat", self.languages[lang]["defeat_message"].format(lives=self.health))
                self.player_power = int(self.player_power * 0.9)
                self.next_round()
        self.update_stats()
        
    def open_shop(self):
        shop_window = tk.Toplevel(self.root)
        shop_window.title(self.languages[self.current_lang.get()]["shop_title"])
        
        for index, item in enumerate(self.shop_items):
            if item['name'] in self.purchased_items and item.get('consumable', False):
                continue 
            frame = tk.Frame(shop_window, padx=10, pady=5)
            frame.pack(fill='x')
            
            tk.Label(frame, text=item["name"], font=('Arial', 12)).pack(side='left')
            tk.Label(frame, text=f"🏷️ {item['cost']}", font=('Arial', 10)).pack(side='left', padx=15)
            
            btn = tk.Button(frame, text="Buy", 
                          command=lambda idx=index: self.buy_item(idx),
                          state='normal' if self.coins >= item['cost'] else 'disabled',
                          bg='#FFD700' if self.coins >= item['cost'] else '#808080')
            btn.pack(side='right')

    def buy_item(self, index):
        item = self.shop_items[index]
        lang = self.current_lang.get()
        
        if item['name'] in self.purchased_items and item.get('consumable', False):
            messagebox.showerror("Error", self.languages[lang]["buy_error"])
            return
            
        if self.coins >= item['cost']:
            self.coins -= item['cost']
            item['effect']()
            
            if item.get('consumable', False):
                self.purchased_items.add(item['name'])
                
            self.update_stats()
            messagebox.showinfo("Success", self.languages[lang]["buy_success"])
        else:
            messagebox.showerror("Error", self.languages[lang]["buy_error"])

    def add_power(self, amount):
        self.player_power += amount
        
    def multiply_power(self, multiplier):
        self.player_power = int(self.player_power * multiplier)
        
    def add_crit_chance(self, amount):
        self.crit_chance = min(100, self.crit_chance + amount)
        
    def apply_temp_boost(self, multiplier):
        self.temp_bonus = multiplier
        
    def heal(self, amount):
        self.health += amount

    def random_boost(self):
        effect = random.choice([
            lambda: self.add_power(100),
            lambda: self.multiply_power(2.0),
            lambda: self.add_crit_chance(25),
            lambda: self.heal(2),
            lambda: self.player_power // 2
        ])
        effect()
        messagebox.showinfo("🔮 Random!", "Random effect applied!")

    def freeze_enemy(self):
        self.enemy_power = int(self.enemy_power * 0.7)
        messagebox.showinfo("❄️ Freeze!", self.languages[self.current_lang.get()]["freeze_effect"])
        self.update_stats()

    def blood_sacrifice(self):
        lang = self.current_lang.get()
        if self.health > 1:
            self.health -= 1
            self.player_power += 200
            messagebox.showwarning("💀 Sacrifice!", "Traded 1 life for +200 power!")
        else:
            messagebox.showerror("Error", self.languages[lang]["sacrifice_error"])

    def rewind_time(self):
        if self.round > 1:
            self.round = max(1, self.round - 3)
            self.next_round()
            messagebox.showinfo("⏳ Rewind", self.languages[self.current_lang.get()]["rewind_message"])
            
    def crit_roulette(self):
        self.crit_chance = random.randint(5, 95)
        messagebox.showinfo("🎲 Roulette", self.languages[self.current_lang.get()]["roulette_message"].format(chance=self.crit_chance))

    def clone_power(self):
        self.player_power *= 1.5
        self.enemy_power *= 1.2
        messagebox.showwarning("👥 Clones", self.languages[self.current_lang.get()]["clone_message"])

    def duel_challenge(self):
        lang = self.current_lang.get()
        if random.random() < 0.4:
            self.player_power *= 3
            messagebox.showinfo("⚡ Duel", self.languages[lang]["duel_win"])
        else:
            self.health -= 1
            messagebox.showerror("⚡ Duel", self.languages[lang]["duel_lose"])
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = NumberWarrior()
    game.run()