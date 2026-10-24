<!-- Project badges -->
<div align="center">

# 🧠 CryptoX Neuron
### Customer Intelligence & Segmentation

**Turning customer data into clearer business insights.**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![API](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/Database-MongoDB-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![ML](https://img.shields.io/badge/ML-scikit--learn-orange?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Deployment](https://img.shields.io/badge/Deploy-Render-46E3B7?logo=render&logoColor=111)](https://render.com/)
[![Purpose](https://img.shields.io/badge/Built%20for-Internship%20Project-blueviolet)](#)

</div>

---

## ✨ About CryptoX Neuron

**CryptoX Neuron** is a customer intelligence and segmentation application I built as part of my internship project. The idea is to make customer data easier to organise, explore, and understand through a simple web dashboard and machine-learning workflows.

I see this project as a starting point. With the right guidance, a stronger technical foundation, and further development, I would like to explore turning it into a more complete **SaaS product** in the future.

## 🚀 Features

- 📊 **Customer dashboard** — view customer totals, analysis status, and segment summaries.
- 👥 **Customer management** — organise and review customer records.
- 🧠 **Machine-learning analysis** — explore customer segmentation and prediction workflows.
- 📁 **Bulk upload** — import customer data using the supported file format.
- 🧾 **Analysis history** — review saved analysis results.
- 🔐 **Account access** — login and registration flows.
- 💳 **Subscription workflow** — plan and upgrade interface with verification controls.
- 📱 **Responsive interface** — designed to work across different screen sizes.

## 🎨 Themes & Design

- ☀️ **Light theme** — bright surfaces and clean cards.
- 🌙 **Dark theme** — dark surfaces with high-contrast text.
- 💜 **Gradient accents** — indigo/purple highlights and colourful result cards.
- 🪟 **Modern dashboard UI** — rounded cards, soft shadows, and clear navigation.
- ✨ **Glass-style sign-in page** — dark gradient background and translucent card.

*Theme availability can vary by page; the sign-in screen uses its own dark visual style.*

## 🔐 Security Considerations

- 🔑 Sensitive configuration belongs in environment variables, not source control.
- 🧑‍💻 Customer and analysis-history records are intended to be scoped to the signed-in workspace.
- 🧱 Authentication endpoints include basic rate-limiting controls.
- 🧪 Demo authentication is configuration-controlled and should remain disabled in production unless deliberately needed.
- 🛡️ Sensitive operations such as training and payment verification use separate keys or controls.

These are project-level safeguards, not a claim of a complete security audit. Correct deployment configuration and testing remain important. Never commit database URLs, session secrets, API keys, or cloud credentials.

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

## 🏪 Potential Use Cases

CryptoX Neuron could be explored for customer-insight tasks in areas such as:

- 🛍️ Retail shops and shopping malls
- 🛒 E-commerce stores
- 👕 Fashion and lifestyle businesses
- 📦 Small businesses tracking repeat customers
- 📣 Marketing teams exploring customer groups

It can help explore customer purchase patterns and similar spending groups. Results should support human decisions, not be treated as guaranteed predictions.

## 🧾 Example Customer Fields

Depending on the form and upload schema, useful customer attributes may include:

- Customer ID or name
- Age and basic profile information
- Income and spending score
- Purchase count or frequency
- Product or category preferences

Check the application's accepted column names before uploading a CSV. Use dummy data for demonstrations, and only process real customer information when you have permission and a valid reason.

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

Use `.env.example` as a guide to create a local `.env` file. Configure MongoDB and the session secret; add AWS credentials only if required by your setup. Never commit your real `.env` file.

### 5. Start the app

```bash
uvicorn app:app --reload
```

Open the local URL printed by Uvicorn, usually http://127.0.0.1:8000.

## ☁️ Deployment

The repository includes a Render configuration. Connect the GitHub repository, confirm the build and start commands, set the required environment variables in Render, and inspect the latest logs if startup fails.

## 📚 Project Documentation

See [docs/PROJECT_DOCUMENTATION.md](docs/PROJECT_DOCUMENTATION.md) for a concise project write-up.

## 🔭 Future Vision

My long-term goal is to explore whether CryptoX Neuron can grow into a SaaS platform for customer insights. That would require a stronger foundation, feedback and mentorship, more testing, and further work on reliability, privacy, security, and scalability. For now, this repository represents the current internship project and a foundation to learn from and improve.

<div align="center">

**Built with Python, curiosity, and a vision to keep learning.** 💜

</div>
