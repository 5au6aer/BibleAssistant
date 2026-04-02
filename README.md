# Bible Assistant v1.4

An intelligent reading plan manager and lock-screen reminder to keep your spiritual goals on track.

## New in v1.4
- **Multi-Plan Support:** Import and switch between different reading plans.
- **Enhanced PDF Export:** Professional reports with biblical sorting.
- **Smart Filtering:** Quick-search books in the lock screen (ignores case/dots).
- **Security:** Master password protection for administrative actions (Reset/Delete/Import).
- **Session Tracking:** Automatic "Skip" detection if a session is started but not completed.

## Project Structure
- `main.py`: The entry point and UI dashboard.
- `src/database.py`: Core logic, statistics, and data management.
- `data/`: Contains progress, plans, and the master password.
- `exports/`: Destination for PDF reports and backups.

## Setup & Usage
1. Install requirements: `pip install customtkinter fpdf`
2. Run `python main.py`.
3. If you haven't read today, the lock screen will appear.
4. Use the Dashboard to track progress or export your data.

*Note: Your master password is automatically generated in `data/master_pass.txt`.*

## System Requirements
- Python 3.x
- Operating System: Windows (tested), Linux/macOS (compatible)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.