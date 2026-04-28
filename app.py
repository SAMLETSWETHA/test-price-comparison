from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

CSV_PATH = "data/lab_prices.csv"

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError("lab_prices.csv not found. Please run generate_data.py first.")

df = pd.read_csv(CSV_PATH)

df.columns = df.columns.str.strip()
df["Lab_Name"] = df["Lab_Name"].astype(str).str.strip()
df["Test_Name"] = df["Test_Name"].astype(str).str.strip()
df["City"] = df["City"].astype(str).str.strip()
df["Area"] = df["Area"].astype(str).str.strip()
df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get-filters")
def get_filters():
    cities = sorted(df["City"].dropna().unique().tolist())
    areas = sorted(df["Area"].dropna().unique().tolist())
    tests = sorted(df["Test_Name"].dropna().unique().tolist())
    labs = sorted(df["Lab_Name"].dropna().unique().tolist())

    return jsonify({
        "cities": cities,
        "areas": areas,
        "tests": tests,
        "labs": labs
    })


@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()

    test_name = data.get("test", "").strip().lower()
    city = data.get("city", "").strip().lower()
    area = data.get("area", "").strip().lower()

    result = df.copy()

    if test_name:
        result = result[result["Test_Name"].str.lower().str.contains(test_name, na=False)]

    if city:
        result = result[result["City"].str.lower() == city]

    if area:
        result = result[result["Area"].str.lower() == area]

    if result.empty:
        return jsonify({
            "status": "error",
            "message": "No matching diagnostic labs found."
        })

    result = result.sort_values(by="Price")
    cheapest = result.iloc[0]

    return jsonify({
        "status": "success",
        "cheapest": {
            "Lab_Name": cheapest["Lab_Name"],
            "Test_Name": cheapest["Test_Name"],
            "Price": int(cheapest["Price"]),
            "City": cheapest["City"],
            "Area": cheapest["Area"],
            "Latitude": float(cheapest["Latitude"]),
            "Longitude": float(cheapest["Longitude"])
        },
        "results": result.head(50).to_dict(orient="records")
    })


