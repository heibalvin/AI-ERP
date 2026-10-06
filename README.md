# AI-ERP
Modern ERP massively using AI as an assistant to keep you organised...

## Prerequisites

Ensure the following local services are running on your machine:

* **PostgreSQL** running on `localhost:5432` with administrative access (e.g., user `postgres`, password `postgres`).
* **Ollama** running at `http://localhost:11434` with the `llama3.1:8b` model pulled:
```bash
ollama pull llama3.1:8b

```



---

## 1. Project Directory Structure

Ensure your project files are organized as follows:

```text
.
├── config/
│   └── .env
├── data/
│   └── init_db.py
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── main.py
│   ├── erp/
│   │   ├── __init__.py
│   │   └── agent.py
│   └── task/
│       ├── __init__.py
│       ├── agent.py
│       ├── crud.py
│       └── tools.py
└── requirements.txt

```

---

## 2. Environment Configuration (`config/.env`)

Create or update `config/.env` with your target database credentials and Ollama endpoint:

```ini
# POSTGRES (Dedicated AI-ERP Database & User)
POSTGRES_USER=ai_erp_user
POSTGRES_PASSWORD=ai_erp_password
POSTGRES_DB=ai_erp_db
POSTGRES_HOST=localhost
POSTGRES_URI=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/${POSTGRES_DB}

# OLLAMA
OLLAMA_HOST=localhost
OLLAMA_URI=http://${OLLAMA_HOST}:11434/api

```

---

## 3. Installation

1. Create and activate a Python 3.12 virtual environment:
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```


2. Install dependencies:
```bash
pip install -r requirements.txt

```



---

## 4. Initialize Database via Python

Run `data/init_db.py` to automatically create the dedicated PostgreSQL user (`ai_erp_user`), database (`ai_erp_db`), schema (`api`), and table (`ai_tasks`):

```bash
python -m data.init_db

```

---

## 5. Run the AI-ERP Agent

Launch the interactive CLI session:

```bash
python -m src.main

```

---

## 6. Example Interactions

Try typing the following requests in the `User >` prompt:

* **Create a task:**
```text
User > Add a task to review the Q3 budget report by tomorrow.

```


* **List pending tasks:**
```text
User > Show me my active tasks.

```


* **Update task status:**
```text
User > Mark task 1 as completed.

```


* **General web query (Fallback routing):**
```text
User > What are the latest technological developments in AI?

```