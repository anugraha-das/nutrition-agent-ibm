# 🌿 NutriGenius — AI-Powered Nutrition Agent

> **IBM Watsonx.ai + Granite Models · Flask · Bootstrap 5 · Dark Mode · Mobile-First**

A fully-featured AI Nutrition web application that provides personalized meal plans, calorie analysis, BMI calculations, healthy recipe suggestions, and family diet recommendations — powered by IBM Watsonx.ai's Granite LLM.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💬 **AI Chat** | Conversational nutrition coaching with IBM Granite LLM |
| 📋 **Meal Planner** | 1–14 day personalized Indian meal plans |
| ⚖️ **BMI Calculator** | BMI, BMR, TDEE, and calorie targets |
| 👨‍👩‍👧 **Family Profiles** | Multi-member family nutrition plans |
| 🍳 **Recipe Finder** | Healthy recipes from available ingredients |
| 📊 **Dashboard** | Nutrition stats, macro breakdown, meal log |
| 🌙 **Dark Mode** | Persistent dark/light theme toggle |
| 📱 **Mobile-First** | Fully responsive Bootstrap 5 UI |

---

## 🏗️ Architecture & System Design

### 1. High-Level System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                        Frontend (Browser)                        │
│  Bootstrap 5 UI + Dark Mode + Mobile-First                      │
│  (Chat, Meal Planner, BMI Calculator, Dashboard)                │
└────────────────────────┬───────────────────────────────────────┘
                         │ HTTP/JSON
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                    Flask Web Application                         │
│                         (app.py)                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  /api/chat              Generate AI response             │   │
│  │  /api/meal-plan         Create personalized meal plan    │   │
│  │  /api/bmi               BMI, BMR, TDEE calculation       │   │
│  │  /api/analyze-food      Nutritional analysis             │   │
│  │  /api/family-plan       Family nutrition planning        │   │
│  │  /api/healthy-recipes   Recipe suggestions               │   │
│  │  /api/health-check      Connectivity status              │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬───────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
   ┌──────────────────┐         ┌──────────────────────┐
   │  DEMO Mode       │         │ IBM Watsonx.ai       │
   │  (Fallback)      │         │ + Granite Models     │
   │  - Hardcoded     │         │                      │
   │    responses     │         │ - Real AI inference  │
   │  - Demo data     │         │ - Context-aware      │
   └──────────────────┘         └──────────────────────┘
```

### 2. Request-Response Flow (Chat & AI Processing)

```
┌────────────────────────────────────────────────────────────────┐
│                      User Request                               │
│  (Message, History, User Profile/Context)                      │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │   generate_ai_response()       │
        │  - Accept: message, history    │
        │  - Context: user profile       │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────────────┐
        │  build_system_prompt()                 │
        │  ┌────────────────────────────────┐   │
        │  │ Inject AGENT_INSTRUCTIONS:     │   │
        │  │  • PERSONA (name, role, tone)  │   │
        │  │  • SPECIALIZATION (diet focus) │   │
        │  │  • SAFETY_RULES (disclaimers)  │   │
        │  │  • INDIAN_FOODS (knowledge)    │   │
        │  │  • CALORIES_DB (quick ref)     │   │
        │  │  • RESPONSE_STYLE (format)     │   │
        │  └────────────────────────────────┘   │
        └────────────┬──────────────────────────┘
                     │
        ┌────────────▼──────────────┐
        │ Watsonx.ai Model          │
        │ Available?                │
        └────────────┬──────────────┘
                     │
        ┌────────────┴────────────────┐
        │                             │
       YES                            NO
        │                             │
        ▼                             ▼
    ┌──────────────┐         ┌───────────────┐
    │  Call Model  │         │ _demo_response│
    │  inference   │         │ (Fallback)    │
    │  API         │         └───────────────┘
    └──────────────┘
        │
        ▼
    ┌──────────────────────────────┐
    │  Add Disclaimer (if needed)  │
    │  & Format Response           │
    └──────────────┬───────────────┘
                   │
                   ▼
        ┌────────────────────────┐
        │ JSON Response to Client│
        │ - response text        │
        │ - timestamp            │
        │ - model ID             │
        └────────────────────────┘
```

### 3. Data Processing Pipeline for Meal Plans

```
┌──────────────────────────────┐
│  User Profile Input          │
│  • Age, Gender, Weight       │
│  • Height, Activity Level    │
│  • Goal, Diet Type           │
│  • Health Conditions         │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────────┐
│  generate_meal_plan()            │
│  - Construct detailed prompt     │
│  - Include user profile data     │
└──────────┬──────────────────────┘
           │
           ▼
