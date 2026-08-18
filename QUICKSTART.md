# Quick Start Guide

## Prerequisites

- Docker and Docker Compose installed
- OpenShift cluster access (to generate input files)
- OpenAI API key (optional, for AI features)

## Step 1: Environment Setup

```bash
# Navigate to project directory
cd openshift-upgrade-advisor

# Set up backend environment
cd backend
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
cd ..

# Set up frontend environment
cd frontend
cp .env.example .env
cd ..
```

## Step 2: Start Services

```bash
# Start all services with Docker Compose
docker-compose up -d

# Check services are running
docker-compose ps
```

Expected output:
```
NAME                         STATUS
openshift-upgrade-advisor-backend-1    Up
openshift-upgrade-advisor-frontend-1   Up
openshift-upgrade-advisor-postgres-1   Up
openshift-upgrade-advisor-redis-1      Up
```

## Step 3: Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Step 4: Collect Cluster Data

On your OpenShift cluster, run:

```bash
# Create a directory for outputs
mkdir cluster-data

# Collect cluster version
oc get clusterversion version -o json > cluster-data/clusterversion.json

# Collect subscriptions
oc get sub -A -o json > cluster-data/subscriptions.json

# Collect CSVs
oc get csv -A -o json > cluster-data/csv.json

# Collect catalog sources
oc get catalogsource -A -o json > cluster-data/catalogsource.json

# Collect package manifests
oc get packagemanifest -o json > cluster-data/packagemanifest.json
```

## Step 5: Analyze Your Cluster

1. Open http://localhost:5173 in your browser
2. Upload the 5 JSON files from `cluster-data/` directory
3. Select your target OpenShift version (e.g., 4.16)
4. Click "Analyze Compatibility"
5. View results with AI insights and upgrade recommendations

## Step 6: Download Reports

On the results page, you can:
- Download HTML report
- Download JSON data
- View upgrade paths
- See AI-generated recommendations

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart
```

### "Analysis failed" error
- Verify all 5 JSON files are uploaded
- Check files are valid JSON
- Ensure files are from the same cluster
- Check backend logs: `docker-compose logs backend`

### AI features not working
- Verify OPENAI_API_KEY is set in backend/.env
- Check API key is valid
- The application will work without AI, but explanations will be basic

### Port conflicts
If ports 5173, 8000, 5432, or 6379 are already in use:

Edit `docker-compose.yml` and change port mappings:
```yaml
ports:
  - "3000:5173"  # Frontend on port 3000 instead
  - "8080:8000"  # Backend on port 8080 instead
```

## Development Mode

### Backend Only
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Only
```bash
cd frontend
npm install
npm run dev
```

## Stopping Services

```bash
# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v
```

## Next Steps

- Read the full README.md for detailed documentation
- Check API docs at http://localhost:8000/docs
- Customize compatibility matrix in `backend/app/services/compatibility.py`
- Add more operators and versions to the matrix

## Common Use Cases

### Testing with Sample Data
If you don't have access to an OpenShift cluster, you can create minimal sample JSON files for testing.

### Customizing Compatibility Matrix
Edit `backend/app/services/compatibility.py` to add your operators:

```python
COMPATIBILITY_MATRIX = {
    "your-operator": {
        "4.16": ["1.0", "1.1"],
        "4.17": ["1.1", "1.2"],
    }
}
```

### Running Without AI
The app works without OpenAI API key. You'll get basic compatibility information without AI-generated explanations.

---

**Need Help?** Check the full README.md or open an issue on GitHub.
