# DEPLOYMENT INSTRUCTIONS

## Local Environment Setup

1. **Python Installation:** Ensure Python 3.11+ is installed.
2. **System Dependencies:** `ffmpeg` and `redis-server` binaries must be installed on your system PATH.
   ```bash
   sudo apt-get update && sudo apt-get install -y ffmpeg redis-server
   ```
3. **Virtual Environment & Dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Starting and Managing Services

The project provides unified automation scripts to boot and stop the stack cleanly:

- **Start all services (FastAPI, Redis, Celery):**
  ```bash
  ./start_services.sh
  ```
- **Stop all services gracefully:**
  ```bash
  ./stop_services.sh
  ```

### Desktop System Tray Manager
Launch the native desktop tray icon controller to manage background servers from your system tray:
```bash
python src/tray_icon.py
# Or headless status check mode:
python src/tray_icon.py --headless
# Or stop background servers:
python src/tray_icon.py --stop
```

## Frontend Operations Dashboard

Scaffolded with Vite and React in `/frontend`:
```bash
cd frontend
npm install
npm run dev     # Starts dev server on port 5173
npm run build   # Production bundle in dist/
npx playwright test  # End-to-end integration tests
```

## API Credentials & Configuration

### YouTube Data API v3
To enable the headless publisher module, place your Google OAuth 2.0 client secret at `client_secrets.json`.

### Basic Authentication
The REST API enforces HTTP Basic Authentication configured via environment variables:
- `API_USERNAME` (default: `admin`)
- `API_PASSWORD` (default: `local_dev_password` in local development)

The dashboard includes a dynamic token-refresh handshake modal to update credentials without halting background Celery tasks.

## Kubernetes Deployment
To deploy the pipeline to a Kubernetes cluster for large-scale batch processing:
```bash
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/worker-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```
