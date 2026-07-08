"""
╔══════════════════════════════════════════════════════════════════════════════╗
║           AI-POWERED NUTRITION AGENT — IBM Watsonx.ai + Granite             ║
║                      Flask Backend  |  app.py                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

HOW TO CUSTOMISE THE AGENT
──────────────────────────
Edit the AGENT_INSTRUCTIONS dict below to change:
  • PERSONA        – agent name, role, tone
  • SPECIALIZATION – diet focus (e.g. "Keto", "Ayurvedic", "Diabetic-friendly")
  • SAFETY_RULES   – disclaimers & hard limits the agent must respect
  • INDIAN_FOODS   – preferred Indian ingredients / cuisine knowledge
  • RESPONSE_STYLE – verbosity, language, bullet vs. prose
  • CALORIES_DB    – quick calorie look-up reference injected into every prompt
"""

import os, json, re, traceback
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from dotenv import load_dotenv

# ─── IBM Watsonx.ai SDK ───────────────────────────────────────────────────────
try:
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    WATSONX_AVAILABLE = True
except ImportError:
    WATSONX_AVAILABLE = False
    print("⚠  ibm-watsonx-ai not installed — running in DEMO mode.")

load_dotenv()

# ══════════════════════════════════════════════════════════════════════════════
#  AGENT INSTRUCTIONS  ←  CUSTOMISE THIS SECTION
# ══════════════════════════════════════════════════════════════════════════════
AGENT_INSTRUCTIONS = {

    # ── Who the agent is ──────────────────────────────────────────────────────
    "PERSONA": {
        "name": "NutriGenius",
        "role": "AI Nutrition & Wellness Coach",
        "tone": "friendly, motivating, and evidence-based",
        "language": "English (switch to simple language when asked)",
        "greeting": (
            "Namaste! 🌿 I am NutriGenius, your personal AI Nutrition Coach. "
            "I can help you with personalized meal plans, calorie analysis, "
            "healthy recipe suggestions, and family diet recommendations. "
            "How can I nourish your day?"
        ),
    },

    # ── Diet specialization focus ─────────────────────────────────────────────
    "SPECIALIZATION": {
        "primary_focus": "Balanced Indian & Mediterranean nutrition",
        "supported_diets": [
            "Vegetarian", "Vegan", "Jain", "Keto", "Low-carb",
            "Diabetic-friendly", "Heart-healthy", "Weight-loss",
            "Weight-gain / muscle building", "Ayurvedic",
        ],
        "preferred_cuisines": ["Indian", "Mediterranean", "South Asian"],
        "always_consider": [
            "Local seasonal ingredients",
            "Budget-friendly options",
            "Cooking time constraints",
            "Cultural food preferences",
        ],
    },

    # ── Safety & medical disclaimer rules ────────────────────────────────────
    "SAFETY_RULES": {
        "always_add_disclaimer": True,
        "disclaimer_text": (
            "⚠️ This advice is for educational purposes only and does not "
            "replace professional medical or dietitian consultation."
        ),
        "never_do": [
            "Prescribe medication or supplements as treatment",
            "Diagnose medical conditions",
            "Recommend extreme calorie restriction below 1200 kcal/day without medical supervision",
            "Advise against prescribed medications",
        ],
        "always_refer_doctor_for": [
            "Pregnancy or breastfeeding",
            "Diagnosed diabetes, kidney disease, heart disease",
            "Eating disorders",
            "Children under 12 (general guidance only)",
        ],
    },

    # ── Indian food knowledge base injected into prompts ─────────────────────
    "INDIAN_FOODS": {
        "staples": [
            "Dal (lentils)", "Roti/Chapati", "Brown rice", "Quinoa",
            "Poha (flattened rice)", "Idli", "Dosa", "Upma",
        ],
        "protein_sources": [
            "Paneer", "Chana (chickpeas)", "Rajma (kidney beans)",
            "Moong dal", "Tofu", "Curd/Yogurt", "Sprouts",
        ],
        "healthy_snacks": [
            "Roasted chana", "Makhana (fox nuts)", "Fruit chaat",
            "Dhokla", "Sprout salad", "Coconut water",
        ],
        "superfoods": [
            "Turmeric (anti-inflammatory)", "Amla (Vitamin C)",
            "Moringa (iron + protein)", "Flaxseeds (omega-3)",
            "Methi/Fenugreek (blood sugar)", "Ashwagandha",
        ],
        "regional_preferences": {
            "North Indian": "Whole wheat roti, dal, sabzi, lassi",
            "South Indian": "Idli, sambar, rasam, coconut-based dishes",
            "Bengali": "Fish curry, mustard-based dishes, mishti doi",
            "Gujarati": "Dhokla, thepla, dal dhokli, khichdi",
            "Maharashtrian": "Bhakri, pithla, puran poli, sol kadhi",
        },
    },

    # ── Response style preferences ────────────────────────────────────────────
    "RESPONSE_STYLE": {
        "use_bullet_points": True,
        "include_emojis": True,
        "max_response_length": "comprehensive but concise",
        "always_include_in_meal_plans": [
            "Calorie count", "Macronutrients (protein/carbs/fat)",
            "Preparation time", "Key nutrients",
        ],
        "format_meal_plans_as_tables": True,
    },

    # ── Quick calorie reference (used in prompt context) ──────────────────────
    "CALORIES_DB": {
        "Idli (1 piece)": "39 kcal",
        "Chapati/Roti": "71 kcal",
        "Cooked white rice (1 cup)": "206 kcal",
        "Dal (1 cup cooked)": "230 kcal",
        "Paneer (100g)": "265 kcal",
        "Boiled egg": "78 kcal",
        "Banana (medium)": "89 kcal",
        "Apple (medium)": "95 kcal",
        "Milk (1 glass 250ml)": "149 kcal",
        "Curd (1 cup)": "98 kcal",
        "Chicken breast (100g)": "165 kcal",
        "Almonds (10 pieces)": "70 kcal",
        "Walnuts (5 halves)": "87 kcal",
        "Avocado (half)": "120 kcal",
        "Oats (1/2 cup dry)": "150 kcal",
    },
}
# ══════════════════════════════════════════════════════════════════════════════

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
CORS(app)

