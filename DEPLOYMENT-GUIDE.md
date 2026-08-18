# 🚀 OpenShift Operator Upgrade Advisor - Deployment Guide

**How to share this tool with your team**

---

## 🎯 Quick Summary

| Method | Best For | Difficulty | URL Access |
|--------|----------|------------|------------|
| **Docker** | Most teams | ⭐ Easy | `http://server:8000` |
| **Shared Server** | Enterprise | ⭐⭐ Medium | `http://server:8000` |
| **OpenShift** | OCP users | ⭐⭐ Medium | `https://route.apps.cluster` |
| **GitHub Pages** | Public sharing | ⭐ Easy | `https://yourorg.github.io` |
| **Podman** | RHEL users | ⭐ Easy | `http://server:8000` |

---

## 🐳 Option 1: Docker (Recommended)

### Step 1: Build the Docker Image

```bash
cd /Users/nsenthil/AI_TOOL/openshift-upgrade-advisor

# Build image
docker build -t ocp-upgrade-advisor:latest .

# Test locally
docker run -d -p 8000:8000 --name ocp-advisor ocp-upgrade-advisor:latest

# Verify
curl http://localhost:8000/health
```

### Step 2: Share with Team

**Option A: Push to Private Registry**
```bash
# Tag for your registry
docker tag ocp-upgrade-advisor:latest registry.company.com/tools/ocp-upgrade-advisor:latest

# Push
docker push registry.company.com/tools/ocp-upgrade-advisor:latest

# Team pulls and runs:
docker pull registry.company.com/tools/ocp-upgrade-advisor:latest
docker run -d -p 8000:8000 registry.company.com/tools/ocp-upgrade-advisor:latest
```

**Option B: Save as TAR (Air-Gapped)**
```bash
# Save image
docker save ocp-upgrade-advisor:latest -o ocp-upgrade-advisor.tar

# Share via file transfer
scp ocp-upgrade-advisor.tar team-server:/tmp/

# Team loads and runs:
docker load -i /tmp/ocp-upgrade-advisor.tar
docker run -d -p 8000:8000 ocp-upgrade-advisor:latest
```

**Option C: Docker Compose (Simplest)**
```bash
# Team clones repo or gets zip
git clone <your-repo>
cd openshift-upgrade-advisor

# Start with one command
docker-compose up -d

# Access at http://localhost:8000
```

---

## 🖥️ Option 2: Deploy on Shared Server

### For RHEL/Linux Server

```bash
# 1. Copy files to server
scp -r /Users/nsenthil/AI_TOOL/openshift-upgrade-advisor/ \
  user@your-server.company.com:/opt/

# 2. SSH to server
ssh user@your-server.company.com

# 3. Start the service
cd /opt/openshift-upgrade-advisor/backend
nohup python3 simple_server_enhanced.py > /var/log/ocp-advisor.log 2>&1 &

# 4. Verify
curl http://localhost:8000/health
```

### As a Systemd Service (Production)

Create `/etc/systemd/system/ocp-upgrade-advisor.service`:

```ini
[Unit]
Description=OpenShift Operator Upgrade Advisor
After=network.target

[Service]
Type=simple
User=ocpadmin
Group=ocpadmin
WorkingDirectory=/opt/openshift-upgrade-advisor/backend
ExecStart=/usr/bin/python3 simple_server_enhanced.py
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/var/log/ocp-advisor/access.log
StandardError=append:/var/log/ocp-advisor/error.log

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ocp-upgrade-advisor
sudo systemctl start ocp-upgrade-advisor
sudo systemctl status ocp-upgrade-advisor
```

**Team accesses:**
```
http://your-server.company.com:8000
```

### Behind Apache/Nginx Reverse Proxy

**Nginx config** (`/etc/nginx/conf.d/ocp-advisor.conf`):
```nginx
server {
    listen 80;
    server_name ocp-advisor.company.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Team accesses:**
```
http://ocp-advisor.company.com
```

---

## ☸️ Option 3: Deploy on OpenShift

### Create OpenShift Resources

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ocp-upgrade-advisor
  namespace: openshift-tools
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ocp-upgrade-advisor
  template:
    metadata:
      labels:
        app: ocp-upgrade-advisor
    spec:
      containers:
      - name: advisor
        image: registry.company.com/tools/ocp-upgrade-advisor:latest
        ports:
        - containerPort: 8000
          name: http
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: ocp-upgrade-advisor
  namespace: openshift-tools
spec:
  selector:
    app: ocp-upgrade-advisor
  ports:
  - port: 8000
    targetPort: 8000
    name: http
---
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: ocp-upgrade-advisor
  namespace: openshift-tools
spec:
  to:
    kind: Service
    name: ocp-upgrade-advisor
  port:
    targetPort: http
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
```

**Deploy:**
```bash
oc create namespace openshift-tools
oc apply -f deployment.yaml

# Get the route
oc get route -n openshift-tools
```

**Team accesses:**
```
https://ocp-upgrade-advisor-openshift-tools.apps.your-cluster.com
```

---

## 📦 Option 4: Podman (RHEL Default)

```bash
# Build with Podman
podman build -t ocp-upgrade-advisor:latest .

# Run
podman run -d -p 8000:8000 \
  --name ocp-advisor \
  --restart=always \
  ocp-upgrade-advisor:latest

# Generate systemd service
podman generate systemd --new --name ocp-advisor > ~/.config/systemd/user/ocp-advisor.service

# Enable as user service
systemctl --user enable --now ocp-advisor.service
```

