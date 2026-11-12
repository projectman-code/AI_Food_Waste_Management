import os
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models.waste_predictor import predict_waste
from models.food_image_analyzer import analyze_food_image
from database import init_db, get_db

app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
init_db()

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def current_user():
    if "user_id" not in session:
        return None
    db = get_db()
    user = db.execute("SELECT id, name, email, role FROM users WHERE id=?", (session["user_id"],)).fetchone()
    db.close()
    return user

@app.context_processor
def inject_user():
    return {"logged_in_user": current_user()}

@app.route("/")
def index():
    db = get_db()
    stats = {
        "donations": db.execute("SELECT COUNT(*) FROM donations WHERE status='Claimed'").fetchone()[0],
        "saved_kg": db.execute("SELECT COALESCE(SUM(quantity_kg),0) FROM donations WHERE status='Claimed'").fetchone()[0],
        "listings": db.execute("SELECT COUNT(*) FROM donations WHERE status='Available'").fetchone()[0],
    }
    db.close()
    return render_template("index.html", stats=stats)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "Donor")
        if not name or not email or len(password) < 6:
            flash("Enter your name, email and a password with at least 6 characters.", "error")
            return redirect(url_for("register"))
        if role not in ("Donor", "NGO", "Admin"):
            role = "Donor"
        db = get_db()
        try:
            db.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)",
                       (name, email, generate_password_hash(password), role))
            db.commit()
            flash("Account created. Please sign in.", "success")
            return redirect(url_for("login"))
        except Exception:
            flash("That email is already registered.", "error")
        finally:
            db.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        db.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    db = get_db()
    if user["role"] == "Admin":
        donations = db.execute("SELECT d.*,u.name AS donor_name FROM donations d JOIN users u ON u.id=d.donor_id ORDER BY d.created_at DESC").fetchall()
    elif user["role"] == "NGO":
        donations = db.execute("SELECT d.*,u.name AS donor_name FROM donations d JOIN users u ON u.id=d.donor_id ORDER BY d.created_at DESC").fetchall()
    else:
        donations = db.execute("SELECT d.*,u.name AS donor_name FROM donations d JOIN users u ON u.id=d.donor_id WHERE d.donor_id=? ORDER BY d.created_at DESC", (user["id"],)).fetchall()
    totals = db.execute("SELECT COUNT(*) AS count, COALESCE(SUM(quantity_kg),0) AS kg FROM donations WHERE status='Claimed'").fetchone()
    db.close()
    return render_template("dashboard.html", donations=donations, totals=totals)

