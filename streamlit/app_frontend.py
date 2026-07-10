import streamlit as st
import requests
import base64
from pathlib import Path
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError

# Initialize session state for coordinates if they don't exist yet
if "lat" not in st.session_state:
    st.session_state.lat = 0.00
if "lon" not in st.session_state:
    st.session_state.lon = 0.00

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
        div[data-testid="stFormSubmitButton"] button {{
            background-color: #6D28D9 !important;
            color: #FFFFFF !important;
            font-size: 1.15rem !important;
            font-weight: bold !important;
            padding: 0.75rem 2rem !important;
            border-radius: 10px !important;
            border: none !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(109, 40, 217, 0.3) !important;
        }}
        div[data-testid="stFormSubmitButton"] button:hover {{
            background-color: #5B21B6 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(109, 40, 217, 0.4) !important;
        }}

        /* Uniform card look for grouped sections */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: rgba(255, 255, 255, 0.55) !important;
            border: 1px solid #D8CCF0 !important;
            border-radius: 14px !important;
            padding: 0.5rem 0.5rem !important;
            margin-bottom: 1.25rem !important;
        }}

        /* Uniform border/color for ALL input-like widgets */
        div[data-testid="stNumberInput"] div[data-baseweb="input"],
        div[data-testid="stTextInput"] div[data-baseweb="input"],
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
            border: 1.5px solid #B9A6E8 !important;
            border-radius: 8px !important;
            background-color: #FFFFFF !important;
            box-shadow: none !important;
        }}
        div[data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within,
        div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {{
            border: 1.5px solid #6D28D9 !important;
            box-shadow: 0 0 0 2px rgba(109, 40, 217, 0.15) !important;
        }}

        /* Secondary "search coordinates" button matched to the theme */
        div[data-testid="stButton"] button {{
            border: 1.5px solid #6D28D9 !important;
            color: #6D28D9 !important;
            background-color: #FFFFFF !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }}
        div[data-testid="stButton"] button:hover {{
            background-color: #F3EEFD !important;
            border-color: #5B21B6 !important;
            color: #5B21B6 !important;
        }}

        /* Checkbox accent to match theme */
        div[data-testid="stCheckbox"] label span {{
            border-color: #B9A6E8 !important;
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
st.write("Fill the property parameters below to estimate the target sales price.")

# --- POPUP DIALOG FOR GEOLOCATION ---
@st.dialog("🔍 Coordinate Lookup Tool")
def lookup_coordinates_popup():
    st.write("Enter a Belgian city, municipality, or postal code to auto-fill the form.")
    search_query = st.text_input("Location search:", placeholder="e.g., Ghent, Antwerp 2000, Liège")

    if st.button("Find Coordinates", use_container_width=True):
        if search_query:
            geolocator = Nominatim(user_agent="belgium_property_predictor_v2_2026")
            try:
                location = geolocator.geocode(f"{search_query}, Belgium", timeout=10)
                if location:
                    # Update session state values
                    st.session_state.lat = location.latitude
                    st.session_state.lon = location.longitude
                    st.success(f"📍 Found! Coordinates set to: {st.session_state.lat:.4f}, {st.session_state.lon:.4f}")
                    st.rerun()
                else:
                    st.error("❌ Could not find location. Please check the spelling.")
            except GeocoderServiceError:
                st.error("🔌 OpenStreetMap server is rate-limiting requests. Enter coordinates manually.")

# --- Location & coordinate lookup (OUTSIDE the form, since st.button can't live inside st.form) ---
with st.container(border=True):
    st.subheader("📍 Location & Type")

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        category = st.selectbox("Property Type", ["house", "apartment"])
    with row1_col2:
        province = st.selectbox("Province", ["Brussels","Luxembourg", "Limburg", "Flemish Brabant", "Walloon Brabant",
            "Namur", "East Flanders", "Antwerp", "Liège", "West Flanders", "Hainaut" ])

    row2_col1, row2_col2, row2_col3 = st.columns([1, 1, 1], vertical_alignment="bottom")
    with row2_col1:
        latitude = st.number_input("Latitude", value=st.session_state.lat, format="%.4f", key="lat")
    with row2_col2:
        longitude = st.number_input("Longitude", value=st.session_state.lon, format="%.4f", key="lon")
    with row2_col3:
        if st.button("🌐 Search coordinates", use_container_width=True):
            lookup_coordinates_popup()

# 3. Use a clean web form to collect the remaining input fields
with st.form("property_form"):
    with st.container(border=True):
        st.subheader("📐 Structural Details")

        col3, col4, col5 = st.columns(3)
        with col3:
            bedrooms = st.number_input("Bedrooms", min_value=1, max_value=20, value=1)
            bathrooms = st.number_input("Bathrooms", min_value=1, max_value=10, value=1)
        with col4:
            livable_surface = st.number_input("Livable Surface (m²)", min_value=50.0, max_value=2000.0, value=90.0)
            toilets = st.number_input("Toilets", min_value=1, max_value=10, value=1)
        with col5:
            epc = st.selectbox("EPC Rating", ["unknown","A++", "A+", "A", "B", "C", "D", "E", "F", "G"])
            building_state = st.selectbox("Building Condition", ["unknown","To demolish", "To restore", "Under construction",
                "Fully renovated", "to renovate", "To be renovated", "Excellent", "Normal", "New" ])

        has_parking = st.checkbox("Property includes parking?", value=False)

    st.write("")  # small breathing room above the button

    # Center the submit button using a 3-column layout, button in the middle column
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1.4, 1])
    with btn_col2:
        submit_button = st.form_submit_button(label="🔮 Estimate Property Price", use_container_width=True)

# 4. Handle prediction request execution
if submit_button:
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

    with st.spinner("Connecting to model API..."):
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                result = response.json()
                if result.get("status_code") == 200 and result.get("prediction") is not None:
                    predicted_price = result["prediction"]
                    st.success(f"### 🎯 Estimated Market Value: €{predicted_price:,.2f}")
                else:
                    st.error("⚠️ The API encountered an issue parsing your values.")
            else:
                st.error(f"❌ Connection failed. API responded with status code: {response.status_code}")
        except requests.exceptions.RequestException:
            st.error("🔌 Could not reach the prediction server.")
