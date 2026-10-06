# AI-ERP-AGENT

Personae: The AI-ERP-Agent is your personal assistant on your day to day business. It will be able to manage sub-agent for each domains. 

Task: Will be able to identify the type of request, and ask clarification questions or route to specific sub-agents. Also will be able to provide feedback when other sub-task agent has completed their task. Daily will be able to provide a digest of day, week, month upcoming events.

Format: it will be connected in a modular way to sub-agents for each of their domains (task, calendar, contacts, finance, emails). These sub-agent will be name AI-Task-Agent, or AI-Calendar-Agent... And they will have connectivity to external tools like google task, google calendar, postrges, etc ...

Context: AI-ERP source code is under "src" folder, written in python (Python 3.12.13). It will be connected to ollama:3.34.4 (at http://localhost:114343) using model llama3.1:8b. And to a Postgres:18.6 database (at http://localhost:5432). Ollama and Postgres are already deployed we will use config/.env enviroment parameter to connect (do not redeploy). AI-ERP is coded in langraph library and will try to connect to specific sub-agents, if not sub-agents found, it will try to answer the request directly or from internet.

config/.env
```
# POSTGRES
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=default
POSTGRES_HOST=localhost
POSTGRES_URI=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/${POSTGRES_DB}

# POSTGREST
PGRST_DB_URI=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/${POSTGRES_DB}
PGRST_DB_SCHEMA=api
PGRST_DB_ANON_ROLE=web_anon

#OLLAMA
OLLAMA_HOST=localhost
OLLAMA_URI=http://${OLLAMA_HOST}:11434/api
```

Steps: 
 - Create a first AI-ERP agent under "src".
 - Connect AI-ERP to Ollama for the LLM and to Postgres for Memory (do not deploy Ollama or Postgres, already done).
 - Create a second agent AI-Task-Agent under "src/task".
 - Connect AI-Task-Agent to Postgres and create a task task.
 - Create a CRUD functions to Postgres task table useuable by AI-ERP.