@app.route("/ai-assistant", methods=["POST"])
def ai_assistant():
    data = request.get_json()
    user_msg = data.get("message", "").strip().lower()

    if not user_msg:
        return jsonify({
            "reply": "Please ask something like: Which lab is cheapest for blood test in Ramnagar?"
        })

    tests = df["Test_Name"].dropna().unique()
    areas = df["Area"].dropna().unique()
    labs = df["Lab_Name"].dropna().unique()

    found_test = None
    found_area = None
    found_lab = None

    shortcuts = {
        "cbc": "Complete Blood Count",
        "blood test": "Complete Blood Count",
        "blood count": "Complete Blood Count",
        "complete blood": "Complete Blood Count",
        "complete blood count": "Complete Blood Count",

        "sugar": "Blood Sugar Test",
        "blood sugar": "Blood Sugar Test",
        "fasting sugar": "Fasting Blood Sugar",
        "fbs": "Fasting Blood Sugar",
        "post lunch sugar": "Post Lunch Blood Sugar",
        "plbs": "Post Lunch Blood Sugar",

        "thyroid": "Thyroid Profile",
        "lipid": "Lipid Profile",
        "liver": "Liver Function Test",
        "kidney": "Kidney Function Test",
        "vitamin d": "Vitamin D Test",
        "vitamin b12": "Vitamin B12 Test",
        "urine": "Urine Routine Test",
        "crp": "CRP Test",
        "esr": "ESR",
        "dengue": "Dengue NS1 Antigen",
        "typhoid": "Typhoid Test",
        "full body": "Full Body Checkup",
        "diabetes": "Diabetes Profile",
        "blood group": "Blood Group Test"
    }

    lab_shortcuts = {
        "diagnostic centre": "Tapadia Diagnostic Centre",
        "diagnostic center": "Tapadia Diagnostic Centre",
        "apollo": "Apollo Diagnostics",
        "tapadia": "Tapadia Diagnostic Centre",
        "tapaida": "Tapadia Diagnostic Centre",
        "vijaya": "Vijaya Diagnostics",
        "lucid": "Lucid Diagnostics",
        "medplus": "MedPlus Diagnostics",
        "metropolis": "Metropolis Healthcare",
        "srl": "SRL Diagnostics",
        "thyrocare": "Thyrocare",
        "redcliffe": "Redcliffe Labs",
        "lal path": "Dr Lal PathLabs",
        "aarthi": "Aarthi Scans",
        "kims": "KIMS Diagnostics",
        "tenet": "Tenet Diagnostics",
        "care": "Care Diagnostics",
        "tesla": "Tesla Diagnostics",
        "matrix": "Matrix Diagnostics",
        "medquest": "MedQuest Diagnostics"
    }

    for test in tests:
        if test.lower() in user_msg:
            found_test = test
            break

    if found_test is None:
        for key, value in shortcuts.items():
            if key in user_msg:
                found_test = value
                break

    for area in areas:
        if area.lower() in user_msg:
            found_area = area
            break

    for lab in labs:
        if lab.lower() in user_msg:
            found_lab = lab
            break

    if found_lab is None:
        for key, value in lab_shortcuts.items():
            if key in user_msg:
                found_lab = value
                break

    if "help" in user_msg or "what can you do" in user_msg:
        return jsonify({
            "reply": "I can find cheapest labs, compare test prices, search by area, and guide you to a lab location. Example: Which lab is cheapest for blood test in Ramnagar? Or Navigate me to Apollo Diagnostics in Ramnagar."
        })

    navigation_words = [
        "navigate", "route", "direction", "directions", "go to",
        "location", "map", "near me", "take me", "guide me"
    ]

    if any(word in user_msg for word in navigation_words):
        if found_lab and found_area:
            branch = df[
                (df["Lab_Name"].str.lower() == found_lab.lower()) &
                (df["Area"].str.lower() == found_area.lower())
            ]

            if not branch.empty:
                row = branch.iloc[0]
                lat = float(row["Latitude"])
                lng = float(row["Longitude"])

                return jsonify({
                    "reply": (
                        f"{found_lab} branch is available in {found_area}. "
                        f"Click below to navigate from your current location:<br>"
                        f"<button class='map-btn' onclick='openCurrentLocationMap({lat}, {lng})'>Open Google Maps</button>"
                    )
                })

            return jsonify({
                "reply": f"Sorry, I could not find {found_lab} branch in {found_area} in my dataset."
            })

        if found_lab:
            branches = df[df["Lab_Name"].str.lower() == found_lab.lower()]
            available_areas = sorted(branches["Area"].dropna().unique().tolist())[:12]

            return jsonify({
                "reply": (
                    f"{found_lab} is available in these areas: "
                    f"{', '.join(available_areas)}. Please mention one area for navigation."
                )
            })

        if found_area:
            branches = df[df["Area"].str.lower() == found_area.lower()]
            available_labs = sorted(branches["Lab_Name"].dropna().unique().tolist())[:12]

            return jsonify({
                "reply": (
                    f"In {found_area}, these labs are available: "
                    f"{', '.join(available_labs)}. Please mention one lab for navigation."
                )
            })

        return jsonify({
            "reply": "Please mention both lab name and area. Example: Navigate me to Apollo Diagnostics in Ramnagar."
        })

    if found_test is None:
        return jsonify({
            "reply": "Please mention a test name like blood test, CBC, HbA1c, thyroid, lipid, liver function, kidney function, vitamin D, or full body checkup."
        })

    result = df[df["Test_Name"].str.lower() == found_test.lower()]

    if found_area:
        result = result[result["Area"].str.lower() == found_area.lower()]

    if found_lab:
        result = result[result["Lab_Name"].str.lower() == found_lab.lower()]

    if result.empty:
        if found_area:
            return jsonify({
                "reply": f"Sorry, I could not find {found_test} in {found_area}. Try another area or test."
            })
        return jsonify({
            "reply": "Sorry, I could not find the requested test. Try another test or area."
        })

    result = result.sort_values(by="Price")
    cheapest = result.iloc[0]

    if found_area and found_lab:
        reply = (
            f"For {found_test} at {found_lab} in {found_area}, "
            f"the price is ₹{int(cheapest['Price'])}."
        )
    elif found_area:
        reply = (
            f"The cheapest lab for {found_test} in {found_area} is "
            f"{cheapest['Lab_Name']} at ₹{int(cheapest['Price'])}."
        )
    elif found_lab:
        reply = (
            f"The cheapest branch of {found_lab} for {found_test} is in "
            f"{cheapest['Area']} at ₹{int(cheapest['Price'])}."
        )
    else:
        reply = (
            f"The cheapest lab for {found_test} in Hyderabad is "
            f"{cheapest['Lab_Name']} at {cheapest['Area']} for ₹{int(cheapest['Price'])}."
        )

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True)