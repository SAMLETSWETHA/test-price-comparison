from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import pytesseract
from PIL import Image

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

DATA_FILE = os.path.join("data", "lab_prices.csv")

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame(columns=[
            "Lab_Name", "Test_Name", "Price", "City", "Area", "Latitude", "Longitude"
        ])

    try:
        # first try tab-separated
        df = pd.read_csv(DATA_FILE, sep="\t")
        if len(df.columns) == 1:
            # if still one big column, try comma-separated
            df = pd.read_csv(DATA_FILE)
    except Exception:
        df = pd.read_csv(DATA_FILE)

    # clean column names
    df.columns = df.columns.str.strip()

    # if file was read as one combined column, split manually
    if len(df.columns) == 1:
        first_col = df.columns[0]
        temp = df[first_col].astype(str).str.split(r"\s{2,}|\t|,", expand=True)

        if temp.shape[1] >= 7:
            temp = temp.iloc[:, :7]
            temp.columns = ["Lab_Name", "Test_Name", "Price", "City", "Area", "Latitude", "Longitude"]
            df = temp

    df = df.fillna("")

    print("Detected columns:", df.columns.tolist())

    return df


@app.route("/")
def home():
    df = load_data()

    if "City" not in df.columns or "Area" not in df.columns or "Test_Name" not in df.columns:
        return f"Column error. Detected columns: {df.columns.tolist()}"

    cities = sorted(df["City"].dropna().astype(str).unique().tolist()) if not df.empty else []
    areas = sorted(df["Area"].dropna().astype(str).unique().tolist()) if not df.empty else []
    tests = sorted(df["Test_Name"].dropna().astype(str).unique().tolist()) if not df.empty else []

    return render_template("index.html", cities=cities, areas=areas, tests=tests)


@app.route("/suggest-tests", methods=["GET"])
def suggest_tests():
    df = load_data()
    query = request.args.get("q", "").strip().lower()

    if df.empty or "Test_Name" not in df.columns:
        return jsonify([])

    all_tests = sorted(df["Test_Name"].astype(str).dropna().unique().tolist())

    if not query:
        return jsonify(all_tests)

    suggestions = [test for test in all_tests if query in test.lower()]
    return jsonify(suggestions)


@app.route("/search", methods=["POST"])
def search():
    df = load_data()

    if df.empty:
        return jsonify([])

    required_cols = ["Test_Name", "City", "Area", "Price"]
    for col in required_cols:
        if col not in df.columns:
            return jsonify({"error": f"Missing column: {col}", "columns_found": df.columns.tolist()})

    test_name = request.form.get("test_name", "").strip().lower()
    city = request.form.get("city", "").strip().lower()
    area = request.form.get("area", "").strip().lower()

    filtered_df = df.copy()

    if test_name:
        filtered_df = filtered_df[
            filtered_df["Test_Name"].astype(str).str.lower().str.contains(test_name, na=False)
        ]

    if city:
        filtered_df = filtered_df[
            filtered_df["City"].astype(str).str.lower() == city
        ]

    if area:
        filtered_df = filtered_df[
            filtered_df["Area"].astype(str).str.lower() == area
        ]

    if not filtered_df.empty and "Price" in filtered_df.columns:
        filtered_df["Price"] = pd.to_numeric(filtered_df["Price"], errors="coerce")
        filtered_df = filtered_df.sort_values(by="Price", ascending=True)

    return jsonify(filtered_df.to_dict(orient="records"))


@app.route("/upload-prescription", methods=["POST"])
def upload_prescription():
    df = load_data()

    if "prescription" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["prescription"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    try:
        extracted_text = pytesseract.image_to_string(Image.open(file_path)).lower()
    except Exception as e:
        return jsonify({"error": f"OCR failed: {str(e)}"}), 500

    matched_tests = []
    if not df.empty and "Test_Name" in df.columns:
        unique_tests = sorted(df["Test_Name"].astype(str).dropna().unique().tolist())
        for test in unique_tests:
            if test.lower() in extracted_text:
                matched_tests.append(test)

    return jsonify({
        "extracted_text": extracted_text,
        "matched_tests": matched_tests
    })


@app.route("/get-tests", methods=["GET"])
def get_tests():
    df = load_data()
    if df.empty or "Test_Name" not in df.columns:
        return jsonify([])
    return jsonify(sorted(df["Test_Name"].astype(str).dropna().unique().tolist()))


@app.route("/get-areas", methods=["GET"])
def get_areas():
    df = load_data()
    if df.empty or "Area" not in df.columns:
        return jsonify([])
    return jsonify(sorted(df["Area"].astype(str).dropna().unique().tolist()))


if __name__ == "__main__":
    app.run(debug=True)