# ─── Watsonx.ai client initialisation ────────────────────────────────────────
_watsonx_model = None

def get_watsonx_model():
    global _watsonx_model
    if _watsonx_model is not None:
        return _watsonx_model
    if not WATSONX_AVAILABLE:
        return None
    api_key    = os.getenv("IBM_API_KEY")
    project_id = os.getenv("WATSONX_PROJECT_ID")
    url        = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    model_id   = os.getenv("GRANITE_MODEL_ID", "ibm/granite-13b-instruct-v2")

    if not api_key or not project_id:
        print("⚠  IBM_API_KEY or WATSONX_PROJECT_ID not set — using DEMO mode.")
        return None
    try:
        credentials = Credentials(url=url, api_key=api_key)
        client      = APIClient(credentials)
        _watsonx_model = ModelInference(
            model_id   = model_id,
            api_client = client,
            project_id = project_id,
            params     = {
                GenParams.MAX_NEW_TOKENS: 1024,
                GenParams.TEMPERATURE:    0.7,
                GenParams.TOP_P:          0.9,
                GenParams.TOP_K:          50,
                GenParams.REPETITION_PENALTY: 1.1,
            },
        )
        print(f"✅ Watsonx.ai connected — model: {model_id}")
        return _watsonx_model
    except Exception as exc:
        print(f"❌ Watsonx.ai init failed: {exc}")
        return None


# ─── Build the system prompt from AGENT_INSTRUCTIONS ─────────────────────────
def build_system_prompt(user_context: dict = None) -> str:
    ai   = AGENT_INSTRUCTIONS
    ctx  = user_context or {}
    cal_list = "\n".join(
        f"  • {food}: {cal}"
        for food, cal in ai["CALORIES_DB"].items()
    )
    indian_staples = ", ".join(ai["INDIAN_FOODS"]["staples"])
    indian_protein = ", ".join(ai["INDIAN_FOODS"]["protein_sources"])
    superfoods     = ", ".join(ai["INDIAN_FOODS"]["superfoods"])
    never_do       = "\n".join(f"  - {r}" for r in ai["SAFETY_RULES"]["never_do"])
    supported_diets = ", ".join(ai["SPECIALIZATION"]["supported_diets"])

    user_section = ""
    if ctx:
        user_section = f"""
Current User Profile:
  Name: {ctx.get('name', 'User')}
  Age: {ctx.get('age', 'unknown')}
  Gender: {ctx.get('gender', 'unknown')}
  Weight: {ctx.get('weight', 'unknown')} kg
  Height: {ctx.get('height', 'unknown')} cm
  Goal: {ctx.get('goal', 'healthy lifestyle')}
  Activity Level: {ctx.get('activity', 'moderate')}
  Dietary Preference: {ctx.get('diet', 'balanced')}
  Health Conditions: {ctx.get('conditions', 'none')}
  Daily Calorie Target: {ctx.get('calories', 'maintenance')}
"""

    return f"""You are {ai['PERSONA']['name']}, an {ai['PERSONA']['role']}.
Tone: {ai['PERSONA']['tone']}.
Supported diets: {supported_diets}.

Indian Food Knowledge:
  Staples: {indian_staples}
  Protein sources: {indian_protein}
  Superfoods: {superfoods}

Quick Calorie Reference:
{cal_list}

Safety Rules — NEVER:
{never_do}

Always append this disclaimer when giving dietary advice:
"{ai['SAFETY_RULES']['disclaimer_text']}"

{user_section}
Respond in a structured, helpful manner using bullet points and emojis where appropriate.
Keep meal plans organized with calorie counts, macronutrients, and preparation times.
"""


