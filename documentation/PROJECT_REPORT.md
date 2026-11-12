# AI FOOD WASTE MANAGEMENT SYSTEM
## Mini Project Report — FreshLoop

### Abstract
Food waste is a major social, economic and environmental concern. FreshLoop is a web-based prototype designed to help food donors record surplus food and connect with NGO users. It provides an inventory risk estimator, a basic image-feature analysis demonstration, donation management and summary reports. The system is implemented using Python Flask, SQLite, HTML, CSS and JavaScript.

### Problem statement
Food businesses and households may have surplus food while nearby organizations are unaware of its availability. Manual tracking can make it difficult to identify surplus early, coordinate donations and measure the quantity redistributed. A simple digital workflow can improve visibility and coordination.

### Objectives
1. Provide role-based accounts for donors, NGOs and administrators.
2. Record food name, category, quantity, expiry date and pickup location.
3. Estimate potential waste risk from stock, demand, expiry time and ambient temperature.
4. Demonstrate image feature extraction from uploaded food photographs.
5. Display donation and category-level reports.

### Proposed system
The donor creates a listing. NGO users can view available listings and record a claim. The prediction module calculates a transparent risk score from user-entered inventory values and suggests actions. The image module extracts basic brightness and colour statistics. Reports summarize total listings, quantities and claimed quantities.

### System architecture
Browser (HTML/CSS/JavaScript) → Flask routes and validation → SQLite database. AI utility modules are called by Flask routes: the waste-risk estimator uses deterministic rules; the image-analysis utility uses Pillow image statistics.

### Modules
- Authentication: registration, password hashing, login and logout.
- Donation management: create, list and claim surplus-food records.
- Waste risk estimation: estimate surplus and a low/medium/high indicator.
- Image analysis: calculate basic visual statistics from uploaded images.
- Reports: aggregate donation quantity by category and display a chart.

### Software requirements
Python 3.10+, Flask, Pillow, SQLite, modern browser, VS Code (optional).

### Hardware requirements
A standard laptop/desktop with 4 GB RAM recommended; no GPU required.

### Testing plan
1. Register using a new email; verify duplicate email is rejected.
2. Login with valid and invalid credentials.
3. Create a positive-quantity donation; verify it appears in dashboard.
4. Login as NGO and claim an available donation.
5. Submit stock greater than demand and verify surplus is positive.
6. Upload a supported image and verify analysis is returned.
7. Open reports and verify category totals reflect database entries.

### Expected outcome
A working local web prototype that demonstrates digital surplus-food listings, NGO claim workflow, a baseline risk estimator, image feature analysis and reporting.

### Limitations and future scope
The current estimator is rule-based and has not been trained or validated on real operational data. Image analysis is not a CNN classifier and cannot determine freshness, contamination or food safety. Future work can include a properly labelled local food image dataset, CNN transfer learning, time-series demand forecasting using historical sales, geospatial donor-to-NGO matching, expiry alerts, multilingual UI, audit logs and deployment with security hardening.

### Conclusion
FreshLoop demonstrates how a lightweight web platform can support food-waste reduction workflows. It provides a foundation for further research and evaluation using real datasets and validated AI models.
