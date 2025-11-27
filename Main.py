import tkinter as tk
import customtkinter as ctk
import json
import os
import re
import datetime
from openai import OpenAI
from dotenv import load_dotenv

# ---------- Backend ----------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ai_response(message: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are PedramBot, a helpful assistant."},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"خطا در پاسخ: {e}"

# ---------- Persistence ----------
HISTORY_FILE = "chat_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def clear_history_file():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

# ---------- Helpers ----------
def is_rtl(text: str) -> bool:
    return re.search(r'[\u0600-\u06FF]', text) is not None

def now_time():
    return datetime.datetime.now().strftime("%H:%M")

def sanitize(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text).strip()

def render_markdown(parent, text, base_font, code_font, wrap=780, rtl=False, text_color=None):
    blocks = split_markdown_blocks(text)
    for kind, content in blocks:
        if kind == "code":
            code_frame = ctk.CTkFrame(parent, fg_color=("#222222", "#222222"), corner_radius=6)
            code_frame.pack(fill="x", padx=6, pady=2)
            code_label = ctk.CTkLabel(
                code_frame,
                text=content,
                font=code_font,
                text_color="#d4d4d4",
                justify="left",
                wraplength=wrap
            )
            code_label.pack(padx=6, pady=4, anchor="w")
        else:
            formatted = re.sub(r"\*\*(.+?)\*\*", r"\1", content)
            formatted = re.sub(r"\*(.+?)\*", r"\1", formatted)
            label = ctk.CTkLabel(
                parent,
                text=("\u200F" + formatted) if rtl else formatted,
                font=base_font,
                text_color=text_color,
                justify="right" if rtl else "left",
                wraplength=wrap
            )
            label.pack(fill="x", padx=6, pady=1, anchor="w")

def split_markdown_blocks(text: str):
    lines = text.splitlines()
    blocks = []
    in_code = False
    buf = []
    for line in lines:
        if line.strip().startswith("```"):
            if not in_code:
                if buf:
                    blocks.append(("text", "\n".join(buf).strip()))
                    buf = []
                in_code = True
            else:
                blocks.append(("code", "\n".join(buf)))
                buf = []
                in_code = False
        else:
            buf.append(line)
    if buf:
        blocks.append(("code" if in_code else "text", "\n".join(buf).strip()))
    return blocks

# ============================================================
# ======================= LOGIN SCREEN =======================
# ============================================================

class LoginWindow(ctk.CTk):
    PIN = "123123"  # PIN ثابت (6 رقمی)

    def __init__(self):
        super().__init__()

        # ---------- Set Window Icon ----------
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PedramBot.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(default=icon_path)
            except Exception as e:
                print("⚠ مشکل در بارگذاری آیکون LoginWindow:", e)
        else:
            print("⚠ فایل آیکون یافت نشد (LoginWindow):", icon_path)

        # ---------- UI ----------
        self.title("ورود")
        self.geometry("360x260")
        ctk.set_appearance_mode("dark")

        title = ctk.CTkLabel(self, text="ورود با PIN",
                             font=ctk.CTkFont(family="B Nazanin", size=20, weight="bold"))
        title.pack(pady=20)

        self.pin_entry = ctk.CTkEntry(
            self,
            placeholder_text="PIN شش رقمی",
            show="●",
            width=220,
            font=ctk.CTkFont(family="B Nazanin", size=18)
        )
        self.pin_entry.pack(pady=10)

        self.error_label = ctk.CTkLabel(
            self, text="", text_color="red",
            font=ctk.CTkFont(family="B Nazanin", size=14)
        )
        self.error_label.pack()

        login_btn = ctk.CTkButton(
            self,
            text="ورود",
            width=140,
            command=self.check_pin,
            font=ctk.CTkFont(family="B Nazanin", size=16, weight="bold")
        )
        login_btn.pack(pady=20)

        self.pin_entry.bind("<Return>", lambda e: self.check_pin())

    def check_pin(self):
        pin = self.pin_entry.get().strip()

        if not pin.isdigit():
            self.error_label.configure(text="❌ فقط عدد وارد کنید")
            return

        if len(pin) != 6:
            self.error_label.configure(text="❌ PIN باید ۶ رقمی باشد")
            return

        if pin == self.PIN:
            self.destroy()
            self.open_main()
        else:
            self.error_label.configure(text="❌ PIN اشتباه است")

    def open_main(self):
        app = PedramBotUI()
        app.mainloop()

# ============================================================
# ======================= MAIN UI ============================
# ============================================================

class PedramBotUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PedramBot.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(default=icon_path)
            except Exception as e:
                print("⚠ مشکل در بارگذاری آیکون PedramBotUI:", e)
        else:
            print("⚠ فایل آیکون یافت نشد:", icon_path)

        self.title("گفتگوی هوشمند")
        self.geometry("980x640")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Fonts
        self.font_msg = ctk.CTkFont(family="B Nazanin", size=15)
        self.font_meta = ctk.CTkFont(family="B Nazanin", size=11)
        self.font_code = ctk.CTkFont(family="Consolas", size=13)
        self.font_btn = ctk.CTkFont(family="B Nazanin", size=12, weight="bold")
        self.font_title = ctk.CTkFont(family="B Nazanin", size=14, weight="bold")

        # App bar
        app_bar = ctk.CTkFrame(self, corner_radius=0)
        app_bar.pack(fill="x")
        theme_btn = ctk.CTkButton(app_bar, text="تغییر تم", font=self.font_btn, width=90, command=self.toggle_theme)
        theme_btn.pack(side="right", padx=10, pady=8)
        settings_btn = ctk.CTkButton(app_bar, text="⚙ تنظیمات", font=self.font_btn, width=90,
                                     command=lambda: [self.animate_button(settings_btn), self.open_settings()])
        settings_btn.pack(side="right", padx=6, pady=8)

        # Conversation area
        self.stream_frame = ctk.CTkFrame(self)
        self.stream_frame.pack(fill="both", expand=True, padx=0, pady=(0, 0))
        self.stream = ctk.CTkScrollableFrame(self.stream_frame, corner_radius=0, fg_color="#1e1e1e")
        self.stream.pack(fill="both", expand=True, padx=8, pady=8)

        # Input bar
        input_bar = ctk.CTkFrame(self, corner_radius=12, fg_color="#26292e")
        input_bar.pack(fill="x", padx=16, pady=6)

        self.user_input = tk.Text(
            input_bar,
            height=3,
            font=("B Nazanin", 15),
            wrap="word",
            bg="#26292e",
            fg="#eaeaea",
            insertbackground="white",
            bd=0,
            padx=6,
            pady=4
        )
        self.user_input.pack(side="left", fill="both", expand=True, pady=4)

        self.placeholder = tk.Label(
            self.user_input, text="پیام خود را بنویسید...", fg="gray80",
            bg="#26292e", font=("B Nazanin", 15)
        )
        self.placeholder.place(relx=0.5, rely=0.5, anchor="center")

        def hide_placeholder(event=None):
            if self.user_input.get("1.0", "end-1c").strip() != "":
                self.placeholder.place_forget()

        def show_placeholder(event=None):
            if self.user_input.get("1.0", "end-1c").strip() == "":
                self.placeholder.place(relx=0.5, rely=0.5, anchor="center")

        self.user_input.bind("<FocusIn>", hide_placeholder)
        self.user_input.bind("<FocusOut>", show_placeholder)
        self.user_input.bind("<KeyRelease>", show_placeholder)
        self.user_input.bind("<Shift-Return>", self._newline)
        self.user_input.bind("<Return>", self._enter_send)

        self.send_btn = ctk.CTkButton(
            input_bar,
            text="➤",
            width=60,
            font=ctk.CTkFont(family="B Nazanin", size=18, weight="bold"),
            command=lambda: [self.animate_button(self.send_btn), self.send_message()]
        )
        self.send_btn.pack(side="right", padx=6)

        # Typing Indicator
        self.typing_holder = ctk.CTkFrame(self.stream, fg_color="transparent")
        self.typing_label = ctk.CTkLabel(self.typing_holder, text="", font=self.font_meta, text_color="lightgray")

        # State
        self.history = load_history()
        self.typing_animation_running = False

        for item in self._normalize_history(self.history):
            self._add_panel(item[0], item[1], item[2], animate=False)

        self.after(200, lambda: self.user_input.focus())

    # ---------- Utilities ----------
    def _normalize_history(self, hist):
        normalized = []
        for item in hist:
            if len(item) == 3:
                normalized.append(item)
            elif len(item) == 2:
                normalized.append((item[0], item[1], now_time()))
        return normalized

    def animate_button(self, btn):
        original = btn.cget("fg_color")
        btn.configure(fg_color=("gray", "gray"))
        self.after(120, lambda: btn.configure(fg_color=original))

    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        ctk.set_appearance_mode("light" if current == "Dark" else "dark")

    def _newline(self, event):
        self.user_input.insert("insert", "\n")
        return "break"

    def _enter_send(self, event):
        text = self.user_input.get("1.0", "end").strip()
        if text:
            self.send_btn.invoke()
            return "break"

    # ---------- Chat Panels ----------
    def _add_panel(self, sender: str, message: str, ts: str, animate: bool = True):
        rtl = is_rtl(message)
        content = sanitize(message)
        bg = ("#202225", "#202225") if sender == "شما" else ("#26292e", "#26292e")

        panel = ctk.CTkFrame(self.stream, corner_radius=6, fg_color=bg)
        panel.pack(fill="x", padx=6, pady=2)
        panel.update_idletasks()

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.pack(fill="x", padx=4, pady=(2, 0))
        sender_label = ctk.CTkLabel(header, text=("شما" if sender == "شما" else "ربات"), font=self.font_title)
        sender_label.pack(side="left")
        time_label = ctk.CTkLabel(header, text=ts, font=self.font_meta, text_color="#a0a0a0")
        time_label.pack(side="right")

        render_markdown(panel, content, self.font_msg, self.font_code, wrap=700, rtl=rtl, text_color="#eaeaea")
        self.stream._parent_canvas.yview_moveto(1.0)

    # ---------- Typing ----------
    def _show_typing(self):
        self.typing_holder.pack(fill="x", padx=16, pady=(0, 8))
        self.typing_label.pack(anchor="center")
        self.start_typing_animation()

    def _hide_typing(self):
        self.stop_typing_animation()
        try:
            self.typing_label.pack_forget()
            self.typing_holder.pack_forget()
        except Exception:
            pass

    def start_typing_animation(self):
        self.typing_animation_running = True
        self._animate_typing(step=0)

    def stop_typing_animation(self):
        self.typing_animation_running = False
        self.typing_label.configure(text="")

    def _animate_typing(self, step):
        if not self.typing_animation_running:
            return
        dots = "●" * (step % 3 + 1)
        self.typing_label.configure(text=f"\u200Fدر حال پاسخ‌گویی {dots}")
        self.after(500, lambda: self._animate_typing(step + 1))

    # ---------- Send ----------
    def send_message(self):
        user_msg = self.user_input.get("1.0", "end").strip()
        if not user_msg:
            return

        ts = now_time()
        self._add_panel("شما", user_msg, ts)
        self.history.append(("شما", user_msg, ts))
        save_history(self.history)

        self.user_input.delete("1.0", "end")
        self.placeholder.place(relx=0.5, rely=0.5, anchor="center")

        self._show_typing()
        self.update_idletasks()

        bot_text = ai_response(user_msg)
        bot_ts = now_time()

        self._hide_typing()
        self._add_panel("ربات", bot_text, bot_ts)
        self.history.append(("ربات", bot_text, bot_ts))
        save_history(self.history)

    # ---------- Settings ----------
    def open_settings(self):
        win = ctk.CTkToplevel(self)

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PedramBot.ico")
        if os.path.exists(icon_path):
            try:
                win.iconbitmap(default=icon_path)  # <-- icon برای تنظیمات
            except Exception as e:
                print("⚠ مشکل در بارگذاری آیکون تنظیمات:", e)

        win.title("تنظیمات")
        win.geometry("380x330")

        title = ctk.CTkLabel(win, text="تنظیمات", font=self.font_title)
        title.pack(pady=10)

        theme_label = ctk.CTkLabel(win, text="تم برنامه", font=self.font_msg)
        theme_label.pack(pady=(8, 4))

        row = ctk.CTkFrame(win)
        row.pack(pady=6)

        light_btn = ctk.CTkButton(row, text="روشن", width=90, font=self.font_btn, command=lambda: ctk.set_appearance_mode("light"))
        dark_btn = ctk.CTkButton(row, text="تیره", width=90, font=self.font_btn, command=lambda: ctk.set_appearance_mode("dark"))
        light_btn.pack(side="left", padx=6)
        dark_btn.pack(side="left", padx=6)

        size_label = ctk.CTkLabel(win, text="اندازه فونت پاسخ‌ها", font=self.font_msg)
        size_label.pack(pady=(14, 4))

        def apply_font_size(v):
            v = int(float(v))
            self.font_msg.configure(size=v)
            self.font_code.configure(size=max(11, v - 2))
            self.font_meta.configure(size=max(10, v - 4))

        slider = ctk.CTkSlider(win, from_=13, to=19, command=apply_font_size)
        slider.set(15)
        slider.pack(padx=18, pady=6, fill="x")

        clear_btn = ctk.CTkButton(win, text="🗑 پاک کردن تاریخچه", width=160, font=self.font_btn,
                                  command=self._confirm_clear_history)
        clear_btn.pack(pady=16)

    def _confirm_clear_history(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("تأیید حذف")
        dialog.geometry("320x180")

        msg = ctk.CTkLabel(dialog, text="آیا از پاک کردن تاریخچه مطمئن هستید؟", font=self.font_msg)
        msg.pack(pady=16)

        row = ctk.CTkFrame(dialog)
        row.pack(pady=10)

        yes_btn = ctk.CTkButton(row, text="بله", font=self.font_btn, width=90,
                                command=lambda: self._do_clear(dialog))
        no_btn = ctk.CTkButton(row, text="خیر", font=self.font_btn, width=90, command=dialog.destroy)
        yes_btn.pack(side="left", padx=8)
        no_btn.pack(side="left", padx=8)

    def _do_clear(self, dialog):
        dialog.destroy()
        clear_history_file()
        self.history = []
        for child in self.stream.winfo_children():
            child.destroy()
        self._add_panel("سیستم", "تاریخچه گفتگو پاک شد ✅", now_time())

# ============================================================
# ======================= RUN ==============================
# ============================================================

if __name__ == "__main__":
    login = LoginWindow()
    login.mainloop()
