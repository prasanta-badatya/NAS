# Private NAS — Local Photo Cloud

A self-hosted photo and video storage system that runs on your home PC and is
accessible from any device on the same Wi-Fi network.  Think of it as a private
Google Photos that never leaves your house.

---

## What it does

- Upload photos and videos from your phone or laptop via a browser
- Browse your gallery with thumbnails, full-size view, and delete
- Every file is deduplicated (same photo won't be stored twice)
- Thumbnails are generated automatically on upload
- Works on LAN — phone and PC must be on the same Wi-Fi

---

## Tech stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Backend  | Python 3.11 + Django 5 + DRF      |
| Frontend | Angular 17 (TypeScript)           |
| Database | SQLite (local, single file)       |
| Storage  | Local filesystem (`NAS_STORAGE/`) |
| Auth     | DRF Token Authentication          |

---

## Project layout

```
NAS/
├── nas_server/          # Django project
│   ├── accounts/        # User registration, login, logout
│   ├── media_manager/   # Upload, storage, gallery API
│   ├── brain/           # Agent architecture (events + memory)
│   └── nas_server/      # Django settings and URL routing
├── nas-ui/              # Angular frontend
│   └── src/app/
│       ├── auth/        # Login page
│       ├── gallery/     # Gallery, upload, photo grid
│       └── core/        # API service, auth service, guard
├── requirements.txt     # Python dependencies
└── .gitignore
```

---

## Setup — first time

### 1. Python backend

```bash
# From the NAS/ root
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt

cd nas_server
python manage.py migrate
python manage.py createsuperuser   # optional admin account
```

### 2. Angular frontend

```bash
cd nas-ui
npm install        # or: pnpm install
```

---

## Running the app

### Start the backend

```bash
cd nas_server
python manage.py runserver 0.0.0.0:8000
```

`0.0.0.0` makes Django listen on all network interfaces so your phone can reach
it over Wi-Fi.  Using `127.0.0.1` would lock it to localhost only.

### Start the frontend

```bash
cd nas-ui
ng serve --host 0.0.0.0
```

The UI is then available at:

| Device  | URL                          |
|---------|------------------------------|
| Laptop  | http://localhost:4200        |
| Phone   | http://192.168.1.35:4200     |

> Change `192.168.1.35` to your actual PC IP.  Find it with `ipconfig` (Windows)
> or `ip a` (Linux/Mac).

---

## Windows Firewall (one-time, run as Administrator)

The firewall blocks incoming connections by default.  Run these once in an
elevated PowerShell:

```powershell
netsh advfirewall firewall add rule name="NAS Backend" dir=in action=allow protocol=TCP localport=8000
netsh advfirewall firewall add rule name="NAS Frontend" dir=in action=allow protocol=TCP localport=4200
```

---

## API endpoints

Base URL: `http://<your-pc-ip>:8000`

### Auth  (`/api/auth/`)

| Method | Path              | Auth? | Description              |
|--------|-------------------|-------|--------------------------|
| POST   | `/register/`      | No    | Create account           |
| POST   | `/login/`         | No    | Returns token (5/min limit) |
| POST   | `/logout/`        | Yes   | Deletes token            |
| GET    | `/profile/`       | Yes   | Current user info        |

### Media  (`/api/media/`)

| Method | Path                  | Auth?       | Description                  |
|--------|-----------------------|-------------|------------------------------|
| POST   | `/upload/`            | Yes         | Upload one or more files     |
| GET    | `/`                   | Yes         | Paginated list of your files |
| GET    | `/<id>/`              | Yes         | Single file details          |
| DELETE | `/<id>/`              | Yes         | Delete file + thumbnail      |
| GET    | `/<id>/serve/`        | token param | Serve full-size file         |
| GET    | `/<id>/thumbnail/`    | token param | Serve thumbnail              |
| GET    | `/history/`           | Yes         | Upload history log           |

**Why `token param`?**  Browser `<img src>` tags cannot send Authorization
headers.  The serve and thumbnail endpoints accept a `?token=` query parameter
as an alternative so images display correctly in the gallery.

---

## Configuration

All settings live in `nas_server/nas_server/settings.py`.  The most common
things to change:

| Setting              | What it does                               | How to change           |
|----------------------|--------------------------------------------|-------------------------|
| `ALLOWED_HOSTS`      | IPs Django accepts requests from           | Env var or edit directly |
| `CORS_ALLOWED_ORIGINS` | Origins the Angular app is served from  | Env var or edit directly |
| `NAS_STORAGE_ROOT`   | Where files are saved on disk              | Set path in settings     |
| `MAX_UPLOAD_SIZE_MB` | Max file size (default 500 MB)             | Edit settings            |
| `ALLOWED_MIME_TYPES` | Allowed file types (images + video)        | Edit settings            |

**Environment variables (optional, for production):**

```bash
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=192.168.1.35,localhost
CORS_ALLOWED_ORIGINS=http://192.168.1.35:4200
```

---

## File storage layout

Files are organised on disk by user and date:

```
NAS_STORAGE/
└── users/
    └── <user_id>/
        ├── images/
        │   └── 2025-03-01/
        │       └── photo.jpg
        └── thumbnails/
            └── 2025-03-01/
                └── photo_thumb.jpg
```

Thumbnails are JPEG, max 320×320 px, generated by Pillow on upload.

---

## Security notes

- Passwords: minimum 8 characters, hashed with Django's PBKDF2-SHA256
- Login: rate-limited to 5 attempts per minute per IP
- File paths: every read and write is validated with `os.path.realpath()` to
  prevent path traversal attacks (a file can never escape `NAS_STORAGE/`)
- File types: only whitelisted MIME types are accepted
- Tokens: deleted on logout — old tokens stop working immediately
- CORS: restricted to your Angular origin only

---

## Data models (quick reference)

### User  (`accounts.User`)
Extends Django's built-in user with two extra fields:
- `phone_name` — name of the device used to register
- `storage_used` — total bytes stored (updated atomically on upload/delete)

### MediaFile  (`media_manager.MediaFile`)
One row per uploaded file.  Key fields:
- `file_hash` — SHA-256, used for duplicate detection
- `file_path` / `thumbnail_path` — absolute paths on disk
- `media_type` — `image`, `video`, or `other`
- `taken_at` — date from EXIF data (if available), otherwise null
- `device_source` — User-Agent of the uploading device

### UploadHistory  (`media_manager.UploadHistory`)
Audit log — every upload attempt (success or failure) is recorded here.

---

## Brain Driven Agent Architecture

The `brain/` module is a developer-assistant system built on top of this project.
It is not part of the NAS functionality itself — it is a meta-layer for code
maintenance.

- **Brain** — the orchestrator.  All decisions belong here.
- **Agents** — Analyser, Implementer, Tester, Doc, Refactor.
  Agents only observe and execute.  They never contain decision logic.
- **Events** — typed messages (`DevTaskEvent`, `AgentResult`) passed between
  Brain and agents.
- **Memory** — `TaskMemory` / `Memory` classes keep context across agent calls
  within a session.

Rules are documented in `.claude/agent_rules.md`.

---

## Common commands

```bash
# Run migrations after changing models
python manage.py makemigrations
python manage.py migrate

# Open Django admin (superuser required)
# http://localhost:8000/admin/

# Build Angular for production
cd nas-ui && ng build

# Check what is stored in the DB
python manage.py shell
>>> from media_manager.models import MediaFile
>>> MediaFile.objects.all()
```
