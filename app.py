import os
import secrets
import bcrypt
import io
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file, send_from_directory, Response, current_app
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_session import Session
from fpdf import FPDF
import pdfkit
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import secrets  # Secure key generation
from flask import Flask, request, jsonify, Response, current_app
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import os
import io


app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["hospital_db"]
users_collection = db["users"]
patients_collection = db["patients"]
consultations_collection = db["consultations"]
diagnostics_collection = db["diagnostics"]
appointments_collection = db["appointments"]
medical_records = db["medical_records"]

# Configure Uploads
UPLOAD_FOLDER = os.path.join(os.getcwd(), "static/uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_access_key():
    return secrets.token_hex(8)  # Generates a secure access key

# 🔹 Serve Medical Record Upload Page
@app.route("/upload_record_page")
def upload_record_page():
    return render_template("upload_record.html")  # Ensure you have this HTML page

# 🔹 Serve View Records Page
@app.route("/view_records_page")
def view_records_page():
    return render_template("view_records.html")  # Ensure you have this HTML page

# 🔹 Patient Uploads Medical Record
@app.route("/upload_record", methods=["POST"])
def upload_record():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file format"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    access_key = generate_access_key()
    patient_id = session.get("patient_id")  # Ensure session contains patient ID

    record = {
        "patient_id": patient_id,
        "filename": filename,
        "filepath": filepath,
        "access_key": access_key,
        "uploaded_at": datetime.utcnow(),
    }
    medical_records.insert_one(record)

    return jsonify({"message": "File uploaded successfully", "access_key": access_key})

# 🔹 Doctor Enters Access Key to Fetch Medical Records
@app.route("/get_records", methods=["POST"])
def get_records():
    data = request.json
    access_key = data.get("access_key")

    record = medical_records.find_one({"access_key": access_key})
    if not record:
        return jsonify({"error": "Invalid Access Key"}), 400

    return jsonify({
        "filename": record["filename"],
        "filepath": url_for("serve_file", filename=record["filename"], _external=True),
        "uploaded_at": record["uploaded_at"].strftime("%Y-%m-%d %H:%M:%S")
    })

# 🔹 Serve Uploaded Medical Records Securely
@app.route("/serve_file/<filename>")
def serve_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        address = request.form["address"]
        role = request.form["role"]
        walletAddress = request.form["walletAddress"]
        specialization = request.form.get("specialization", "")  # Only applicable for doctors

        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            flash("⚠️ Username already exists!", "danger")  # Error toast
            return redirect(url_for("signup"))

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # Save user data in MongoDB
        user_data = {
            "username": username,
            "password": hashed_password,
            "email": email,
            "mobile": mobile,
            "address": address,
            "role": role,
            "walletAddress":walletAddress
        }

        if role == "doctor":
            user_data["specialization"] = specialization  # Store specialization for doctors

        users_collection.insert_one(user_data)

        flash("✅ Signup successful! Please log in.", "success")  # Success toast
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users_collection.find_one({"username": username})
        print(user)
        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            session["user_id"] = str(user["_id"])  # Store user ID in session
            session["username"] = user["username"]
            session["role"] = user["role"]

            flash("Login successful!", "success")

            # Redirect patients to book_appointment, doctors to dashboard
            if user["role"] == "patient":
                return redirect(url_for("book_appointment"))
            else:
                return redirect(url_for("dashboard"))

        flash("Invalid username or password!", "danger")

    return render_template("login.html")


# # User Login
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]

#         user = users_collection.find_one({"username": username})
#         if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
#             session["user_id"] = str(user["_id"])  # Store user ID in session
#             session["username"] = username
#             session["role"] = user["role"]
#             flash("Login successful!", "success")
#             return redirect(url_for("dashboard"))
#         else:
#             flash("Invalid username or password!", "danger")

#     return render_template("login.html")


# Dashboard Route
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for("login"))

    role = session["role"]
    return render_template("dashboard.html", role=role)


# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/admission", methods=["GET", "POST"])
def admission_form():
    if "username" not in session or session["role"] != "patient":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))
    
    today_date = datetime.today().strftime('%Y-%m-%d')  # Format YYYY-MM-DD
    
    if request.method == "POST":
        print("request.form",request)
        patient_data = {
            "admission_date": request.form.get("admission_date", today_date),  
            "name": request.form["name"],
            "dob": request.form["dob"],
            "age": request.form["age"],
            "height": request.form["height"],
            "weight": request.form["weight"],
            "gender": request.form["gender"], 
            "marital_status": request.form["marital_status"],
            "referring_doctor": request.form["referring_doctor"],
            "last_exam": request.form["last_exam"],
            "medical_problems": request.form["medical_problems"],
            "allergies": request.form["allergies"],
            "medications": request.form["medications"],
            "medical_history": request.form["medical_history"],
            "smoking": request.form["smoking"],
            "alcohol": request.form["alcohol"],
            "aadhaar_number": request.form["aadhaar_number"],  # New Field
            "has_insurance": request.form["has_insurance"],  # New Field
            "insurance_company": request.form.get("insurance_company", ""),  # New Field (Optional)
            "insurance_id": request.form.get("insurance_id", ""),  # New Field (Optional)
            "username": session["username"],
            "status": "pending_review",
            "hash" : request.form.get("hash_id", "")
        }
        result = patients_collection.insert_one(patient_data)

        flash("Admission form submitted successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("admission_form.html", today_date=today_date)



# Doctor Reviews Pending Patients
@app.route("/patients_for_review")
def patients_for_review():
    if "username" not in session or session["role"] != "doctor":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    pending_patients = list(patients_collection.find({"status": "pending_review"}))
    return render_template("patients_for_review.html", patients=pending_patients)


# Doctor Reviews Admission Details
@app.route("/review_patient/<patient_id>")
def review_patient(patient_id):
    if "username" not in session or session["role"] != "doctor":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    patient_data = patients_collection.find_one({"_id": ObjectId(patient_id)})
    print("patient_data",patient_data)
    if not patient_data:
        flash("Patient not found!", "danger")
        return redirect(url_for("patients_for_review"))

    return render_template("review_patient.html", patient=patient_data)


def generate_diagnostic_graph(patient_id, metrics_data):
    plt.figure(figsize=(10, 5))  # Adjust figure size for better readability

    # Extract keys (labels) and values from the dictionary
    labels = list(metrics_data.keys())
    # values = [metrics_data[key][-1] for key in labels]  # Take the latest value
    numeric_labels = []
    numeric_values = []

    for key in labels:
        try:
            val = float(metrics_data[key][-1])  # Convert to float (latest value)
            numeric_labels.append(key)
            numeric_values.append(val)
        except (ValueError, TypeError):
            print(f"Skipping non-numeric value for key '{key}': {metrics_data[key][-1]}")

    # Create a bar graph
    bars = plt.bar(numeric_labels, numeric_values, color=["#3498db", "#2ecc71", "#e74c3c", "#f39c12", "#9b59b6", "#1abc9c"])
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=30, ha="right", fontsize=12)
    plt.yticks(fontsize=12)
    
    # Set labels and title
    plt.ylabel("Measurement", fontsize=14)
    plt.title(f"Diagnostic Metrics for Patient {patient_id}", fontsize=16)

    # Add value labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 5, round(yval, 2), ha="center", fontsize=12)

    # Set a fixed y-axis range up to 500
    plt.ylim(0, 500)

    # Save and return the file path
    file_path = f"static/reports/{patient_id}_report.png"
    plt.savefig(file_path, bbox_inches="tight")
    plt.close()

    return file_path


