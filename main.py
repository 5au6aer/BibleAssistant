import os
import sys
import secrets
import string
import customtkinter as ctk
from tkinter import messagebox

# Path logic for src folder
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from database import BibleDatabase

# --- TRANSLATIONS ---
LANG_DICT = {
    "de": {
        "search": "Buch suchen...", "selected": "Ausgewählt", "read": "Bereits gelesen", 
        "rem": "Verbleibend", "chapters": "Kapitel (z.B. 1-5)", "btn_save": "Speichern & Entsperren",
        "btn_skip": "Heute überspringen (zählt als Skip)", "cancel": "Abbrechen", "dashboard": "Dashboard",
        "manual": "Manueller Log", "export": "PDF Report", "quit": "Beenden", "import": "Plan importieren",
        "delete": "Plan löschen", "reset": "Fortschritt zurücksetzen", "theme": "Dunkel-Modus", "lang_btn": "Sprache: DE",
        "sec_prog": "--- FORTSCHRITT NACH ABSCHNITT ---", "books_prog": "--- BÜCHER IN ARBEIT ---",
        "comp_books": "--- ABGESCHLOSSENE BÜCHER ---", "skips": "Plan Skips", "gold": "GOLD STATUS ERREICHT",
        "none": "Keine", "no_comp": "Noch kein Buch abgeschlossen."
    },
    "en": {
        "search": "Search book...", "selected": "Selected", "read": "Already read", 
        "rem": "Remaining", "chapters": "Chapters (e.g. 1-5)", "btn_save": "Save & Unlock",
        "btn_skip": "Skip today (counts as skip)", "cancel": "Cancel", "dashboard": "Dashboard",
        "manual": "Manual Log", "export": "PDF Report", "quit": "Quit", "import": "Import Plan",
        "delete": "Delete Plan", "reset": "Reset Progress", "theme": "Dark Mode", "lang_btn": "Language: EN",
        "sec_prog": "--- PROGRESS BY SECTION ---", "books_prog": "--- BOOKS IN PROGRESS ---",
        "comp_books": "--- COMPLETED BOOKS ---", "skips": "Plan Skips", "gold": "GOLD STATUS ACHIEVED",
        "none": "None", "no_comp": "No book completed yet."
    },
    "no": {
        "search": "Søk bok...", "selected": "Valgt", "read": "Allerede lest", 
        "rem": "Gjenstår", "chapters": "Kapittel (f.eks. 1-5)", "btn_save": "Lagre og lås opp",
        "btn_skip": "Hopp over i dag", "cancel": "Avbryt", "dashboard": "Dashbord",
        "manual": "Manuell logg", "export": "PDF-rapport", "quit": "Avslutt", "import": "Importer plan",
        "delete": "Slett plan", "reset": "Nullstill fremdrift", "theme": "Mørk modus", "lang_btn": "Språk",
        "sec_prog": "--- FREMDRIFT PER SEKSJON ---", "books_prog": "--- BØKER UNDER ARBEID ---",
        "comp_books": "--- FULLFØRTE BØKER ---", "skips": "Planhopp", "gold": "GULLSTATUS OPPNÅDD",
        "none": "Ingen", "no_comp": "Ingen bøker fullført ennå."
    }
}

def get_or_create_master_pass():
    """Reads the password from data/master_pass.txt or generates a new one."""
    # Absolute path to the project root directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    pass_file = os.path.join(data_dir, "master_pass.txt")
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    if os.path.exists(pass_file):
        with open(pass_file, "r", encoding="utf-8") as f: 
            pw = f.read().strip()
            # Small debug print
            print(f"DEBUG: Password loaded from {pass_file}.") 
            return pw
    else:
        alphabet = string.ascii_letters + string.digits
        new_pass = ''.join(secrets.choice(alphabet) for _ in range(12))
        with open(pass_file, "w", encoding="utf-8") as f: 
            f.write(new_pass)
        return new_pass