# ─── Generate AI response ─────────────────────────────────────────────────────
def generate_ai_response(user_message: str, conversation_history: list,
                          user_context: dict = None) -> str:
    model = get_watsonx_model()
    system_prompt = build_system_prompt(user_context)

    # Build conversation string for Granite instruct format
    history_text = ""
    for msg in conversation_history[-6:]:          # last 6 turns for context
        role = "User" if msg["role"] == "user" else "NutriGenius"
        history_text += f"{role}: {msg['content']}\n"

    full_prompt = (
        f"{system_prompt}\n\n"
        f"Conversation:\n{history_text}"
        f"User: {user_message}\n"
        f"NutriGenius:"
    )

    if model:
        try:
            result   = model.generate_text(prompt=full_prompt)
            response = result.strip() if isinstance(result, str) else str(result)
            # Ensure disclaimer is present when needed
            keywords = ["calorie", "diet", "nutrition", "meal", "food", "weight",
                        "protein", "carb", "fat", "vitamin", "mineral"]
            if any(kw in user_message.lower() for kw in keywords):
                disclaimer = AGENT_INSTRUCTIONS["SAFETY_RULES"]["disclaimer_text"]
                if disclaimer not in response:
                    response += f"\n\n{disclaimer}"
            return response
        except Exception as exc:
            traceback.print_exc()
            return _demo_response(user_message)
    else:
        return _demo_response(user_message)


