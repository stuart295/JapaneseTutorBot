import tkinter as tk
from tkinter import ttk, TOP, NW
import re
import threading

from tutor import Tutor


class WordBubble(tk.Toplevel):
    def __init__(self, master, x, y, text):
        super().__init__(master)
        self.geometry(f"+{x}+{y}")
        self.overrideredirect(1)

        ttk.Label(self, text=text, background="white", relief="solid", borderwidth=1).pack(padx=5, pady=5)


class JapanesePracticeApp(tk.Tk):
    def __init__(self):
        super().__init__()

        with open("openai_key", 'r') as f:
            self.tutor = Tutor(f.read().strip())

        self.title("Japanese Practice App")
        self.geometry("1280x720")

        self.create_widgets()

        # Start the lesson
        threading.Thread(target=self.begin_lesson).start()

    def begin_lesson(self):
        self.set_input_enabled(False)
        opening_response = self.tutor.start_lesson()
        self.show_tutor_response(opening_response)
        self.set_input_enabled(True)

    def create_widgets(self):
        self.chat_frame = tk.Frame(self)
        self.chat_frame.pack(expand=True, fill="both", padx=10, pady=0)

        self.chat_log = tk.Text(self.chat_frame, wrap=tk.WORD, font=("Helvetica", 14), state="disabled")
        self.chat_log.pack(side="left", expand=True, fill="both")
        self.chat_log.tag_configure("bold", font=("Helvetica", 14, "bold"))

        self.scrollbar = ttk.Scrollbar(self.chat_frame, command=self.chat_log.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.chat_log["yscrollcommand"] = self.scrollbar.set

        self.input_frame = tk.Frame(self)
        self.input_frame.pack(expand=True, fill="x", padx=10, pady=(8, 8), side=TOP, anchor=NW)

        self.chat_input = ttk.Entry(self.input_frame, font=("Helvetica", 18))
        self.chat_input.pack(side="top", expand=True, fill="x", padx=(0, 10))
        self.chat_input.bind('<Return>', lambda event: threading.Thread(target=self.send_message).start())

        self.send_button = ttk.Button(self.input_frame, text="Send", command=lambda: threading.Thread(target=self.send_message).start(), style='TButton', width=10)
        self.send_button.pack(side="bottom", anchor="e", ipadx=10, ipady=5, pady=(8, 16), padx=10)

    def set_input_enabled(self, enabled: bool):
        if enabled:
            self.chat_input.config(state='normal')
            self.send_button.config(state='normal')
        else:
            self.chat_input.config(state='disabled')
            self.send_button.config(state='disabled')

    def send_message(self, event=None):
        message = self.chat_input.get()
        self.chat_input.delete(0, tk.END)

        # Disable the input and button
        self.set_input_enabled(False)

        # Display user input in log
        self.show_student_response(message)

        # Get and show tutor response
        response = self.tutor.speak(message)
        self.show_tutor_response(response)

        # Re-enable the input and button
        self.set_input_enabled(True)

    def show_tutor_response(self, response: list):
        self.chat_log.configure(state="normal")
        self.chat_log.insert(tk.END, "Tutor\n", "bold")

        for index, item in enumerate(response):
            character, info = item
            tag_name = f"tag_ai_{index}"
            self.chat_log.insert(tk.END, character, tag_name)
            self.chat_log.tag_bind(tag_name, "<Button-1>", self.show_info_bubble)
            self.chat_log.tag_config(tag_name, font=("Helvetica", 14))

        self.chat_log.insert(tk.END, "\n\n")
        self.chat_log.configure(state="disabled")
        self.current_response = response

    def show_student_response(self, message: str):
        self.chat_log.configure(state="normal")
        self.chat_log.insert(tk.END, "You\n", "bold")
        self.chat_log.insert(tk.END, f"{message}\n\n", "tag_you")
        # self.chat_input.delete(0, tk.END)
        self.chat_log.configure(state="disabled")

    def show_info_bubble(self, event):
        clicked_tag = self.chat_log.tag_names(tk.CURRENT)[0]
        tag_index = int(clicked_tag.split("_")[-1])
        _, info_text = self.current_response[tag_index]

        if info_text:
            try:
                self.bubble.destroy()
            except AttributeError:
                pass

            x, y, _, _ = self.chat_log.bbox(tk.CURRENT)
            x += self.chat_log.winfo_rootx()
            y += self.chat_log.winfo_rooty()

            self.bubble = WordBubble(self, x, y - 30, info_text)

        self.chat_log.configure(state="disabled")


if __name__ == "__main__":
    app = JapanesePracticeApp()
    app.mainloop()
