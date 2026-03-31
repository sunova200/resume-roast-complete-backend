# 📄 Resume Roast - Backend

> **AI-powered resume analysis and feedback API** built with FastAPI, MongoDB, and Groq LLM integration.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.135.1-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat&logo=mongodb)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🗂️ Table of Contents

- [Overview](#-overview)
- [Architecture Diagram](#-architecture-diagram)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [🚀 Quick Start (Docker)](#-quick-start-docker)
- [🛠️ Local Development Setup](#-local-development-setup)
- [⚙️ Environment Variables](#-environment-variables)
- [📁 Project Structure](#-project-structure)
- [🔌 API Endpoints](#-api-endpoints)
- [🧪 Testing](#-testing)
- [🤝 Contributing](#-contributing)
- [📜 License](#-license)

---

## 🔍 Overview

**Resume Roast Backend** is a scalable REST API that powers an AI-driven resume review application. It accepts resume files (PDF/DOCX), extracts text, analyzes content using LLMs (via Groq), and returns actionable feedback to help users improve their resumes.

✨ **Key Features:**
- 📤 Resume file upload & parsing (PDF support via `poppler-utils`)
- 🤖 AI-powered analysis using Groq LLM API
- 💾 Persistent storage with MongoDB
- ⚡ Async task queuing with Valkey (Redis-compatible)
- 🐳 Fully containerized with Docker & Docker Compose
- 🔐 Environment-based configuration for dev/prod

---

## 🏗️ Architecture Diagram

<pre>
```mermaid
graph TD
    subgraph Client["🌐 Client Layer"]
        A[Frontend / Mobile App]
    end

    subgraph Backend["⚙️ Backend Services"]
        B[FastAPI Server<br/>app/server.py]
        C[File Parser<br/>utils/pdf_parser.py]
        D[AI Service<br/>utils/groq_client.py]
        E[Task Queue<br/>queue/worker.py]
    end

    subgraph Data["🗄️ Data Layer"]
        F[(MongoDB<br/>resumes, feedback)]
        G[(Valkey<br/>job queue, cache)]
    end

    subgraph External["🌍 External APIs"]
        H[Groq LLM API]
    end

    A -->|POST /api/roast| B
    B -->|Parse PDF| C
    B -->|Queue Job| E
    C -->|Extracted Text| D
    E -->|Process with LLM| D
    D -->|Call| H
    D -->|Save Results| F
    B -->|Cache/Async| G
    F <--> B
    G <--> B

    style Backend fill:#e3f2fd,stroke:#1976d2
    style Data fill:#e8f5e9,stroke:#388e3c
    style External fill:#fff3e0,stroke:#f57c00
```
</pre>

> 💡 *GitHub renders Mermaid diagrams natively in README files!*

---

## 🧰 Tech Stack

| Category | Technology |
|----------|-----------|
| **Framework** | FastAPI 0.135.1, Uvicorn |
| **Language** | Python 3.12 |
| **Database** | MongoDB 7.x (via Motor async driver) |
| **Cache/Queue** | Valkey (Redis-compatible) |
| **AI/LLM** | Groq API |
| **File Processing** | PyPDF2, python-docx, poppler-utils |
| **Containerization** | Docker, Docker Compose |
| **Dev Tools** | VS Code Dev Containers, autopep8 |

---

## ✅ Prerequisites

Before you begin, ensure you have installed:

- 🐳 [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
- 🐍 [Python 3.12+](https://www.python.org/downloads/) *(for local development)*
- 🔑 [Groq API Key](https://console.groq.com/) *(for AI features)*

---

## 🚀 Quick Start (Docker)

```bash
# 1️⃣ Clone the repository
git clone https://github.com/sunova200/resume-roast-complete-backend.git
cd resume-roast-complete-backend

# 2️⃣ Create environment file
cp .env.example .env

# 3️⃣ Start all services
docker-compose up --build

# 4️⃣ Access the API
# 🌐 API Docs: http://localhost:8000/docs
```

### Inside Container
```bash
docker-compose exec app bash
pip install -r requirements.txt
./run.sh
```

---

## 🛠️ Local Development Setup

```bash
# Install system dependencies
# Ubuntu/Debian:
sudo apt install -y poppler-utils python3.12 python3.12-venv

# macOS:
brew install poppler python@3.12

# Set up Python environment
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start dependencies
docker run -d -p 27017:27017 --name mongo mongo:latest
docker run -d -p 6379:6379 --name valkey valkey/valkey:latest

# Configure & run
cp .env.example .env
./run.sh
```

---

## ⚙️ Environment Variables

Create `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
MONGODB_URL=mongodb://admin:admin@localhost:27017
MONGODB_DB_NAME=resume_roast
VALKEY_URL=redis://localhost:6379/0
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
DEFAULT_LLM_MODEL=llama3-70b-8192
MAX_RESUME_SIZE_MB=10
```

> 🔐 Never commit `.env` - it's in `.gitignore`

---

## 📁 Project Structure

```
resume-roast-complete-backend/
├── app/
│   ├── main.py
│   ├── server.py
│   ├── db/
│   │   ├── connection.py
│   │   └── models.py
│   ├── queue/
│   │   └── worker.py
│   ├── utils/
│   │   ├── pdf_parser.py
│   │   ├── groq_client.py
│   │   └── validators.py
│   └── __init__.py
├── Dockerfile
├── docker-compose.yml
├── devcontainer.json
├── requirements.txt
├── run.sh
├── worker.sh
├── .env.example
├── .gitignore
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/roast` | Upload resume for AI analysis | Optional |
| GET | `/api/roast/{job_id}` | Get results by job ID | Optional |
| GET | `/health` | Health check | Public |
| GET | `/docs` | Swagger UI | Public |

### Example Request
```bash
curl -X POST http://localhost:8000/api/roast \
  -F "file=@resume.pdf" \
  -F "focus_areas=experience,skills"
```

### Example Response
```json
{
  "job_id": "abc123",
  "status": "processing",
  "message": "Resume received"
}
```

---

## 🧪 Testing

```bash
pytest tests/
pytest --cov=app tests/ -v
autopep8 --in-place --recursive app/
```

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feature/xyz`
3. Commit: `git commit -m 'Add xyz'`
4. Push: `git push origin feature/xyz`
5. Open Pull Request

✅ Follow PEP 8 | 🧪 Add tests | 📝 Update docs

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file.

<details>
<summary>Expand License</summary>

```
MIT License

Copyright (c) 2026 sunova200

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
</details>

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [Groq](https://groq.com/)
- [MongoDB](https://www.mongodb.com/)
- [Poppler](https://poppler.freedesktop.org/)

---

> 💡 **Pro Tip**: Use VS Code Dev Containers for instant setup!

---

*Made with ❤️ by [sunova200](https://github.com/sunova200)*  
*🚀 Ready to roast some resumes?*