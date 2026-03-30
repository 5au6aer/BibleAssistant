import os
import sys
import secrets
import string
import customtkinter as ctk
from tkinter import messagebox

# Pfad-Logik für src-Ordner
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from database import BibleDatabase

def get_or_create_master_pass():
    """Liest das Passwort aus data/master_pass.txt oder erstellt ein neues."""
    # Absoluter Pfad zum Hauptverzeichnis des Projekts
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    pass_file = os.path.join(data_dir, "master_pass.txt")
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    if os.path.exists(pass_file):
        with open(pass_file, "r", encoding="utf-8") as f: 
            pw = f.read().strip()
            # Kleiner Debug-Print (kannst du später löschen)
            print(f"DEBUG: Passwort aus {pass_file} geladen.") 
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
    app.title("Bibel Assistent - Sperrbildschirm")
    app.attributes("-fullscreen", True)
    app.attributes("-topmost", True)
    
    # Vers-Anzeige
    v, q = db.get_random_verse()
    ctk.CTkLabel(app, text=f"\"{v}\"", font=("Arial", 28, "italic"), wraplength=1000).pack(pady=(150, 20))
    ctk.CTkLabel(app, text=q, font=("Arial", 18)).pack(pady=(0, 50))
    
    # Eingabe-Container
    f = ctk.CTkFrame(app)
    f.pack(pady=20, padx=20)
    
    books = db.get_books()
    sel_book = ctk.StringVar(value=books[0] if books else "")
    
    # Suchfeld für Bücher
    search = ctk.CTkEntry(f, placeholder_text="Buch suchen...", width=350)
    search.pack(pady=10)
    
    # Scroll-Liste für Bücher
    l_box = ctk.CTkScrollableFrame(f, width=330, height=180)
    l_box.pack()
    
    # Status-Labels (Wiederhergestellt: Gelesen & Offen)
    cur_lbl = ctk.CTkLabel(f, text=f"Ausgewählt: {sel_book.get()}", text_color="#3498db", font=("Arial", 14, "bold"))
    cur_lbl.pack(pady=(10, 2))
    
    read_lbl = ctk.CTkLabel(f, text=f"Bereits gelesen: {', '.join(map(str, db.get_read_chapters_list(sel_book.get()))) or 'Keines'}", text_color="#27ae60", font=("Arial", 11))
    read_lbl.pack()
    
    msg_lbl = ctk.CTkLabel(f, text=f"Noch offen: {db.get_missing_chapters(sel_book.get())}", font=("Arial", 12))
    msg_lbl.pack(pady=(0, 10))

    def update_sel(b): 
        sel_book.set(b)
        cur_lbl.configure(text=f"Ausgewählt: {b}")
        read_list = db.get_read_chapters_list(b)
        read_lbl.configure(text=f"Bereits gelesen: {', '.join(map(str, read_list)) or 'Keines'}")
        msg_lbl.configure(text=f"Noch offen: {db.get_missing_chapters(b)}")

    def filter_b(*args):
        for c in l_box.winfo_children(): c.destroy()
        query = search.get().lower()
        for b in [x for x in books if query in x.lower()]:
            ctk.CTkButton(l_box, text=b, fg_color="transparent", anchor="w", command=lambda x=b: update_sel(x)).pack(fill="x")

    search.bind("<KeyRelease>", filter_b)
    filter_b()

    # Kapitel & Notiz
    kap = ctk.CTkEntry(f, placeholder_text="Kapitel (z.B. 1-5)", width=350)
    kap.pack(pady=10)
    
    note = ctk.CTkTextbox(f, width=450, height=100)
    note.pack(pady=10)

    def save():
        res, m = db.log_reading(sel_book.get(), kap.get(), note.get("1.0", "end-1c"))
        if res: 
            db.confirm_reading()
            app.destroy()
        else: 
            messagebox.showerror("Fehler", m)

    ctk.CTkButton(f, text="Fortschritt speichern & Entsperren", fg_color="#27ae60", width=350, height=45, command=save).pack(pady=10)
    
    btn_text = "Abbrechen" if is_voluntary else "Heute überspringen (Skip einrechnen)"
    ctk.CTkButton(f, text=btn_text, fg_color="#c0392b" if not is_voluntary else "gray", width=350, command=app.destroy).pack()
    
    app.mainloop()

