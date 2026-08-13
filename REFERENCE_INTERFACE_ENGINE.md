# REFERENCE_INTERFACE_ENGINE

The "interface engine" in CSTC_1524 is a Qt desktop shell + direct ORM data access pattern.

| Abstraction | Path | Responsibility | Input | Output | Dependencies | Consumers | Can it be reused by Wagtopia? | Reuse Risk |
|---|---|---|---|---|---|---|---|---|
| App Shell | `PetCarePro/app.py` | Bootstrap app lifecycle, DB init/seed, show login | Process startup | Qt app + login window | settings, db_manager, seed | all users | Partial (shell pattern only) | Medium |
| Root Window | `PetCarePro/ui/main_window.py` | Main nav shell with sidebar and stacked pages | authenticated user | page switching + page widgets | PySide6 widgets, dashboard | all logged-in users | Yes (layout/navigation patterns) | Medium |
| Login Form | `PetCarePro/ui/login_window.py` | Authenticate user and transition to main shell | username/password | `MainWindow` or error | db_manager, models, security | app bootstrap | Yes (UX pattern), not logic | Medium |
| Dashboard Card Helpers | `PetCarePro/ui/dashboard.py` | Generate KPI cards and section cards | title/value/icon | QWidget cards | Qt layout/widgets | dashboard page | Yes | Low-Medium |
| Page Registry | `PetCarePro/ui/main_window.py` | Hardcoded page/menu registration | menu item list | stacked widget pages | local code | main window | Yes, but replace with stronger route registry | Medium |
| Notification Surface | `PetCarePro/ui/dashboard.py` | Render recent notifications list | ORM notification rows | label rows | Notification model | dashboard | Partial | Medium |
| API Abstraction | N/A | Not present | - | - | - | - | Must be created for Wagtopia integration | High |
| State Abstraction | N/A (`current_user` fields only) | Minimal local state | local assignments | local behavior | object instance vars | windows/widgets | Needs adapter/state layer | High |
| Loading Abstraction | `ui/login_window.py` | Simple button state transitions | submit action | loading text/disable | widget state | login flow | Yes | Low |
| Error Abstraction | `QMessageBox` + label methods | User-visible error dialogs/messages | exceptions/validation errors | modal or inline message | Qt widgets | multiple pages | Yes | Low |
| Modal System | `QMessageBox` usages | confirmations and alerts | prompt + severity | user choice/alert | Qt | login/logout/errors | Yes | Low |
| Route Registration | `menu_items` array in `main_window.py` | maps keys to page labels | static list | menu entries | local code | navigation | Yes (concept) | Medium |
| Data Access Engine | `config/database.py` + ORM models | session management and schema binding | query intents | ORM rows | SQLAlchemy | login/dashboard | Reuse concept only | Medium |

## Reuse assessment summary
- Reusable directly: shell layout pattern, card composition methods, modal/error UX patterns.
- Reuse with adapter: navigation model, notification section, detail card rendering.
- Not reusable directly: data access model and auth/business logic (CSTC is clinic ERP domain, not Wagtopia scientific analysis domain).
