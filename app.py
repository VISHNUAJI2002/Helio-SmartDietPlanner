from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
import joblib
import numpy as np
import tensorflow as tf
import random
from datetime import datetime
import json
import re 
from itsdangerous import URLSafeTimedSerializer
# --- NEW: Import Flask-Mail ---
from flask_mail import Mail, Message

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/ProjectHelio")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# --- NEW: Configure Flask-Mail ---
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail = Mail(app) # Initialize Flask-Mail

mongo = PyMongo(app)

s = URLSafeTimedSerializer(app.secret_key)

# --- CORRECT: Models are loaded correctly here ---
model = tf.keras.models.load_model("model/diet_model.keras")
scaler = joblib.load("model/scaler.pkl")
meal_encoder = joblib.load("model/meal_encoder.pkl")
# --- END CORRECT ---


# --- Load Diet, Workout, and Health Tip Data ---
def load_diet_plans():
    try:
        with open('data/diet_plans.json', 'r') as f:
            data = json.load(f)
        return {diet['name']: diet for diet in data['diets']}
    except Exception as e:
        print(f"ERROR loading diet plans: {e}")
        return {}

def load_workout_plans():
    try:
        with open('data/workouts.json', 'r') as f:
            data = json.load(f)
        return data.get('workout_plans', [])
    except Exception as e:
        print(f"ERROR loading workout plans: {e}")
        return []

def load_health_tips():
    try:
        with open('data/health_tips.json', 'r') as f:
            data = json.load(f)
        return data.get('tips', [])
    except Exception as e:
        print(f"ERROR loading health tips: {e}")
        return []

DIET_PLANS_DATA = load_diet_plans()
WORKOUT_PLANS_DATA = load_workout_plans()
HEALTH_TIPS_DATA = load_health_tips()


login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]
        self.password_hash = user_data["password"]
        self.email = user_data.get("email")

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email") 
        password = request.form.get("password")
        
        if len(password) < 5:
            flash("Password must be at least 5 characters long.", "danger")
            return redirect(url_for("register"))
        if not re.search(r"\d", password):
            flash("Password must contain at least one number.", "danger")
            return redirect(url_for("register"))
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            flash("Password must contain at least one special character.", "danger")
            return redirect(url_for("register"))

        if mongo.db.users.find_one({"username": username}):
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))
        
        if mongo.db.users.find_one({"email": email}):
            flash("Email address is already registered.", "danger")
            return redirect(url_for("register"))
            
        hashed_pw = generate_password_hash(password)
        mongo.db.users.insert_one({"username": username, "email": email, "password": hashed_pw})
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user_data = mongo.db.users.find_one({"email": email})
        if user_data and check_password_hash(user_data["password"], password):
            user = User(user_data)
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid email or password", "danger")
    return render_template("login.html")


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = mongo.db.users.find_one({"email": email})

        if user:
            token = s.dumps(email, salt='password-reset-salt')
            reset_url = url_for('reset_password', token=token, _external=True)
            
            try:
                subject = "Password Reset Request for Helio"
                body = f"Hello,\n\nPlease click the following link to reset your password:\n{reset_url}\n\nIf you did not request this, please ignore this email."
                msg = Message(subject=subject, recipients=[email], body=body)
                mail.send(msg)
                flash("A password reset link has been sent to your email.", "success")
            except Exception as e:
                print(f"Email sending failed: {e}")
                flash("Failed to send reset email. Please try again later.", "danger")
        else:
            flash("Email address not found.", "danger")
        
        return redirect(url_for("forgot_password"))
        
    return render_template("forgot_password.html")


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=1800)
    except:
        flash("The password reset link is invalid or has expired.", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("password")
        
        if len(new_password) < 5:
            flash("Password must be at least 5 characters long.", "danger")
            return render_template("reset_password.html", token=token)

        hashed_pw = generate_password_hash(new_password)
        mongo.db.users.update_one({"email": email}, {"$set": {"password": hashed_pw}})
        
        flash("Your password has been reset successfully! You can now login.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html", token=token)


@app.route("/dashboard")
@login_required
def dashboard():
    profile = mongo.db.profiles.find_one({"user_id": current_user.id})
    return render_template( "dashboard.html", profile=profile )


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        age = request.form.get("age")
        gender = request.form.get("gender")
        height_cm = request.form.get("height_cm")
        weight_kg = request.form.get("weight_kg")
        bmi = None
        if height_cm and weight_kg:
            try:
                height_m = float(height_cm) / 100
                weight = float(weight_kg)
                bmi = round(weight / (height_m ** 2), 1)
            except (ValueError, ZeroDivisionError):
                bmi = None
        data = {
            "user_id": current_user.id, "age": age, "gender": gender,
            "height_cm": height_cm, "weight_kg": weight_kg, "bmi": bmi,
            "chronic_disease": request.form.get("chronic_disease"),
            "blood_pressure_systolic": request.form.get("blood_pressure_systolic"),
            "blood_pressure_diastolic": request.form.get("blood_pressure_diastolic"),
            "cholesterol_level": request.form.get("cholesterol_level"),
            "blood_sugar_level": request.form.get("blood_sugar_level"),
            "sleep_hours": request.form.get("sleep_hours"),
        }
        mongo.db.profiles.update_one({"user_id": current_user.id}, {"$set": data}, upsert=True)
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))
    profile = mongo.db.profiles.find_one({"user_id": current_user.id})
    return render_template("profile.html", profile=profile)


