import streamlit as st
import requests
import base64
from pathlib import Path

# Helper function to convert your local image file to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 1. Page configuration
st.set_page_config(
    page_title="Belgian Property Price Predictor",
    page_icon="🏠",
    layout="centered"
)

# Dynamically find the project root folder from this script's position
# __file__ is 'project/streamlit/app_frontend.py' -> .parent is 'streamlit' -> .parent.parent is 'project' root
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
image_abs_path = project_root / "images" / "bg_belgium.jpeg"

# Load the background image using the absolute path
try:
    bin_str = get_base64_image(image_abs_path)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bin_str}");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        
        /* 
           Allows the container to stretch up to 1200px wide, 
           while centering it on the wide layout screen.
        */
        .stMainBlockContainer {{
            max-width: 850px !important;
            margin: 0 auto !important;
            background-color: rgba(255, 255, 255, 0.85) !important;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            padding: 3rem;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
       

        /* Customizes the submit button to a prominent, centered block */
        div[data-testid="stFormSubmitButton"] button {{
            background-color: #6D28D9 !important; /* Premium deep violet */
            color: #FFFFFF !important;            /* White button text */
            font-size: 1.25rem !important;        /* Makes text bigger */
            font-weight: bold !important;
            padding: 0.75rem 2.5rem !important;   /* Comfortable padding around text */
            border-radius: 10px !important;
            border: none !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(109, 40, 217, 0.3) !important;
        }}

        /* Subtle button pop animation when hovering your cursor over it */
        div[data-testid="stFormSubmitButton"] button:hover {{
            background-color: #5B21B6 !important; /* Darker violet on hover */
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(109, 40, 217, 0.4) !important;
        }}
        
        </style>
        """,
        unsafe_allow_html=True
    )
except FileNotFoundError:
    st.warning(f"Background image path not found at: {image_abs_path}")


# 2. Define your live Render API endpoint
API_URL = "https://immo-eliza-deployment-9tez.onrender.com/predict"

st.title("🏠 Belgian Property Price Predictor")
st.write("Fill in the structural properties below to estimate the target sales price.")

# 3. Use a clean web form to collect input fields
with st.form("property_form"):
    st.subheader("📍 Location & Type")
    
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("Property Type", ["house", "apartment"])
        province = st.selectbox("Province", ["Luxembourg","Limburg","Flemish Brabant", "Walloon Brabant",
            "Namur","East Flanders", "Antwerp","Liège", "West Flanders","Hainaut", "Brussels" ])
    with col2:
        latitude = st.number_input("Latitude (e.g. Brussels: 50.8503)", format="%.4f")
        longitude = st.number_input("Longitude (e.g. Brussels: 4.3517)", format="%.4f")

    st.divider()
    st.subheader("📐 Structural Details")
    
    col3, col4, col5 = st.columns(3)
    with col3:
        bedrooms = st.number_input("Bedrooms", min_value=1, max_value=20, value=1)
        bathrooms = st.number_input("Bathrooms", min_value=1, max_value=10, value=1)
    with col4:
        livable_surface = st.number_input("Livable Surface (m²)", min_value=50.0, max_value=2000.0, value=90.0)
        toilets = st.number_input("Toilets", min_value=1, max_value=10, value=1)
    with col5:
        epc = st.selectbox("EPC Rating", ["A++","A+","A", "B", "C", "D", "E", "F", "G"])
        building_state = st.selectbox("Building Condition", ["To demolish","To restore","Under construction","Fully renovated"
                                                             ,"to renovate","To be renovated","Excellent","Normal","New","unknown"])

    has_parking = st.checkbox("Property includes parking?", value=False)
    
    # Form submission button
    submit_button = st.form_submit_button(label="🔮 Estimate Property Price")

# 4. Handle prediction request execution
if submit_button:
    # Match the nested payload format expected by your Pydantic "PredictionInput"
    payload = {
        "data": {
            "latitude": float(latitude),
            "longitude": float(longitude),
            "bedrooms": int(bedrooms),
            "livable_surface": float(livable_surface),
            "bathrooms": int(bathrooms),
            "toilets": int(toilets),
            "category": str(category),
            "province": str(province),
            "epc": str(epc),
            "building_state": str(building_state),
            "has_parking": 1 if has_parking else 0
        }
    }
    
    with st.spinner("Connecting to model API... (May take a moment if container is waking up)"):
        try:
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # Check status code payload embedded within your FastAPI dictionary
                if result.get("status_code") == 200 and result.get("prediction") is not None:
                    predicted_price = result["prediction"]
                    st.success(f"### 🎯 Estimated Market Value: €{predicted_price:,.2f}")
                else:
                    st.error("⚠️ The API encountered an issue parsing your values. Double-check feature types.")
            else:
                st.error(f"❌ Connection failed. API responded with status code: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            st.error("🔌 Could not reach the prediction server. Please verify your Render instance is live.")