---

## 🌐 Option 5: GitHub Pages (Static Version)

For **view-only sharing** without backend:

```bash
# 1. Create GitHub repo
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourorg/ocp-upgrade-advisor.git
git push -u origin main

# 2. Enable GitHub Pages
# Go to repo Settings → Pages → Source: main branch

# 3. Update compatibility matrix URL in index.html
# Change API_URL to point to raw GitHub file
```

**Team accesses:**
```
https://yourorg.github.io/ocp-upgrade-advisor/
```

---

## 📧 Option 6: Share as Standalone Package

### Create Distribution Package

```bash
cd /Users/nsenthil/AI_TOOL

# Create tarball
tar -czf ocp-upgrade-advisor-v1.0.tar.gz \
  openshift-upgrade-advisor/backend/simple_server_enhanced.py \
  openshift-upgrade-advisor/cli-analyzer-enhanced.py \
  openshift-upgrade-advisor/compatibility_matrix.json \
  openshift-upgrade-advisor/index.html \
  openshift-upgrade-advisor/README.md

# Share via email/Slack/Confluence
```

**Recipients run:**
```bash
tar -xzf ocp-upgrade-advisor-v1.0.tar.gz
cd openshift-upgrade-advisor/backend
python3 simple_server_enhanced.py &
```

**Access:** http://localhost:8000

---

## 🔐 Security Considerations

### Production Deployment Checklist

- [ ] **Authentication:** Add SSO/LDAP (use reverse proxy)
- [ ] **HTTPS:** Enable TLS certificates
- [ ] **Firewall:** Restrict access to internal network
- [ ] **Rate Limiting:** Prevent abuse
- [ ] **Logging:** Enable audit logs
- [ ] **Updates:** Plan for compatibility matrix updates

### Example with Basic Auth (Nginx)

```nginx
location / {
    auth_basic "OCP Upgrade Advisor";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8000;
}
```

Create password file:
```bash
sudo htpasswd -c /etc/nginx/.htpasswd teamuser
```

---

## 🔄 Updating the Tool

### Update Compatibility Matrix

```bash
# On the server
cd /opt/openshift-upgrade-advisor
python3 parse-oc-mirror-data.py

# Restart service
sudo systemctl restart ocp-upgrade-advisor

# Or for Docker
docker restart ocp-advisor
```

### Update Code

```bash
# Pull latest changes
git pull origin main

# Rebuild Docker image
docker build -t ocp-upgrade-advisor:latest .
docker stop ocp-advisor
docker rm ocp-advisor
docker run -d -p 8000:8000 --name ocp-advisor ocp-upgrade-advisor:latest
```

---

## 📊 Monitoring & Logs

### Check Service Health

```bash
# Health endpoint
curl http://server:8000/health

# Expected response
{"status": "healthy", "operators": 180}
```

### View Logs

**Systemd:**
```bash
sudo journalctl -u ocp-upgrade-advisor -f
```

**Docker:**
```bash
docker logs -f ocp-advisor
```

**Podman:**
```bash
podman logs -f ocp-advisor
```

---

## 🎯 Recommended Setup by Team Size

### Small Team (1-10 people)
✅ **Docker on shared server**
```bash
docker run -d -p 8000:8000 ocp-upgrade-advisor:latest
```
Access: `http://server:8000`

### Medium Team (10-50 people)
✅ **Systemd service + Nginx reverse proxy**
- Service: `/etc/systemd/system/ocp-upgrade-advisor.service`
- Proxy: `http://ocp-advisor.company.com`
- LDAP auth via Nginx

### Large Team (50+ people)
✅ **OpenShift deployment**
- Replicas: 2-3
- Route: `https://ocp-advisor.apps.cluster.com`
- SSO integration (OAuth2)

---

## 📝 Team Communication Template

### Email/Slack Announcement

```
Subject: 🚀 New Tool: OpenShift Operator Upgrade Advisor

Hi Team,

I've deployed a new tool to help us check operator compatibility before 
OpenShift cluster upgrades.

🔗 URL: http://ocp-advisor.company.com

📚 What it does:
- Checks if your operators are compatible with target OCP version
- Shows which operators need upgrades
- Provides recommended versions
- Works for all Red Hat operators (180 operators, OCP 4.12-4.22)

📋 How to use:
1. Collect cluster data:
   (echo '{"clusterVersion":'; oc get clusterversion version -o json; \
    echo ',"subscriptions":'; oc get sub -A -o json; \
    echo ',"clusterServiceVersions":'; oc get csv -A -o json; \
    echo '}') > cluster-data.json

2. Upload cluster-data.json to the tool
3. Select target OCP version
4. Click "Analyze Compatibility"
5. Review results!

💡 Supports both GUI (web) and CLI modes.

Questions? Let me know!
```

---

## ✅ Quick Start Commands

### For Team Members:

**Browser Access:**
```
http://your-server:8000
```

**CLI Usage:**
```bash
# Download analyzer
curl -O http://your-server:8000/cli-analyzer-enhanced.py

# Use it
python3 cli-analyzer-enhanced.py cluster-data.json --target-ocp 4.22
```

---

## 🎉 Summary

**Easiest:** Docker (`docker run -d -p 8000:8000 ocp-upgrade-advisor`)  
**Most Secure:** OpenShift with SSO  
**Fastest Setup:** Shared server with systemd  

Choose based on your infrastructure! 🚀
