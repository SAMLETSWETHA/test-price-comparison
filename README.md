# Diagnostic Test Price Comparison Assistant

## Project Overview

Diagnostic Test Price Comparison Assistant is a smart healthcare web application that helps users compare diagnostic test prices across different labs in Hyderabad.

The system allows users to search for medical tests, compare prices, find the cheapest diagnostic lab, and navigate to the selected lab from their current location using Google Maps.

This prototype also includes an AI Assistant with microphone support, so users can ask questions using text or voice.

---

## Problem Statement

Patients often do not know which diagnostic lab offers a medical test at the lowest price. The same test may have different prices in different labs and areas.

Searching manually on Google can take time because users need to open many websites and compare prices by themselves.

---

## Solution

This project provides a direct and simple solution where users can:

- Search diagnostic tests by name
- Filter results by city and area
- Compare lab prices
- Find the cheapest lab automatically
- Navigate to the selected lab from current location
- Ask an AI assistant using text or microphone

---

## Key Features

- Diagnostic test price comparison
- Cheapest lab recommendation
- Area-wise search
- Dynamic city, area, and test dropdowns
- AI assistant chatbot
- Voice input using microphone
- Google Maps navigation from current location
- Prescription upload option as future scope
- Dataset with multiple Hyderabad areas, labs, tests, and prices

---

## Tech Stack

- Python
- Flask
- Pandas
- HTML
- CSS
- JavaScript
- CSV Dataset
- Google Maps Direction Link
- Web Speech API for microphone input

## Project Structure

```text
test-price-comparison/
│
├── app.py
├── generate_data.py
├── requirements.txt
├── README.md
│
├── data/
│   └── lab_prices.csv
│
├── templates/
│   └── index.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── script.js

Installation and Run

1. Clone the repository
git clone https://github.com/SAMLETSWETHA/test-price-comparison.git

2. Go to the project folder
cd test-price-comparison

3. Create virtual environment
python -m venv .venv

4. Activate virtual environment
For Windows PowerShell:
.\.venv\Scripts\activate

If activation is blocked, run this command first:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
Then activate again:
.\.venv\Scripts\activate

5. Install requirements
pip install -r requirements.txt

6. Generate dataset
python generate_data.py

7. Run Flask app
python app.py

8. Open in browser
http://127.0.0.1:5000

How AI Assistant Works
The AI assistant understands user queries such as:

Which lab is cheapest for blood test in Ramnagar?
Navigate me to Apollo Diagnostics in Ramnagar
Find cheapest Vitamin D Test in Tarnaka
Which branch of Tapadia Diagnostic Centre is cheapest for HbA1c?
The assistant identifies the test name, lab name, and area from the query. Then it searches the dataset and gives the cheapest lab recommendation or navigation option.

Dataset

The dataset contains diagnostic lab details such as:

Lab Name
Test Name
Price
City
Area
Latitude
Longitude

The dataset is generated using generate_data.py

NOTE: In this prototype, sample data is used for demonstration. In real-time implementation, the data can be connected to official diagnostic lab APIs, verified lab databases, or an admin panel.

Sample AI Assistant Questions?
Which lab is cheapest for blood test in Ramnagar?
Find cheapest Vitamin D Test in Tarnaka
Which branch of Tapadia Diagnostic Centre is cheapest for HbA1c?
Navigate me to Apollo Diagnostics in Ramnagar

Future Enhancements
Real-time diagnostic lab API integration
Prescription OCR to read uploaded prescriptions
User login and search history
Verified live price updates
Nearby lab recommendation based on live location
Appointment booking feature
Admin dashboard to update lab prices

Why This Project is Useful?

Google provides many search results, and ChatGPT gives general information. But this project gives direct, structured, and local diagnostic test price comparison.
It saves time, reduces confusion, and helps users choose affordable diagnostic labs easily.

Author
Samlet Swetha
B.Tech Data Science
Sreyas Institute of Engineering and Technology
