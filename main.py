#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import threading
import time

# from tkinter import *  # I know bad practice
import tkinter as tk
from tkinter import Button, filedialog
from tkinter import messagebox as mb
from tkinter import scrolledtext, ttk
from tkinter.constants import END
from tkinter.filedialog import askdirectory

from bs4 import BeautifulSoup
from requests import get

arguments = dict()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Accept-Language": "ja",
    "Referer": "https://www.google.com/",
}

window = tk.Tk()
window.title("Ncode grabber")
window.minsize(width=600, height=300)
FONTS = ("Arial", 14)
is_overwrite = tk.BooleanVar()


# GUI start
# Canvas for logo
canvas = tk.Canvas(width=300, height=263)
bg_image = tk.PhotoImage(file=".\\data\\background.png")
canvas.create_image(150, 110, image=bg_image)
canvas.grid(row=7, column=5, columnspan=3, sticky="n")

# Labels _lb suffix
title_lb = tk.Label(text="Ncode Grabber", font=("Arial", 28, "bold"))
title_lb.grid(row=0, column=1, columnspan=4, sticky="e")

save_path_lb = tk.Label(text="Save path", font=FONTS)
save_path_lb.grid(row=1, column=0, sticky="w")

url_path_lb = tk.Label(text="URL link", font=FONTS)
url_path_lb.grid(row=2, column=0, sticky="w")

start_chapter_lb = tk.Label(text="Starting chapter", font=FONTS)
start_chapter_lb.grid(row=3, column=0, sticky="w")

end_chapter_lb = tk.Label(text="End chapter", font=FONTS)
end_chapter_lb.grid(row=4, column=0, sticky="w")

file_name_lb = tk.Label(text="File name", font=FONTS)
file_name_lb.grid(row=5, column=0, sticky="w")

overwrite_lb = tk.Label(text="Overwrite file?", font=FONTS)
overwrite_lb.config(fg="Red")
overwrite_lb.grid(row=6, column=0, sticky="w")

# Entry's  _ent suffix
save_path_ent = tk.Entry(width=50)
save_path_ent.grid(row=1, column=1, sticky="w")

url_path_ent = tk.Entry(width=50)
url_path_ent.grid(row=2, column=1, sticky="n")

start_chapter_ent = tk.Entry(width=10)
start_chapter_ent.grid(row=3, column=1, sticky="w")

end_chapter_ent = tk.Entry(width=10)
end_chapter_ent.grid(row=4, column=1, sticky="w")

file_name_ent = tk.Entry(width=30)
file_name_ent.grid(row=5, column=1, sticky="w")

# Check box _ck suffix
is_overwrite_ck = tk.Checkbutton(variable=is_overwrite)  # Returns 0 or 1
is_overwrite_ck.grid(row=6, column=1, sticky="w")

# Text area for log
text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=35, height=8, font=("Times New Roman", 9))
text_area.grid(row=7, column=0, columnspan=2, sticky="w")
window.grid_columnconfigure(0, weight=1, uniform="foo")


# Program Logic
def log_print(txt):
    """
    Logs all, and show's in log window
    """
    text_area.configure(state="normal")
    text_area.insert(tk.INSERT, str(txt) + "\n")
    text_area.see(END)
    text_area.configure(state="disabled")


def paste_url():
    """
    Pasting url from clipboard to entry field
    """
    clipboard = window.clipboard_get()
    url_path_ent.delete(0, END)
    url_path_ent.insert(0, clipboard)


def clear_url():
    url_path_ent.delete(0, END)


def save_settings(key, value):
    """
    Saving user input and settings  (File paths, file name, etc)
    Data saves in dictionary as kye, value pair.
    """
    arguments[key] = value
    return 0


def browse_save_path():
    """
    Opens ask directory window, to set directory for saving the result txt file.
    """
    path = filedialog.askdirectory()
    if path == "":
        path = os.getcwd()
    path = path.replace("/", "\\") + "\\"
    save_settings("path", path)
    save_path_ent.delete(0, END)
    save_path_ent.insert(0, path)
    log_print(f"Save path: {path}")


