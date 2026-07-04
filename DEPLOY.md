# DEPLOYMENT INSTRUCTIONS

## Local Environment Setup

1. **Python Installation:** Ensure Python 3.11+ is installed.
2. **System Dependencies:** `ffmpeg` binaries must be installed on your system PATH as it is required by the `moviepy` rendering engine.
3. **Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## API Credentials & Configuration

### YouTube Data API v3
To enable the headless publisher module, you must provide Google OAuth 2.0 credentials.

1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Enable the **YouTube Data API v3**.
4. Navigate to **Credentials** -> **Create Credentials** -> **OAuth client ID**.
5. Configure the OAuth consent screen if prompted (set it to 'Testing' or 'External' depending on your org rules).
6. Download the resulting JSON credentials file.
7. Rename the file to `client_secrets.json` and place it in the root directory of this repository.

*Note: On the first run of the pipeline, a browser window will open to authorize the app. A `token.json` file will be generated locally to maintain session state for subsequent headless runs.*

## Local Execution (Docker)
You can run the full API and worker stack using Docker Compose:
```bash
docker-compose up --build
```
This will spin up the FastAPI backend (port 8000), a Redis broker, and a Celery worker.

## Kubernetes Deployment
To deploy the pipeline to a Kubernetes cluster for large-scale batch processing:

1. **Create the credentials secret:**
   ```bash
   kubectl create secret generic api-credentials \
     --from-literal=username=your_admin_user \
     --from-literal=password=your_secure_password
   ```

2. **Apply the deployment manifests:**
   ```bash
   kubectl apply -f k8s/redis-deployment.yaml
   kubectl apply -f k8s/api-deployment.yaml
   kubectl apply -f k8s/worker-deployment.yaml
   kubectl apply -f k8s/ingress.yaml
   ```

3. **Verify running pods:**
   ```bash
   kubectl get pods
   ```

The FastAPI application will be accessible based on the Ingress controller configuration. You can trigger the video pipeline by sending a POST request to the `/generate` endpoint on the API server.