def _demo_response(user_message: str) -> str:
    """Fallback demo responses when Watsonx.ai is not configured."""
    msg = user_message.lower()
    if any(k in msg for k in ["meal plan", "diet plan", "weekly plan"]):
        return """🌿 **Sample 7-Day Indian Nutrition Plan** (1800 kcal/day)

**Day 1:**
| Meal | Food | Calories |
|------|------|---------|
| 🌅 Breakfast (7–8 am) | 2 Idli + Sambar + Green chutney | ~250 kcal |
| 🌞 Mid-morning | 1 banana + 5 almonds | ~159 kcal |
| 🍽️ Lunch (1 pm) | 2 Roti + Dal + Sabzi + Curd | ~550 kcal |
| ☕ Snack (4 pm) | Roasted chana + green tea | ~170 kcal |
| 🌙 Dinner (7–8 pm) | Brown rice + Rajma + Salad | ~520 kcal |

**Macronutrients:** Protein 75g | Carbs 240g | Fat 45g

> ⚠️ This advice is for educational purposes only and does not replace professional medical or dietitian consultation."""

    if any(k in msg for k in ["calorie", "calories", "how many cal"]):
        return """🔥 **Calorie Guide for Common Indian Foods:**

| Food Item | Serving | Calories |
|-----------|---------|---------|
| Idli | 1 piece | 39 kcal |
| Chapati/Roti | 1 medium | 71 kcal |
| Rice (cooked) | 1 cup | 206 kcal |
| Dal | 1 cup | 230 kcal |
| Paneer | 100g | 265 kcal |
| Curd | 1 cup | 98 kcal |

**Daily Calorie Needs (approximate):**
- 🚶 Sedentary adult: 1600–2000 kcal
- 🏃 Moderately active: 2000–2400 kcal
- 💪 Very active: 2400–3000 kcal

> ⚠️ This advice is for educational purposes only and does not replace professional medical or dietitian consultation."""

    if any(k in msg for k in ["bmi", "weight", "overweight", "obese"]):
        return """📊 **BMI & Healthy Weight Guide:**

| BMI Range | Category |
|-----------|---------|
| < 18.5 | Underweight |
| 18.5 – 24.9 | Normal weight ✅ |
| 25.0 – 29.9 | Overweight |
| ≥ 30.0 | Obese |

**For healthy weight management:**
- 🥗 Eat balanced meals with whole grains, dal, vegetables
- 🚶 30 min moderate activity daily
- 💧 8–10 glasses water/day
- 😴 7–8 hours sleep

> ⚠️ This advice is for educational purposes only and does not replace professional medical or dietitian consultation."""

    if any(k in msg for k in ["protein", "muscle", "gym", "workout"]):
        return """💪 **High-Protein Indian Foods:**

🥚 **Animal Sources:**
- Eggs (6g/egg), Chicken breast (31g/100g), Fish (22g/100g)

🌱 **Plant Sources:**
- Paneer (18g/100g), Moong dal (24g/100g), Rajma (9g/100g)
- Chickpeas (19g/100g), Tofu (17g/100g), Edamame (11g/100g)

**Tip:** Combine rice + dal = complete protein profile!

**Daily protein target:**
- Sedentary: 0.8g per kg body weight
- Active/Gym: 1.2–2.0g per kg body weight

> ⚠️ This advice is for educational purposes only and does not replace professional medical or dietitian consultation."""

    return (
        f"🌿 Thank you for your question about: *{user_message}*\n\n"
        "I'm NutriGenius, your AI Nutrition Coach! I can help you with:\n"
        "- 📋 **Personalized meal plans** (Indian, Mediterranean, Keto, etc.)\n"
        "- 🔥 **Calorie & macro analysis** for any food\n"
        "- 👨‍👩‍👧 **Family diet recommendations**\n"
        "- ⚖️ **BMI & weight management** guidance\n"
        "- 🌿 **Healthy recipe suggestions**\n\n"
        "*(Demo mode — connect IBM Watsonx.ai for full AI-powered responses)*\n\n"
        "> ⚠️ This advice is for educational purposes only and does not replace "
        "professional medical or dietitian consultation."
    )


# ══════════════════════════════════════════════════════════════════════════════
#  FLASK ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data    = request.get_json(force=True)
    message = data.get("message", "").strip()
    history = data.get("history", [])
    profile = data.get("profile", {})

    if not message:
        return jsonify({"error": "Empty message"}), 400

    try:
        response = generate_ai_response(message, history, profile)
        return jsonify({
            "response": response,
            "timestamp": datetime.now().strftime("%I:%M %p"),
            "model": os.getenv("GRANITE_MODEL_ID", "ibm/granite-13b-instruct-v2"),
        })
    except Exception as exc:
        traceback.print_exc()
        return jsonify({"error": str(exc)}), 500


@app.route("/api/meal-plan", methods=["POST"])
def generate_meal_plan():
    data    = request.get_json(force=True)
    profile = data.get("profile", {})
    days    = data.get("days", 7)

    prompt = (
        f"Create a detailed {days}-day Indian nutrition meal plan for:\n"
        f"- Age: {profile.get('age', 30)}, Gender: {profile.get('gender', 'any')}\n"
        f"- Weight: {profile.get('weight', 70)}kg, Height: {profile.get('height', 170)}cm\n"
        f"- Goal: {profile.get('goal', 'maintain weight')}\n"
        f"- Diet type: {profile.get('diet', 'balanced vegetarian')}\n"
        f"- Activity level: {profile.get('activity', 'moderate')}\n"
        f"- Health conditions: {profile.get('conditions', 'none')}\n\n"
        f"Include breakfast, lunch, snack, dinner with calorie counts and macros for each day. "
        f"Use Indian recipes and ingredients. Format as a structured table."
    )

    response = generate_ai_response(prompt, [], profile)
    return jsonify({"plan": response, "days": days})