def show_lock_screen(db, is_voluntary=False):
    db.mark_session_started()
    app = ctk.CTk()
    app.title("Bible Assistant - Lock Screen")
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
    if os.path.exists(icon_path):
        app.after(200, lambda: app.iconbitmap(icon_path))
    app.attributes("-fullscreen", True)
    app.attributes("-topmost", True)
    
    # Load settings
    L = LANG_DICT[db.progress["settings"].get("lang", "de")]
    ctk.set_appearance_mode(db.progress["settings"].get("theme", "dark"))
    
    # Verse display
    v, q = db.get_random_verse()
    ctk.CTkLabel(app, text=f"\"{v}\"", font=("Arial", 28, "italic"), wraplength=1000).pack(pady=(150, 20))
    ctk.CTkLabel(app, text=q, font=("Arial", 18)).pack(pady=(0, 50))
    
    # Input container
    f = ctk.CTkFrame(app)
    f.pack(pady=20, padx=20)
    
    books = db.get_books()
    sel_book = ctk.StringVar(value=books[0] if books else "")
    
    # Search field for books
    search = ctk.CTkEntry(f, placeholder_text=L["search"], width=350)
    search.pack(pady=10)
    
    # Scrollable list for books
    l_box = ctk.CTkScrollableFrame(f, width=330, height=180)
    l_box.pack()
    
    # Status labels (Read & Missing)
    cur_lbl = ctk.CTkLabel(f, text=f"{L['selected']}: {sel_book.get()}", text_color="#3498db", font=("Arial", 14, "bold"))
    cur_lbl.pack(pady=(10, 2))
    
    # Updated to use Range formatting
    read_list = db.get_read_chapters_list(sel_book.get())
    read_lbl = ctk.CTkLabel(f, text=f"{L['read']}: {db.format_ranges(read_list) or L['none']}", text_color="#27ae60", font=("Arial", 11))
    read_lbl.pack()
    
    msg_lbl = ctk.CTkLabel(f, text=f"{L['rem']}: {db.get_missing_chapters(sel_book.get())}", font=("Arial", 12))
    msg_lbl.pack(pady=(0, 10))

    def update_sel(b): 
        sel_book.set(b)
        cur_lbl.configure(text=f"{L['selected']}: {b}")
        r_list = db.get_read_chapters_list(b)
        read_lbl.configure(text=f"{L['read']}: {db.format_ranges(r_list) or L['none']}")
        msg_lbl.configure(text=f"{L['rem']}: {db.get_missing_chapters(b)}")

    def filter_b(*args):
        for c in l_box.winfo_children(): 
            c.destroy()
        
        # Sanitize input: lowercase and ignore spaces/dots for comparison
        query = search.get().lower().replace(" ", "").replace(".", "")
        
        if not query:
            filtered_books = books
        else:
            # Also sanitize book names during comparison (e.g., "1.Mose" -> "1mose")
            filtered_books = [
                b for b in books 
                if query in b.lower().replace(" ", "").replace(".", "")
            ]

        for b in filtered_books:
            ctk.CTkButton(
                l_box, 
                text=b, 
                fg_color="transparent", 
                anchor="w", 
                command=lambda x=b: update_sel(x)
            ).pack(fill="x")

    search.bind("<KeyRelease>", filter_b)
    filter_b()

    # Chapters & Note
    kap = ctk.CTkEntry(f, placeholder_text=L["chapters"], width=350)
    kap.pack(pady=10)
    
    note = ctk.CTkTextbox(f, width=450, height=100)
    note.pack(pady=10)

    def save():
        res, m = db.log_reading(sel_book.get(), kap.get(), note.get("1.0", "end-1c"))
        if res: 
            db.confirm_reading()
            app.destroy()
        else: 
            messagebox.showerror("Error", m)

    ctk.CTkButton(f, text=L["btn_save"], fg_color="#27ae60", width=350, height=45, command=save).pack(pady=10)
    
    btn_text = L["cancel"] if is_voluntary else L["btn_skip"]
    ctk.CTkButton(f, text=btn_text, fg_color="#c0392b" if not is_voluntary else "gray", width=350, command=app.destroy).pack()
    
    app.mainloop()

