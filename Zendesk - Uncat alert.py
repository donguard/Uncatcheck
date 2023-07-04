from tkinter import ttk
from tkinter import Tk, Label
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk, Image
from plyer import notification
from pathlib import Path
import tkinter as tk
import sys
import json
import sv_ttk
import pygame
import contextlib
import configparser
import threading
import soundfile
import requests
from win11toast import toast
import os

config = configparser.ConfigParser()

# EXE PATH
if getattr(sys, 'frozen', False):
    exe_path = os.path.dirname(sys.executable)
elif __file__:
    exe_path = os.path.dirname(__file__)


# Just a small function to write the file
def write_file():
    config.write(open(f"{exe_path}\\config.INI", 'w'))


if not os.path.exists(f"{exe_path}\\config.INI"):
    config['DEFAULT'] = {'remember_username': 'False',
                         'username': '',
                         'theme': 'light',
                         'alarm_sound': f'{exe_path}\\uncat.mp3',
                         'always_notify': '1',
                         'windows_notify': '1', }

    write_file()


def create_json_file(filename):
    if not os.path.exists(filename):
        data = ["360034746134 - CM, MM & Coll", "360034745954 - ICMS/Connext"]
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
    else:
        pass


# Example usage
filename = f"{exe_path}\\view_id.json"
create_json_file(filename)

with open(f"{exe_path}\\view_id.json", "r") as file:
    if not json.load(file):
        with open(f"{exe_path}\\view_id.json", "w") as file:
            initial_values = ["360034746134 - CM, MM & Coll", "360034745954 - ICMS/Connext"]
            json.dump(initial_values, file)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


with contextlib.redirect_stdout(None):
    import pygame

config = configparser.ConfigParser()
config.read(f"{exe_path}\\config.INI")

Username: str = config['DEFAULT']['username']
Remember_username: str = config['DEFAULT']['remember_username']
theme_current: str = config['DEFAULT']['theme']
always_notify: str = config['DEFAULT']['always_notify']
alarm_sound: str = config['DEFAULT']['alarm_sound']
windows_notify: str = config['DEFAULT']['windows_notify']
path_clean = Path(alarm_sound)

username_logged_in = ""
password_logged_in = ""


def open_login_window():
    def login():
        global username_logged_in
        global password_logged_in
        username = username_entry.get()
        password = password_entry.get()
        if username != "" and password != "":
            auth = username, password
            url = f'https://onguard.zendesk.com/api/v2/views/360034745954/tickets.json'
            response = requests.get(url, auth=auth)
            if not response.ok:
                login_window.withdraw()
                messagebox.showwarning("Fout", "Gebruikersnaam/wachtwoord combinatie niet gevonden.")
                login_window.deiconify()
            else:
                if switch_var.get():
                    config['DEFAULT']['Username'] = username
                    with open(f"{exe_path}\\config.INI", 'w') as configfile:  # save
                        config.write(configfile)
                else:
                    config['DEFAULT']['Username'] = ""
                    with open(f"{exe_path}\\config.INI", 'w') as configfile:  # save
                        config.write(configfile)
                root.deiconify()  # Show the main window
                login_window.withdraw()  # Close the login window
                username_logged_in = username
                password_logged_in = password
        else:
            pass

    global login_window
    global switch_var

    login_window = tk.Toplevel(root)
    login_window.title("Uncat alert - Login")
    root.eval(f'tk::PlaceWindow {str(login_window)} center')
    login_window.bind('<Destroy>', lambda e: sys.exit())

    login_window.resizable(False, False)

    login_frame = ttk.Frame(login_window, padding=5)
    login_frame.pack(side='left', padx=(30, 0))

    username_label = ttk.Label(login_frame, text="Username:")
    username_label.pack(side='top')

    username_entry = ttk.Entry(login_frame, width=30, justify='center')
    username_entry.pack(pady=10, side='top')

    if Remember_username == "True" and Username != '':
        username_entry.insert(0, Username)
    else:
        username_entry.insert(0, "")

    switch_var = tk.BooleanVar(value=Remember_username)

    def remember_username_toggle():
        if switch_var.get():
            config['DEFAULT']['Remember_username'] = "True"
            config['DEFAULT']['Username'] = ""
            with open(f"{exe_path}\\config.INI", 'w') as configfile:  # save
                config.write(configfile)
        else:
            config['DEFAULT']['Remember_username'] = "False"
            with open(f"{exe_path}\\config.INI", 'w') as configfile:  # save
                config.write(configfile)

    switch = ttk.Checkbutton(login_frame, text='Remember me', variable=switch_var, style='Switch.TCheckbutton',
                             command=lambda: remember_username_toggle())
    switch.pack(pady=(0, 10))

    password_label = ttk.Label(login_frame, text="Password:")
    password_label.pack(side='top')

    password_entry = ttk.Entry(login_frame, show="*", width=30, justify='center')
    password_entry.pack(pady=10, side='top')

    login_button = ttk.Button(login_frame, text="Login", command=lambda: login(), width=7, style='Accent.TButton')
    login_button.pack(pady=10, anchor='center', fill='x')
    if theme_current == "light":
        photo = ImageTk.PhotoImage(Image.open(resource_path("logo_light.png")))
    else:
        photo = ImageTk.PhotoImage(Image.open(resource_path("uncatalert.png")))

    logo_label = Label(login_window, image=photo)
    logo_label.image = photo
    logo_label.pack(side='right', padx=(30, 5))


