# Three-Tier Flask and PostgreSQL App

This is the standalone sample application used throughout the Kubernetes learning sessions.

The application folder owns only the app source code and Docker assets. Kubernetes manifests are intentionally kept outside this folder under `../sessions/` so each Kubernetes topic can introduce its own YAML step by step.

## Architecture

```text
Browser UI -> Flask application -> PostgreSQL database
```

Tiers:

- Presentation tier: HTML/CSS UI rendered in the browser.
- Application tier: Python Flask app that handles requests and database operations.
- Data tier: PostgreSQL stores submitted messages.

The app is a small message board. Users submit a name and message from the UI, Flask validates the input, and PostgreSQL stores the records.

## Folder Structure

```text
three-tier-flask-postgres-app/
  app/
    app.py
    requirements.txt
    static/
    templates/
  Dockerfile
  docker-compose.yml
  .dockerignore
```

## Local Development With Docker Compose

From this folder:

```bash
docker compose up --build
```

Open:

```text
http://localhost:5000
```

Stop the local environment:

```bash
docker compose down
```

Remove the local PostgreSQL volume too:

```bash
docker compose down -v
```

## Build the App Image

```bash
docker build -t prashantdey/appk8stutorial:1.0 .
```

## Push to Docker Hub

Login:

```bash
docker login
```

Push:

```bash
docker push prashantdey/appk8stutorial:1.0
```

The Kubernetes session manifests use this image placeholder:

```text
prashantdey/appk8stutorial:1.0
```

Before applying session manifests, replace it with your real Docker Hub image.

## App Configuration

The Flask container reads database settings from environment variables:

| Variable | Purpose | Example |
| --- | --- | --- |
| `DB_HOST` | PostgreSQL hostname | `postgres` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_NAME` | Database name | `appdb` |
| `DB_USER` | Database username | `appuser` |
| `DB_PASSWORD` | Database password | `apppassword` |
| `FLASK_SECRET_KEY` | Flask session secret | `change-this` |

Health endpoints:

- `/healthz`: process health check.
- `/readyz`: database connectivity check.

## Kubernetes Sessions

Kubernetes examples for this app are kept in:

```text
../sessions/
```

Current sessions:

- `01-core-k8s`: Namespace, Pod, Deployment, Service, labels, selectors, and basic troubleshooting.
- `02-storage-pv-pvc-statefulset`: PV, PVC, StorageClass, StatefulSet, and database persistence.