@app.route("/api/bmi", methods=["POST"])
def calculate_bmi():
    data   = request.get_json(force=True)
    weight = float(data.get("weight", 0))
    height = float(data.get("height", 0))
    age    = int(data.get("age", 25))
    gender = data.get("gender", "other")

    if weight <= 0 or height <= 0:
        return jsonify({"error": "Invalid weight or height"}), 400

    bmi = round(weight / ((height / 100) ** 2), 1)

    if bmi < 18.5:
        category, color, advice = "Underweight", "#3b82f6", "increase calorie intake with nutrient-dense foods"
    elif bmi < 25:
        category, color, advice = "Normal Weight ✅", "#22c55e", "maintain your current healthy diet"
    elif bmi < 30:
        category, color, advice = "Overweight", "#f59e0b", "reduce calorie intake by 300–500 kcal/day"
    else:
        category, color, advice = "Obese", "#ef4444", "consult a doctor and follow a supervised diet plan"

    # Rough TDEE calculation
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    activity_map = {
        "sedentary": 1.2, "light": 1.375, "moderate": 1.55,
        "active": 1.725, "very_active": 1.9,
    }
    activity_factor = activity_map.get(data.get("activity", "moderate"), 1.55)
    tdee = round(bmr * activity_factor)

    return jsonify({
        "bmi": bmi,
        "category": category,
        "color": color,
        "advice": advice,
        "bmr": round(bmr),
        "tdee": tdee,
        "weight_loss_calories": tdee - 500,
        "weight_gain_calories": tdee + 500,
    })


@app.route("/api/analyze-food", methods=["POST"])
def analyze_food():
    data  = request.get_json(force=True)
    foods = data.get("foods", "")

    if not foods:
        return jsonify({"error": "No food items provided"}), 400

    prompt = (
        f"Analyze the nutritional content of these foods: {foods}\n"
        "For each item provide: calories, protein, carbohydrates, fats, fiber, "
        "key vitamins/minerals, and a healthiness score out of 10. "
        "Then give an overall meal assessment and improvement suggestions. "
        "Use Indian food equivalents and portion sizes where applicable."
    )
    response = generate_ai_response(prompt, [])
    return jsonify({"analysis": response})


@app.route("/api/family-plan", methods=["POST"])
def family_plan():
    data    = request.get_json(force=True)
    members = data.get("members", [])

    if not members:
        return jsonify({"error": "No family members provided"}), 400

    members_text = "\n".join(
        f"  - {m.get('name', 'Member')}: Age {m.get('age')}, "
        f"{m.get('gender', 'any')}, Goal: {m.get('goal', 'healthy')}, "
        f"Diet: {m.get('diet', 'balanced')}, Conditions: {m.get('conditions', 'none')}"
        for m in members
    )

    prompt = (
        f"Create a comprehensive family nutrition plan for {len(members)} members:\n"
        f"{members_text}\n\n"
        "Provide:\n"
        "1. A common family meal plan that suits everyone\n"
        "2. Individual modifications for each member\n"
        "3. Shopping list for 1 week\n"
        "4. Budget-friendly Indian meal tips\n"
        "5. Family healthy eating habits and tips"
    )
    response = generate_ai_response(prompt, [])
    return jsonify({"plan": response, "member_count": len(members)})


@app.route("/api/healthy-recipes", methods=["POST"])
def healthy_recipes():
    data        = request.get_json(force=True)
    ingredients = data.get("ingredients", "")
    diet_type   = data.get("diet_type", "vegetarian")
    max_time    = data.get("max_time", 30)

    prompt = (
        f"Suggest 3 healthy Indian recipes using these ingredients: {ingredients}\n"
        f"Diet preference: {diet_type}\n"
        f"Max cooking time: {max_time} minutes\n\n"
        "For each recipe include:\n"
        "- Recipe name and brief description\n"
        "- Ingredients with quantities\n"
        "- Step-by-step cooking instructions\n"
        "- Calories per serving and macros\n"
        "- Health benefits\n"
        "- Serving suggestions"
    )
    response = generate_ai_response(prompt, [])
    return jsonify({"recipes": response})


@app.route("/api/health-check")
def health_check():
    model_available = get_watsonx_model() is not None
    return jsonify({
        "status": "healthy",
        "watsonx_connected": model_available,
        "model": os.getenv("GRANITE_MODEL_ID", "ibm/granite-13b-instruct-v2"),
        "timestamp": datetime.now().isoformat(),
        "agent_name": AGENT_INSTRUCTIONS["PERSONA"]["name"],
    })


if __name__ == "__main__":
    port  = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    print(f"\n🌿 {AGENT_INSTRUCTIONS['PERSONA']['name']} starting on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
