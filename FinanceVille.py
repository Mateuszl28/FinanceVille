import tkinter as tk
from tkinter import messagebox
import sqlite3
import random

class FinanceVille:
    def __init__(self, master):
        self.master = master
        self.master.title("💰 FinanceVille: Economic Adventure")
        self.master.geometry("500x600")

        # Game state
        self.balance = 1000
        self.population_happiness = 50
        self.tax_rate = 10
        self.dark_mode = False
        self.achievements = []

        # Database
        self.conn = sqlite3.connect('financeville.db')
        self.cursor = self.conn.cursor()
        self.create_table()
        self.load_last_game()

        self.create_widgets()
        self.update_labels()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS game_data (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            balance INTEGER,
                            happiness INTEGER,
                            taxes INTEGER
                            )''')
        self.conn.commit()

    def save_game(self):
        self.cursor.execute("INSERT INTO game_data (balance, happiness, taxes) VALUES (?, ?, ?)",
                            (self.balance, self.population_happiness, self.tax_rate))
        self.conn.commit()
        messagebox.showinfo("Game Saved", "Your game has been saved!")

    def load_last_game(self):
        self.cursor.execute("SELECT balance, happiness, taxes FROM game_data ORDER BY id DESC LIMIT 1")
        data = self.cursor.fetchone()
        if data:
            self.balance, self.population_happiness, self.tax_rate = data
            messagebox.showinfo("Game Loaded", "Previous game loaded successfully!")

    def create_widgets(self):
        self.master.configure(bg="#f5f5f5")
        tk.Label(self.master, text="🏦 FinanceVille", font=("Arial", 20, "bold"), bg="#f5f5f5").pack(pady=10)

        self.balance_label = tk.Label(self.master, text="", font=("Arial", 14), bg="#f5f5f5")
        self.balance_label.pack(pady=5)

        self.happiness_label = tk.Label(self.master, text="", font=("Arial", 14), bg="#f5f5f5")
        self.happiness_label.pack(pady=5)

        self.tax_label = tk.Label(self.master, text="", font=("Arial", 14), bg="#f5f5f5")
        self.tax_label.pack(pady=5)

        btn_frame = tk.Frame(self.master, bg="#f5f5f5")
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="📈 Invest in Stocks", width=20, command=self.invest_stocks, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="🏫 Build School ($300)", width=20, command=self.build_school, bg="#2196F3", fg="white").grid(row=1, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="💳 Set Taxes", width=20, command=self.set_taxes, bg="#FFC107", fg="black").grid(row=2, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="📝 Financial Quiz", width=20, command=self.take_quiz, bg="#9C27B0", fg="white").grid(row=3, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="📅 Daily Challenge", width=20, command=self.daily_challenge, bg="#00bcd4", fg="white").grid(row=4, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="📊 View Stats", width=20, command=self.show_stats, bg="#607d8b", fg="white").grid(row=5, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="🌓 Toggle Dark Mode", width=20, command=self.toggle_dark_mode, bg="#555", fg="white").grid(row=6, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="💾 Save Game", width=20, command=self.save_game, bg="#FF5722", fg="white").grid(row=7, column=0, padx=5, pady=5)

    def update_labels(self):
        self.balance_label.config(text=f"💵 Balance: ${self.balance}")
        self.happiness_label.config(text=f"😊 Happiness: {self.population_happiness}%")
        self.tax_label.config(text=f"📊 Tax Rate: {self.tax_rate}%")

    def check_achievements(self):
        new_achievements = []

        if self.balance >= 2000 and "Wealthy!" not in self.achievements:
            new_achievements.append("Wealthy!")

        if self.population_happiness >= 90 and "Loved by the People" not in self.achievements:
            new_achievements.append("Loved by the People")

        if self.tax_rate == 0 and "Tax-Free Economy" not in self.achievements:
            new_achievements.append("Tax-Free Economy")

        for achievement in new_achievements:
            self.achievements.append(achievement)
            messagebox.showinfo("🎉 Achievement Unlocked!", f"You unlocked: {achievement}")

    def invest_stocks(self):
        result = random.choice([-200, -100, 0, 100, 200, 300, 500])
        self.balance += result
        if result >= 0:
            messagebox.showinfo("Investment Result", f"You earned ${result}!")
        else:
            messagebox.showwarning("Investment Result", f"You lost ${-result}.")
        self.update_labels()
        self.check_achievements()

    def build_school(self):
        if self.balance >= 300:
            self.balance -= 300
            self.population_happiness += 10
            messagebox.showinfo("Build School", "School built! Happiness +10%.")
        else:
            messagebox.showerror("Not enough money", "You need at least $300.")
        self.update_labels()
        self.check_achievements()

    def set_taxes(self):
        tax_window = tk.Toplevel(self.master)
        tax_window.title("Set Tax Rate")
        tax_window.geometry("300x150")
        tax_window.configure(bg="#f5f5f5")

        tk.Label(tax_window, text="Choose tax rate (0–50%)", bg="#f5f5f5").pack(pady=10)
        tax_scale = tk.Scale(tax_window, from_=0, to=50, orient="horizontal")
        tax_scale.set(self.tax_rate)
        tax_scale.pack()

        def apply():
            self.tax_rate = tax_scale.get()
            revenue = self.tax_rate * 10
            happiness_change = -self.tax_rate // 5
            self.balance += revenue
            self.population_happiness += happiness_change
            messagebox.showinfo("Taxes Applied", f"Revenue: ${revenue}, Happiness: {happiness_change}%")
            tax_window.destroy()
            self.update_labels()
            self.check_achievements()

        tk.Button(tax_window, text="Apply", command=apply, bg="#4CAF50", fg="white").pack(pady=10)

    def take_quiz(self):
        quiz_window = tk.Toplevel(self.master)
        quiz_window.title("Financial Quiz")
        quiz_window.geometry("400x250")
        quiz_window.configure(bg="#f5f5f5")

        question = "What does 'inflation' mean?"
        options = [
            ("A general increase in prices", True),
            ("A drop in wages", False),
            ("More taxes", False),
            ("Lower banking interest", False)
        ]

        tk.Label(quiz_window, text=question, wraplength=380, bg="#f5f5f5").pack(pady=10)
        answer_var = tk.StringVar()

        for text, _ in options:
            tk.Radiobutton(quiz_window, text=text, variable=answer_var, value=text, bg="#f5f5f5").pack(anchor='w')

        def submit():
            selected = answer_var.get()
            correct = next(opt[0] for opt in options if opt[1])
            if selected == correct:
                self.balance += 150
                messagebox.showinfo("Correct!", "You earned $150.")
            else:
                messagebox.showinfo("Incorrect", f"The correct answer was: {correct}")
            quiz_window.destroy()
            self.update_labels()
            self.check_achievements()

        tk.Button(quiz_window, text="Submit", command=submit, bg="#4CAF50", fg="white").pack(pady=10)

    def daily_challenge(self):
        challenges = [
            ("You saved $100. What should you do?", ["Spend", "Invest", "Burn it", "Hide it"], "Invest"),
            ("You got a high-interest loan. What's most important?", ["Amount", "Rate", "Deadline", "Bank name"], "Rate")
        ]
        question, options, correct = random.choice(challenges)

        win = tk.Toplevel(self.master)
        win.title("Daily Challenge")
        win.geometry("400x250")
        win.configure(bg="#e0f7fa")

        tk.Label(win, text=question, wraplength=380, font=("Arial", 12), bg="#e0f7fa").pack(pady=10)

        answer_var = tk.StringVar()
        for opt in options:
            tk.Radiobutton(win, text=opt, variable=answer_var, value=opt, bg="#e0f7fa").pack(anchor='w')

        def submit():
            if answer_var.get() == correct:
                self.balance += 200
                messagebox.showinfo("Correct!", "You earned $200!")
            else:
                messagebox.showinfo("Incorrect", f"Correct answer: {correct}")
            win.destroy()
            self.update_labels()
            self.check_achievements()

        tk.Button(win, text="Submit", command=submit, bg="#009688", fg="white").pack(pady=10)

    def show_stats(self):
        stats = f"""
        💵 Balance: ${self.balance}
        😊 Happiness: {self.population_happiness}%
        📊 Tax Rate: {self.tax_rate}%
        🏅 Achievements: {', '.join(self.achievements) if self.achievements else 'None'}
        """
        messagebox.showinfo("Your Stats", stats)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg_color = "#2c2c2c" if self.dark_mode else "#f5f5f5"
        fg_color = "white" if self.dark_mode else "black"
        self.master.configure(bg=bg_color)

        for widget in self.master.winfo_children():
            try:
                widget.configure(bg=bg_color, fg=fg_color)
                for child in widget.winfo_children():
                    child.configure(bg=bg_color, fg=fg_color)
            except:
                pass

    def close_app(self):
        self.conn.close()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceVille(root)
    root.protocol("WM_DELETE_WINDOW", app.close_app)
    root.mainloop()