@app.route("/consultation/<patient_id>", methods=["GET", "POST"])
def consultation_form(patient_id):
    if "username" not in session or session["role"] != "doctor":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    patient_data = patients_collection.find_one({"_id": ObjectId(patient_id)})
    if not patient_data:
        flash("Patient not found!", "danger")
        return redirect(url_for("patients_for_review"))

    smoking_status = patient_data.get("smoking", "Unknown")
    alcohol_consumption = patient_data.get("alcohol", "Unknown")

    if request.method == "POST":
        new_observation = request.form["observations"]
        detailed_metrics = {
            "Blood Pressure": int(request.form["blood_pressure"]),
            "Heart Rate": int(request.form["heart_rate"]),
            "Sugar Level": int(request.form["sugar_level"]),
            "Cholesterol": int(request.form["cholesterol"]),
            "Weight": float(request.form["weight"]),
            "BMI": float(request.form["bmi"]),
            "consultation_hash" : request.form.get("consultation_id", "")
        }

        existing_report = diagnostics_collection.find_one({"patient_id": patient_id})

        if existing_report:
            diagnostics_collection.update_one(
                {"patient_id": patient_id},
                {
                    "$set": {
                        "smoking_status": smoking_status,
                        "alcohol_consumption": alcohol_consumption,
                        "detailed_analysis": existing_report["detailed_analysis"],
                        "timestamp": datetime.utcnow(),
                        "report_file": generate_diagnostic_graph(patient_id, existing_report["detailed_analysis"])
                    }
                }
            )
        else:
            print("generate",  generate_diagnostic_graph(patient_id, {k: [v] for k, v in detailed_metrics.items()}))
            diagnostics_collection.insert_one({
                "patient_id": patient_id,
                "doctor_name": session["username"],
                "observations": new_observation,
                "detailed_analysis": {k: [v] for k, v in detailed_metrics.items()},
                "smoking_status": smoking_status,
                "alcohol_consumption": alcohol_consumption,
                "timestamp": datetime.utcnow(),
                "report_file": generate_diagnostic_graph(patient_id, {k: [v] for k, v in detailed_metrics.items()})
            })

        # **Fix: Update the status explicitly with correct ObjectId conversion**
        update_result = patients_collection.update_one(
            {"_id": ObjectId(patient_id)},
            {"$set": {"status": "consulted" , "consultation_hash" : request.form.get("consultation_id", "")}}  # Update status and hash
        )
        print("update_result",update_result)
        if update_result.modified_count == 0:
            flash("Status update failed!", "danger")
        else:
            flash("Consultation updated, diagnostic report generated, and status updated!", "success")

        return redirect(url_for("diagnostic_report", patient_id=patient_id))

    return render_template(
        "consultation_form.html", 
        patient=patient_data, 
        smoking_status=smoking_status, 
        alcohol_consumption=alcohol_consumption
    )



# @app.route("/consultation/<patient_id>", methods=["GET", "POST"])
# def consultation_form(patient_id):
#     if "username" not in session or session["role"] != "doctor":
#         flash("Access denied!", "danger")
#         return redirect(url_for("dashboard"))

#     patient_data = patients_collection.find_one({"_id": ObjectId(patient_id)})
#     if not patient_data:
#         flash("Patient not found!", "danger")
#         return redirect(url_for("patients_for_review"))

#     smoking_status = patient_data.get("smoking", "Unknown")
#     alcohol_consumption = patient_data.get("alcohol", "Unknown")

#     if request.method == "POST":
#         new_observation = request.form["observations"]
#         detailed_metrics = {
#             "Blood Pressure": int(request.form["blood_pressure"]),
#             "Heart Rate": int(request.form["heart_rate"]),
#             "Sugar Level": int(request.form["sugar_level"]),
#             "Cholesterol": int(request.form["cholesterol"]),
#             "Weight": float(request.form["weight"]),
#             "BMI": float(request.form["bmi"]),
#         }

#         # 🔹 Generate a unique access key for the report
#         access_key = secrets.token_hex(8)

#         # Save diagnostic data along with the access key
#         diagnostics_collection.update_one(
#             {"patient_id": str(patient_id)},
#             {
#                 "$set": {
#                     "doctor_name": session["username"],
#                     "observations": new_observation,
#                     "detailed_analysis": detailed_metrics,
#                     "timestamp": datetime.utcnow(),
#                     "access_key": access_key,  # Store the generated key
#                     "report_file": generate_diagnostic_graph(patient_id, detailed_metrics)
#                 }
#             },
#             upsert=True
#         )