@app.route("/donations/new", methods=["GET", "POST"])
def new_donation():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    if request.method == "POST":
        f = request.form
        try:
            quantity = float(f.get("quantity_kg", 0))
            if quantity <= 0:
                raise ValueError()
        except ValueError:
            flash("Quantity must be a positive number.", "error")
            return redirect(url_for("new_donation"))
        db = get_db()
        db.execute("""INSERT INTO donations(donor_id,food_name,category,quantity_kg,expiry_date,location,description,status)
                      VALUES(?,?,?,?,?,?,?,'Available')""",
                   (user["id"], f.get("food_name","").strip(), f.get("category","Other"),
                    quantity, f.get("expiry_date"), f.get("location","").strip(), f.get("description","").strip()))
        db.commit()
        db.close()
        flash("Surplus food listed successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("new_donation.html")

@app.route("/donations/<int:donation_id>/edit", methods=["GET", "POST"])
@app.route("/edit_donation/<int:donation_id>", methods=["GET", "POST"], endpoint="edit_donation_page")
def edit_donation(donation_id):
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    db = get_db()
    donation = db.execute("SELECT * FROM donations WHERE id=?", (donation_id,)).fetchone()
    if not donation:
        db.close()
        flash("Food listing not found.", "error")
        return redirect(url_for("dashboard"))
    if user["role"] != "Admin" and not (user["role"] == "Donor" and donation["donor_id"] == user["id"]):
        db.close()
        flash("You are not allowed to edit this listing.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        form = request.form
        food_name = form.get("food_name", "").strip()
        try:
            quantity = float(form.get("quantity_kg", 0))
            if not food_name or quantity <= 0:
                raise ValueError()
        except ValueError:
            db.close()
            flash("Enter a food name and a quantity greater than zero.", "error")
            return redirect(url_for("edit_donation", donation_id=donation_id))
        status = form.get("status", donation["status"]) if user["role"] == "Admin" else donation["status"]
        if status not in ("Available", "Claimed"):
            status = donation["status"]
        db.execute("""UPDATE donations SET food_name=?, category=?, quantity_kg=?, expiry_date=?,
                      location=?, description=?, status=? WHERE id=?""",
                   (food_name, form.get("category", "Other"), quantity,
                    form.get("expiry_date") or None, form.get("location", "").strip(),
                    form.get("description", "").strip(), status, donation_id))
        db.commit()
        db.close()
        flash("Food listing updated successfully.", "success")
        return redirect(url_for("dashboard"))

    db.close()
    return render_template("edit_donation.html", donation=donation)


@app.route("/donations/<int:donation_id>/delete", methods=["POST"])
def delete_donation(donation_id):
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    db = get_db()
    donation = db.execute("SELECT donor_id FROM donations WHERE id=?", (donation_id,)).fetchone()
    if not donation:
        db.close()
        flash("Food listing not found.", "error")
        return redirect(url_for("dashboard"))
    if user["role"] != "Admin" and not (user["role"] == "Donor" and donation["donor_id"] == user["id"]):
        db.close()
        flash("You are not allowed to delete this listing.", "error")
        return redirect(url_for("dashboard"))
    db.execute("DELETE FROM donations WHERE id=?", (donation_id,))
    db.commit()
    db.close()
    flash("Food listing deleted successfully.", "success")
    return redirect(url_for("dashboard"))


@app.route("/donations/<int:donation_id>/claim", methods=["POST"])
def claim_donation(donation_id):
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    if user["role"] not in ("NGO", "Admin"):
        flash("Only NGO or Admin accounts can claim a donation.", "error")
        return redirect(url_for("dashboard"))
    db = get_db()
    db.execute("UPDATE donations SET status='Claimed', claimed_by=? WHERE id=? AND status='Available'",
               (user["id"], donation_id))
    db.commit()
    db.close()
    flash("Donation claim recorded (coordinate collection with the donor).", "success")
    return redirect(url_for("dashboard"))

@app.route("/ai/predict", methods=["GET", "POST"])
def prediction():
    if not current_user():
        return redirect(url_for("login"))
    result = None
    if request.method == "POST":
        try:
            result = predict_waste(
                stock_kg=float(request.form["stock_kg"]),
                expected_demand_kg=float(request.form["demand_kg"]),
                days_to_expiry=int(request.form["days_to_expiry"]),
                temperature_c=float(request.form["temperature_c"])
            )
        except (ValueError, KeyError):
            flash("Please enter valid numeric values.", "error")
    return render_template("prediction.html", result=result)

@app.route("/ai/image", methods=["GET", "POST"])
def image_analysis():
    if not current_user():
        return redirect(url_for("login"))
    result = None
    image_url = None
    if request.method == "POST":
        file = request.files.get("food_image")
        if not file or not file.filename:
            flash("Choose an image first.", "error")
        elif not allowed_file(file.filename):
            flash("Allowed image formats: PNG, JPG, JPEG and WEBP.", "error")
        else:
            safe_name = secure_filename(file.filename)
            stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
            filename = stamp + "_" + safe_name
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            result = analyze_food_image(path)
            image_url = url_for("static", filename="uploads/" + filename)
    return render_template("image_analysis.html", result=result, image_url=image_url)

@app.route("/reports")
def reports():
    if not current_user():
        return redirect(url_for("login"))
    db = get_db()
    rows = db.execute("""SELECT category, COUNT(*) AS listings, COALESCE(SUM(quantity_kg),0) AS kg
                         FROM donations GROUP BY category ORDER BY kg DESC""").fetchall()
    totals = db.execute("""SELECT COUNT(*) AS total, COALESCE(SUM(quantity_kg),0) AS kg,
                           SUM(CASE WHEN status='Claimed' THEN quantity_kg ELSE 0 END) AS claimed_kg
                           FROM donations""").fetchone()
    db.close()
    return render_template("reports.html", rows=rows, totals=totals)

if __name__ == "__main__":
    app.run(debug=True)
