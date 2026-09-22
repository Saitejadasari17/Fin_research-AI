# 🚀 FinResearch AI — Deployment Guide

This guide details how to deploy **FinResearch AI** to production.

---

## 🛠️ Architecture Overview
* **Backend**: FastAPI (Python 3.12) with Uvicorn.
* **Frontend**: React + Vite SPA.

---

## 🌐 Option 1: Free PaaS Deployment (Recommended for Portfolio / Demos)

### 1. Backend Deployment (Render / Railway / Fly.io)

1. Sign up at [Render.com](https://render.com/).
2. Click **New +** → **Web Service**.
3. Connect your GitHub repository (`Fin_research-AI`).
4. Select the `backend` directory as Root Directory.
5. Set:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Click **Deploy Web Service**.
7. Copy your backend live URL (e.g. `https://finresearch-backend.onrender.com`).

---

### 2. Frontend Deployment (Vercel / Netlify)

1. Sign up at [Vercel.com](https://vercel.com/).
2. Click **Add New...** → **Project**.
3. Import your GitHub repository (`Fin_research-AI`).
4. Set:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
5. Under **Environment Variables**, add:
   - `VITE_API_BASE_URL` = `https://finresearch-backend.onrender.com` (your Render backend URL from Step 1).
6. Click **Deploy**.

---

## 🐳 Option 2: Docker / Container Deployment (Self-Hosted / VPS)

To run the entire system on any server with Docker installed:

```bash
# Clone the repository
git clone https://github.com/Saitejadasari17/Fin_research-AI.git
cd Fin_research-AI

# Build and start services in detached mode
docker-compose up -d --build
```

Access:
* **Frontend UI**: `http://localhost:5173`
* **FastAPI Backend**: `http://localhost:8000`
* **API Docs**: `http://localhost:8000/docs`

---

## 🔒 Production Security Best Practices
- CORS settings in `backend/app/main.py` can be restricted to your specific Vercel frontend URL in production:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["https://your-app.vercel.app"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
