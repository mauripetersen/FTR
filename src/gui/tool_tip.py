import tkinter as tk

__all__ = ["CTkToolTip"]


class CTkToolTip:
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.after_id = None

        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.cancel)
        self.widget.bind("<Motion>", self.move)

    def schedule(self, event=None):
        self.after_id = self.widget.after(self.delay, self.show_tooltip)

    def cancel(self, event=None):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        self.hide_tooltip()

    def move(self, event):
        if self.tooltip_window:
            x = self.widget.winfo_pointerx() + 12
            y = self.widget.winfo_pointery() + 20
            self.tooltip_window.geometry(f"+{x}+{y}")

    def show_tooltip(self):
        if self.tooltip_window or not self.text:
            return
        x = self.widget.winfo_pointerx() + 12
        y = self.widget.winfo_pointery() + 20
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("Segoe UI", 10))
        label.pack(ipadx=4, ipady=2)

    def hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
