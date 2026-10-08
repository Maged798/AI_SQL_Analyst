# QueryPilot: AI SQL Analyst

QueryPilot lets you ask questions about a database in everyday language. It reads the database schema, asks an AI model to create a SQL query, checks that the query is read only, runs it, and shows the SQL, results, a short analysis, and a chart.

This folder is the complete project. It does not depend on the course notebooks in `test`, and it never downloads AI models. You can connect a provider of your choice by entering that provider's API key, API base URL, and model ID.

## What you need

* Windows, macOS, or Linux
* Python 3.10 or newer
* An API key from an AI provider
* An SQLite database, or use the sample shop database included with the app

## First time setup on Windows

Open PowerShell in this project folder, named `ai-sql-analyst`.

Create a project environment and install the required packages:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If you already use the repository level environment named `ai-sql`, activate it instead:

```powershell
..\ai-sql\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

These commands install Python libraries only. They do not download AI models.

## Connect your AI provider

The app sidebar contains three provider fields:

1. **Provider API key:** paste the secret API key from your provider's developer dashboard. Do not paste the dashboard webpage address here.
2. **API base URL:** copy the API base URL from the provider's API documentation. Do not use the dashboard or API key webpage address. Most providers require a custom URL.
3. **Model name:** enter the model ID exactly as shown in the provider's documentation.

The key stays in the current app session and is not saved by the app. Use a provider whose API supports the common Chat Completions request format and JSON object responses. Providers that use a different API format need an adapter before they can work with this version.

You can use a different provider key at any time by changing these three fields. The app sends requests to the base URL you provide.

## Save provider settings in a file

You may save the settings in a private `.env` file instead of entering them in the sidebar. Copy the example and edit it:

```powershell
Copy-Item .env.example .env
notepad .env
```

Fill in values from your provider:

```env
AI_API_KEY=put_your_secret_key_here
AI_BASE_URL=https://your-provider.example/v1
AI_MODEL=your-model-id
SQLITE_DB_PATH=data/sample_shop.db
```

Replace the example URL and model ID with the values in your provider's API documentation. Keep `.env` private; it is excluded from Git. The app continues to accept the older `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL` variable names for existing setups, but new setups should use the generic `AI_` names above.

## Start the app

From the project folder, with your Python environment active, run:

```powershell
streamlit run app.py
```

Open the local address printed in the terminal. The sample database is created automatically the first time the app starts.

Try this question:

> Show the best selling products

The sample data should put **Insulated Bottle** first with 6 units sold. The app shows the SQL, result table, chart, and analysis. Each question uses your provider's API and may incur charges.

## Use your own database

This version supports SQLite database files. In the sidebar, enter the path in **SQLite database file**, or set `SQLITE_DB_PATH` in `.env`. The file must be accessible to the computer running Streamlit. Queries use a read only connection and return at most 500 rows.

## Troubleshooting

* **Missing API key:** enter one in the sidebar or set `AI_API_KEY` in `.env`.
* **Connection error:** check the API base URL carefully. It must come from your provider's API documentation, not its website or key page.
* **Model not found:** use the exact model ID shown by your provider.
* **Unsupported request format:** the provider must support Chat Completions and JSON object responses.
* **No credits or quota:** check the billing and usage limits for the provider that issued the key.
* **Changes in `.env` do not apply:** stop Streamlit with `Ctrl+C`, save `.env`, and run `streamlit run app.py` again.

## Safety notes

The app accepts one read only SQL query and uses a read only SQLite connection. Your provider receives the database schema and your question. It also receives a small sample of query results to write the analysis. Do not connect sensitive data unless your provider and account settings are appropriate for it.

## Project files

```text
ai-sql-analyst/
├── app.py          Streamlit user interface
├── sql_agent.py    Provider connection, query plan, and analysis
├── db.py           Schema reading and safe SQLite queries
├── charts.py       Result charts
├── seed_db.py      Sample database creator
├── data/           Local sample database location
├── requirements.txt
└── .env.example
```
