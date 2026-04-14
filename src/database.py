import os
import json
import shutil
from datetime import date
import random
from tkinter import filedialog

class BibleDatabase:
    def __init__(self):
        # Initialize directory paths
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        self.main_dir = os.path.abspath(os.path.join(self.base_dir, '..'))
        self.progress_path = os.path.join(self.base_dir, 'progress.json')
        
        # Initialize plan info variable
        self.plan_info = ""

        # Create data directory if it doesn't exist
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
            
        self.load_progress()
        self.available_plans = self._discover_plans()
        
        # Determine the active plan from settings
        self.active_plan = self.progress.get("settings", {}).get("active_plan", "Standard")
        if self.active_plan not in self.available_plans:
            self.active_plan = self.available_plans[0] if self.available_plans else "Standard"
            
        self.load_structure(self.active_plan)
        self._check_for_skips()

    def _discover_plans(self):
        """Scans the data directory for all available plan structure files."""
        plans = []
        if os.path.exists(self.base_dir):
            for file in os.listdir(self.base_dir):
                if file.endswith("_structure.json"):
                    plans.append(file.replace("_structure.json", ""))
        return sorted(plans) if plans else ["Standard"]

    def load_progress(self):
        """Loads progress from JSON or initializes a new one if file is missing/corrupt."""
        if os.path.exists(self.progress_path):
            try:
                with open(self.progress_path, 'r', encoding='utf-8') as f:
                    self.progress = json.load(f)
            except: 
                self._create_empty_progress()
        else: 
            self._create_empty_progress()
        
        # Safety Check: Ensure essential keys exist (crucial for legacy files)
        if "settings" not in self.progress:
            self.progress["settings"] = {"active_plan": "Standard", "theme": "dark", "lang": "de"}
        
        if "lang" not in self.progress["settings"]:
            self.progress["settings"]["lang"] = "de"
            
        if "plans" not in self.progress:
            self.progress["plans"] = {}

    def _create_empty_progress(self):
        """Initializes a fresh progress dictionary."""
        self.progress = {"settings": {"active_plan": "Standard", "theme": "dark", "lang": "de"}, "plans": {}}
        self.save_progress()

    def load_structure(self, plan_name):
        """Loads the Bible structure and metadata for the selected plan."""
        self.active_plan = plan_name
        self.progress["settings"]["active_plan"] = plan_name
        path = os.path.join(self.base_dir, f"{plan_name}_structure.json")
        
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Check for new format with "info" and "structure" keys
                if isinstance(data, dict) and "structure" in data:
                    self.bible_structure = data["structure"]
                    self.plan_info = data.get("info", "No info available.")
                else:
                    # Legacy format: entire file is the structure
                    self.bible_structure = data
                    self.plan_info = "Standard Reading Plan"
        else:
            self.bible_structure = {"Basis": {"Info": 1}}
            self.plan_info = "Plan not found."
        
        # Ensure the plan entry exists in progress storage
        if plan_name not in self.progress["plans"]:
            self.progress["plans"][plan_name] = {
                "chapters_read": [], 
                "reading_log": [], 
                "skips": 0, 
                "pending_session_date": None
            }
        self.save_progress()

    def switch_plan(self, new_plan):
        """Switches the active reading plan."""
        if new_plan in self.available_plans:
            self.load_structure(new_plan)
            return True
        return False

    def save_progress(self):
        """Writes current progress to the JSON file."""
        with open(self.progress_path, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=4, ensure_ascii=False)

    def set_theme(self, mode):
        """Updates the theme setting (light/dark)."""
        self.progress["settings"]["theme"] = mode
        self.save_progress()

    def set_lang(self, lang_code):
        """Updates the language setting (de/en)."""
        self.progress["settings"]["lang"] = lang_code
        self.save_progress()

    def get_books(self):
        """Returns a flat list of all book names in the current structure."""
        all_books = []
        for group in self.bible_structure.values():
            all_books.extend(group.keys())
        return all_books

    def get_max_chapters(self, book):
        """Returns the total chapter count for a given book."""
        for group in self.bible_structure.values():
            if book in group: return group[book]
        return 0

    def get_read_chapters_list(self, book):
        """Returns a sorted list of unique chapter numbers read for a book."""
        plan = self.progress["plans"].get(self.active_plan, {})
        return sorted(list(set([c['chapter'] for c in plan.get("chapters_read", []) if c['book'] == book])))

    def format_ranges(self, chapter_list):
        """Helper to group consecutive numbers into ranges (e.g., 1-5, 7)."""
        if not chapter_list: return ""
        nums = sorted(list(set(int(c) for c in chapter_list)))
        ranges = []
        if not nums: return ""
        start = nums[0]
        for i in range(1, len(nums) + 1):
            if i < len(nums) and nums[i] == nums[i-1] + 1: continue
            else:
                end = nums[i-1]
                ranges.append(str(start) if start == end else f"{start}-{end}")
                if i < len(nums): start = nums[i]
        return ", ".join(ranges)

    def get_missing_chapters(self, book):
        """Generates a string representing unread chapters and ranges."""
        total = self.get_max_chapters(book)
        read = self.get_read_chapters_list(book)
        missing = [ch for ch in range(1, total + 1) if ch not in read]
        
        if len(read) == 0: return f"1-{total} (Total: {total})"
        if not missing: return f"Completed ({total}/{total})"
        
        return f"{self.format_ranges(missing)} ({len(missing)} of {total} left)"

    def log_reading(self, book, range_str, note):
        """Validates and records a new reading session."""
        try:
            range_str = range_str.replace(" ", "")
            if "-" in range_str:
                parts = range_str.split("-"); start, end = int(parts[0]), int(parts[1])
            else: start = end = int(range_str)
            max_c = self.get_max_chapters(book)
            if start > max_c or end > max_c or start < 1: return False, f"Error: Max {max_c} chapters."
            plan = self.progress["plans"][self.active_plan]
            for ch in range(min(start, end), max(start, end) + 1):
                if not any(e['book'] == book and e['chapter'] == ch for e in plan["chapters_read"]):
                    plan["chapters_read"].append({"book": book, "chapter": ch, "date": date.today().isoformat()})
            plan["reading_log"].append({"book": book, "display": f"{book} {range_str}", "date": date.today().isoformat(), "note": note})
            self.save_progress()
            return True, "Saved!"
        except: return False, "Format Error!"

    def get_stats(self):
        """Calculates detailed progress statistics for the UI."""
        plan_data = self.progress["plans"][self.active_plan]
        read_ch = plan_data.get("chapters_read", [])
        total_ch = 0
        total_read = 0
        group_details = []
        
        # 1. Calculate group progress (OT/NT etc.)
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

        # 2. Determine status of individual books
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

        # 3. Final percentage and Gold Status
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
        """Checks if a previously started session was abandoned (tracking skips)."""
        today = date.today().isoformat()
        plan = self.progress["plans"][self.active_plan]
        last = plan.get("pending_session_date")
        if last and last != today:
            plan["skips"] = plan.get("skips", 0) + 1
            plan["pending_session_date"] = None
            self.save_progress()

    def mark_session_started(self):
        """Records the current date to track session activity."""
        self.progress["plans"][self.active_plan]["pending_session_date"] = date.today().isoformat()
        self.save_progress()

    def confirm_reading(self):
        """Clears pending session status upon successful log."""
        self.progress["plans"][self.active_plan]["pending_session_date"] = None
        self.save_progress()

    def reset_current_plan(self):
        """Clears all progress data for the active plan."""
        self.progress["plans"][self.active_plan] = {"chapters_read": [], "reading_log": [], "skips": 0, "pending_session_date": None}
        self.save_progress(); return True, "Plan reset."

    def delete_current_plan(self):
        """Deletes plan structure and progress (prevents deleting Standard plan)."""
        if self.active_plan == "Standard": return False, "Not possible."
        path = os.path.join(self.base_dir, f"{self.active_plan}_structure.json")
        if os.path.exists(path): os.remove(path)
        del self.progress["plans"][self.active_plan]
        self.available_plans = self._discover_plans(); self.load_structure(self.available_plans[0])
        return True, "Plan deleted."

    def export_backup(self):
        """Exports a copy of the progress file via file dialog."""
        from datetime import datetime
        export_dir = os.path.join(self.main_dir, "exports")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            
        timestamp = datetime.now().strftime("%Y-%m-%d")
        default_name = f"Backup_{timestamp}.json"
        
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
        """Overwrites current progress with a selected backup file."""
        export_dir = os.path.join(self.main_dir, "exports")
        path = filedialog.askopenfilename(initialdir=export_dir)
        if path: 
            shutil.copy2(path, self.progress_path)
            self.load_progress()
            return True, path
        return False, ""

    def import_new_plan(self):
        """Imports a new structure JSON file into the application."""
        path = filedialog.askopenfilename()
        if path:
            name = os.path.basename(path).replace("_structure.json", "").replace(".json", "")
            shutil.copy2(path, os.path.join(self.base_dir, f"{name}_structure.json"))
            self.available_plans = self._discover_plans(); return True, name
        return False, ""

    def has_read_today(self):
        """Checks if a log entry exists for today's date."""
        today = date.today().isoformat()
        plan = self.progress["plans"].get(self.active_plan, {})
        return any(e['date'] == today for e in plan.get("reading_log", []))

    def get_random_verse(self):
        """Returns a random encouraging Bible verse (translated for report/UI)."""
        return random.choice([
            ("Your word is a lamp to my feet and a light to my path.", "Psalm 119:105"),
            ("Blessed are those who hear the word of God and keep it.", "Luke 11:28"),
            ("For the word of God is living and active...", "Hebrews 4:12"),
            ("Heaven and earth will pass away, but my words will not pass away.", "Matthew 24:35")
        ])

    def export_pdf(self):
        """Generates a PDF report of the reading history with formatting fixes."""
        try:
            from fpdf import FPDF
            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            stats = self.get_stats(); plan_data = self.progress["plans"][self.active_plan]
            raw_log = plan_data.get("reading_log", []); book_order = self.get_books()

            # Helper for sorting log entries by biblical order and chapter numbers
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
            pdf.cell(0, 15, f"Reading Log: {self.active_plan}".encode('latin-1', 'replace').decode('latin-1'), ln=True)
            pdf.set_font("helvetica", "B", 10)
            status_text = f"Progress: {stats['percent']}% | Skips: {stats['skips']}"
            if stats.get('is_gold'): status_text += " | STATUS: 100% GOLD"
            pdf.cell(0, 8, status_text.encode('latin-1', 'replace').decode('latin-1'), ln=True)
            pdf.line(10, 35, 200, 35); pdf.ln(10)

            current_book = None
            if not sorted_log:
                pdf.cell(0, 10, "No entries found.", ln=True)
            else:
                for entry in sorted_log:
                    if entry['book'] != current_book:
                        current_book = entry['book']; pdf.ln(5)
                        pdf.set_font("helvetica", "B", 14); pdf.set_text_color(52, 152, 219)
                        pdf.cell(0, 10, current_book.encode('latin-1', 'replace').decode('latin-1'), ln=True)
                        pdf.set_text_color(0, 0, 0); pdf.line(10, pdf.get_y(), 60, pdf.get_y()); pdf.ln(2)
                    
                    pdf.set_font("helvetica", "", 10)
                    full_text = f"[{entry['date']}] {entry['display']}: {entry['note']}"
                    # Replacing special dashes with standard hyphen to avoid PDF encoding issues (?)
                    full_text = full_text.replace("–", "-").replace("—", "-") 
                    pdf.multi_cell(190, 6, full_text.encode('latin-1', 'replace').decode('latin-1'))
                    pdf.ln(1)
            
            # Export logic with directory check
            export_dir = os.path.join(self.main_dir, "exports")
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
                
            path = os.path.join(export_dir, f"Report_{self.active_plan}.pdf")
            pdf.output(path)
            return True, path
            
        except Exception as e: return False, str(e)