def setflag(event):
    global ontop
    ontop = False
    print_button.config(state='enabled')
    root.deiconify()
    combobox.config(values=values)


def settings():
    root.withdraw()
    global ontop
    if not ontop:
        print_button.config(state='disabled')

        settings_window = tk.Toplevel(root)
        settings_window.bind('<Destroy>', setflag)
        settings_window.title("Zendesk uncat alert - Settings")
        settings_window.resizable(False, False)
        settings_window.geometry("450x275")

        notebook = ttk.Notebook(settings_window)

        # Create and add tabs to the notebook
        tab1 = ttk.Frame(notebook, padding=15)
        tab2 = ttk.Frame(notebook, padding=20)
        tab3 = ttk.Frame(notebook, padding=20)

        notebook.add(tab1, text="View ID's")
        notebook.add(tab2, text="Notifications and theme")
        notebook.add(tab3, text="Reset")

        # View ID settings
        def add_value():
            settings_window.withdraw()

            def save_value():
                new_view_id = view_id_entry.get()
                new_name = name_entry.get()
                if new_view_id and new_name != "":
                    new_value = f"{new_view_id} - {new_name}"

                    values.append(new_value)
                    save_values_to_file()

                    view_id_entry.delete(0, tk.END)
                    name_entry.delete(0, tk.END)
                    view_id_combo_settings['values'] = values

                    add_window.withdraw()  # Close the window after saving
                    settings_window.deiconify()
                    view_id_combo_settings.set(new_value)

            add_window = tk.Toplevel(root)
            add_window.title("Add view ID")
            add_window.resizable(False, False)

            view_id_add_frame1 = ttk.Frame(add_window)
            view_id_add_frame1.pack(side='top', fill='x')
            view_id_label1 = ttk.Label(view_id_add_frame1, text="View ID:")
            view_id_label1.pack(padx=10, pady=10, side='left')
            view_id_entry = ttk.Entry(view_id_add_frame1, width=40)
            view_id_entry.pack(padx=10, pady=10, side='right')

            view_id_add_frame2 = ttk.Frame(add_window)
            view_id_add_frame2.pack(side='top', fill='x')
            name_label = ttk.Label(view_id_add_frame2, text="Name:")
            name_label.pack(padx=10, pady=10, side='left')
            name_entry = ttk.Entry(view_id_add_frame2, width=40)
            name_entry.pack(padx=10, pady=10, side='right')

            save_button = ttk.Button(add_window, text="Save", command=save_value)
            save_button.pack(padx=10, pady=10, side='top')

            add_window.bind('<Destroy>', lambda e: settings_window.deiconify())

        def delete_value():
            settings_window.withdraw()
            if len(values) > 1:
                if messagebox.askyesno(f"Confirmation",
                                       "This will delete the selected View ID.\n\nDo you want to proceed?"):
                    values.remove(view_id_combo_settings.get())
                    save_values_to_file()
                    with open(f"{exe_path}\\view_id.json", "r") as file:
                        if not json.load(file):
                            with open(f"{exe_path}\\view_id.json", "w") as file:
                                initial_values = ["360034746134 - CM, MM & Coll", "360034745954 - ICMS/Connext"]
                                json.dump(initial_values, file)
                    settings_window.deiconify()
                else:
                    view_id_combo_settings.set(values[0]) if view_id_combo_settings['values'] else None
                    view_id_combo_settings.config(values=values)
                    view_id_delete.config(state='enabled')
                    settings_window.deiconify()
                    load_values_from_file()
                    view_id_combo_settings.config(values=values)
            else:
                messagebox.showwarning(f"Warning",
                                       "Can not have less than one view ID. Please add a different view ID and "
                                       "try again.")
                settings_window.deiconify()

        view_id_window = ttk.Label(tab1)
        view_id_window.pack(anchor='center', pady=10, fill='x')

        view_id_label = ttk.Label(view_id_window, text="Add and delete View ID's.")
        view_id_label.pack(side='top', padx=10, pady=(10, 30), anchor='n')

        view_id_combo_settings = ttk.Combobox(view_id_window, values=values, state="readonly")
        view_id_combo_settings.pack(side='top', fill='x', padx=10, anchor='s')

        view_id_frame = ttk.Frame(view_id_window)
        view_id_frame.pack(side='top', padx=(10, 0), fill='x', pady=(15, 0))

        view_id_add = ttk.Button(view_id_frame, text="Add view ID", command=lambda: add_value(), width=15)
        view_id_add.pack(side='left', padx=(0, 10))

        view_id_delete = ttk.Button(view_id_frame, text="Delete selected", command=lambda: delete_value(), width=15)
        view_id_delete.pack(side='right', padx=(0, 10))

        # Theme settings
        def toggle_theme():
            theme = sv_ttk.get_theme()
            new_theme = "light" if theme == "dark" else "dark"
            sv_ttk.use_light_theme() if new_theme == "light" else sv_ttk.use_dark_theme()
            config['DEFAULT']['theme'] = new_theme
            with open(f"{exe_path}\\config.INI", 'w') as configfile:
                config.write(configfile)

        theme_frame = ttk.Frame(tab2)
        theme_frame.pack(side='top', pady=5, fill='x', expand=True)

        theme_label = ttk.Label(theme_frame, text=f"Dark mode")
        theme_label.pack(side='left', padx=(0, 10))

        theme_toggle = ttk.Checkbutton(theme_frame, style='Switch.TCheckbutton', command=lambda: toggle_theme())
        theme_toggle.pack(side='right', pady=5)
        theme_toggle.state(["selected"]) if sv_ttk.get_theme() == "dark" else None

        # Always notify settings
        def always_notify_toggle():
            global always_notify
            always_notify = "0" if always_notify == "1" else "1"
            config['DEFAULT']['always_notify'] = always_notify
            with open(f"{exe_path}\\config.INI", 'w') as configfile:  # save
                config.write(configfile)

        always_notify_frame = ttk.Frame(tab2)
        always_notify_frame.pack(side='top', pady=5, expand=True, fill='x')

        always_notify_label = ttk.Label(always_notify_frame, text="Always notify")
        always_notify_label.pack(side='left', padx=(0, 17), pady=5)

        always_notify_chkbtn = ttk.Checkbutton(always_notify_frame, style='Switch.TCheckbutton',
                                               variable=tk.IntVar(value=always_notify),
                                               command=lambda: always_notify_toggle())
        always_notify_chkbtn.pack(side='right', pady=5)

        # Use Windows notifications
        def use_windows_notifications():
            global windows_notify
            windows_notify = "0" if windows_notify == "1" else "1"
            config['DEFAULT']['windows_notify'] = windows_notify
            with open(f"{exe_path}\\config.INI", 'w') as configfile:  # save
                config.write(configfile)

        windows_notify_frame = ttk.Frame(tab2)
        windows_notify_frame.pack(side='top', pady=5, expand=True, fill='x')

        windows_notify_label = ttk.Label(windows_notify_frame, text="Windows notifications")
        windows_notify_label.pack(side='left', padx=(0, 17), pady=5)

        windows_notify_chkbtn = ttk.Checkbutton(windows_notify_frame, style='Switch.TCheckbutton',
                                                variable=tk.IntVar(value=windows_notify),
                                                command=lambda: use_windows_notifications())
        windows_notify_chkbtn.state(["selected"]) if windows_notify == "1" else None
        windows_notify_chkbtn.pack(side='right', pady=5)

        # Sound file
        def ask_for_sound():
            settings_window.withdraw()
            full_path = filedialog.askopenfilename(filetypes=[("Audio files", ".mp3 .wave .wav")], initialfile=f'{exe_path}\\uncat.mp3')
            if full_path == "":
                settings_window.deiconify()
            f = soundfile.SoundFile(full_path)
            sound_length = format(f.frames / f.samplerate)
            if full_path:
                if float(sound_length) > 10:
                    messagebox.showwarning("Warning", "Sound file can not exceed 10 seconds.")
                    settings_window.deiconify()
                else:
                    settings_window.deiconify()
                    file_selected = full_path.rsplit('/', 1)[1]
                    sound_file.config(text=file_selected)
                    config['DEFAULT']['alarm_sound'] = full_path
                    with open(f"{exe_path}\\config.INI", 'w') as configfile:
                        config.write(configfile)

        sound_frame = ttk.Frame(tab2)
        sound_frame.pack(side='top', pady=5, expand=True, fill='both')

        sound_label = ttk.Label(sound_frame, text="Alert sound")
        sound_label.pack(side='left', padx=(0, 35), pady=5)

        sound_file_frame = ttk.Frame(sound_frame, style='Card.TFrame')
        sound_file_frame.pack(side='right', expand=True, fill='both', ipady=5)

        sound_button = ttk.Label(sound_file_frame, text="📁")
        sound_button.bind("<Button-1>", lambda e: ask_for_sound())
        sound_button.pack(side='right', padx=(0, 5))

        sound_file = ttk.Label(sound_file_frame, text=str(Path(config['DEFAULT']['alarm_sound'])).rsplit('\\', 1)[1])
        sound_file.pack(side='left', padx=(10, 10))

        # buh

        def restore_defaults():
            global values
            settings_window.withdraw()
            if messagebox.askyesno(f"Confirmation",
                                   "This will overwrite existing view ID's and notification settings, and can not be undone."
                                   "\n\nDo you wish to proceed? A restart is required."):
                with open('view_id.json', 'w') as file:
                    data = ["360034746134 - CM, MM & Coll", "360034745954 - ICMS/Connext"]
                    json.dump(data, file)
                if os.path.exists(f"{exe_path}\\config.INI"):
                    config['DEFAULT'] = {'remember_username': 'False',
                                         'username': '',
                                         'theme': 'light',
                                         'alarm_sound': f'{exe_path}\\uncat.mp3',
                                         'always_notify': '1',
                                         'windows_notify': '1', }

                    write_file()
                sys.exit()

            else:
                settings_window.deiconify()

        reset_frame = ttk.Frame(tab3)
        reset_frame.pack(side='top', pady=5, expand=True, fill='both')

        reset_btn = ttk.Button(reset_frame, text="Restore default", style='Accent.TButton', command=lambda: restore_defaults())
        reset_btn.pack(pady=5)

        # Pack the notebook
        notebook.pack(expand=True, fill="both")
        ontop = True


