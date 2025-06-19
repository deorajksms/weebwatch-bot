import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import webbrowser
import json
import os

# --- Constants ---
FAV_FILE = "favorites.json"

# --- Functions ---
def search_jikan():
    category = category_var.get()
    query = entry.get().strip()

    if not query:
        messagebox.showwarning("Input Error", "Please enter a search query.")
        return

    url = f"https://api.jikan.moe/v4/{category}?q={query}&limit=5"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        results_box.delete("1.0", tk.END)
        image_label.config(image='')

        if 'data' in data and data['data']:
            first = True
            for item in data['data']:
                title = item.get('title', 'N/A')
                score = item.get('score', 'N/A')
                synopsis = item.get('synopsis', 'No synopsis available')[:300]
                url = item.get('url', '')

                results_box.insert(tk.END, f"📺 Title: {title}\n")
                results_box.insert(tk.END, f"⭐ Score: {score}\n")
                results_box.insert(tk.END, f"📝 Synopsis: {synopsis}...\n")
                results_box.insert(tk.END, f"🔗 URL: {url}\n\n")

                if first:
                    current_result['title'] = title
                    current_result['url'] = url
                    current_result['image_url'] = item.get("images", {}).get("jpg", {}).get("image_url")
                    first = False

                    image_url = current_result['image_url']
                    if image_url:
                        img_data = requests.get(image_url).content
                        img = Image.open(BytesIO(img_data)).resize((100, 140))
                        img_tk = ImageTk.PhotoImage(img)
                        image_label.configure(image=img_tk)
                        image_label.image = img_tk
        else:
            results_box.insert(tk.END, "❌ No results found.")

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", str(e))

def open_trailer():
    if current_result['title']:
        query = current_result['title'] + " trailer"
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")

def add_to_favorites():
    if not current_result['title']:
        messagebox.showwarning("No Result", "Please search and select an anime/manga first.")
        return

    fav = {
        "title": current_result['title'],
        "url": current_result['url'],
        "image_url": current_result['image_url']
    }

    favorites = []
    if os.path.exists(FAV_FILE):
        with open(FAV_FILE, "r") as f:
            favorites = json.load(f)

    favorites.append(fav)
    with open(FAV_FILE, "w") as f:
        json.dump(favorites, f, indent=2)

    messagebox.showinfo("Added", f"'{current_result['title']}' added to favorites!")

def view_favorites():
    if not os.path.exists(FAV_FILE):
        messagebox.showinfo("No Favorites", "No favorites found.")
        return

    with open(FAV_FILE, "r") as f:
        favorites = json.load(f)

    fav_win = tk.Toplevel(root)
    fav_win.title("Favorites")
    fav_win.geometry("500x400")

    fav_box = tk.Text(fav_win, wrap=tk.WORD)
    fav_box.pack(expand=True, fill="both")

    for fav in favorites:
        fav_box.insert(tk.END, f"📺 {fav['title']}\n🔗 {fav['url']}\n\n")

def toggle_theme():
    global is_dark
    is_dark = not is_dark

    bg = "#333" if is_dark else "#fff"
    fg = "#fff" if is_dark else "#000"

    root.config(bg=bg)
    for widget in root.winfo_children():
        try:
            widget.config(bg=bg, fg=fg)
        except:
            pass
    results_box.config(bg=bg, fg=fg)

# --- GUI Setup ---
root = tk.Tk()
root.title("Anime/Manga Search (Jikan API)")
root.geometry("750x580")

current_result = {'title': None, 'url': None, 'image_url': None}

# Top input frame
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

category_var = tk.StringVar(value="anime")
category_menu = ttk.Combobox(top_frame, textvariable=category_var, values=["anime", "manga", "characters"], width=10)
category_menu.grid(row=0, column=0, padx=5)

entry = tk.Entry(top_frame, width=50)
entry.grid(row=0, column=1, padx=5)

search_button = tk.Button(top_frame, text="Search", command=search_jikan, bg="#4CAF50", fg="white")
search_button.grid(row=0, column=2, padx=5)

# Image display
image_label = tk.Label(root)
image_label.pack(pady=10)

# Results text box
text_frame = tk.Frame(root)
text_frame.pack(expand=True, fill="both")

scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

results_box = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, font=("Arial", 11))
results_box.pack(expand=True, fill="both")

scrollbar.config(command=results_box.yview)

# Bottom buttons
bottom_frame = tk.Frame(root)
bottom_frame.pack(pady=10)

trailer_btn = tk.Button(bottom_frame, text="Watch Trailer", command=open_trailer, bg="#2196F3", fg="white")
trailer_btn.grid(row=0, column=0, padx=5)

fav_btn = tk.Button(bottom_frame, text="Add to Favorites", command=add_to_favorites, bg="#FF5722", fg="white")
fav_btn.grid(row=0, column=1, padx=5)

view_fav_btn = tk.Button(bottom_frame, text="View Favorites", command=view_favorites, bg="#9C27B0", fg="white")
view_fav_btn.grid(row=0, column=2, padx=5)

theme_btn = tk.Button(bottom_frame, text="Toggle Light/Dark", command=toggle_theme, bg="#607D8B", fg="white")
theme_btn.grid(row=0, column=3, padx=5)

# Set default theme
is_dark = False

root.mainloop()
