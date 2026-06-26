import tkinter as tk
from tkinter import messagebox, simpledialog
import smtplib
from email.mime.text import MIMEText
import requests
import time
import os

# 🔐 CONFIG (change later for safety)
sender_email = "jash.coldcoffee@gmail.com"
app_password = "oyrjwwsdbjxcqykh"

CONTACT_FILE = "contact.txt"

danger_keywords = ["help", "scared", "danger", "save me", "please help"]


class SafetyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Suraksha 🛡️")
        self.root.geometry("520x520")
        self.root.config(bg="#0f0f0f")

        # ⏱️ typing tracking
        self.last_key_time = time.time()
        self.typing_gaps = []
        self.backspace_count = 0
        self.total_keys = 0

        # Load contact
        self.receiver_email = self.load_contact()
        if not self.receiver_email:
            self.set_contact()

        # 🔴 HEADER
        tk.Label(
            root,
            text="Suraksha 🛡️",
            font=("Segoe UI", 20, "bold"),
            bg="#b30000",
            fg="white",
            pady=10
        ).pack(fill="x")

        # 📝 TEXT BOX
        self.text_box = tk.Text(
            root,
            height=10,
            font=("Segoe UI", 12),
            bg="#1a1a1a",
            fg="white",
            insertbackground="white",
            bd=0,
            padx=10,
            pady=10,
            wrap="word"
        )
        self.text_box.pack(padx=20, pady=20, fill="both")
        self.text_box.bind("<Key>", self.track_typing)

        # 🔘 BUTTONS
        frame = tk.Frame(root, bg="#0f0f0f")
        frame.pack()

        tk.Button(
            frame, text="Analyze",
            bg="#b30000", fg="white",
            command=self.analyze_text
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            frame, text="Change Contact",
            bg="#333333", fg="white",
            command=self.set_contact
        ).grid(row=0, column=1, padx=10)

        # 🔴 Hidden SOS button
        tk.Button(
            root, text="●",
            bg="#0f0f0f", fg="red",
            relief="flat",
            command=self.trigger_sos
        ).place(x=490, y=10)

        # 📊 STATUS
        self.status = tk.Label(
            root, text="Status: Ready",
            fg="#00ff99", bg="#0f0f0f"
        )
        self.status.pack(pady=5)

        self.score_label = tk.Label(
            root, text="Danger Score: 0",
            fg="white", bg="#0f0f0f"
        )
        self.score_label.pack()

        # ⌨️ hidden shortcut
        self.root.bind("<Control-s>", lambda e: self.trigger_sos())

    # 📞 CONTACT
    def load_contact(self):
        if os.path.exists(CONTACT_FILE):
            with open(CONTACT_FILE, "r") as f:
                return f.read().strip()
        return ""

    def set_contact(self):
        email = simpledialog.askstring("Emergency Contact", "Enter emergency email:")
        if email:
            with open(CONTACT_FILE, "w") as f:
                f.write(email)
            self.receiver_email = email
            messagebox.showinfo("Saved", "Contact saved!")

    # ⏱️ TRACK TYPING
    def track_typing(self, event):
        now = time.time()
        gap = now - self.last_key_time
        self.typing_gaps.append(gap)
        self.last_key_time = now

        self.total_keys += 1
        if event.keysym == "BackSpace":
            self.backspace_count += 1

    # 📍 LOCATION (ROBUST)
    def get_location(self):
        try:
            res = requests.get("https://ipapi.co/json/", timeout=5)
            data = res.json()

            lat = data.get("latitude")
            lon = data.get("longitude")
            city = data.get("city")
            region = data.get("region")
            country = data.get("country_name")

            if lat and lon:
                return f"""
Approx Location: {city}, {region}, {country}

Map:
https://www.google.com/maps?q={lat},{lon}
"""
        except:
            pass

        try:
            res = requests.get("http://ip-api.com/json/", timeout=5)
            data = res.json()

            lat = data.get("lat")
            lon = data.get("lon")
            city = data.get("city")
            region = data.get("regionName")
            country = data.get("country")

            if lat and lon:
                return f"""
Approx Location: {city}, {region}, {country}

Map:
https://www.google.com/maps?q={lat},{lon}
"""
        except:
            pass

        return "Approx Location: Unable to fetch, but alert sent"

    # 🧠 ANALYSIS
    def analyze_text(self):
        text = self.text_box.get("1.0", tk.END).lower()
        score = 0

        for word in danger_keywords:
            if word in text:
                score += 5

        if self.typing_gaps:
            avg_gap = sum(self.typing_gaps) / len(self.typing_gaps)
            if avg_gap > 1.5:
                score += 3
            if max(self.typing_gaps) > 3:
                score += 4

        if self.total_keys > 0:
            ratio = self.backspace_count / self.total_keys
            if ratio > 0.3:
                score += 4

        if self.typing_gaps and len(self.typing_gaps) > 5:
            if max(self.typing_gaps) > 2:
                score += 2

        self.score_label.config(text=f"Danger Score: {score}")

        if score >= 7:
            self.status.config(text="⚠ Danger detected", fg="red")
            self.trigger_sos()
        else:
            self.status.config(text="Normal", fg="#00ff99")

    # 📧 EMAIL
    def send_email(self, message, location):
        msg = MIMEText(f"""
🚨 EMERGENCY ALERT 🚨

Message:
{message}

{location}
""")

        msg["Subject"] = "SOS ALERT"
        msg["From"] = sender_email
        msg["To"] = self.receiver_email

        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(sender_email, app_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print("Email Error:", e)
            return False

    # 🚨 SOS
    def trigger_sos(self):
        message = self.text_box.get("1.0", tk.END).strip()
        if not message:
            message = "Emergency triggered"

        self.status.config(text="Getting location...", fg="orange")
        self.root.update()

        location = self.get_location()

        self.status.config(text="Sending alert...", fg="#ff4d4d")
        self.root.update()

        success = self.send_email(message, location)

        if success:
            self.status.config(text="Alert sent", fg="#00ff99")
            messagebox.showinfo("Success", "🚨 Alert sent successfully!")
        else:
            self.status.config(text="Error", fg="red")
            messagebox.showerror("Error", "Failed to send alert!")


# ▶ RUN
root = tk.Tk()
app = SafetyApp(root)
root.mainloop()