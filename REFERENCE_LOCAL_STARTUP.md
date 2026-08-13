# REFERENCE_LOCAL_STARTUP

## Startup modes discovered

### Mode A (primary app runtime)
- Working directory: `CSTC_1524/Downloads/Cham soc thu cung/PetCarePro`
- Command:
  - `pip install -r requirements.txt`
  - `python app.py`
- Process: single Python process running Qt event loop
- Server process: none
- Frontend process: none (native desktop UI)
- Port: none
- Browser URL: none
- Auto-open browser: no
- Frontend/backend relation: same process, in-process UI + ORM

### Mode B (database seed only)
- Working directory: same as above
- Command: `python database/seed.py`
- Purpose: initialize/seed data
- No UI launch

## Preconditions
- Python environment with PySide6 + SQLAlchemy + bcrypt dependencies
- Writable filesystem for SQLite database/log files

## Environment variables/config
- DB behavior from `config/settings.py` defaults (`DB_TYPE=sqlite`) unless overridden.
- No discovered .bat/.cmd/.ps1 startup scripts in the reference runtime project.

## Simplest demo mode
- `python app.py` from PetCarePro directory.