def show_dashboard(db):
    app = ctk.CTk()
    app.title("Bible Assistant - Dashboard")
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
    if os.path.exists(icon_path):
            app.after(200, lambda: app.iconbitmap(icon_path))
    app.geometry("1150x900")
    
    # Sprache und Theme aus der Datenbank laden
    L = LANG_DICT[db.progress["settings"].get("lang", "de")]
    ctk.set_appearance_mode(db.progress["settings"].get("theme", "dark"))
    master_password = get_or_create_master_pass()

    # --- HEADER ---
    h = ctk.CTkFrame(app, height=100)
    h.pack(fill="x", padx=20, pady=10)
    
    stats = db.get_stats()
    
    # Linke Seite: Plan Info & Gold Status
    ctk.CTkLabel(h, text=f"Plan: {db.active_plan}", font=("Arial", 20, "bold")).pack(side="left", padx=20)
    
    if stats['is_gold']:
        ctk.CTkLabel(h, text=f"   🏆   {L['gold']}   🏆   ", fg_color="#f1c40f", text_color="#2c3e50", font=("Arial", 20, "bold"), corner_radius=10, height=50).pack(side="left", padx=30)
    
    ctk.CTkLabel(h, text=f"⚠️ {L['skips']}: {stats['skips']}", text_color="#e74c3c", font=("Arial", 16, "bold")).pack(side="left", padx=20)
    
    # Rechte Seite: Steuerung (Sprache, Plan, Theme)
    
    # 1. Sprach-Dropdown
    def change_lang(new_lang_name):
        mapping = {"Deutsch": "de", "English": "en", "Norsk": "no"}
        db.set_lang(mapping[new_lang_name])
        app.destroy()
        show_dashboard(db)

    lang_frame = ctk.CTkFrame(h, fg_color="transparent")
    lang_frame.pack(side="right", padx=10)
    ctk.CTkLabel(lang_frame, text=f"{L['lang_btn']}:").pack(side="left", padx=5)
    
    lang_options = ["Deutsch", "English", "Norsk"]
    current_lang_code = db.progress["settings"].get("lang", "de")
    rev_mapping = {"de": "Deutsch", "en": "English", "no": "Norsk"}
    
    l_menu = ctk.CTkOptionMenu(lang_frame, values=lang_options, command=change_lang, width=120)
    l_menu.set(rev_mapping.get(current_lang_code, "Deutsch"))
    l_menu.pack(side="left")

    # 2. Plan-Auswahl
    plan_frame = ctk.CTkFrame(h, fg_color="transparent")
    plan_frame.pack(side="right", padx=10)
    ctk.CTkLabel(plan_frame, text="Plan:").pack(side="left", padx=5)
    p_menu = ctk.CTkOptionMenu(plan_frame, values=db.available_plans, command=lambda v: [db.switch_plan(v), app.destroy(), show_dashboard(db)])
    p_menu.set(db.active_plan)
    p_menu.pack(side="left")
    
    # 3. Theme Switch
    t_sw = ctk.CTkSwitch(h, text=L["theme"], command=lambda: [ctk.set_appearance_mode("light" if ctk.get_appearance_mode()=="Dark" else "dark"), db.set_theme(ctk.get_appearance_mode().lower())])
    if db.progress["settings"]["theme"] == "dark": t_sw.select()
    t_sw.pack(side="right", padx=10)

    # --- MITTELTEIL (Scrollbar) ---
    s = ctk.CTkScrollableFrame(app, fg_color="transparent")
    s.pack(fill="both", expand=True, padx=20)
    
    ctk.CTkLabel(s, text=f"{stats['percent']}% Total Progress", font=("Arial", 36, "bold"), text_color="#2ecc71").pack(pady=20)
    
    ctk.CTkLabel(s, text=db.plan_info, font=("Arial", 14, "italic"), text_color="gray", wraplength=800, justify="center").pack(pady=(0, 20))

    # Fortschritt nach Abschnitten (Horizontal)
    ctk.CTkLabel(s, text=L["sec_prog"], font=("Arial", 18, "bold"), text_color="#f39c12").pack(pady=(20, 5))
    h_scroll = ctk.CTkScrollableFrame(s, height=110, orientation="horizontal", fg_color="transparent")
    h_scroll.pack(fill="x", padx=10, pady=5)

    for g in stats['groups']:
        card = ctk.CTkFrame(h_scroll, width=180, height=80, border_width=1, border_color="#555")
        card.pack(side="left", padx=8, pady=5)
        card.pack_propagate(False)
        p_color = "#27ae60" if g['perc'] == 100 else "#3498db"
        ctk.CTkLabel(card, text=g['name'], font=("Arial", 11, "bold"), wraplength=160).pack(pady=(5, 0))
        ctk.CTkLabel(card, text=f"{g['perc']}%", font=("Arial", 16, "bold"), text_color=p_color).pack()
        ctk.CTkLabel(card, text=f"Ch: {g['count']}", font=("Arial", 9), text_color="gray").pack()

    # Bücher in Arbeit
    ctk.CTkLabel(s, text=L["books_prog"], font=("Arial", 18, "bold"), text_color="#3498db").pack(pady=(30, 10))
    for b in stats['started']:
        row = ctk.CTkFrame(s)
        row.pack(fill="x", pady=2, padx=20)
        ctk.CTkLabel(row, text=b['book'], width=150, anchor="w", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(row, text=f"Progress: {b['count']}/{b['max']} Chapters", font=("Arial", 11)).pack(side="left", padx=10)
        ctk.CTkLabel(row, text=f"Missing: {b['missing']}", font=("Arial", 10, "italic"), text_color="gray").pack(side="left", fill="x", expand=True)
    
    # Abgeschlossene Bücher
    ctk.CTkLabel(s, text=L["comp_books"], font=("Arial", 18, "bold"), text_color="#27ae60").pack(pady=(30, 10))
    comp_txt = ", ".join(stats['completed']) if stats['completed'] else L["no_comp"]
    ctk.CTkLabel(s, text=comp_txt, wraplength=1000, font=("Arial", 12, "italic")).pack(padx=40)

    # --- FOOTER (Aktionen) ---
    f_box = ctk.CTkFrame(app, height=200, border_width=2)
    f_box.pack(fill="x", side="bottom", padx=20, pady=20)
    
    def sec_check(name, func):
        input_pass = ctk.CTkInputDialog(text=f"Master-PW for {name}:").get_input()
        if input_pass == master_password:
            ok, m = func()
            messagebox.showinfo("Info", m)
            app.destroy()
            show_dashboard(db)
        elif input_pass is not None:
            messagebox.showerror("Error", "Incorrect password!")

    def handle_pdf():
        ok, res = db.export_pdf()
        if ok: os.startfile(res)
        else: messagebox.showerror("Error", res)

    # Zeile 1: Haupt-Buttons
    r1 = ctk.CTkFrame(f_box, fg_color="transparent")
    r1.pack(pady=10)
    ctk.CTkButton(r1, text=f"📄 {L['export']}", fg_color="#27ae60", width=220, height=45, command=handle_pdf).pack(side="left", padx=15)
    ctk.CTkButton(r1, text=f"➕ {L['manual']}", fg_color="#3498db", width=220, height=45, command=lambda: [app.destroy(), show_lock_screen(db, True), show_dashboard(db)]).pack(side="left", padx=15)
    ctk.CTkButton(r1, text=f"❌ {L['quit']}", fg_color="#c0392b", width=220, height=45, command=sys.exit).pack(side="left", padx=15)

    # Zeile 2: Management
    r2 = ctk.CTkFrame(f_box, fg_color="transparent")
    r2.pack(pady=5)
    ctk.CTkButton(r2, text=f"📥 {L['import']}", command=lambda: sec_check("Import", db.import_new_plan)).pack(side="left", padx=5)
    ctk.CTkButton(r2, text=f"🗑️ {L['delete']}", fg_color="#34495e", command=lambda: sec_check("Delete", db.delete_current_plan)).pack(side="left", padx=5)
    ctk.CTkButton(r2, text=f"🔄 {L['reset']}", fg_color="#e67e22", command=lambda: sec_check("Reset", db.reset_current_plan)).pack(side="left", padx=5)
    
    # Zeile 3: Backup
    r3 = ctk.CTkFrame(f_box, fg_color="transparent")
    r3.pack(pady=5)
    ctk.CTkButton(r3, text="💾 Export Backup", fg_color="#7f8c8d", width=245, command=db.export_backup).pack(side="left", padx=5)
    ctk.CTkButton(r3, text="📂 Import Backup", fg_color="#7f8c8d", width=245, command=lambda: [db.import_backup(), app.destroy(), show_dashboard(db)]).pack(side="left", padx=5)

    app.mainloop()

if __name__ == "__main__":
    db = BibleDatabase()
    if not db.has_read_today(): 
        show_lock_screen(db)
    show_dashboard(db)