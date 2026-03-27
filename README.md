# Django Social Media App

## Development Setup

### Prerequisites
- Python 3.14+
- Node.js 22+

### Install dependencies
```bash
pip install -r requirements.txt
npm install
```

### Run database migrations
```bash
cd webapp
python manage.py migrate
```

### Start development server
In two terminals:

```bash
# Terminal 1 — Tailwind CSS watcher
npm run watch:css

# Terminal 2 — Django dev server
cd webapp
python manage.py runserver
```

---

## Deployment with Docker (mounted repo)

The app is served by **Gunicorn** on port **8100** with **WhiteNoise** handling static files.

### Build the image

```bash
docker build -f .devcontainer/Dockerfile -t webapp .
```

### Run with the repo mounted from the host

```bash
docker run --rm -it \
  -p 8100:8100 \
  -v "$(pwd)":/workspace \
  --env-file .env \
  webapp
```

The `start.sh` script runs automatically and will:
1. Install Python and Node.js dependencies
2. Build the Tailwind CSS bundle
3. Apply database migrations
4. Collect static files
5. Start Gunicorn on `0.0.0.0:8100`

### Environment variables

Create a `.env` file in the repo root (copy from `.env.example` if present):

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key (required in production) |
| `DEBUG` | Set to `False` for production |
| `DATABASE_URL` | Database connection string (optional; defaults to SQLite) |

### Manual startup (without Docker)

```bash
./start.sh
```
