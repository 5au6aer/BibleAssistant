import os
import json
import shutil
from datetime import date
import random
from tkinter import filedialog

class BibleDatabase:
    def __init__(self):
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        self.main_dir = os.path.abspath(os.path.join(self.base_dir, '..'))
        self.progress_path = os.path.join(self.base_dir, 'progress.json')
        
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
            
        self.load_progress()
        self.available_plans = self._discover_plans()
        
        self.active_plan = self.progress.get("settings", {}).get("active_plan", "Standard")
        if self.active_plan not in self.available_plans:
            self.active_plan = self.available_plans[0] if self.available_plans else "Standard"
            
        self.load_structure(self.active_plan)
        self._check_for_skips()

    def _discover_plans(self):
        plans = []
        if os.path.exists(self.base_dir):
            for file in os.listdir(self.base_dir):
                if file.endswith("_structure.json"):
                    plans.append(file.replace("_structure.json", ""))
        return sorted(plans) if plans else ["Standard"]

    def load_progress(self):
        if os.path.exists(self.progress_path):
            try:
                with open(self.progress_path, 'r', encoding='utf-8') as f:
                    self.progress = json.load(f)
            except: self._create_empty_progress()
        else: self._create_empty_progress()
        
        if "settings" not in self.progress:
            self.progress["settings"] = {"active_plan": "Standard", "theme": "dark"}
        if "plans" not in self.progress:
            self.progress["plans"] = {}

    def _create_empty_progress(self):
        self.progress = {"settings": {"active_plan": "Standard", "theme": "dark"}, "plans": {}}
        self.save_progress()

    def load_structure(self, plan_name):
        self.active_plan = plan_name
        self.progress["settings"]["active_plan"] = plan_name
        path = os.path.join(self.base_dir, f"{plan_name}_structure.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                self.bible_structure = json.load(f)
        else:
            self.bible_structure = {"Basis": {"Info": 1}}
        
        if plan_name not in self.progress["plans"]:
            self.progress["plans"][plan_name] = {
                "chapters_read": [], "reading_log": [], "skips": 0, "pending_session_date": None
            }
        self.save_progress()

    def switch_plan(self, new_plan):
        if new_plan in self.available_plans:
            self.load_structure(new_plan)
            return True
        return False

    def save_progress(self):
        with open(self.progress_path, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=4, ensure_ascii=False)

    def set_theme(self, mode):
        self.progress["settings"]["theme"] = mode
        self.save_progress()

    def get_books(self):
        all_books = []
        for group in self.bible_structure.values():
            all_books.extend(group.keys())
        return all_books

    def get_max_chapters(self, book):
        for group in self.bible_structure.values():
            if book in group: return group[book]
        return 0

    def get_read_chapters_list(self, book):
        plan = self.progress["plans"].get(self.active_plan, {})
        return sorted(list(set([c['chapter'] for c in plan.get("chapters_read", []) if c['book'] == book])))

    def get_missing_chapters(self, book):
        total = self.get_max_chapters(book)
        read = self.get_read_chapters_list(book)
        missing = [ch for ch in range(1, total + 1) if ch not in read]
        
        if len(read) == 0: return f"1-{total} (Gesamt: {total})"
        if not missing: return f"Vollständig ({total}/{total})"
        
        ranges = []; start = missing[0]
        for i in range(1, len(missing) + 1):
            if i < len(missing) and missing[i] == missing[i-1] + 1: continue
            else:
                end = missing[i-1]
                ranges.append(str(start) if start == end else f"{start}-{end}")
                if i < len(missing): start = missing[i]
        return f"{', '.join(ranges)} (Noch {len(missing)} von {total})"

    def log_reading(self, book, range_str, note):
        try:
            range_str = range_str.replace(" ", "")
            if "-" in range_str:
                parts = range_str.split("-"); start, end = int(parts[0]), int(parts[1])
            else: start = end = int(range_str)
            max_c = self.get_max_chapters(book)
            if start > max_c or end > max_c or start < 1: return False, f"Fehler: Max {max_c} Kap."
            plan = self.progress["plans"][self.active_plan]
            for ch in range(min(start, end), max(start, end) + 1):
                if not any(e['book'] == book and e['chapter'] == ch for e in plan["chapters_read"]):
                    plan["chapters_read"].append({"book": book, "chapter": ch, "date": date.today().isoformat()})
            plan["reading_log"].append({"book": book, "display": f"{book} {range_str}", "date": date.today().isoformat(), "note": note})
            self.save_progress()
            return True, "Gespeichert!"
        except: return False, "Formatfehler!"

    def get_stats(self):
        plan_data = self.progress["plans"][self.active_plan]
        read_ch = plan_data.get("chapters_read", [])
        total_ch = 0
        total_read = 0
        group_details = []
        
        # 1. Gruppen-Fortschritt berechnen (AT/NT etc.)
        for group_name, books in self.bible_structure.items():
            g_total = sum(books.values())
            g_read = len([c for c in read_ch if c['book'] in books])
            total_ch += g_total
            total_read += g_read
            
            perc = round((g_read / g_total * 100), 1) if g_total > 0 else 0
            group_details.append({
                "name": group_name,
                "perc": perc,
                "count": f"{g_read}/{g_total}"
            })

        # 2. Status der einzelnen Bücher ermitteln
        started = []
        completed = []
        for book in self.get_books():
            count = len(self.get_read_chapters_list(book))
            max_c = self.get_max_chapters(book)
            if count >= max_c:
                completed.append(book)
            elif count > 0:
                started.append({
                    "book": book, 
                    "count": count, 
                    "max": max_c, 
                    "missing": self.get_missing_chapters(book)
                })

        # 3. Gesamt-Prozent und Gold-Status
        perc_overall = round((total_read / total_ch * 100), 1) if total_ch > 0 else 0
        
        return {
            "percent": perc_overall,
            "groups": group_details,
            "started": started,
            "completed": completed,
            "skips": plan_data.get("skips", 0),
            "is_gold": (perc_overall >= 100.0)
        }

    def _check_for_skips(self):
        today = date.today().isoformat()
        plan = self.progress["plans"][self.active_plan]
        last = plan.get("pending_session_date")
        if last and last != today:
            plan["skips"] = plan.get("skips", 0) + 1
            plan["pending_session_date"] = None
            self.save_progress()

    def mark_session_started(self):
        self.progress["plans"][self.active_plan]["pending_session_date"] = date.today().isoformat()
        self.save_progress()

    def confirm_reading(self):
        self.progress["plans"][self.active_plan]["pending_session_date"] = None
        self.save_progress()

    def reset_current_plan(self):
        self.progress["plans"][self.active_plan] = {"chapters_read": [], "reading_log": [], "skips": 0, "pending_session_date": None}
        self.save_progress(); return True, "Plan zurückgesetzt."

    def delete_current_plan(self):
        if self.active_plan == "Standard": return False, "Nicht möglich."
        path = os.path.join(self.base_dir, f"{self.active_plan}_structure.json")
        if os.path.exists(path): os.remove(path)
        del self.progress["plans"][self.active_plan]
        self.available_plans = self._discover_plans(); self.load_structure(self.available_plans[0])
        return True, "Plan gelöscht."

    def export_backup(self):
        from datetime import datetime
        
        # 1. Export-Ordner vorbereiten
        export_dir = os.path.join(self.main_dir, "exports")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            
        # 2. Standard-Dateiname generieren (z.B. Backup_2026-03-30.json)
        timestamp = datetime.now().strftime("%Y-%m-%d")
        default_name = f"Backup_{timestamp}.json"
        
        # 3. Dialog mit Startpfad öffnen
        path = filedialog.asksaveasfilename(
            initialdir=export_dir,
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")]
        )
        
        if path: 
            shutil.copy2(self.progress_path, path)
            return True, path
        return False, ""

    def import_backup(self):
        export_dir = os.path.join(self.main_dir, "exports")
        path = filedialog.askopenfilename(initialdir=export_dir)
        if path: 
            shutil.copy2(path, self.progress_path)
            self.load_progress()
            return True, path
        return False, ""

    def import_new_plan(self):
        path = filedialog.askopenfilename()
        if path:
            name = os.path.basename(path).replace("_structure.json", "").replace(".json", "")
            shutil.copy2(path, os.path.join(self.base_dir, f"{name}_structure.json"))
            self.available_plans = self._discover_plans(); return True, name
        return False, ""

    def has_read_today(self):
        today = date.today().isoformat()
        plan = self.progress["plans"].get(self.active_plan, {})
        return any(e['date'] == today for e in plan.get("reading_log", []))

    def get_random_verse(self):
        return random.choice([
            ("Dein Wort ist meines Fußes Leuchte und ein Licht auf meinem Wege.", "Psalm 119,105"),
            ("Selig sind, die Gottes Wort hören und bewahren.", "Lukas 11,28"),
            ("Denn das Wort Gottes ist lebendig und kräftig und schärfer als jedes zweischneidige Schwert.", "Hebräer 4,12"),
            ("Himmel und Erde werden vergehen; aber meine Worte werden nicht vergehen.", "Matthäus 24,35")
        ])

    def export_pdf(self):
        try:
            from fpdf import FPDF
            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            stats = self.get_stats(); plan_data = self.progress["plans"][self.active_plan]
            raw_log = plan_data.get("reading_log", []); book_order = self.get_books()

            def sort_key(entry):
                b_idx = book_order.index(entry['book']) if entry['book'] in book_order else 999
                try:
                    num_part = entry['display'].replace(entry['book'], "").strip()
                    start_ch = int(num_part.split("-")[0]) if "-" in num_part else int(num_part)
                    end_ch = int(num_part.split("-")[1]) if "-" in num_part else start_ch
                except: start_ch = end_ch = 0
                return (b_idx, start_ch, end_ch)

            sorted_log = sorted(raw_log, key=sort_key)
            pdf.set_font("helvetica", "B", 20)
            pdf.cell(0, 15, f"Lese-Protokoll: {self.active_plan}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
            pdf.set_font("helvetica", "B", 10)
            status_text = f"Fortschritt: {stats['percent']}% | Skips: {stats['skips']}"
            if stats.get('is_gold'): status_text += " | STATUS: 100% GOLD"
            pdf.cell(0, 8, status_text.encode('latin-1', 'replace').decode('latin-1'), ln=True)
            pdf.line(10, 35, 200, 35); pdf.ln(10)

            current_book = None
            if not sorted_log:
                pdf.cell(0, 10, "Keine Einträge.", ln=True)
            else:
                for entry in sorted_log:
                    if entry['book'] != current_book:
                        current_book = entry['book']; pdf.ln(5)
                        pdf.set_font("helvetica", "B", 14); pdf.set_text_color(52, 152, 219)
                        pdf.cell(0, 10, current_book.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                        pdf.set_text_color(0, 0, 0); pdf.line(10, pdf.get_y(), 60, pdf.get_y()); pdf.ln(2)
                    pdf.set_font("helvetica", "", 10)
                    full_text = f"[{entry['date']}] {entry['display']}: {entry['note']}"
                    pdf.multi_cell(190, 6, full_text.encode('latin-1', 'replace').decode('latin-1'))
                    pdf.ln(1)
            
            # --- NEUE PFAD-LOGIK START ---
            export_dir = os.path.join(self.main_dir, "exports")
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
                
            path = os.path.join(export_dir, f"Report_{self.active_plan}.pdf")
            pdf.output(path)
            return True, path
            # --- NEUE PFAD-LOGIK ENDE ---
            
        except Exception as e: return False, str(e)