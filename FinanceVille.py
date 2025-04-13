import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import random
import datetime

# ------------------- LOGIN / REGISTER -------------------

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("FinanceVille Login")
        self.root.geometry("400x300")
        self.root.configure(bg="#ECEFF1")

        self.conn = sqlite3.connect('financeville.db')
        self.cursor = self.conn.cursor()
        self.create_users_table()
        self.create_quiz_table()

        tk.Label(root, text="Login to FinanceVille", font=("Helvetica", 16, "bold"), bg="#ECEFF1").pack(pady=20)
        tk.Label(root, text="Username:", bg="#ECEFF1").pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        tk.Label(root, text="Password:", bg="#ECEFF1").pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        tk.Button(root, text="Login", width=15, command=self.login, bg="#4CAF50", fg="white").pack(pady=10)
        tk.Button(root, text="Register", width=15, command=self.register, bg="#2196F3", fg="white").pack()

    def create_users_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                balance INTEGER,
                savings INTEGER,
                happiness INTEGER,
                tax_rate INTEGER
            )
        ''')
        self.conn.commit()

    def create_quiz_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                option1 TEXT,
                option2 TEXT,
                option3 TEXT,
                option4 TEXT,
                correct_option INTEGER
            )
        ''')
        self.conn.commit()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = self.cursor.fetchone()
        if user:
            self.root.destroy()
            root = tk.Tk()
            app = FinanceVille(root, username, is_admin=(username == "admin"))
            root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password.")

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Missing Data", "Please enter both username and password.")
            return
        try:
            self.cursor.execute("INSERT INTO users VALUES (?, ?, 1000, 0, 50, 10)", (username, password))
            self.conn.commit()
            messagebox.showinfo("Registered", "Account created successfully! You can now log in.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists.")
# ------------------- GŁÓWNA GRA -------------------

