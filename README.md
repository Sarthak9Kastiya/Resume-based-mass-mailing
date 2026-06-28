# 📧 Resume-Based Mass Mailing Engine

An AI-powered mass mailing tool that generates **personalized cold emails** for internship/job applications. Upload your resume, provide a list of targets (professors, recruiters, companies), and the engine will scrape their web profiles, generate tailored emails using AI, and send them — all from a beautiful dashboard.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Next.js](https://img.shields.io/badge/Next.js-16-black)

---

## ✨ Features

- **AI-Powered Email Generation** — Uses Claude, Gemini, GPT, or Groq to write personalized emails based on your resume and the recipient's public profile.
- **Web Scraping** — Automatically scrapes target URLs (faculty pages, company pages) to gather context for personalization.
- **Campaign Management** — Organize your outreach into campaigns with full status tracking.
- **Bulk CSV/Excel Upload** — Upload a spreadsheet of targets (name, email, URL) and process them all at once.
- **Email Preview & Approval** — Review every AI-generated draft before sending. Edit, approve, or regenerate.
- **SMTP Email Sending** — Send emails directly from your Gmail (or any SMTP provider) with App Passwords.
- **Beautiful Dashboard** — Modern, dark-themed UI built with Next.js and shadcn/ui.

---

## 🏗️ Architecture

```
┌──────────────────────┐         ┌──────────────────────┐
│     Frontend         │  HTTP   │     Backend          │
│  (Next.js + React)   │ ◄─────► │  (FastAPI + Python)  │
│  localhost:3000      │         │  localhost:8000       │
└──────────────────────┘         └──────────┬───────────┘
                                            │
                              ┌─────────────┼──────────────┐
                              │             │              │
                         SQLite DB    AI APIs (LLMs)   Gmail SMTP
```

---

## 📋 Prerequisites

Before you begin, make sure you have the following installed:

| Tool | Version | Check |
|------|---------|-------|
| **Python** | 3.10+ | `python3 --version` |
| **Node.js** | 18+ | `node --version` |
| **npm** | 9+ | `npm --version` |
| **Git** | Any | `git --version` |

You will also need:
- A **Gmail account** with [2-Step Verification](https://myaccount.google.com/security) enabled
- A **Gmail App Password** (see [Step 4](#4-generate-a-gmail-app-password))
- At least one **AI API key** (Anthropic Claude, Google Gemini, OpenAI, or Groq)

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Sarthak9Kastiya/Resume-based-mass-mailing.git
cd Resume-based-mass-mailing
```

### 2. Set Up the Backend

```bash
cd backend

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up the Frontend

Open a **new terminal window**:

```bash
cd frontend

# Install Node.js dependencies
npm install
```

### 4. Generate a Gmail App Password

To send emails through Gmail, you need an **App Password** (not your regular Gmail password).

1. Go to [Google Account Security](https://myaccount.google.com/security).
2. Make sure **2-Step Verification** is turned **ON**.
3. Go to [App Passwords](https://myaccount.google.com/apppasswords).
4. Select **"Mail"** as the app and **"Mac"** (or your device) as the device.
5. Click **Generate** — Google will give you a **16-character password** (e.g., `abcd efgh ijkl mnop`).
6. **Copy this password** (remove spaces). You will paste it into the app later.

> ⚠️ **Important:** If you don't see the "App Passwords" option, make sure 2-Step Verification is enabled first.

### 5. Get an AI API Key

You need at least one AI API key to generate personalized emails. Choose one (or more):

| Provider | Get API Key | Model Examples |
|----------|------------|----------------|
| **Anthropic (Claude)** | [console.anthropic.com](https://console.anthropic.com/) | `claude-opus-4.7`, `claude-sonnet-4.6` |
| **OpenAI (GPT)** | [platform.openai.com](https://platform.openai.com/api-keys) | `gpt-5.5`, `gpt-5.4-pro` |
| **DeepSeek** | [platform.deepseek.com](https://platform.deepseek.com/) | `deepseek-v4-pro`, `deepseek-v4-flash` |
| **Google (Gemini)** | [aistudio.google.com](https://aistudio.google.com/apikey) | `gemini-3.5-flash`, `gemini-3.1-pro` |
| **Mistral AI** | [console.mistral.ai](https://console.mistral.ai/) | `mistral-large-3`, `mistral-small-4` |
| **Together AI** | [together.ai](https://together.ai) | Latest Llama 4 line (Scout & Maverick) |
| **Groq, Perplexity, OpenRouter** | Respective Consoles | Any compatible models |

---

## ▶️ Running the Application

### Start the Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Start the Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

You should see:
```
▲ Next.js 16.x.x
- Local: http://localhost:3000
✓ Ready
```

### Open the App

Open your browser and go to: **[http://localhost:3000](http://localhost:3000)**

---

## ⚙️ Configuration (First-Time Setup)

After opening the app, go to the **Settings** page (`http://localhost:3000/settings`):

### SMTP Settings
| Field | Value |
|-------|-------|
| SMTP Host | `smtp.gmail.com` |
| SMTP Port | `587` |
| SMTP Username | Your Gmail address (e.g., `you@gmail.com`) |
| SMTP Password | Your 16-character App Password |
| Sender Name | Your full name |
| Sender Email | Your Gmail address |

Click **"Test Connection"** to verify. You should see a green success toast.

### AI API Keys
1. Scroll down to the **API Keys** section.
2. Click **"Add API Key"**.
3. Select your provider (e.g., Anthropic), enter the model name and your API key.
4. Click **Save**.

---

## 📨 Sending Your First Campaign

### Step 1: Create a Campaign
- Go to **Campaigns** → Click **"New Campaign"** → Give it a name (e.g., "Summer 2025 Internships").

### Step 2: Upload Your Resume
- Click **"Upload Resume"** and select your resume PDF.
- The app will parse and extract the text automatically.

### Step 3: Upload Targets
- Prepare a CSV or Excel file with these columns:

| name | email | organization | designation_or_department | provided_url |
|------|-------|-------------|--------------------------|-------------|
| Dr. Jane Smith | jane@university.edu | MIT | Computer Science | https://faculty.mit.edu/jane |

- Click **"Upload Targets"** and select your file.

### Step 4: Configure Email Settings
- Choose **Subject Type**: "Personalized" (AI generates unique subjects) or "Constant" (same subject for all).
- Add a **Signature** (your sign-off block).
- Add **Additional AI Context** (e.g., "I am looking for summer research internships in ML. Keep the tone very formal.").

### Step 5: Process Targets
- Click **"Process All"** — the engine will:
  1. Scrape each target's URL for context
  2. Feed your resume + scraped data to the AI
  3. Generate a personalized email draft for each target

### Step 6: Review & Approve
- Review each generated email. You can **edit** the subject/body directly.
- Click **"Approve All"** when you're satisfied.

### Step 7: Send
- Click **"Send All"** to send approved emails via Gmail SMTP.
- Track delivery status in real-time on the dashboard.

---

## 📁 Project Structure

```
Resume-based-mass-mailing/
├── backend/
│   ├── main.py              # FastAPI app & API routes
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── crud.py              # Database CRUD operations
│   ├── database.py          # SQLite database connection
│   ├── worker.py            # Background task workers
│   ├── requirements.txt     # Python dependencies
│   └── services/
│       ├── email.py         # SMTP email sending logic
│       ├── scraper.py       # Web scraping logic
│       ├── ai_engine.py     # AI email generation (multi-provider)
│       └── parser.py        # Resume & CSV/Excel parsing
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js pages (campaigns, settings)
│   │   ├── components/      # Reusable UI components (shadcn/ui)
│   │   └── lib/
│   │       └── api.ts       # Axios API client
│   ├── package.json
│   └── tsconfig.json
├── .gitignore
└── README.md
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `SMTP Connection Failed` | Make sure you're using a Gmail **App Password** (not your regular password). Ensure 2-Step Verification is ON. |
| `Port 3000 already in use` | Kill the existing process: `lsof -ti:3000 \| xargs kill -9` |
| `Port 8000 already in use` | Kill the existing process: `lsof -ti:8000 \| xargs kill -9` |
| `Module not found` (backend) | Make sure your virtual environment is activated: `source venv/bin/activate` |
| `npm install` fails | Delete `node_modules` and `package-lock.json`, then run `npm install` again. |
| AI generation fails | Check that your API key is correct and has credits/quota remaining. |

---

## 📝 Notes

- This application is designed to run **locally** on your machine. All data (credentials, emails, campaigns) is stored in a local SQLite database that never leaves your computer.
- The database file (`mailing_engine.db`) is automatically created on first run.
- Your Gmail App Password and AI API keys are stored locally and are never transmitted anywhere except to their respective services (Gmail SMTP, AI providers).

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
