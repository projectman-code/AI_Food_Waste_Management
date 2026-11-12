# FreshLoop — AI Food Waste Management System

A beginner-friendly Flask web application prototype for a final-year college project.

## Features
- User registration and login with hashed passwords
- Donor, NGO and Admin account roles
- Surplus-food listing and NGO claim workflow
- Rule-based food waste risk estimator
- Basic uploaded-image feature analysis demo
- Reports dashboard with category chart
- SQLite database; no external database server required

## Important AI limitations
The waste estimator is a transparent rule-based baseline, not a trained forecasting model. The image module checks simple image brightness and colour statistics; it is not a food classifier and cannot establish freshness or safety. Do not use either output to make food-safety decisions. For a research-grade project, gather labelled local data, train a model, evaluate it on a held-out test set, and document precision/recall and limitations.

## Requirements
- Python 3.10 or newer
- pip
- Internet connection only for Google Fonts and Chart.js CDN (core app works without them except chart rendering)

## Run on Windows
1. Extract the ZIP.
2. Open Command Prompt in the extracted `AI_Food_Waste_Management` folder.
3. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\\Scripts\\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the app:
   ```bash
   python app.py
   ```
6. Open `http://127.0.0.1:5000` in your browser.
7. Register a Donor account and an NGO account in separate browser sessions to test the donation workflow.

## Run on macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Demo walkthrough
1. Register a Donor account and sign in.
2. Add a food listing with quantity, expiry date and location.
3. Sign out; register/sign in as an NGO.
4. Claim an available listing.
5. Open AI Prediction and try sample inputs: stock 20 kg, demand 12 kg, expiry in 2 days, temperature 28 °C.
6. Upload a food photo in Food Image AI.
7. Open Reports to view recorded quantities.

## Security and deployment notes
This is an educational local prototype. Before public deployment: change `SECRET_KEY`, disable debug mode, add CSRF protection, enforce role/ownership authorization, validate all fields server-side, add rate limiting, configure secure cookies and HTTPS, scan uploaded files, set retention rules, and use a production WSGI server. The demo allows Admin self-registration for ease of evaluation; restrict that in a real system.
