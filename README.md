#  TraderCopilot Swing
### Institutional-Grade AI Assistant for Swing Trading

![License](https://img.shields.io/badge/license-Proprietary-black?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16.0-black?style=for-the-badge&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)

---

##  The Vision
**TraderCopilot Swing** is not just another trading bot; it is a **comprehensive intelligence platform** designed to bridge the gap between retail and institutional trading. 

By combining **Quantitative Rigor** (Donchian Breakouts, Trend Following) with **Generative AI** (RAG-enhanced Market Analysis), it provides traders with a "Copilot" that doesn't just signal *when* to trade, but explains *why*.

---

##  Key Features

###  AI Analyst Core (RAG Engine)
*   **Context-Aware Intelligence**: Retrieves real-time data from 5+ sources (Price Action, On-Chain Data, Social Sentiment, News) to generate institutional-grade trade theses.
*   **Gemini 2.0 Integration**: Powered by Google's latest LLM models for sub-second inference and deep reasoning.
*   **Structured Reports**: Generates detailed Markdown reports with "Executive Summaries", "Risk Assessments", and "Invalidation Levels".

###  Quantitative Signal Engine
*   **Multi-Strategy Support**:
    *   **Donchian V2**: Classic breakout strategy optimized for volatility compression.
    *   **Trend Native**: Pure trend-following logic for high-timeframe captures.
*   **Real-Time Screening**: Scans 50+ markets simultaneously for setup criteria.
*   **Smart Filtering**: Filters out low-quality chops using ADX and Volatility thresholds.

###  Premium User Experience (Frontend)
*   **Modern Stack**: Built with **Next.js 16 (App Router)** and **React 19**.
*   **Glassmorphic Design**: Sleek, dark-themed UI with **Tailwind CSS 4** and **Radix UI** primitives.
*   **Interactive Visualization**: Dynamic charts powered by **Recharts**.
*   **Mobile-First**: Fully responsive with native-like drawers (Vaul) and touch gestures.

###  Enterprise-Grade Backend
*   **Robust API**: Async **FastAPI** architecture capable of handling high-concurrency requests.
*   **Self-Healing Database**: Automatic schema migrations on startup with **Alembic**.
*   **Secure Auth**: HttpOnly Cookies, JWT, and Role-Based Access Control (RBAC).
*   **Billing & Monetization**: Deep integration with **Stripe** for subscription management.

---

##  Technology Stack

### Backend
*   **Language**: Python 3.11
*   **Framework**: FastAPI
*   **Database**: PostgreSQL + SQLAlchemy (Async)
*   **Migrations**: Alembic (Auto-healing)
*   **AI Provider**: Google Gemini (via `google-generativeai`)
*   **Payments**: Stripe API

### Frontend (`/web`)
*   **Framework**: Next.js 16 (App Router)
*   **Library**: React 19
*   **Styling**: Tailwind CSS 4 + Tailwind Animate
*   **State**: Server Components + React Hooks
*   **Components**: Radix UI (Headless), Lucide React (Icons)
*   **Charts**: Recharts

---

##  Getting Started

### Prerequisites
*   Python 3.11+
*   Node.js 18+ (for Frontend)
*   PostgreSQL 14+
*   Git

### 1. Clone the Repository
```bash
git clone https://github.com/tsmluky/TraderCopilot-Swing.git
cd TraderCopilot-Swing
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt

# Run the Server (Auto-migrates DB on start)
python main.py
```
*Port: `8000`*

### 3. Frontend Setup
```bash
cd web
npm install
npm run dev
```
*Port: `3000`*

---

##  Gallery
*(Add your premium screenshots here)*

---

##  License
Proprietary Software. All rights reserved.
Developed by **Lukx** for **TraderCopilot**.