def save_values_to_file():
    with open(f"{exe_path}\\view_id.json", "w") as file:
        json.dump(values, file)


def load_values_from_file():
    try:
        with open(f"{exe_path}\\view_id.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        with open(f"{exe_path}\\view_id.json", "w") as file:
            initial_values = ["Initial View - Name"]
            json.dump(initial_values, file)
            return initial_values


def refresh_combobox():
    combobox['values'] = values


def toggle_print():
    global print_toggle
    global old_amount
    global uncats

    if print_toggle:
        settings_btn.config(state='enabled')
        print_button.config(text="Start", state='disabled')
        print_toggle = False
        combobox.config(state='disabled')
        message_label.config(text=f"Stopped checking {combobox.get()}, last known amount: {old_amount}.")
        root.after(2000, lambda: print_button.config(text="Start", state='enabled'))
        combobox.config(state='readonly')
        uncats = 0
        old_amount = 0
    else:
        uncats = 0
        old_amount = 0
        settings_btn.config(state='disabled')
        print_button.config(text="Stop", state='disabled')
        print_toggle = True
        print_button.config(text="Stop")
        print_selected_value()
        combobox.config(state='disabled')
        root.after(2000, lambda: print_button.config(text="Stop", state='enabled'))


def print_selected_value():
    global old_amount
    global minute_var
    global uncats

    def show_toast(amount):
        if amount < 2:
            toast(f"Zendesk alert", f"{amount} uncat. Click to open view ID in browser.", audio={'silent': 'true'},
                  on_click=f'https://onguard.zendesk.com/agent/filters/{view_id}')
        else:
            toast(f"Zendesk alert", f"{amount} uncats. Click to open view ID in browser.", audio={'silent': 'true'},
                  on_click=f'https://onguard.zendesk.com/agent/filters/{view_id}')

    def run_toast_in_thread():
        thread = threading.Thread(target=lambda: show_toast(len(uncats)))
        thread.start()
        threading.Timer(3, thread.join).start()

    if print_toggle:
        try:
            auth = username_logged_in, password_logged_in
            view_tickets = []
            view_id = combobox.get().split(" - ", 1)[0]
            url = f'https://onguard.zendesk.com/api/v2/views/{view_id}/tickets.json'
            while url:
                response = requests.get(url, auth=auth)
                page_data = response.json()
                tickets = page_data['tickets']  # extract the "tickets" list from the page
                view_tickets.extend(tickets)
                url = page_data['next_page']
                uncats = []

            # Define a row per ticket and append
            for ticket in view_tickets:
                row = (
                    ticket['id'],
                    ticket['subject'],
                    ticket['requester_id'],
                    ticket['assignee_id'],
                    ticket['created_at'],
                    ticket['status'],
                    f'https://support.zendesk.com/agent/tickets/{ticket["id"]}'
                )
                uncats.append(row)

            pygame.mixer.init()
            alarm_sound: str = config['DEFAULT']['alarm_sound']
            sound_notification = pygame.mixer.Sound(alarm_sound)
            sound_notification.set_volume(tick_scale.get())

            if len(uncats) > 0:
                if len(uncats) > old_amount or (len(uncats) == old_amount and always_notify == "1"):
                    if windows_notify == "1":
                        run_toast_in_thread()
                    sound_notification.play()

            old_amount = len(uncats)
        except:
            pass

        message_label.config(text=f"Checking: {len(uncats)} uncategorized tickets for {combobox.get()}.")
        selected_value = int(combobox_time.get()) * 60000
        root.after(selected_value, print_selected_value)


root = tk.Tk()
root.title("Zendesk - Uncat alert")
root.resizable(False, False)
root.withdraw()  # Hide the main window initially

open_login_window()  # Open the login window

values = load_values_from_file()

upper_frame = ttk.Frame(root)
upper_frame.pack(side='top', padx=5, pady=3)

label = ttk.Label(upper_frame, text="View ID:")
label.pack(side='left', padx=10)

combobox = ttk.Combobox(upper_frame, values=values, state="readonly", width=40)
combobox.pack(side='left', padx=(10, 0), ipady=4, ipadx=4)

print_toggle = False
print_button = ttk.Button(upper_frame, text="Start", command=lambda: toggle_print(), style='Accent.TButton', width=5)
print_button.pack(side='left', padx=10, pady=10)

settings_btn = ttk.Button(upper_frame, text="Settings", command=lambda: settings())
settings_btn.pack(side='left', padx=(0, 5))

message_frame = ttk.Frame(root, padding=4, style='Card.TFrame')
message_frame.pack(side='top', padx=10, pady=(0, 7), expand=True, fill='x')

message_label = ttk.Label(message_frame, text="Idle.", justify='center')
message_label.pack(side='top', padx=10, pady=10)

bottom_frame = ttk.Frame(root)
bottom_frame.pack(side='top', padx=10, pady=(4, 11), fill='x')

label3 = ttk.Label(bottom_frame, text="🔈", justify='center')
label3.pack(side='left')

tick_scale = ttk.Scale(bottom_frame)
tick_scale.set(1)
tick_scale.pack(side='left')

label3 = ttk.Label(bottom_frame, text="🔊", justify='center')
label3.pack(side='left')

label3 = ttk.Label(bottom_frame, text="min.", justify='center')
label3.pack(side='right')

minute_var = tk.StringVar()
options = ['5', '10', '15', '20', '25', '30']

combobox_time = ttk.Combobox(bottom_frame, values=options,
                             state="readonly", width=4, textvariable=minute_var)
combobox_time.set(options[0])
combobox_time.pack(side='right', padx=(10, 10))

if values:
    combobox.set(value=values[0])

label3 = ttk.Label(bottom_frame, text="Refresh")
label3.pack(side='right')

ontop = False

sv_ttk.set_theme(theme_current)

root.bind('<Destroy>', lambda e: sys.exit())

ico = Image.open(resource_path("onguardico.png"))
photo = ImageTk.PhotoImage(ico)
root.wm_iconphoto(True, photo)
root.mainloop()