┌────────────────────────────────────────┐
│  AI Generates:                         │
│  • Breakfast (with calories/macros)    │
│  • Lunch (with calories/macros)        │
│  • Snacks (with calories/macros)       │
│  • Dinner (with calories/macros)       │
│  • Daily totals (protein/carbs/fat)    │
└──────────┬────────────────────────────┘
           │
           ▼
    ┌─────────────────────────┐
    │  JSON Meal Plan         │
    │  - Days: 7/14           │
    │ - Full meal breakdown   │
    │ - Nutritional values    │
    └─────────────────────────┘
```

### 4. LangFlow Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    LangFlow Workflow Pipeline                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐                                                │
│  │ 1. User      │                                                │
│  │    Input     │                                                │
│  └──────┬───────┘                                                │
│         │                                                         │
│         ▼                                                         │
│  ┌──────────────────────────────────────┐                        │
│  │ 2. Input Validation & Formatting     │                        │
│  │    - Parse JSON request              │                        │
│  │    - Validate user data              │                        │
│  │    - Sanitize input                  │                        │
│  └──────┬───────────────────────────────┘                        │
│         │                                                         │
│         ▼                                                         │
│  ┌──────────────────────────────────────┐                        │
│  │ 3. Context & Memory Management       │                        │
│  │    - Load user profile               │                        │
│  │    - Retrieve chat history           │                        │
│  │    - Build conversation context      │                        │
│  └──────┬───────────────────────────────┘                        │
│         │                                                         │
│         ▼                                                         │
│  ┌──────────────────────────────────────┐                        │
│  │ 4. Prompt Construction & Injection   │                        │
│  │    ┌─ PERSONA Configuration           │                        │
│  │    ├─ SPECIALIZATION Rules            │                        │
│  │    ├─ SAFETY_RULES & Disclaimers      │                        │
│  │    ├─ INDIAN_FOODS Knowledge Base     │                        │
│  │    ├─ CALORIES_DB Reference           │                        │
│  │    └─ RESPONSE_STYLE Formatting       │                        │
│  └──────┬───────────────────────────────┘                        │
│         │                                                         │
│    ┌────┴────────┐                                               │
│    │             │                                               │
│    ▼             ▼                                               │
│  ┌──────────┐  ┌────────────────────────┐                        │
│  │ Decision │  │ IBM Watsonx.ai Check   │                        │
│  │ Branch   │  │ - Credentials valid?   │                        │
│  │ 5a.      │  │ - API accessible?      │                        │
│  └──────────┘  └────────────────────────┘                        │
│    │             │                                               │
│    │         YES │                      NO                       │
│    │             │                       │                       │
│    │             ▼                       ▼                       │
│    │     ┌──────────────────────┐  ┌───────────────┐             │
│    │     │ 6. LLM Inference     │  │ 5b. Demo Mode │             │
│    │     │ - Send prompt        │  │ - Return      │             │
│    │     │ - Stream/await       │  │   hardcoded   │             │
│    │     │   response           │  │   response    │             │
│    │     └──────┬───────────────┘  └───────┬───────┘             │
│    │            │                         │                     │
│    └────────────┼─────────────────────────┘                     │
│                 │                                                │
│                 ▼                                                │
│  ┌──────────────────────────────────────┐                        │
│  │ 7. Response Processing & Formatting  │                        │
│  │    - Parse LLM output                │                        │
│  │    - Add disclaimers (if needed)     │                        │
│  │    - Format JSON response            │                        │
│  │    - Add metadata (timestamp, model) │                        │
│  └──────┬───────────────────────────────┘                        │
│         │                                                         │
│         ▼                                                         │
│  ┌──────────────────────────────────────┐                        │
│  │ 8. Output & Client Response          │                        │
│  │    - Send JSON to frontend           │                        │
│  │    - Update UI (streaming/complete)  │                        │
│  │    - Log interaction                 │                        │
│  └──────────────────────────────────────┘                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 5. API Endpoint Coverage

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask Routes                             │
├──────────────────┬──────────────────────────────────────────┤
│ GET  /           │ Serve index.html (main UI)               │
├──────────────────┼──────────────────────────────────────────┤
│ POST /api/chat   │ AI conversational coaching               │
│                  │ → generate_ai_response()                 │
├──────────────────┼──────────────────────────────────────────┤
│ POST /api/meal-  │ 1–14 day personalized meal plans         │
│      plan        │ → generate_meal_plan()                   │
├──────────────────┼──────────────────────────────────────────┤
│ POST /api/bmi    │ BMI, BMR, TDEE calculations              │
│                  │ → calculate_bmi()                        │
├──────────────────┼──────────────────────────────────────────┤
│ POST /api/       │ Analyze nutritional content of foods     │
│      analyze-    │ → analyze_food()                         │
│      food        │                                          │
├──────────────────┼──────────────────────────────────────────┤
│ POST /api/       │ Multi-member family diet plans           │
│      family-plan │ → family_plan()                          │
├──────────────────┼──────────────────────────────────────────┤
│ POST /api/       │ 3+ healthy recipe suggestions            │
│      healthy-    │ → healthy_recipes()                      │
│      recipes     │                                          │
├──────────────────┼──────────────────────────────────────────┤
│ GET  /api/       │ Connection status & model availability   │
│      health-check│ → health_check()                         │
└──────────────────┴──────────────────────────────────────────┘
```