# --- REMOVED: Duplicate and incorrect model loading lines were here ---

@app.route("/get-prediction")
@login_required
def get_prediction():
    profile = mongo.db.profiles.find_one({"user_id": current_user.id}) or {}
    if not all(k in profile for k in ["age", "gender", "height_cm", "weight_kg"]) or not profile["age"]:
        return jsonify({"success": False, "message": "Please complete your profile first! Age, gender, height, and weight are required."})
    try:
        features = [
            float(profile.get("age")), float(profile.get("gender")), float(profile.get("height_cm")), float(profile.get("weight_kg")),
            float(profile.get("bmi") or 24.2), float(profile.get("chronic_disease") or 0),
            float(profile.get("blood_pressure_systolic") or 120), float(profile.get("blood_pressure_diastolic") or 80),
            float(profile.get("cholesterol_level") or 180), float(profile.get("blood_sugar_level") or 95),
            float(profile.get("sleep_hours") or 7),
        ]
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid data in profile. Please check your details."})

    features_scaled = scaler.transform([features])
    prediction = model.predict(features_scaled)
    meal_idx = int(np.argmax(prediction))
    meal_plan_map = {0: "Balanced Diet", 1: "High Protein", 2: "Low Carb", 3: "Low Fat", 4: "Mediterranean"}
    meal_plan_name = meal_plan_map.get(meal_idx)

    if not meal_plan_name or meal_plan_name not in DIET_PLANS_DATA:
        return jsonify({"success": False, "message": "Could not find a matching diet plan for the prediction."})
    
    predicted_diet_data = DIET_PLANS_DATA[meal_plan_name]
    all_recommendations = predicted_diet_data.get("meal_options", [])
    
    single_recommendation = None
    if all_recommendations:
        single_recommendation = random.choice(all_recommendations)

    return jsonify({ "success": True, "meal_plan": meal_plan_name, "recommendation": single_recommendation })


