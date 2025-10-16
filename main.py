import customtkinter as ctk
from tkinter import filedialog, messagebox
import os, re, json, sys
from tkinter import simpledialog

# ---------- Определяем путь программы ----------
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APP_NAME = os.path.basename(BASE_DIR)
CONFIG_PATH = os.path.join(BASE_DIR, "config", "settings.json")

# ---------- Настройки ----------
def load_settings():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("game_path", "")
        except Exception as e:
            print("Ошибка чтения настроек:", e)
    return ""

def save_settings(game_path):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"game_path": game_path}, f, indent=4, ensure_ascii=False)

def get_game_path_from_config(config_path=CONFIG_PATH):
    """
    Читает путь к игре Hearts of Iron IV из JSON-конфигурации.
    Возвращает строку с путем, либо пустую строку, если не найдено.
    """
    if not os.path.exists(config_path):
        print(f"Файл конфигурации не найден: {config_path}")
        return ""

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        game_path = data.get("game_path", "")
        if game_path and os.path.exists(game_path):
            return game_path
        else:
            print("Путь к игре не найден в JSON или папка не существует")
            return ""
    except Exception as e:
        print(f"Ошибка чтения конфигурации: {e}")
        return ""


# ---------- Основные функции ----------
def browse_game_path():
    path = filedialog.askdirectory(title="Выберите папку с Hearts of Iron IV")
    if path:
        game_path_var.set(path)
        save_settings(path)

def browse_mod_file():
    file_path = filedialog.askopenfilename(
        title="Выберите .mod файл шаблона",
        filetypes=[("Hearts of Iron IV Mod File", "*.mod")]
    )
    if file_path:
        mod_file_var.set(file_path)
        extract_mod_path(file_path)

def extract_mod_path(mod_file):
    with open(mod_file, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'path="(.+?)"', content)
    if match:
        mod_path_var.set(match.group(1))
    else:
        messagebox.showerror("Ошибка", "Не удалось найти путь к моду в файле .mod")

# ---------- Окно создания страны ----------
def open_country_creator():
    if not mod_path_var.get():
        messagebox.showwarning("Ошибка", "Сначала выбери .mod файл!")
        return

    win = ctk.CTkToplevel(root)
    win.title("Создание страны")
    win.geometry("520x640")
    win.transient(root)
    win.grab_set()
    win.focus_force()

    tag_var = ctk.StringVar()
    name_var = ctk.StringVar()
    color_var = ctk.StringVar(value="255 0 0")
    gfx_var = ctk.StringVar(value="Западно-Европейская")
    r_var, g_var, b_var = ctk.IntVar(value=255), ctk.IntVar(value=0), ctk.IntVar(value=0)

    gfx_options = {
        "Восточно-Европейская": ("eastern_european_gfx", "eastern_european_2d"),
        "Африканская": ("african_gfx", "african_2d"),
        "Ближневосточная": ("middle_eastern_gfx", "middle_eastern_2d"),
        "Азиатская": ("asian_gfx", "asian_2d"),
        "Южноамериканская": ("southamerican_gfx", "southamerican_2d"),
        "Британская": ("commonwealth_gfx", "commonwealth_2d"),
        "Западно-Европейская": ("western_european_gfx", "western_european_2d"),
    }

    def update_color_preview(*_):
        r, g, b = r_var.get(), g_var.get(), b_var.get()
        color_preview.configure(fg_color=f"#{r:02x}{g:02x}{b:02x}")
        color_var.set(f"{r} {g} {b}")

    def create_country():
        tag, name, color, gfx_choice = tag_var.get().upper(), name_var.get(), color_var.get(), gfx_var.get()
        if not (tag and name):
            messagebox.showerror("Ошибка", "Заполни все поля!")
            return

        mod_path = mod_path_var.get()
        gfx_3d, gfx_2d = gfx_options[gfx_choice]
        os.makedirs(os.path.join(mod_path, "common", "countries"), exist_ok=True)
        os.makedirs(os.path.join(mod_path, "history", "countries"), exist_ok=True)
        os.makedirs(os.path.join(mod_path, "common", "country_tags"), exist_ok=True)

        with open(os.path.join(mod_path, "common", "countries", f"{name}.txt"), "w", encoding="utf-8") as f:
            f.write(f"graphical_culture = {gfx_3d}\n")
            f.write(f"graphical_culture_2d = {gfx_2d}\n")
            f.write(f"color = {{ {color} }}\n")

        with open(os.path.join(mod_path, "history", "countries", f"{tag} - {name}.txt"), "w", encoding="utf-8") as f:
            f.write("capital = 1\nset_research_slots = 3\n")

        with open(os.path.join(mod_path, "common", "countries", "colors.txt"), "a", encoding="utf-8") as f:
            f.write(f"\n{tag} = {{ color = rgb {{ {color} }} color_ui = rgb {{ {color} }} }}\n")

        with open(os.path.join(mod_path, "common", "country_tags", "02_countries.txt"), "a", encoding="utf-8") as f:
            f.write(f"{tag} = \"countries/{name}.txt\"\n")

        messagebox.showinfo("Готово", f"Создана страна {name} ({tag})!")
        win.destroy()

    # ---------- Интерфейс ----------
    frame = ctk.CTkFrame(win, corner_radius=10)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    font_label = ("Arial", 13)
    font_entry = ("Arial", 13)

    ctk.CTkLabel(frame, text="Создание новой страны", font=("Arial", 18, "bold")).pack(pady=10)

    ctk.CTkLabel(frame, text="TAG страны (3 буквы):", font=font_label).pack(pady=3)
    ctk.CTkEntry(frame, textvariable=tag_var, width=200, font=font_entry).pack()

    ctk.CTkLabel(frame, text="Название страны:", font=font_label).pack(pady=3)
    ctk.CTkEntry(frame, textvariable=name_var, width=300, font=font_entry).pack()

    ctk.CTkLabel(frame, text="Цвет страны (RGB):", font=font_label).pack(pady=10)
    color_preview = ctk.CTkFrame(frame, width=100, height=30, fg_color="#ff0000")
    color_preview.pack(pady=5)

    for label, var in [("R", r_var), ("G", g_var), ("B", b_var)]:
        row = ctk.CTkFrame(frame)
        row.pack(fill="x", padx=20, pady=2)
        ctk.CTkLabel(row, text=label, width=20, font=font_label).pack(side="left")
        ctk.CTkSlider(row, from_=0, to=255, variable=var, command=update_color_preview).pack(fill="x", expand=True)

    ctk.CTkEntry(frame, textvariable=color_var, justify="center", font=font_entry, state="readonly").pack(pady=5)

    ctk.CTkLabel(frame, text="Графическая культура:", font=font_label).pack(pady=10)
    ctk.CTkComboBox(frame, values=list(gfx_options.keys()), variable=gfx_var, width=250, font=font_entry).pack(pady=5)

    ctk.CTkButton(frame, text="Создать страну", command=create_country, height=40,
                  fg_color="#4CAF50", hover_color="#45A049", font=("Arial", 14, "bold")).pack(pady=20)

    update_color_preview()


