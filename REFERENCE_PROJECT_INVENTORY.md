# REFERENCE_PROJECT_INVENTORY

## 1) Technology stack
- Python desktop application using `PySide6` for UI.
- SQLAlchemy ORM over SQLite (`database/petcare.db`) with WAL files.
- Security utilities via `bcrypt`.
- Logging via Python `logging`.

## 2) Framework
- Qt Widgets desktop framework (`PySide6`), not a web SPA.

## 3) Frontend architecture
- Qt widget hierarchy with three real UI modules:
  - `ui/login_window.py`
  - `ui/main_window.py`
  - `ui/dashboard.py`
- Inline Qt style sheets per widget; no centralized theme file.

## 4) Backend architecture
- In-process monolith (no HTTP server).
- UI modules query SQLAlchemy models directly through `db_manager.get_session()`.

## 5) Entrypoint
- `CSTC_1524/Downloads/Cham soc thu cung/PetCarePro/app.py`

## 6) Startup command
- `python app.py` from `PetCarePro` directory.

## 7) Browser URL
- None (native desktop windows).

## 8) Port
- No app listening port.

## 9) Routing mechanism
- Sidebar selection (`QListWidget`) drives `QStackedWidget` page index in `ui/main_window.py`.

## 10) State management
- Local object state (`self.current_user`, widget-local fields).
- No global store pattern.

## 11) API communication
- No REST/API layer inside CSTC_1524.
- Data access is direct ORM calls from UI code.

## 12) Data flow
- User interaction -> widget handler -> SQLAlchemy query -> ORM rows -> widget updates.

## 13) Component hierarchy
- `QApplication` -> `LoginWindow` -> `MainWindow` -> `QStackedWidget` pages.
- Only `DashboardWidget` is fully implemented; other pages are placeholders.

## 14) Page hierarchy
- Menu includes dashboard/customers/pets/appointments/medical/medicines/services/spa/hotel/invoices/inventory/employees/reports/notifications/settings.
- Only dashboard has full data querying/rendering.

## 15) Styling system
- Inline `setStyleSheet()` strings in UI modules.
- No reusable style token system beyond constants in code.

## 16) Asset system
- Paths referenced (`assets/icons`, `assets/images`) but asset tree is absent in inspected source.

## 17) Database/data layer
- SQLAlchemy models under `models/`.
- SQLite default configured in `config/settings.py` + `config/database.py`.
- Seed logic in `database/seed.py`.

## 18) Authentication
- Username/password login UI.
- Password verification via `bcrypt` helpers in `config/security.py`.
- Lockout/attempt logic in `ui/login_window.py`.

## 19) Demo data system
- Seed command (`database/seed.py`) creates admin, role/permission records, sample domain rows.

## 20) Build/dev tooling
- `requirements.txt` dependency install only.
- No JS bundler, no Dockerfile, no web build pipeline, no API server scripts.