def show_dashboard(db):
    app = ctk.CTk()
    app.title("Bibel Assistent - Dashboard")
    app.geometry("1150x900")
    
    ctk.set_appearance_mode(db.progress["settings"].get("theme", "dark"))
    master_password = get_or_create_master_pass()

    # HEADER
    h = ctk.CTkFrame(app, height=100) # Etwas höher für mehr Präsenz
    h.pack(fill="x", padx=20, pady=10)
    
    stats = db.get_stats()
    ctk.CTkLabel(h, text=f"Aktiver Plan: {db.active_plan}", font=("Arial", 20, "bold")).pack(side="left", padx=20)
    
    # --- PROMINENTER GOLD STATUS ---
    if stats['is_gold']:
        gold_btn = ctk.CTkLabel(
            h, 
            text="  🏆  GOLD STATUS ERREICHT  🏆  ", 
            fg_color="#f1c40f", 
            text_color="#2c3e50", 
            font=("Arial", 20, "bold"),
            corner_radius=10,
            height=50
        )
        gold_btn.pack(side="left", padx=30)
    else:
        ctk.CTkLabel(h, text="🏆 GOLD STATUS", text_color="gray", font=("Arial", 16, "bold")).pack(side="left", padx=30)
    
    ctk.CTkLabel(h, text=f"⚠️ Plan-Skips: {stats['skips']}", text_color="#e74c3c", font=("Arial", 16, "bold")).pack(side="left", padx=20)
    
    # Leseplan-Umschalter
    plan_frame = ctk.CTkFrame(h, fg_color="transparent")
    plan_frame.pack(side="right", padx=10)
    ctk.CTkLabel(plan_frame, text="Leseplan:").pack(side="left", padx=5)
    p_menu = ctk.CTkOptionMenu(plan_frame, values=db.available_plans, command=lambda v: [db.switch_plan(v), app.destroy(), show_dashboard(db)])
    p_menu.set(db.active_plan)
    p_menu.pack(side="left")
    
    # Theme-Switch
    t_sw = ctk.CTkSwitch(h, text="Dark Mode", command=lambda: [ctk.set_appearance_mode("light" if ctk.get_appearance_mode()=="Dark" else "dark"), db.set_theme(ctk.get_appearance_mode().lower())])
    if db.progress["settings"]["theme"] == "dark": t_sw.select()
    t_sw.pack(side="right", padx=10)

