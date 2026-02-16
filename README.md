# GEAR Project Setup

This guide explains how to set up and run the GEAR Django project locally.


### 1. Create a Virtual Environment

Run this command in the **root directory** (`GEAR/`):

```bash
python -m venv venv
```

### 2. Activate the Virtual Environment

* Windows (Command Prompt)

```bash
venv\Scripts\activate
```

* Windows (PowerShell)


```bash
venv\Scripts\Activate.ps1
```

* Windows (macOS/Linux)

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r gear/src/requirements.txt
```

### 4. Run Django Development Server

```bash
cd gear/src
```

```bash
python manage.py runserver
```

## Project Structure

```
GEAR/
├── gear/
│   └── src/
│       ├── apps/
│       │   ├── accounts/       # User authentication and account management
│       │   │   ├── admin.py
│       │   │   ├── apps.py
│       │   │   ├── models.py
│       │   │   ├── views.py
│       │   │   └── migrations/
│       │   ├── analytics/      # Data analytics and reporting
│       │   ├── finance/        # Financial transactions and payment management
│       │   ├── inventory/      # Inventory and stock management
│       │   ├── main/           # Core application logic, landing pages
│       │   └── orders/         # Order processing and management
│       ├── config/              # Django configuration
│       │   ├── settings.py
│       │   ├── urls.py
│       │   ├── wsgi.py
│       │   └── asgi.py
│       ├── manage.py            # Django management script
│       └── requirements.txt     # Project dependencies
└── db.sqlite3                   # Default SQLite database (if used)
```

### Folder Descriptions

- **`apps/`**: Contains all Django applications. Each app is self-contained with its own `models.py`, `views.py`, `admin.py`, and `migrations/`.  
  - **`accounts`**: Handles user registration, login, profiles, and authentication-related functionality.  
  - **`analytics`**: Responsible for gathering, processing, and displaying analytical data.  
  - **`finance`**: Manages financial transactions, billing, and payments.  
  - **`inventory`**: Tracks and manages stock, products, and warehouse operations.  
  - **`main`**: Core app for general project logic and shared resources.  
  - **`orders`**: Handles order creation, updates, and tracking.

- **`config/`**: Contains Django project-wide settings, URL configurations, and ASGI/WSGI entry points.

- **`manage.py`**: Django management script used to run the server, make migrations, and other administrative tasks.

- **`requirements.txt`**: List of Python packages required to run the project.

- **`db.sqlite3`**: Default SQLite database file (can be replaced with another database in production).

### Notes

- All applications are located under `gear/src/apps` for a clear separation of concerns.
- Migrations are stored inside each app's `migrations/` folder.
- `config/` separates project-level configuration from app-level code.

