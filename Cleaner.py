import tkinter as tk
from tkinter import ttk
from bs4 import BeautifulSoup, Comment
import re

INLINE_ONE_LINE_PATTERN = re.compile(
    r"<(\w+)>\s*([^<\n]+?)\s*</\1>",
    re.MULTILINE
)

def clean_html():
    raw_html = input_text.get("1.0", tk.END).strip()
    if not raw_html:
        return

    soup = BeautifulSoup(raw_html, "html.parser")

    # Strip attributes
    if strip_attrs_var.get():
        for tag in soup.find_all(True):
            tag.attrs = {}

    # Remove selected tags but keep content
    tags_to_unwrap = [
        t.strip().lower()
        for t in unwrap_tags_var.get().split(",")
        if t.strip()
    ]

    if tags_to_unwrap:
        for tag in soup.find_all(tags_to_unwrap):
            tag.unwrap()

    # Remove comments
    if remove_comments_var.get():
        for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
            comment.extract()

    html = str(soup)

    # Formatting
    if pretty_format_var.get():
        html = soup.prettify().replace("    ", "\t")

        if collapse_inline_var.get():
            html = INLINE_ONE_LINE_PATTERN.sub(
                lambda m: f"<{m.group(1)}>{m.group(2).strip()}</{m.group(1)}>",
                html
            )

    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, html)

    root.clipboard_clear()
    root.clipboard_append(html)
    root.update()  # now it stays on clipboard after the app is closed

# Smart paste function
def smart_paste(event):
    widget = event.widget
    try:
        widget.delete("sel.first", "sel.last")
    except tk.TclError:
        pass  # no selection

    try:
        text = widget.clipboard_get()
        widget.insert("insert", text)
    except tk.TclError:
        pass

    return "break"

# Clear input function
def clear_input():
    input_text.delete("1.0", tk.END)

# Trigger clean on Enter key
def trigger_clean(event):
    clean_html()
    return "break"

# --- GUI ---

def select_all(event):
    event.widget.tag_add("sel", "1.0", "end-1c")
    return "break"

root = tk.Tk()
root.title("HTML Cleanup Tool")

root.geometry("900x700")

frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

# Options setup
strip_attrs_var = tk.BooleanVar(value=True)
remove_comments_var = tk.BooleanVar(value=True)
pretty_format_var = tk.BooleanVar(value=True)
collapse_inline_var = tk.BooleanVar(value=True)

# Options checkboxes
options_frame = ttk.LabelFrame(frame, text="Options", padding=10)
options_frame.pack(fill="x", pady=10)

ttk.Checkbutton(
    options_frame,
    text="Strip all attributes",
    variable=strip_attrs_var
).pack(anchor="w")

ttk.Checkbutton(
    options_frame,
    text="Remove HTML comments",
    variable=remove_comments_var
).pack(anchor="w")

ttk.Checkbutton(
    options_frame,
    text="Pretty formatting (tabs & line breaks)",
    variable=pretty_format_var
).pack(anchor="w")

ttk.Checkbutton(
    options_frame,
    text="Keep text-only tags on one line",
    variable=collapse_inline_var
).pack(anchor="w")

# Tags to unwrap
unwrap_tags_var = tk.StringVar(value="div,span")

ttk.Label(options_frame, text="Remove these tags (keep content):").pack(anchor="w", pady=(10, 0))

unwrap_entry = ttk.Entry(options_frame, textvariable=unwrap_tags_var)
unwrap_entry.pack(fill="x")

ttk.Label(frame, text="Input HTML").pack(anchor="w")
input_text = tk.Text(frame, height=18, wrap="word")
output_text = tk.Text(frame, height=18, wrap="word")

# Key bindings
for w in (input_text, output_text):
    w.bind("<Control-a>", select_all)
    w.bind("<Control-A>", select_all)
    w.bind("<Command-a>", select_all)

for w in (input_text, output_text):
    w.bind("<Control-v>", smart_paste)
    w.bind("<Control-V>", smart_paste)
    w.bind("<Command-v>", smart_paste)  # macOS

root.bind("<Control-Return>", trigger_clean)
root.bind("<Control-KP_Enter>", trigger_clean)  # numpad Enter
root.bind("<Command-Return>", trigger_clean)    # macOS

# Bind Control+Delete for clearing input
root.bind("<Control-Delete>", lambda e: clear_input())
root.bind("<Command-Delete>", lambda e: clear_input())  # macOS

input_text.pack(fill="both", expand=True)

buttons_frame = ttk.Frame(frame)
buttons_frame.pack(pady=10)

ttk.Button(
    buttons_frame,
    text="Clean HTML (auto-copy)",
    command=clean_html
).pack(side="left", padx=5)

ttk.Button(
    buttons_frame,
    text="Clear Input",
    command=clear_input
).pack(side="left", padx=5)


ttk.Label(frame, text="Cleaned Output").pack(anchor="w")

output_text.pack(fill="both", expand=True)

root.mainloop()