### 6. Core Components & Knowledge Base Injection

```
┌─────────────────────────────────────────────────────────────┐
│          AGENT_INSTRUCTIONS Dictionary                       │
│              (Global Configuration)                          │
├─────────────────────────────────────────────────────────────┤
│ PERSONA                     SPECIALIZATION                  │
│ ├─ name: "NutriGenius"      ├─ primary_focus               │
│ ├─ role: AI Coach           ├─ supported_diets (8 types)   │
│ ├─ tone: friendly           ├─ preferred_cuisines          │
│ └─ language: English        └─ always_consider             │
│                                                             │
│ SAFETY_RULES                RESPONSE_STYLE                 │
│ ├─ always_add_disclaimer    ├─ use_bullet_points           │
│ ├─ never_do (4 rules)       ├─ include_emojis              │
│ └─ always_refer_doctor_for  ├─ format_meal_plans_as_tables │
│                             └─ max_response_length         │
│                                                             │
│ INDIAN_FOODS (Knowledge Base)      CALORIES_DB              │
│ ├─ staples (8 items)               ├─ 15+ common foods      │
│ ├─ protein_sources (8 items)       ├─ Idli, Roti, Dal, etc. │
│ ├─ healthy_snacks (6 items)        └─ Quick calorie lookup  │
│ ├─ superfoods (5 items)                                      │
│ └─ regional_preferences (5 regions)                         │
└─────────────────────────────────────────────────────────────┘
           │
           │ Injected into every system prompt
           ▼
  ┌──────────────────────┐
  │ Full System Prompt   │
  │ (~1KB contextual)    │
  └──────────────────────┘
```

### 7. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Deployment Options                       │
├──────────────────┬──────────────────────────────────────────┤
│ Local Dev        │  python app.py (Flask debug mode)        │
├──────────────────┼──────────────────────────────────────────┤
│ Production       │  gunicorn --bind 0.0.0.0:5000 app:app    │
│ (WSGI)           │  (2 workers for concurrency)             │
├──────────────────┼──────────────────────────────────────────┤
│ Docker           │  Dockerfile → Docker image → Container   │
│                  │  Exposed: port 5000                      │
├──────────────────┼──────────────────────────────────────────┤
│ IBM Code Engine  │  ibmcloud ce application create          │
│                  │  + environment secrets                   │
├──────────────────┼──────────────────────────────────────────┤
│ Render/Railway/  │  Git-connected CD pipeline               │
│ Fly.io           │  Automatic deployment on push            │
└──────────────────┴──────────────────────────────────────────┘
        │
        ├─ .env file (credentials)
        ├─ IBM_API_KEY, WATSONX_PROJECT_ID
        └─ FLASK_SECRET_KEY, PORT
```

---

## 📁 Project Structure

```
nutrition_agent/
├── app.py                  # Flask backend + AGENT_INSTRUCTIONS
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
├── .env                    # Your credentials (DO NOT COMMIT)
├── templates/
│   └── index.html          # Full frontend (Bootstrap + CSS + JS)
└── README.md               # This file
```

---

## 🚀 Quick Start

### 1. Clone / Download the project

```bash
git clone https://github.com/anugraha-das/nutrition-agent-ibm.git
cd nutrition-agent-ibm
```

### 2. Create & activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
# Copy the template
cp .env.example .env
```

Open `.env` and fill in your IBM Cloud credentials:

```env
IBM_API_KEY=your_ibm_cloud_api_key_here
WATSONX_PROJECT_ID=your_watsonx_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
GRANITE_MODEL_ID=ibm/granite-13b-instruct-v2
FLASK_SECRET_KEY=your-random-secret-key
FLASK_DEBUG=True
PORT=5000
```