def check_input():
    """
        Cheking input, if there is empty field rise Error windows or add default values.
    If there no errors add input in the dictionary with arguments
    """
    # Cheking is user set the path to save file
    if "path" not in arguments.keys():
        # Getting current directory
        path = os.getcwd()
        path = path.replace("/", "\\") + "\\"
        save_settings("path", path)
        save_path_ent.delete(0, END)
        save_path_ent.insert(0, path)
        log_print(f"Save path: {path}" + "\n")

    # Checking is user entered url leads to the ncode.syosetu.com
    template = "https://ncode.syosetu.com"  # 25 symbols. Also we can use re.match()
    url = url_path_ent.get()
    if url[0:25] != template:
        log_url = url[0:25]
        log_print(f"Wrong url {log_url}")
        mb.showerror(
            "Wrong URL!",
            "Something wrong with url link, please check it. Example: https://ncode.syosetu.com/n7975cr/",
        )
        return 1  # Some error
    else:
        if url[-1] != "/":
            url += "/"
        log_print(url)
        save_settings("url", url)

    # Cheking values of the start and the end chapters, must be positive number
    start_chapter = start_chapter_ent.get()
    end_chapter = end_chapter_ent.get()

    # Also we can use RegExp to avoid using int() later.
    if not (start_chapter.isnumeric() and int(start_chapter) >= 0) or not (
        end_chapter.isnumeric() and int(end_chapter) >= 0
    ):
        mb.showerror("Error!", "Value for 'Starting' or 'Ending' chapter's wrong, it must be integer, bigger or = 0")
        return 1  # Some error
    else:
        if int(start_chapter) > int(end_chapter):
            log_print(f"Start chapter bigger then End chapter! Start = {start_chapter} and End = {end_chapter}.")
            mb.showerror(
                "Error!", f"Start chapter bigger then End chapter! Start = {start_chapter} and End = {end_chapter}."
            )
            return 1  # Some error
        else:
            log_print(f"Start = {start_chapter} and End = {end_chapter}. OK")
            save_settings("start", int(start_chapter))
            save_settings("end", int(end_chapter))

    # Get file name. If empty name = current time in ms
    file_name = file_name_ent.get()
    if len(file_name) < 1:
        random_file_name = str(time.time()).split(".")[0] + ".txt"
        save_settings("file_name", random_file_name)
        log_print(f"File name is: {random_file_name}")
        file_name_ent.insert(0, random_file_name)
    else:
        pattern = r"\.txt"
        if re.search(pattern, file_name):
            save_settings("file_name", file_name)
        else:
            file_name += ".txt"
            save_settings("file_name", file_name)

    # Saving is_overwrite value in arguments dictionary
    save_settings("is_overwrite", is_overwrite.get())
    return 0  # OK


def save_page(text, chapter):
    name = arguments["path"] + arguments["file_name"]  # Name+path
    page_id = str(10_000 + chapter)  # Will be used in the next features
    # is_overwrite = arguments["is_overwrite"]
    with open(name, "a+", encoding="utf-8-sig") as file:
        file.write("\n" + "Chapter: " + str(chapter) + "\n" + text + "\n" + f"[{page_id}]")
        log_print(f"Chapter {chapter} saved!")


def grab_page(url, chapter):
    """
    Parsing page at the given url.
    """
    try:
        resp = get(url, headers=headers)
    except:
        log_print(f"Unknown Connection Error!")
        return
    if resp.status_code != 200:
        log_print(f"Connection Error code: {resp.status_code}")
        return
    soup = BeautifulSoup(resp.text, "html.parser")
    body = soup.find_all(id="novel_honbun")
    text_data = body[0].text
    save_page(text_data, chapter)


def get_response():
    """
    Cheking server aviability, if OK send to parsing function
    """
    url = arguments["url"]
    start = arguments["start"]
    end = arguments["end"]
    try:
        resp = get(url, headers=headers)
    except:
        log_print(f"Unknown Connection Error!")
        return
    else:
        if resp.status_code == 200:
            log_print(f"Connected, resp code = {resp.status_code}")
            chapter = start
            while chapter <= end:
                grab_page(url + str(chapter), chapter)
                chapter += 1
            log_print("Completed!")
        else:
            log_print(f"Connection Error resp code = {resp.status_code}")
            return


def start_button():
    flag = check_input()
    if flag != 1:
        get_response()
    else:
        log_print("Some errors occurred! Please check your input.")


def start_threading():

    thread_1 = threading.Thread(target=start_button)
    thread_1.start()


# GUI Buttons
# Buttons _btn suffix
browse_btn = Button(text="Browse", command=browse_save_path)
browse_btn.grid(row=1, column=3)

browse_btn = Button(text="Paste URL", command=paste_url)
browse_btn.grid(row=2, column=3)

browse_btn = Button(text="Clear", command=clear_url)
browse_btn.grid(row=2, column=4)

start_btn = Button(
    text="START",
    font=("Helvetica", 30),
    bg="#0052cc",
    fg="#ffffff",
    command=start_threading,
)
start_btn.grid(row=7, column=1, sticky="e")

window.mainloop()
