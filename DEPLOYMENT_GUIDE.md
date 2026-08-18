# Deployment Guide - OpenShift Operator Upgrade Advisor

## Current Status

The application has been fully built with:
- ✅ Complete backend (FastAPI + Python)
- ✅ Complete frontend (React + TypeScript)
- ✅ Docker configuration ready
- ✅ All parsers, services, and API endpoints implemented

## Deployment Options

### Option 1: Docker Compose (Recommended)

**Requirements:**
- Docker Desktop or Podman Desktop installed
- At least 4GB RAM available

**Steps:**
```bash
cd openshift-upgrade-advisor

# Set up environment
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit backend/.env and add OPENAI_API_KEY if you have one

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/docs
```

**Services Started:**
- PostgreSQL (database)
- Redis (caching)
- Backend (FastAPI on port 8000)
- Frontend (Vite dev server on port 5173)

### Option 2: Python 3.11/3.12 Local Setup

**Requirements:**
- Python 3.11 or 3.12 (NOT 3.14 - pydantic compatibility)
- Node.js 18+ and npm

**Backend Setup:**
```bash
cd backend

# Create virtual environment with Python 3.11 or 3.12
python3.11 -m venv venv
# OR
python3.12 -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-minimal.txt

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Setup (in separate terminal):**
```bash
cd frontend

# Install dependencies
npm install

# Start frontend
npm run dev
```

### Option 3: Using pyenv for Python Version Management

If you have Python 3.14 installed and need 3.12:

```bash
# Install pyenv (macOS)
brew install pyenv

# Install Python 3.12
pyenv install 3.12.0

# Set local Python version for this project
cd openshift-upgrade-advisor/backend
pyenv local 3.12.0

# Now create venv
python -m venv venv
source venv/bin/activate
pip install -r requirements-minimal.txt
```

## Current Environment

Your system has:
- ✅ Python 3.14.5 (too new for pydantic-core 2.23.4)
- ❌ Docker not installed
- ❌ Node.js not installed

## Recommended Next Steps

### Quick Path: Install Docker Desktop

1. **Download Docker Desktop**:
   - Visit: https://www.docker.com/products/docker-desktop/
   - Download for Mac (Apple Silicon if you have M1/M2/M3)

2. **Install and Start Docker Desktop**

3. **Run the Application**:
   ```bash
   cd /Users/nsenthil/AI_TOOL/openshift-upgrade-advisor
   
   # Set up environment
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   
   # Start services
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   
   # Access app at http://localhost:5173
   ```

### Alternative Path: Install Required Tools Locally

1. **Install Python 3.12** (via pyenv or from python.org)
2. **Install Node.js**: https://nodejs.org/ (LTS version)
3. **Set up PostgreSQL and Redis** (optional, can mock for testing)
4. **Run backend and frontend separately**

## Testing Without Full Setup

You can test the API structure without running services:

```bash
# View the backend code structure
cd /Users/nsenthil/AI_TOOL/openshift-upgrade-advisor/backend
ls -la app/

# View API endpoints
cat app/api/analysis.py
cat app/main.py

# View frontend code
cd ../frontend
ls -la src/
cat src/pages/UploadPage.tsx
```

## Application Features (Ready to Use)

Once deployed, the application provides:

1. **Upload Interface**: Upload 5 JSON files from your OpenShift cluster
2. **Analysis Engine**: Analyzes operator compatibility
3. **AI Insights**: GPT-powered explanations (if API key provided)
4. **Upgrade Paths**: Visual upgrade graphs using NetworkX
5. **Reports**: Download HTML/JSON reports
6. **Risk Assessment**: Low/Medium/High/Critical scoring

## Configuration

### Backend Environment (.env)
```env
OPENAI_API_KEY=your_key_here  # Optional, for AI features
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/openshift_advisor
REDIS_URL=redis://redis:6379/0
```

### Frontend Environment (.env)
```env
VITE_API_URL=http://localhost:8000
```

## Troubleshooting

### "pydantic-core build failed"
- You have Python 3.14 which is too new
- Solution: Use Python 3.11 or 3.12, or use Docker

### "Docker command not found"
- Install Docker Desktop from https://www.docker.com/products/docker-desktop/

### "Port already in use"
- Check what's using ports 5173, 8000, 5432, 6379
- Either stop those services or change ports in docker-compose.yml

### AI Features Not Working
- Make sure OPENAI_API_KEY is set in backend/.env
- The app works without AI, just with basic explanations

## Production Deployment

For production deployment to OpenShift/Kubernetes:

1. Build production images:
   ```bash
   docker build -t openshift-advisor-backend ./backend
   docker build -t openshift-advisor-frontend ./frontend
   ```

2. Push to registry:
   ```bash
   docker tag openshift-advisor-backend your-registry/openshift-advisor-backend:1.0
   docker push your-registry/openshift-advisor-backend:1.0
   ```

3. Deploy to OpenShift:
   ```bash
   oc new-app postgresql-persistent
   oc new-app redis
   oc new-app your-registry/openshift-advisor-backend:1.0
   oc new-app your-registry/openshift-advisor-frontend:1.0
   oc expose svc/openshift-advisor-frontend
   ```

## Next Actions

**Immediate** (Choose one):
- [ ] Install Docker Desktop → Run `docker-compose up -d`
- [ ] Install Python 3.12 + Node.js → Run locally

**After Services Are Running:**
- [ ] Collect JSON files from OpenShift cluster
- [ ] Upload files to http://localhost:5173
- [ ] Analyze compatibility
- [ ] Download reports

## Support

For issues:
1. Check docker-compose logs: `docker-compose logs -f`
2. Verify services: `docker-compose ps`
3. Check backend health: `curl http://localhost:8000/health`
4. View API docs: http://localhost:8000/docs

---

**Project Location**: `/Users/nsenthil/AI_TOOL/openshift-upgrade-advisor`

**Documentation**:
- README.md - Full project documentation
- QUICKSTART.md - Quick setup guide
- PROJECT_SUMMARY.md - Technical details
- This file - Deployment options
