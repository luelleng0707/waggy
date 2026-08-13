# PETCAREPRO_STARTUP_ANALYSIS

Project:
`C:\Users\Admin\Downloads\waggy\CSTC_1524\Downloads\Chăm sóc thú cưng\PetCarePro`

Application type:
`PySide6` native desktop application (`QApplication`, `QWidget` login, `QMainWindow` shell)

Entrypoint:
`app.py` (`main()` creates `QApplication`, initializes DB, seeds data, opens `LoginWindow`)

Required environment:
- Python 3 on Windows (`py -3`)
- No mandatory external server
- No required environment variables for default startup
- Default local SQLite DB path: `database/petcare.db`

Required dependencies (from `requirements.txt`):
- `PySide6>=6.6.0`
- `SQLAlchemy>=2.0.25`
- `bcrypt>=4.1.2`
- `openpyxl>=3.1.2`
- `reportlab>=4.0.8`
- `matplotlib>=3.8.0`
- `Pillow>=10.1.0`
- `python-dateutil>=2.8.2`
- `qrcode>=7.4.2`

Correct Windows launch command:
`py -3 app.py`

Working directory:
`C:\Users\Admin\Downloads\waggy\CSTC_1524\Downloads\Chăm sóc thú cưng\PetCarePro`

Dependency status on this machine:
- All required packages are already installed in the active Python 3.13 environment.

If dependencies are missing on another machine:
- `py -3 -m pip install -r requirements.txt`

Authentication discovery:
- Login is database-backed (`ui/login_window.py` queries `users` table and verifies bcrypt hashes).
- Demo/dev seed users are created in `database/seed.py`:
  - `admin` / `Admin@123`
  - `admin2` / `Admin@123`
  - `doctor1` / `Doctor@123`
  - `spa1` / `Spa@123`
  - `cashier1` / `Cashier@123`
  - `reception1` / `Reception@123`

Runtime launch verification performed:
- Started with `py -3 app.py` from the project directory.
- Process remains running (GUI event loop active).
- Log confirms startup: `Initializing database...`
- Database files present and active: `database/petcare.db`, `database/petcare.db-wal`, `database/petcare.db-shm`

UI smoke verification (read-only, no source changes):
- `LoginWindow` instantiates successfully.
- `MainWindow` instantiates successfully with seeded `admin` user object.
- Sidebar/menu count: `15` items.
- Stacked pages count: `15`.
- Menu navigation index changes update page title without crash.

Notes:
- This analysis and launch are standalone for the reference project only.
- No modifications were made to `app/`, `repository/`, `warehouse/`, or Wagtopia runtime/integration code.
