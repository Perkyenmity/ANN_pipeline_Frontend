import streamlit as st
import requests

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Loan Risk Predictor",
    page_icon="🏦",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
    <style>
        .main { background-color: #f0f4f8; }
        h1 { color: #1a3c5e; font-family: 'Georgia', serif; }
        .stButton>button {
            background-color: #1a3c5e;
            color: white;
            border-radius: 8px;
            padding: 0.5em 2em;
            font-size: 1rem;
            font-weight: bold;
            border: none;
        }
        .stButton>button:hover { background-color: #2e6da4; }
        .result-box {
            background-color: #e8f4e8;
            border-left: 5px solid #28a745;
            padding: 1rem;
            border-radius: 6px;
            font-size: 1.2rem;
        }
        .error-box {
            background-color: #fde8e8;
            border-left: 5px solid #dc3545;
            padding: 1rem;
            border-radius: 6px;
        }
    </style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🏦 Loan Risk Prediction")
st.markdown("Fill in the applicant details below to predict loan approval risk using our ANN model.")
st.divider()

# ── Input Form ────────────────────────────────────────────────────────────────
st.subheader("📋 Applicant Details")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age", min_value=0, max_value=120, value=30, step=1,
                          help="Applicant age (0–120)")
    income = st.number_input("Annual Income (₹)", min_value=0.0, value=50000.0, step=1000.0,
                             help="Annual income in rupees")
    loan_amount = st.number_input("Loan Amount (₹)", min_value=0.0, value=200000.0, step=5000.0,
                                  help="Requested loan amount")
    credit_score = st.number_input("Credit Score", min_value=300, max_value=850, value=650, step=1,
                                   help="Credit score between 300 and 850")
    years_experience = st.number_input("Years of Experience", min_value=0, value=5, step=1,
                                       help="Total years of work experience")

with col2:
    gender = st.selectbox("Gender", options=["Male", "Female"],
                          help="Applicant's gender")
    education = st.selectbox("Education Level",
                             options=["High School", "Bachelors", "Masters", "PhD"],
                             help="Highest education qualification")
    city = st.selectbox("City",
                        options=["Chicago", "Houston", "San Francisco", "New York"],
                        help="City of residence")
    employment_type = st.selectbox("Employment Type",
                                   options=["Salaried", "Self-Employed", "Unemployed"],
                                   help="Current employment status")

st.divider()

# ── Predict Button ─────────────────────────────────────────────────────────────
if st.button("🔍 Predict Loan Risk"):

    payload = {
        "Age": age,
        "Income": income,
        "LoanAmount": loan_amount,
        "CreditScore": credit_score,
        "YearsExperience": years_experience,
        "Gender": gender,
        "Education": education,
        "City": city,
        "EmploymentType": employment_type,
    }

    with st.spinner("Running prediction..."):
        try:
            response = requests.post("https://ann-pipeline-backend.onrender.com/predict", json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()

            # ── Display Result ─────────────────────────────────────────────────
            st.subheader("📊 Prediction Result")

            # Adjust the key below if your API returns a different field name
            prediction = result.get("prediction") or result.get("result") or result.get("loan_approved")

            if prediction is not None:
                st.markdown(f"""
                    <div class="result-box">
                        ✅ <strong>Predicted Value:</strong> {prediction}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.warning(f"Received response but couldn't find prediction key. Full response: {result}")

            # Show full response in expander
            with st.expander("🔎 See full API response"):
                st.json(result)

            # Show input summary
            with st.expander("📄 See your submitted inputs"):
                st.json(payload)

        except requests.exceptions.ConnectionError:
            st.markdown("""
                <div class="error-box">
                    ❌ <strong>Connection Error:</strong> Could not reach the API at
                    <code>https://ann-pipeline-backend.onrender.com</code>. Make sure your FastAPI server is running.
                </div>
            """, unsafe_allow_html=True)

        except requests.exceptions.HTTPError as e:
            st.markdown(f"""
                <div class="error-box">
                    ❌ <strong>HTTP Error:</strong> {e}<br>
                    Response: {response.text}
                </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Unexpected error: {e}")

# ── Sidebar Info ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This app uses an **Artificial Neural Network (ANN)** model to predict
    loan risk based on applicant details.

    **API Endpoint:** `POST /predict`
    **Backend:** FastAPI on `https://ann-pipeline-backend.onrender.com`
    """)
    st.divider()
    st.markdown("**Model Info**")
    try:
        info = requests.get("https://ann-pipeline-backend.onrender.com/model-info", timeout=3).json()
        st.json(info)
    except Exception:
        st.warning("Start the FastAPI server to see model info.")

    st.divider()
    st.markdown("**Health Check**")
    try:
        health = requests.get("https://ann-pipeline-backend.onrender.com/health", timeout=3).json()
        st.success(f"API Status: {health.get('status', 'OK')}")
    except Exception:
        st.error("API is offline")