@app.route("/get-swap", methods=["GET"])
@login_required
def get_swap():
    diet_name = request.args.get("diet_name")
    meal_type = request.args.get("meal_type")
    current_meal = request.args.get("current_meal")

    if not diet_name or not meal_type or not current_meal:
        return jsonify({"success": False, "message": "Missing required parameters."}), 400

    diet_data = DIET_PLANS_DATA.get(diet_name)
    if not diet_data:
        return jsonify({"success": False, "message": "Invalid diet name."}), 404

    meal_options = diet_data.get("meal_options", [])
    possible_swaps = [
        option[meal_type] for option in meal_options 
        if meal_type in option and option[meal_type] != current_meal
    ]

    if not possible_swaps:
        return jsonify({"success": True, "new_meal": current_meal})

    new_meal = random.choice(possible_swaps)
    return jsonify({"success": True, "new_meal": new_meal})


@app.route("/workout-planner", methods=["GET"])
@login_required
def workout_planner():
    if request.args.get('json') == 'true':
        goal = request.args.get('goal')
        level = request.args.get('level')
        duration = request.args.get('duration')
        found_plan = None
        for plan in WORKOUT_PLANS_DATA:
            if plan['goal'] == goal and plan['level'] == level and plan['duration'] == duration:
                found_plan = plan
                break
        if found_plan:
            return jsonify({"success": True, "plan": found_plan})
        else:
            return jsonify({"success": False, "message": "No matching workout found."})
    return render_template("workout_planner.html")


@app.route("/save-workout", methods=["POST"])
@login_required
def save_workout():
    data = request.json
    if not data or 'title' not in data or 'plan' not in data:
        return jsonify({"success": False, "message": "Invalid data."}), 400
    saved_workout = {
        "user_id": current_user.id, "title": data.get("title"),
        "description": data.get("description"), "plan": data.get("plan"),
        "saved_at": datetime.utcnow()
    }
    mongo.db.saved_workouts.insert_one(saved_workout)
    return jsonify({"success": True, "message": "Workout saved successfully!"})


@app.route("/save-prediction", methods=["POST"])
@login_required
def save_prediction():
    data = request.json
    meal_plan_name = data.get("meal_plan_name")
    meals = data.get("meals")
    if not meal_plan_name or not meals:
        return jsonify({"success": False, "message": "Missing data."}), 400
    saved_plan = {
        "user_id": current_user.id, "meal_plan_name": meal_plan_name,
        "meals": meals, "saved_at": datetime.utcnow()
    }
    mongo.db.saved_plans.insert_one(saved_plan)
    return jsonify({"success": True, "message": "Plan saved successfully!"})


@app.route("/saved-plans")
@login_required
def saved_plans():
    user_saved_diets = list(mongo.db.saved_plans.find({"user_id": current_user.id}).sort("saved_at", -1))
    user_saved_workouts = list(mongo.db.saved_workouts.find({"user_id": current_user.id}).sort("saved_at", -1))
    return render_template("saved_plans.html", saved_diets=user_saved_diets, saved_workouts=user_saved_workouts)


@app.route("/delete-plan/<string:plan_id>", methods=["DELETE"])
@login_required
def delete_plan(plan_id):
    result = mongo.db.saved_plans.delete_one({"_id": ObjectId(plan_id), "user_id": current_user.id})
    if result.deleted_count == 1:
        return jsonify({"success": True, "message": "Plan deleted successfully."})
    else:
        return jsonify({"success": False, "message": "Plan not found or permission denied."}), 404


@app.route("/delete-workout/<string:workout_id>", methods=["DELETE"])
@login_required
def delete_workout(workout_id):
    result = mongo.db.saved_workouts.delete_one({"_id": ObjectId(workout_id), "user_id": current_user.id})
    if result.deleted_count == 1:
        return jsonify({"success": True, "message": "Workout deleted successfully."})
    else:
        return jsonify({"success": False, "message": "Workout not found or permission denied."}), 404


@app.route("/get-daily-tip")
@login_required
def get_daily_tip():
    """API endpoint to get a random health tip."""
    if not HEALTH_TIPS_DATA:
        return jsonify({"success": False, "message": "Health tips are currently unavailable."})
    
    tip = random.choice(HEALTH_TIPS_DATA)
    return jsonify({"success": True, "tip": tip})


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)