class FinanceVille:
    def __init__(self, master, username, is_admin=False):
        self.master = master
        self.master.title("FinanceVille – Economic Adventure")
        self.master.geometry("900x600")
        self.master.configure(bg="#ECEFF1")
        self.username = username
        self.is_admin = is_admin

        self.conn = sqlite3.connect('financeville.db')
        self.cursor = self.conn.cursor()

        self.load_user_data()

        self.dark_mode = False
        self.achievements = []
        self.event_log = []

        self.build_gui()
        self.update_info()

    def load_user_data(self):
        self.cursor.execute("SELECT balance, savings, happiness, tax_rate FROM users WHERE username=?", (self.username,))
        data = self.cursor.fetchone()
        if data:
            self.balance, self.savings, self.population_happiness, self.tax_rate = data
        else:
            self.balance, self.savings, self.population_happiness, self.tax_rate = 1000, 0, 50, 10

    def save_user_data(self):
        self.cursor.execute("""
            UPDATE users SET balance=?, savings=?, happiness=?, tax_rate=? WHERE username=?
        """, (self.balance, self.savings, self.population_happiness, self.tax_rate, self.username))
        self.conn.commit()
        self.log_event("Progress saved.")
    def build_gui(self):
        self.font_title = ("Helvetica", 20, "bold")
        self.font_label = ("Helvetica", 13)
        self.font_button = ("Helvetica", 11, "bold")

        self.left_frame = tk.Frame(self.master, bg="#ECEFF1", padx=20, pady=20)
        self.left_frame.pack(side="left", fill="y")

        self.right_frame = tk.Frame(self.master, bg="#FFFFFF", padx=20, pady=20, relief="sunken", bd=2)
        self.right_frame.pack(side="right", fill="both", expand=True)

        tk.Label(self.left_frame, text=f"💼 {self.username}'s FinanceVille", font=self.font_title, bg="#ECEFF1", fg="#37474F").pack(anchor="w", pady=(0, 10))

        self.label_balance = tk.Label(self.left_frame, font=self.font_label, bg="#ECEFF1")
        self.label_balance.pack(anchor="w", pady=5)

        self.label_savings = tk.Label(self.left_frame, font=self.font_label, bg="#ECEFF1")
        self.label_savings.pack(anchor="w", pady=5)

        self.label_happiness = tk.Label(self.left_frame, font=self.font_label, bg="#ECEFF1")
        self.label_happiness.pack(anchor="w", pady=5)

        self.label_tax = tk.Label(self.left_frame, font=self.font_label, bg="#ECEFF1")
        self.label_tax.pack(anchor="w", pady=5)

        actions = [
            ("📈 Invest in Stocks", self.invest_stocks),
            ("🏫 Build School ($300)", self.build_school),
            ("💳 Set Taxes", self.set_taxes),
            ("📝 Financial Quiz", self.take_quiz),
            ("📅 Daily Challenge", self.daily_challenge),
            ("🏦 Open Bank", self.open_bank),
            ("📊 View Stats", self.show_stats),
            ("🌓 Dark Mode", self.toggle_dark_mode),
            ("💾 Save Game", self.save_user_data),
            ("📤 Export Progress", self.export_to_txt),
        ]

        if self.is_admin:
            actions.append(("🧠 Edit Quiz (Admin)", self.edit_quiz))

        for text, cmd in actions:
            tk.Button(self.left_frame, text=text, font=self.font_button, bg="#455A64", fg="white",
                      width=22, pady=6, command=cmd).pack(anchor="w", pady=4)

        tk.Label(self.right_frame, text="📜 Event Log", font=("Helvetica", 14, "bold"),
                 bg="#FFFFFF", fg="#263238").pack(anchor="w")

        self.log_box = tk.Text(self.right_frame, height=25, state="disabled", bg="#FAFAFA", fg="#000000",
                               font=("Courier", 10), wrap="word")
        self.log_box.pack(fill="both", expand=True, pady=(10, 0))

    def update_info(self):
        self.label_balance.config(text=f"💵 Balance: ${self.balance}")
        self.label_savings.config(text=f"🏦 Savings: ${self.savings}")
        self.label_happiness.config(text=f"😊 Happiness: {self.population_happiness}%")
        self.label_tax.config(text=f"📊 Tax Rate: {self.tax_rate}%")

    def log_event(self, text):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_box.config(state="normal")
        self.log_box.insert("end", f"[{timestamp}] {text}\n")
        self.log_box.config(state="disabled")
        self.log_box.see("end")
    def invest_stocks(self):
        result = random.choice([-200, -100, 0, 100, 300, 500])
        self.balance += result
        msg = f"You earned ${result} from stocks!" if result > 0 else f"You lost ${-result} in stocks!"
        self.log_event(msg)
        self.update_info()

    def build_school(self):
        if self.balance >= 300:
            self.balance -= 300
            self.population_happiness += 10
            self.log_event("Built a school. Happiness +10%.")
        else:
            self.log_event("Not enough funds to build a school.")
            messagebox.showerror("Error", "You need at least $300.")
        self.update_info()

    def set_taxes(self):
        window = tk.Toplevel(self.master)
        window.title("Set Tax Rate")
        tk.Label(window, text="Set new tax rate (0–50%)").pack(pady=10)
        scale = tk.Scale(window, from_=0, to=50, orient="horizontal")
        scale.set(self.tax_rate)
        scale.pack()

        def apply():
            self.tax_rate = scale.get()
            revenue = self.tax_rate * 10
            self.balance += revenue
            self.population_happiness -= self.tax_rate // 5
            self.log_event(f"Set taxes to {self.tax_rate}%. Revenue: ${revenue}.")
            self.update_info()
            window.destroy()

        tk.Button(window, text="Apply", command=apply).pack(pady=10)

    def take_quiz(self):
        self.cursor.execute("SELECT * FROM quizzes ORDER BY RANDOM() LIMIT 1")
        data = self.cursor.fetchone()
        if not data:
            messagebox.showinfo("Quiz", "No quiz questions available.")
            return

        qid, question, *options, correct = data

        win = tk.Toplevel(self.master)
        win.title("Quiz")
        tk.Label(win, text=question, wraplength=350).pack(pady=5)
        answer_var = tk.IntVar()

        for i, opt in enumerate(options, start=1):
            tk.Radiobutton(win, text=opt, variable=answer_var, value=i).pack(anchor="w")

        def check_answer():
            if answer_var.get() == correct:
                self.balance += 150
                self.log_event("Correct quiz answer! +$150")
            else:
                self.log_event("Wrong answer in quiz.")
            self.update_info()
            win.destroy()

        tk.Button(win, text="Submit", command=check_answer).pack(pady=5)

    def daily_challenge(self):
        win = tk.Toplevel(self.master)
        win.title("Daily Challenge")
        tk.Label(win, text="What’s the best use of a surprise bonus?", wraplength=350).pack(pady=5)
        answer_var = tk.StringVar()
        options = ["Buy clothes", "Invest it", "Hide it", "Party!"]
        correct = "Invest it"

        for opt in options:
            tk.Radiobutton(win, text=opt, variable=answer_var, value=opt).pack(anchor="w")

        def check():
            if answer_var.get() == correct:
                self.balance += 200
                self.log_event("Daily challenge completed! +$200")
            else:
                self.log_event("Wrong answer in daily challenge.")
            self.update_info()
            win.destroy()

        tk.Button(win, text="Submit", command=check).pack(pady=5)

    def open_bank(self):
        win = tk.Toplevel(self.master)
        win.title("Bank")
        tk.Label(win, text="Transfer amount:").pack()
        entry = tk.Entry(win)
        entry.pack(pady=5)

        def deposit():
            try:
                amt = int(entry.get())
                if self.balance >= amt:
                    self.balance -= amt
                    self.savings += amt
                    self.log_event(f"Deposited ${amt} into savings.")
                else:
                    messagebox.showerror("Error", "Not enough balance.")
                self.update_info()
            except:
                messagebox.showerror("Invalid input", "Enter a valid number.")

        def withdraw():
            try:
                amt = int(entry.get())
                if self.savings >= amt:
                    self.savings -= amt
                    self.balance += amt
                    self.log_event(f"Withdrew ${amt} from savings.")
                else:
                    messagebox.showerror("Error", "Not enough savings.")
                self.update_info()
            except:
                messagebox.showerror("Invalid input", "Enter a valid number.")

        tk.Button(win, text="Deposit", command=deposit).pack(pady=2)
        tk.Button(win, text="Withdraw", command=withdraw).pack(pady=2)

    def show_stats(self):
        stats = f"""
Balance: ${self.balance}
Savings: ${self.savings}
Happiness: {self.population_happiness}%
Tax Rate: {self.tax_rate}%
Achievements: {', '.join(self.achievements) if self.achievements else 'None'}
        """
        messagebox.showinfo("Your Stats", stats)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg = "#263238" if self.dark_mode else "#ECEFF1"
        fg = "white" if self.dark_mode else "#000000"
        self.master.configure(bg=bg)
        self.left_frame.configure(bg=bg)
        self.right_frame.configure(bg="#37474F" if self.dark_mode else "#FFFFFF")
        for widget in self.left_frame.winfo_children():
            widget.configure(bg=bg, fg=fg)
        self.log_box.configure(bg="#263238" if self.dark_mode else "#FAFAFA", fg=fg)

    def export_to_txt(self):
        filename = f"financeville_report_{self.username}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write("📋 FinanceVille Progress Report\n")
            file.write(f"User: {self.username}\n")
            file.write(f"Balance: ${self.balance}\n")
            file.write(f"Savings: ${self.savings}\n")
            file.write(f"Happiness: {self.population_happiness}%\n")
            file.write(f"Tax Rate: {self.tax_rate}%\n")
            file.write("Achievements: " + (", ".join(self.achievements) if self.achievements else "None") + "\n")
            file.write(f"Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.log_event(f"Progress exported to {filename}")
        messagebox.showinfo("Export", f"Exported to {filename}")

    def edit_quiz(self):
        win = tk.Toplevel(self.master)
        win.title("Admin Quiz Editor")

        def add_question():
            q = simpledialog.askstring("New Question", "Enter the question:")
            if not q:
                return
            opts = []
            for i in range(1, 5):
                opt = simpledialog.askstring("Option", f"Enter option {i}:")
                opts.append(opt)
            correct = simpledialog.askinteger("Correct Answer", "Enter number of correct option (1-4):")
            if correct not in [1, 2, 3, 4]:
                messagebox.showerror("Error", "Invalid correct option number.")
                return
            self.cursor.execute("INSERT INTO quizzes (question, option1, option2, option3, option4, correct_option) VALUES (?, ?, ?, ?, ?, ?)",
                                (q, *opts, correct))
            self.conn.commit()
            self.log_event("Admin added new quiz question.")
            view_questions()

        def view_questions():
            for widget in frame.winfo_children():
                widget.destroy()
            self.cursor.execute("SELECT * FROM quizzes")
            for row in self.cursor.fetchall():
                qid, q, o1, o2, o3, o4, correct = row
                text = f"{qid}. {q} (Correct: {correct})"
                tk.Label(frame, text=text, wraplength=380).pack(anchor="w")
                tk.Button(frame, text="🗑 Delete", command=lambda i=qid: delete_question(i)).pack()

        def delete_question(qid):
            self.cursor.execute("DELETE FROM quizzes WHERE id=?", (qid,))
            self.conn.commit()
            self.log_event(f"Admin deleted question ID {qid}.")
            view_questions()

        tk.Button(win, text="➕ Add Question", command=add_question).pack(pady=5)
        frame = tk.Frame(win)
        frame.pack(fill="both", expand=True)
        view_questions()


if __name__ == "__main__":
    root = tk.Tk()
    login = LoginWindow(root)
    root.mainloop()
