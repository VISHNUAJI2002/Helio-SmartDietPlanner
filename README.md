# **Helio - Smart Diet Planner**

**Helio** is an intelligent, full-stack web application designed to help users take control of their health.  
It leverages a **Neural Network** to provide personalized diet and workout recommendations based on a user's unique health profile.

The application serves as a comprehensive wellness dashboard — allowing users to not only receive **AI-driven plans** but also track their progress, save their favorite meals, and get daily health tips.  
The entire frontend is dynamic, fetching and displaying data from the Flask backend without requiring page reloads.

---

## ✨ **Key Features**

### **1. Core ML & Prediction**
- **AI Diet Prediction:** Uses a Keras/TensorFlow Neural Network model to analyze a user’s health metrics (age, BMI, BP, cholesterol, etc.) and predict a suitable diet class (e.g., Balanced, Low Carb, High Protein).  
- **Dynamic Workout Generation:** Generates custom workout plans from a JSON database based on the user’s goal (Weight Loss, Muscle Building), fitness level (Beginner, Active), and available time (15–40 minutes).

---

### **2. User & Profile Management**
- **Secure Authentication:** Full user registration, login, and logout system.  
- **Password Validation:** Enforces strong passwords on registration (min 5 characters, 1 number, 1 special character).  
- **Password Reset:** Secure “Forgot Password” feature that sends a timed reset link via email using Flask-Mail.  
- **Comprehensive User Profile:** Users can create and update their health profile with all metrics used for prediction.  
- **Profile Completion Bar:** A dynamic progress bar on the profile page shows how complete a user’s profile is.  
- **Incomplete Profile Warning:** A friendly modal warns users to fill in optional fields for more accurate predictions.

---

### **3. Interactive Dashboard**
- **Dynamic BMI Gauge:** Real-time ApexCharts gauge visualizing the user’s BMI status.  
- **Daily Health Tip:** Displays a random health tip from a JSON file each time the page loads.  

---

### **4. Dynamic Meal Plan Module**
- **One-Click Prediction:** Instantly generate a random meal plan from the predicted diet class.  
- **Smart Swap:** Replace individual meals (Breakfast, Lunch, Dinner) without changing the rest of the plan.  
- **Save & View Plans:** Save generated diet plans to the user’s account.  
- **Action Buttons:**  
  - **Share:** Copy to clipboard, share via WhatsApp, or use device sharing.  
  - **Print:** Format the plan for printing or downloading.  
  - **Order Food (Swiggy):** Opens a Swiggy search for the specific meal.  
  - **Order Groceries (Blinkit):** Extracts ingredients and opens a Blinkit search.  
  - **Find Stores:** Uses geolocation to open Google Maps with nearby grocery stores.

---

### **5. Workout Planner Module**
- **Dedicated Planner Page:** Generate workout plans based on goal, level, and duration.  
- **Action Buttons:**  
  - **Save & View Plans**  
  - **Share via WhatsApp or Copy to Clipboard**  
  - **Print/Download Workouts**  
  - **"How-to" Links:** YouTube icons open tutorials for each exercise.  

---

### **6. Saved Plans Page**
- **Tabbed Interface:** Separates “Saved Diets” and “Saved Workouts.”  
- **Delete Functionality:** Delete any saved plan using a custom confirmation modal (no default alerts).

---

## 🛠️ **Tech Stack**

### **Backend**
- **Framework:** Flask  
- **Database:** MongoDB (PyMongo)  
- **Machine Learning:** Keras (TensorFlow), Scikit-learn (StandardScaler)  
- **Authentication:** Flask-Login, Werkzeug (for hashing)  
- **Email & Tokens:** Flask-Mail, itsdangerous  
- **Core Languages:** Python, JSON, NumPy  

### **Frontend**
- **Core:** HTML5, CSS3, JavaScript (ES6+)  
- **Framework:** Bootstrap 5  
- **Templating:** Jinja2  
- **Visualization:** ApexCharts.js (BMI gauge), Chart.js (weight chart)  

---

## 📁 **Project Structure**

```
Helio-Smart-Diet-Planner/
├── app.py                   # Main Flask application
├── data/
│   ├── diet_plans.json
│   ├── workouts.json
│   └── health_tips.json
├── model/
│   ├── diet_model.keras     # Trained Neural Network
│   ├── scaler.pkl           # Pre-fitted StandardScaler
│   └── meal_encoder.pkl
├── static/
│   └── css/
│       └── main.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── workout_planner.html
│   └── saved_plans.html
├── .env                     # Local environment variables
├── requirements.txt
└── README.md
```

---

## 🚀 **Setup & Installation**

Follow these steps to run the project locally:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/Helio-Smart-Diet-Planner.git
   cd Helio-Smart-Diet-Planner
   ```

2. **Create and Activate Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a .env File**
   Use `.env.example` as a template and include the following:
   ```bash
   FLASK_SECRET_KEY='your_super_secret_key_here'
   MONGO_URI='your_mongodb_connection_string'

   # For password reset emails
   MAIL_SERVER='smtp.gmail.com'
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME='your-email@gmail.com'
   MAIL_PASSWORD='your-gmail-app-password'
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```

   The app will be live at:  
   👉 **http://127.0.0.1:5000**

---