# MITTELBEREICH (Scrollable)
    s = ctk.CTkScrollableFrame(app, fg_color="transparent")
    s.pack(fill="both", expand=True, padx=20)
    
    # 1. Die große Gesamtanzeige
    ctk.CTkLabel(s, text=f"{stats['percent']}% Gesamtfortschritt", font=("Arial", 36, "bold"), text_color="#2ecc71").pack(pady=20)
    
    # 2. SEITLICH SCROLLBARER FORTSCHRITT NACH BEREICHEN
    ctk.CTkLabel(s, text="--- FORTSCHRITT NACH BEREICHEN ---", font=("Arial", 18, "bold"), text_color="#f39c12").pack(pady=(20, 5))
    
    # Ein Container, der horizontales Scrollen ermöglicht
    h_scroll = ctk.CTkScrollableFrame(s, height=110, orientation="horizontal", fg_color="transparent")
    h_scroll.pack(fill="x", padx=10, pady=5)

    # Erzeugt Karten für alle 9 (oder mehr) Abschnitte
    for g in stats['groups']:
        # Die Karte selbst
        card = ctk.CTkFrame(h_scroll, width=180, height=80, border_width=1, border_color="#555")
        card.pack(side="left", padx=8, pady=5)
        card.pack_propagate(False)
        
        # Logik für die Farbe (Gold bei 100%)
        p_color = "#27ae60" if g['perc'] == 100 else "#3498db"
        
        ctk.CTkLabel(card, text=g['name'], font=("Arial", 11, "bold"), wraplength=160).pack(pady=(5, 0))
        ctk.CTkLabel(card, text=f"{g['perc']}%", font=("Arial", 16, "bold"), text_color=p_color).pack()
        ctk.CTkLabel(card, text=f"Kap: {g['count']}", font=("Arial", 9), text_color="gray").pack()

    # 3. BÜCHER IN ARBEIT
    ctk.CTkLabel(s, text="--- EINZELNE BÜCHER IN ARBEIT ---", font=("Arial", 18, "bold"), text_color="#3498db").pack(pady=(30, 10))
    for b in stats['started']:
        row = ctk.CTkFrame(s)
        row.pack(fill="x", pady=2, padx=20)
        ctk.CTkLabel(row, text=b['book'], width=150, anchor="w", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(row, text=f"Fortschritt: {b['count']}/{b['max']} Kapitel", font=("Arial", 11)).pack(side="left", padx=10)
        ctk.CTkLabel(row, text=f"Offen: {b['missing']}", font=("Arial", 10, "italic"), text_color="gray").pack(side="left", fill="x", expand=True)
    
    # ABGESCHLOSSEN
    ctk.CTkLabel(s, text="--- ABGESCHLOSSENE BÜCHER ---", font=("Arial", 18, "bold"), text_color="#27ae60").pack(pady=(30, 10))
    comp_txt = ", ".join(stats['completed']) if stats['completed'] else "Noch kein Buch beendet."
    ctk.CTkLabel(s, text=comp_txt, wraplength=1000, font=("Arial", 12, "italic")).pack(padx=40)

    # FOOTER
    f_box = ctk.CTkFrame(app, height=200, border_width=2)
    f_box.pack(fill="x", side="bottom", padx=20, pady=20)
    
    def sec_check(name, func):
        input_pass = ctk.CTkInputDialog(text=f"Master-PW für {name}:").get_input()
        if input_pass == master_password:
            ok, m = func()
            messagebox.showinfo("Info", m)
            app.destroy()
            show_dashboard(db)
        elif input_pass is not None:
            messagebox.showerror("Fehler", "Falsches Passwort!")

    def handle_pdf():
        ok, res = db.export_pdf()
        if ok: os.startfile(res)
        else: messagebox.showerror("Fehler", res)

    # Reihe 1: Aktionen
    r1 = ctk.CTkFrame(f_box, fg_color="transparent")
    r1.pack(pady=10)
    ctk.CTkButton(r1, text="📄 PDF Report", fg_color="#27ae60", width=220, height=45, command=handle_pdf).pack(side="left", padx=15)
    ctk.CTkButton(r1, text="➕ Manuell loggen", fg_color="#3498db", width=220, height=45, command=lambda: [app.destroy(), show_lock_screen(db, True), show_dashboard(db)]).pack(side="left", padx=15)
    ctk.CTkButton(r1, text="❌ Beenden", fg_color="#c0392b", width=220, height=45, command=sys.exit).pack(side="left", padx=15)

    # Reihe 2: Verwaltung
    r2 = ctk.CTkFrame(f_box, fg_color="transparent")
    r2.pack(pady=5)
    ctk.CTkButton(r2, text="📥 Plan importieren", command=lambda: sec_check("Import", db.import_new_plan)).pack(side="left", padx=5)
    ctk.CTkButton(r2, text="🗑️ Plan löschen", fg_color="#34495e", command=lambda: sec_check("Löschen", db.delete_current_plan)).pack(side="left", padx=5)
    ctk.CTkButton(r2, text="🔄 Fortschritt resetten", fg_color="#e67e22", command=lambda: sec_check("Reset", db.reset_current_plan)).pack(side="left", padx=5)
    
    # Reihe 3: Backup
    r3 = ctk.CTkFrame(f_box, fg_color="transparent")
    r3.pack(pady=5)
    ctk.CTkButton(r3, text="💾 Backup exportieren", fg_color="#7f8c8d", width=245, command=db.export_backup).pack(side="left", padx=5)
    ctk.CTkButton(r3, text="📂 Backup importieren", fg_color="#7f8c8d", width=245, command=lambda: [db.import_backup(), app.destroy(), show_dashboard(db)]).pack(side="left", padx=5)

    app.mainloop()

if __name__ == "__main__":
    db = BibleDatabase()
    if not db.has_read_today(): 
        show_lock_screen(db)
    show_dashboard(db)