def find_localization_id():
    if not mod_path_var.get():
        messagebox.showwarning("Ошибка", "Сначала выбери .mod файл!")
        return
    
    query = simpledialog.askstring("Поиск ID", "Введите текст для поиска в локализации:")
    if not query:
        return

    results = []

    game_path_var = get_game_path_from_config()
    if game_path_var:
        loc_dir = os.path.join(game_path_var, "localisation")

    for root_dir, _, files in os.walk(loc_dir):
        for file in files:
            if file.endswith(".yml"):
                file_path = os.path.join(root_dir, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            # Убираем комментарии и лишние пробелы
                            clean_line = line.split("#")[0].strip()
                            if query.lower() in clean_line.lower():  # поиск без учета регистра
                                results.append(f"{clean_line} — {file_path} (строка {i})")
                except Exception as e:
                    print(f"Ошибка при чтении {file_path}: {e}")

    if results:
        win = ctk.CTkToplevel(root)
        win.title(f"Результаты поиска: {query}")
        win.geometry("700x400")
        text = ctk.CTkTextbox(win, wrap="none")
        text.pack(fill="both", expand=True, padx=10, pady=10)
        text.insert("0.0", "\n".join(results))
        text.configure(state="disabled")
    else:
        messagebox.showinfo("Поиск завершен", "Совпадений не найдено.")


# ---------- Главное окно ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.title(f"HOI4 Modding Tool — {APP_NAME} — by 💢🖤Schrödinger's Cutie🖤👾")
root.geometry("750x480")

game_path_var = ctk.StringVar(value=load_settings())
mod_file_var = ctk.StringVar()
mod_path_var = ctk.StringVar()

font_label = ("Arial", 13)
font_entry = ("Arial", 13)

# ---------- Компактный интерфейс ----------
frame = ctk.CTkFrame(root, corner_radius=12)
frame.pack(fill="both", expand=True, padx=20, pady=20)

ctk.CTkLabel(frame, text="HOI4 Modding Tool", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=3, pady=(10, 5))
ctk.CTkLabel(frame, text="by 💢🖤Schrödinger's Cutie🖤👾", font=("Arial", 12, "italic")).grid(row=1, column=0, columnspan=3, pady=(0, 15))

# Путь к игре
ctk.CTkLabel(frame, text="Путь к игре:", font=font_label).grid(row=2, column=0, sticky="w", padx=10, pady=5)
ctk.CTkEntry(frame, textvariable=game_path_var, width=450, font=font_entry).grid(row=2, column=1, pady=5)
ctk.CTkButton(frame, text="Обзор", width=80, command=browse_game_path).grid(row=2, column=2, padx=5)

# .mod файл
ctk.CTkLabel(frame, text="Файл .mod:", font=font_label).grid(row=3, column=0, sticky="w", padx=10, pady=5)
ctk.CTkEntry(frame, textvariable=mod_file_var, width=450, font=font_entry).grid(row=3, column=1, pady=5)
ctk.CTkButton(frame, text="Обзор", width=80, command=browse_mod_file).grid(row=3, column=2, padx=5)

# Папка мода
ctk.CTkLabel(frame, text="Папка мода:", font=font_label).grid(row=4, column=0, sticky="w", padx=10, pady=5)
ctk.CTkEntry(frame, textvariable=mod_path_var, width=550, state="readonly", font=font_entry).grid(row=4, column=1, columnspan=2, pady=5, padx=5)

# Нижние кнопки
bottom = ctk.CTkFrame(frame)
bottom.grid(row=5, column=0, columnspan=3, pady=25)
ctk.CTkButton(bottom, text="Создать страну", command=open_country_creator,
              fg_color="#4CAF50", hover_color="#45A049", width=200, height=40, font=("Arial", 14, "bold")).pack(side="left", padx=10)
ctk.CTkButton(bottom, text="Найти ID по локализации", command=find_localization_id,
              fg_color="#2196F3", hover_color="#1976D2", width=200, height=40, font=("Arial", 14, "bold")).pack(side="left", padx=10)
ctk.CTkButton(bottom, text="(Заготовка)", width=200, height=40, font=("Arial", 14, "bold")).pack(side="left", padx=10)

frame.grid_columnconfigure(1, weight=1)
root.mainloop()
