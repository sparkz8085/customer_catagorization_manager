<!-- Project badges -->
<div align="center">

# 🧠 CryptoX Neuron
### Customer Intelligence & Segmentation

**Turn customer data into clearer business insights.**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/Database-MongoDB-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![ML](https://img.shields.io/badge/ML-scikit--learn-orange?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Deployment](https://img.shields.io/badge/Deploy-Render-46E3B7?logo=render&logoColor=111)](https://render.com/)
[![Project](https://img.shields.io/badge/Type-Student%20Project-blueviolet)](#)

</div>

---

## ✨ About

**CryptoX Neuron** is a student-level customer analysis web application. It helps users organise customer information, run customer segmentation/prediction workflows, and review results in a simple dashboard.

## 🚀 Features

- 📊 **Dashboard** — customer totals, analysed records, pending analysis, and segment summaries.
- 👥 **Customer management** — view and manage customer records.
- 🧠 **ML analysis** — customer segmentation and prediction workflows.
- 📁 **Bulk upload** — import customer data using a supported file format.
- 🧾 **Analysis history** — review saved analysis results.
- 🔐 **Account access** — login and registration flows.
- 💳 **Subscription workflow** — plan and upgrade interface with verification controls.
- 📱 **Responsive layout** — designed for different screen sizes.

## 🎨 Themes & Design

- ☀️ **Light theme** — bright surfaces and clean cards.
- 🌙 **Dark theme** — dark surfaces with high-contrast text.
- 💜 **Gradient accents** — indigo/purple highlights and colourful result cards.
- 🪟 **Modern dashboard UI** — rounded cards, soft shadows, and clear navigation.
- ✨ **Glass-style sign-in page** — dark gradient background and translucent card.

*Theme availability can vary by page; the sign-in screen uses its own dark visual style.*

## 🔐 Security Highlights

- 🔑 Sensitive configuration is intended to be stored in environment variables, not committed to Git.
- 🧑‍💻 Customer and analysis-history records are scoped to the signed-in workspace.
- 🧱 Authentication endpoints have basic rate limiting.
- 🧪 Demo authentication is configuration-controlled and should stay disabled in production unless intentionally needed.
- 🛡️ Training and payment-verification operations use separate keys/controls.

**Important:** these controls depend on correct deployment configuration. Never commit database URLs, session secrets, API keys, or cloud credentials. Test login and review deployment logs before sharing the app publicly.

## 🧰 Tech Stack

| Area | Technology |
|---|---|
| Language | Python |
| Web framework | FastAPI, Uvicorn |
| UI | HTML, CSS, Jinja2, Bootstrap |
| Machine learning | scikit-learn, HDBSCAN, pandas, NumPy |
| Database | MongoDB Atlas |
| Optional file storage | AWS S3 |
| Deployment | Render |
| Version control | Git and GitHub |

## 🏪 Possible Use Cases

- 🛍️ Retail shops and shopping malls
- 🛒 E-commerce stores
- 👕 Fashion and lifestyle businesses
- 📦 Small businesses tracking repeat customers
- 📣 Marketing teams exploring customer groups
- 🎓 Student projects and ML demonstrations

It can help explore customer purchase patterns and similar spending groups. Results are decision-support signals, not guaranteed predictions.

## 🧾 Example Customer Fields

Depending on the selected form or upload schema, customer records may include:

- Customer name or ID
- Age and basic profile information
- Income and spending score
- Purchase count or frequency
- Product/category preferences

Check the application's accepted column names before uploading a CSV. Use dummy data for demonstrations and only process real customer information when you have permission and a valid reason.

## ⚙️ Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/sparkz8085/customer_catagorization_manager.git
cd customer_catagorization_manager
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Use `.env.example` as a guide to create a local `.env` file. Configure MongoDB and the session secret; add AWS credentials only if required by your setup. Never commit the real `.env` file.

### 5. Start the app

```bash
uvicorn app:app --reload
```

Open the local URL printed by Uvicorn, usually http://127.0.0.1:8000.

## ☁️ Deployment

The repository includes a Render configuration. Connect the GitHub repository, confirm the build/start commands, add required environment variables in Render, and inspect the latest logs if startup fails.

## 📚 Project Documentation

See [docs/PROJECT_DOCUMENTATION.md](docs/PROJECT_DOCUMENTATION.md) for a short student-level write-up.

## 🎓 Project Note

CryptoX Neuron is a learning project demonstrating web development, database integration, and customer segmentation concepts. It is not a professionally audited production system.

<div align="center">

**Built with Python, curiosity, and a little machine learning.** 💜

</div>
