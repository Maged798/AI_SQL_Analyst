# 🚀 [Tips Hindawi](https://www.tipshindawi.com/) Internship (August–October) 2026

> 🎓 This project was built during the [ **Tips Hindawi** ](https://www.tipshindawi.com/) **Internship (August–October) 2026**.

## 👤 Participant

| Field            | Value                                |
| ---------------- | ------------------------------------ |
| Full Name        |     Maged Ahmed Abdellatif           |
| Project Name     |        AI SQL Analyst                |
| GitHub Username  |           Maged798                   |
| Internship Batch | August–October 2026                  |
| Training Program | Large Language Models (LLMs) Program |
| Organization     | [**Edrak for Ai**](https://edrak4ai.com/en)                         |

---

## 👤 Participant

| Field            | Value                                |
| ---------------- | ------------------------------------ |
| Full Name        |     Adham Alaa Zahran                |
| Project Name     |        AI SQL Analyst                |
| GitHub Username  |           AdhamZahran158             |
| Internship Batch | August–October 2026                  |
| Training Program | Large Language Models (LLMs) Program |
| Organization     | [**Edrak for Ai**](https://edrak4ai.com/en)                         |

---

# 📖 Project Overview

**AI SQL Analyst** is a Streamlit application that lets users explore a SQLite database by asking questions in natural language. It inspects the database schema, asks a hosted AI provider to create a structured SQL query, checks that the query is read only, and runs it against the database.

The app displays the generated SQL, query results, a short explanation of the findings, and a visualization when one suits the result. AI providers are configured with an API key, base URL, and model ID. The provider must support the common Chat Completions request format and JSON object responses. The project does not download or run AI models locally.

---

# ✨ Features

* Ask questions about the database in plain language.
* Inspect available tables, columns, and relationships from the app sidebar.
* Generate and parse a structured query plan containing SQL and visualization guidance.
* Execute one read only SQL query with a 500 row result limit.
* View the generated SQL, results table, natural language analysis, and Plotly chart.
* Connect a compatible AI provider using its API key, base URL, and model ID.
* Try the included sample shop database without importing external data.

---

# 🛠️ Technologies Used

* **Python** for the application and database logic.
* **Streamlit** for the interactive user interface.
* **SQLite** for the sample database and read only query execution.
* **Pandas** for displaying query results.
* **Plotly** for charts.
* **Pydantic** for parsing and validating the model's structured response.
* **SQLGlot** for parsing and checking generated SQL.
* **A hosted AI provider** with a compatible Chat Completions API. No model files are downloaded.

---

# ⚙️ Installation

Open PowerShell in the repository folder, then create and activate a virtual environment inside the project:

```powershell
cd ai-sql-analyst
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a private configuration file:

```powershell
Copy-Item .env.example .env
notepad .env
```

Add the settings provided by your AI provider:

```env
AI_API_KEY=your_secret_api_key
AI_BASE_URL=https://your-provider.example/v1
AI_MODEL=your-model-id
SQLITE_DB_PATH=data/sample_shop.db
```

Use your provider's documented API base URL and exact model ID. Alternatively, enter the key, base URL, and model name in the app sidebar. Keep `.env` private; it is excluded from Git.

---

# 🚀 Usage

Start the app from the `ai-sql-analyst` project folder:

```powershell
streamlit run app.py
```

Open the local URL printed in the terminal. The sample shop database is created automatically the first time the app starts. Enter a question such as **“Show the best selling products”**, then select **Analyze data**. The app presents the SQL, returned rows, analysis, and chart.

For another SQLite database, enter its file path in the **SQLite database file** field in the sidebar. The database must be accessible to the computer running Streamlit.

---

# 📸 Demo

The quickest demo is to run the app using the setup instructions above and ask **“Show the best selling products”**. The sample database includes products, orders, and order items, so the query returns a ranked product result with a chart.

---

# 📈 Results

The sample shop database contains 6 products, 7 orders, and 14 order items. A best selling products query ranks **Insulated Bottle** first with 6 units sold, followed by **Wireless Headphones** with 4 units. A category revenue query returns **Electronics** with total revenue of **718.96**.

Generated SQL is visible in the interface, and database execution is limited to read only queries with a maximum of 500 result rows.

---

# 🔮 Future Improvements

* Add database connectors for PostgreSQL and MySQL.
* Add provider adapters for APIs that do not use the common Chat Completions request format.
* Add CSV export and more chart options.
* Add user authentication and saved query history for multi user deployments.

---

# 📚 About the Internship

This project was developed as part of the [**Tips Hindawi**](https://www.tipshindawi.com/) **Internship (August–October) 2026**, and it will be showcased on the official [Tips Hindawi](https://www.tipshindawi.com/) website.

[Tips Hindawi](https://www.tipshindawi.com/) is the internships department of [**Edrak for Ai**](https://edrak4ai.com/en), and the internship encourages participants to build real-world projects, apply practical skills, and showcase their work through GitHub.

For more information about the internship, training programs, and upcoming batches, visit the official [Tips Hindawi](https://www.tipshindawi.com/) website.

---

# 📄 License

This project is shared for educational and portfolio purposes.