#         # Update patient status
#         patients_collection.update_one(
#             {"_id": ObjectId(patient_id)},
#             {"$set": {"status": "consulted"}}
#         )

#         flash(f"Consultation saved! Patient's access key: {access_key}", "success")
#         return redirect(url_for("diagnostic_report_access", patient_id=patient_id))

#     return render_template(
#         "consultation_form.html",
#         patient=patient_data,
#         smoking_status=smoking_status,
#         alcohol_consumption=alcohol_consumption
#     )

@app.route("/diagnostic_report_access/<patient_id>", methods=["GET", "POST"])
def diagnostic_report_access(patient_id):
    if "username" not in session or session["role"] != "patient":
        flash("Access denied!", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        entered_key = request.form["access_key"]

        # Fetch stored access key
        diagnostic_data = diagnostics_collection.find_one({"patient_id": str(patient_id)})
       
        if diagnostic_data and diagnostic_data.get("access_key") == entered_key:
            return redirect(url_for("diagnostic_report", patient_id=patient_id))

        flash("Invalid access key! Please enter the correct key.", "danger")

    return render_template("enter_access_key.html", patient_id=patient_id)


# Generate Diagnostic Report
@app.route("/diagnostic_report/<patient_id>")
def diagnostic_report(patient_id):
    if "username" not in session:
        return redirect(url_for("login"))

    try:
        patient_data = patients_collection.find_one({"_id": ObjectId(patient_id)})
        if not patient_data:
            return "Patient not found", 404
    except:
        return "Invalid patient ID format", 400

    diagnostic_data = diagnostics_collection.find_one({"patient_id": str(patient_id)})
    
    print("patient_data"   ,patient_data)

    if not diagnostic_data:
        return "Diagnostic report not found", 404

    return render_template(
        "diagnostic_report.html",
        patient_data=patient_data,
        consultation_data=diagnostic_data,
        report_id=str(patient_data["_id"]),  # Convert here instead of Jinja
        report_file=diagnostic_data.get("report_file", ""),
        timestamp=diagnostic_data.get("timestamp", "N/A"),
        combined_observations=diagnostic_data.get("observations", "No observations available"),
    )


@app.route("/download_report", methods=["POST"])
def download_report():
    report_data = request.json  
    image_url = report_data.get("report_image_path", None)  

    # Convert image URL to an absolute file path
    if image_url:
        image_filename = os.path.basename(image_url)  # Extract filename
        image_path = os.path.join(current_app.root_path, "static", "reports", image_filename)
    else:
        image_path = None

    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(name='Header', fontSize=14, leading=20, alignment=1, spaceAfter=12))
    styles.add(ParagraphStyle(name='SubHeader', fontSize=12, leading=16, alignment=1, spaceAfter=6))
    styles.add(ParagraphStyle(name='Body', fontSize=10, leading=14, spaceAfter=6))

    elements = []

    # Add logo
    logo_path = os.path.join(current_app.root_path, "static", "logo.png")  # Ensure you have a logo.png in the static folder
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=100, height=50)
        elements.append(logo)
        elements.append(Spacer(1, 12))

    # Add title
    title = Paragraph("In-Patient Discharge Summary", styles['Header'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Patient Details
    patient_details = [
        ["Patient Name", report_data.get('patient_name', 'N/A')],
        ["Age", report_data.get('age', 'N/A')],
        ["Gender", report_data.get('gender', 'N/A')],
        ["Admission Date", report_data.get('admission_date', 'N/A')]
    ]
    patient_table = Table(patient_details, colWidths=[200, 200])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004080')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 12))

    # Doctor Details
    doctor_details = [
        ["Doctor Name", report_data.get('doctor_name', 'N/A')],
        ["Hospital", report_data.get('hospital_name', 'N/A')],
        ["Consultation Date", report_data.get('consultation_date', 'N/A')]
    ]
    doctor_table = Table(doctor_details, colWidths=[200, 200])
    doctor_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004080')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(doctor_table)
    elements.append(Spacer(1, 12))

    # Health Metrics
    health_metrics = [
        ["Blood Pressure", report_data.get('blood_pressure', 'N/A')],
        ["Heart Rate", report_data.get('heart_rate', 'N/A')],
        ["Sugar Level", report_data.get('sugar_level', 'N/A')],
        ["Cholesterol", report_data.get('cholesterol', 'N/A')],
        ["Weight", report_data.get('weight', 'N/A')],
        ["BMI", report_data.get('bmi', 'N/A')],
        ["Smoking Status", report_data.get('smoking_status', 'N/A')],
        ["Alcohol Consumption", report_data.get('alcohol_consumption', 'N/A')]
    ]
    health_table = Table(health_metrics, colWidths=[200, 200])
    health_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004080')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(health_table)
    elements.append(Spacer(1, 12))

    # Doctor's Observations
    observations_title = Paragraph("<b>Doctor's Observations:</b>", styles['SubHeader'])
    observations_text = Paragraph(report_data.get('observations', 'No observations provided.'), styles['Body'])
    elements.append(observations_title)
    elements.append(observations_text)
    elements.append(Spacer(1, 12))

    # Add the Report Image to the PDF
    if image_path and os.path.exists(image_path):
        try:
            img = Image(image_path, width=300, height=150)
            elements.append(img)
        except Exception as e:
            print("Error loading image:", str(e))
    else:
        print("Image not found:", image_path)

    pdf.build(elements)
    buffer.seek(0)

    return Response(buffer, mimetype="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=diagnostic_report.pdf"})

@app.route("/my_reports")
def user_reports():
    if "username" not in session:
        return redirect(url_for("login"))

    # Fetch all patient records associated with the logged-in user
    patients = list(patients_collection.find({"username": session["username"]}))

    # Get patient IDs as strings
    patient_ids = [str(patient["_id"]) for patient in patients]

    # Fetch all diagnostic reports related to the user's patients
    reports = list(diagnostics_collection.find({"patient_id": {"$in": patient_ids}}))

    return render_template("my_reports.html", reports=reports )

@app.route("/get_doctors")
def get_doctors():
    specialization = request.args.get("specialization")
    doctors = users_collection.find({"role": "doctor", "specialization": specialization})
    doctor_list = [{"_id": str(doc["_id"]), "username": doc["username"]} for doc in doctors]
    return jsonify(doctor_list)

@app.route("/book_appointment", methods=["GET", "POST"])
def book_appointment():
    if "username" not in session or session.get("role") != "patient":
        flash("Please log in as a patient to book an appointment.", "danger")
        return redirect(url_for("login"))

    # Get available specializations from doctors
    specializations = users_collection.distinct("specialization", {"role": "doctor"})
    
    # Get all doctors
    doctors = list(users_collection.find({"role": "doctor"}, {"_id": 0, "username": 1, "specialization": 1}))

    if request.method == "POST":
        patient_username = session["username"]
        doctor_username = request.form["doctor"]
        specialization = request.form["specialization"]
        date = request.form["date"]
        time = request.form["time"]

        appointment_data = {
            "patient_username": patient_username,
            "doctor_username": doctor_username,
            "specialization": specialization,
            "date": date,
            "time": time,
            "status": "Pending",
        }

        appointments_collection.insert_one(appointment_data)
        flash("Appointment booked successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template("book_appointment.html", specializations=specializations, doctors=doctors)

@app.route("/view_appointments", methods=["GET"])
def view_appointments():
    if "username" not in session or session.get("role") != "doctor":
        flash("Please log in as a doctor to view appointments.", "danger")
        return redirect(url_for("login"))

    doctor_username = session["username"]
    appointments = list(appointments_collection.find({"doctor_username": doctor_username}))

    return render_template("view_appointments.html", appointments=appointments)


if __name__ == "__main__":
    app.run(debug=True)
