# CryptoX Neuron — Project Documentation

## 1. Introduction
CryptoX Neuron is a student-level web application for organising customer records and exploring customer segmentation. It combines a web interface, a database, and machine-learning libraries to make customer information easier to review.

## 2. Objectives
- Keep customer information organised.
- Explore patterns in customer spending and purchasing.
- Display analysis results in a simple dashboard.
- Practise web development, database integration, and basic machine-learning concepts.

## 3. Main Features
- **Dashboard:** summary of customers and segmentation results.
- **Customer management:** view and manage customer records.
- **Bulk upload:** import customer data using the supported upload format.
- **Customer analysis:** run available segmentation or prediction workflows.
- **Analysis history:** review saved results.
- **Account and subscription pages:** sign-in, registration, and plan-related interface.

## 4. Technologies Used

| Component | Technology |
|---|---|
| Programming language | Python |
| Web framework | FastAPI |
| Frontend | HTML, CSS, Jinja2, Bootstrap |
| Machine learning | scikit-learn, HDBSCAN |
| Data processing | pandas, NumPy |
| Database | MongoDB Atlas |
| Deployment | Render |

AWS S3 may be used when file-storage features are configured.

## 5. Themes and Interface
The interface uses a dashboard layout with cards, rounded corners, and gradient accents. The stylesheet defines light and dark theme variables. The sign-in page has a separate dark, glass-style design.

## 6. Example Fields for Customer Analysis
Depending on the form and upload schema, useful fields can include customer ID, customer name, age, income, spending score, purchase frequency, purchase totals, and preferred product category. The exact column names should match the application's accepted format.

## 7. Security Basics
- Store database URLs, session secrets, and API keys in environment variables.
- Do not commit real credentials or private customer data to GitHub.
- Use authentication and workspace-scoped access when handling customer records.
- Keep demo authentication disabled in production unless it is deliberately required.
- Restrict administrative operations such as model training and payment verification.
- Use dummy data for classroom demonstrations whenever possible.

These are project-level safeguards; deployment configuration and testing are still important.

## 8. How to Run Locally
1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies with `python -m pip install -r requirements.txt`.
4. Configure required values using `.env.example` as a reference.
5. Start the server with `uvicorn app:app --reload`.
6. Open the local address shown in the terminal, usually `http://127.0.0.1:8000`.

## 9. Possible Applications
The project can be used as a learning prototype for retail shops, shopping malls, online stores, fashion businesses, and marketing exercises. It can help users explore customer groups and purchasing patterns, but results should not be treated as guaranteed business predictions.

## 10. Conclusion
CryptoX Neuron demonstrates how Python, a web framework, a database, and machine-learning tools can be combined in a small customer-analysis application. It is intended as a student project and a starting point for further learning.