### 5. Run the application

```bash
python app.py
```

Open your browser at **http://localhost:5000** 🎉

> **Note:** If IBM credentials are not configured, the app runs in **Demo Mode** with pre-built responses.

---

## 🔑 Getting IBM Cloud Credentials

### IBM Cloud API Key
1. Go to [IBM Cloud Console](https://cloud.ibm.com/)
2. Navigate to **Manage → Access (IAM) → API Keys**
3. Click **Create an IBM Cloud API key**
4. Copy and save the key in your `.env` file

### Watsonx.ai Project ID
1. Go to [IBM Watsonx.ai](https://dataplatform.cloud.ibm.com/wx/home)
2. Create or open a project
3. Go to **Manage → General** tab
4. Copy the **Project ID** to your `.env` file

### Available Granite Models
| Model ID | Description |
|----------|-------------|
| `ibm/granite-13b-instruct-v2` | Recommended — balanced speed & quality |
| `ibm/granite-3-8b-instruct` | Faster, lighter model |
| `ibm/granite-20b-multilingual` | Multilingual support |

---

## 🎛️ Customizing the Agent

All agent behavior is controlled through the `AGENT_INSTRUCTIONS` dict at the **top of `app.py`**:

```python
AGENT_INSTRUCTIONS = {
    "PERSONA": {
        "name": "NutriGenius",        # ← Change agent name
        "role": "AI Nutrition Coach", # ← Change role description
        "tone": "friendly, motivating, evidence-based",  # ← Change tone
    },
    "SPECIALIZATION": {
        "primary_focus": "Balanced Indian & Mediterranean nutrition",
        "supported_diets": ["Vegetarian", "Vegan", "Keto", ...],
    },
    "SAFETY_RULES": {
        "never_do": [
            "Prescribe medication",
            "Diagnose medical conditions",
            ...
        ],
    },
    "INDIAN_FOODS": {
        "staples": ["Dal", "Roti", "Brown rice", ...],
        "superfoods": ["Turmeric", "Amla", "Moringa", ...],
    },
    "CALORIES_DB": {
        "Idli (1 piece)": "39 kcal",  # ← Add your own food entries
        ...
    },
}
```

### Examples of customization:
- **Change to Keto specialist**: Set `primary_focus` to `"Ketogenic diet and low-carb nutrition"`
- **Add Telugu cuisine**: Add entries to `INDIAN_FOODS.regional_preferences`
- **Stricter safety**: Add more items to `SAFETY_RULES.never_do`
- **Different language**: Change `PERSONA.language` to `"Hindi / Hinglish"`

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Main web application |
| `POST` | `/api/chat` | AI chat conversation |
| `POST` | `/api/meal-plan` | Generate personalized meal plan |
| `POST` | `/api/bmi` | Calculate BMI, BMR, TDEE |
| `POST` | `/api/analyze-food` | Nutritional analysis of foods |
| `POST` | `/api/family-plan` | Family nutrition plan |
| `POST` | `/api/healthy-recipes` | Recipe suggestions |
| `GET` | `/api/health-check` | Connection status |

### Example API call

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Give me a 7-day Indian meal plan for weight loss", "history": []}'
```

---

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
```

```bash
# Build and run
docker build -t nutrigenius .
docker run -p 5000:5000 --env-file .env nutrigenius
```

---

## ☁️ Cloud Deployment

### IBM Code Engine
```bash
ibmcloud ce application create \
  --name nutrigenius \
  --image icr.io/your-namespace/nutrigenius:latest \
  --env-from-secret nutrigenius-secrets \
  --port 5000
```

### Render / Railway / Fly.io
1. Connect your GitHub repository
2. Set environment variables in the dashboard
3. Deploy command: `gunicorn --bind 0.0.0.0:$PORT app:app`

---

## 🛡️ Security Notes

- **Never commit `.env`** — add it to `.gitignore`
- Use strong random `FLASK_SECRET_KEY` in production
- Set `FLASK_DEBUG=False` in production
- Consider rate limiting for public deployments

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `flask` | 3.0.3 | Web framework |
| `flask-cors` | 4.0.1 | CORS support |
| `python-dotenv` | 1.0.1 | .env file loading |
| `ibm-watsonx-ai` | 1.1.2 | IBM Watsonx.ai SDK |
| `gunicorn` | 22.0.0 | Production WSGI server |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

**Made with ❤️ using IBM Watsonx.ai + Granite Models**
