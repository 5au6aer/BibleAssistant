# Bible Assistant

An intelligent companion for reading discipline and progress documentation.

Bible Assistant is a functional proof-of-concept (PoC) designed to explore how software can actively support the formation of consistent reading habits. It combines psychological incentives (desktop lock-screen) with data evaluation (PDF reporting).

![Dashboard](docs/Dashboard3.png)

---

## Core Features

### Intelligent Desktop Gatekeeper (Discipline Mode)
Bible Assistant acts as a purposeful entry point to your digital workday.
- Lock-screen Principle: Upon system startup, a full-screen reminder displays a scripture verse and your current reading goal.
- Focus Protection: Access to the desktop is only granted after confirming the daily reading or making a conscious decision to skip.
- Smart Search: High-speed book entry using fault-tolerant filtering logic (ignores case, dots, and special characters).

![Lock Screen](docs/LockScreen.png)

### Professional Reporting & Documentation
Data is valuable, but presentation makes it meaningful.
- PDF Export Engine: Generates print-ready reports covering your entire reading progress.
- Biblical Sorting: Regardless of the chronological reading date, entries are logically sorted from Genesis to Revelation in the final report.
- Integrated Journaling: Capture and export personal notes alongside your completed chapters.

![PDF Report](docs/ReadingLog.png)

### Flexible Multi-Plan Management
The system adapts to the user's individual journey, not the other way around.
- Multi-Plan Support: Seamlessly import and switch between various thematic or chronological plans.
- Custom Structures: Easy integration of personalized reading paths via standardized JSON files.

### Security & Data Integrity
- Master Password: Administrative actions (resetting data, deleting progress, or importing new plans) are protected by an auto-generated master password.
- Session Tracking: Automatically detects interrupted sessions and offers to resume them upon the next startup.

![Master Password](docs/MasterPasswordRequest.png)

---

### Other
- Display if the Reading-Plan is completed:

![Completed](docs/Dashboard100.png)

- Choose other/custom Reading-Plans:

![Select other Plan](docs/OtherPlans.png)

- Create your own Reading-Plans:

![Create Custom Plan](docs/CustomPlan.png)

## Project Structure
- main.py: Central dashboard and UI controller.
- src/database.py: Core logic, statistics, and data processing engine.
- data/: Secure storage for progress, plan structures, and passwords.
- exports/: Destination folder for generated PDF reports and system backups.

---

## Installation & Setup
1. Install dependencies:
   pip install customtkinter fpdf

2. Run the application:
   python main.py

3. First Run: Your unique master password will be automatically generated in data/master_pass.txt.

---

## System Requirements
- Python 3.x
- Operating System: Windows (tested), Linux/macOS (compatible)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.