# Watchtower System Monitor (Upgraded)

This project has been upgraded to a production-ready Django system with enhanced architecture, security, and world-map monitoring capabilities.

## Features Added
- **Security**: Hardened settings (`.env` file usage).
- **Architecture**: `system_service.py` and `auth_service.py` offload logic from views.
- **Monitoring**: Real-time stats are safely cached, mitigating CPU bottlenecks from excessive `psutil` queries.
- **Map View**: Active global tracking of users via Leaflet.js in Admin Dashboard.
- **UI Refinement**: Symmetrical glowing orbs replace heavy radar logic to maintain the Glassmorphism feel.

## Folder Structure (ZIP THIS)
```
the_watchtower/
│
├── accounts/                  # App Dir
│   ├── services/
│   │   ├── auth_service.py    # Extracted OTP logic
│   │   └── system_service.py  # Cached system hardware tracking
│   ├── utils/                 # (Legacy)
│   ├── migrations/
│   ├── models.py              # Contains SystemLog and UserProfile 
│   ├── views.py               # Cleaned controller layer
│   └── urls.py
│
├── the_watchtower/            # Config Dir
│   ├── settings.py            # Secure configuration (dotenv)
│   └── urls.py
│
├── templates/                 # UI HTML 
│   ├── auth_base.html         # Updated to minimal style
│   ├── dashboard_admin.html   # World Map integration
│   └── ...                    # (Existing clean code)
│
├── requirements.txt           # Environment Depedencies
├── manage.py                  # Django orchestrator
└── README.md                  # Instructions
```

## How to Run

1. **ZIP Instructions**: Inside `d:\1 Coding\intern\the_watchtower`, select all contents (folders `accounts`, `the_watchtower`, `templates`, and files `manage.py`, `requirements.txt`, etc.), Right Click -> Send To -> Compressed (zipped) folder.
2. Unzip where desired.
3. **Environment setup**: Create a `.env` file in the root alongside `manage.py` containing:
   ```env
   SECRET_KEY=your_secret_key_here
   DEBUG=True
   ALLOWED_HOSTS=*
   ```
4. **Install Requirements**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Database**: Provide tracking columns:
   ```bash
   python manage.py makemigrations accounts
   python manage.py migrate
   ```
6. **Start Application**:
   ```bash
   python manage.py runserver
   ```
Then visit `http://127.0.0.1:8000`. Login as a superuser to access the Command Center and interact with the World Map!
