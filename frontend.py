# pyrefly: ignore [missing-import]
import streamlit as st
import requests
import time

# API Base URL
API_URL = "http://127.0.0.1:8000"

# --- Styling & Config ---
st.set_page_config(page_title="ZenStore Admin", page_icon="🛒", layout="wide")

# Custom CSS for aesthetics
st.markdown("""
    <style>
    .product-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .status-pending { color: #FFA500; font-weight: bold; }
    .status-ready { color: #00FF00; font-weight: bold; }
    .status-failed { color: #FF0000; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- Session State ---
if "token" not in st.session_state:
    st.session_state.token = None

# --- Helper Functions ---
def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

def fetch_products():
    response = requests.get(f"{API_URL}/products/", headers=get_headers())
    if response.status_code == 200:
        return response.json()
    return []

# --- Sidebar: Authentication ---
with st.sidebar:
    st.title("🔐 Authentication")
    
    if st.session_state.token is None:
        st.write("Please log in to manage your store.")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            with st.spinner("Authenticating..."):
                # Swagger UI expects form data (username, password)
                data = {"username": email, "password": password}
                res = requests.post(f"{API_URL}/auth/login", data=data)
                
                if res.status_code == 200:
                    st.session_state.token = res.json()["access_token"]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
    else:
        st.success("✅ Logged In")
        if st.button("Logout"):
            st.session_state.token = None
            st.rerun()

# --- Main Dashboard ---
st.title("🛒 ZenStore Admin Dashboard")

if st.session_state.token is None:
    st.info("👈 Please log in using the sidebar to view your dashboard.")
else:
    # --- Bulk Upload Section ---
    st.markdown("### 📤 Bulk Upload CSV")
    uploaded_file = st.file_uploader("Drag and drop a CSV file to add products in bulk", type=["csv"])
    if uploaded_file is not None:
        if st.button("Upload CSV"):
            with st.spinner("Uploading..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                res = requests.post(f"{API_URL}/products/bulk-upload", headers=get_headers(), files=files)
                if res.status_code == 202:
                    job_id = res.json()["job_id"]
                    st.success(f"Upload accepted! Background Job ID: {job_id}")
                    time.sleep(2) # Give it a second to process
                    st.rerun()
                else:
                    st.error("Upload failed.")

    st.markdown("---")
    
    # --- Product Grid ---
    st.markdown("### 📦 Your Products")
    products = fetch_products()
    
    if not products:
        st.write("You don't have any products yet.")
    else:
        # Create a dynamic grid (3 columns wide)
        cols = st.columns(3)
        
        for index, product in enumerate(products):
            col = cols[index % 3] # Cycle through the 3 columns
            
            with col:
                with st.container():
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    
                    st.subheader(product["name"])
                    st.write(f"**Price:** ${product['price']} | **Stock:** {product['stock']}")
                    
                    # Display Image if exists
                    if product.get("image_path"):
                        # We have to fetch the image from the API or construct a URL. 
                        # Wait, FastAPI needs to serve static files to render the image directly.
                        # For now, we will just show the metadata.
                        st.caption(f"🖼️ Image attached: {product['image_metadata']['original_name']}")
                    
                    # Display Status and AI
                    status = product["status"]
                    if status == "ready":
                        st.markdown(f"Status: <span class='status-ready'>READY</span>", unsafe_allow_html=True)
                        st.info(f"**Category:** {product.get('category')}\n\n**Marketing:** {product.get('ai_description')}")
                    
                    elif status == "pending" or status == "processing":
                        st.markdown(f"Status: <span class='status-pending'>{status.upper()}</span>", unsafe_allow_html=True)
                        st.warning("No AI description generated yet.")
                        
                        # THE MAGIC BUTTON
                        if st.button("✨ Generate AI Description", key=f"ai_btn_{product['id']}"):
                            with st.spinner("Telling Llama-3.1 to write magic..."):
                                res = requests.post(f"{API_URL}/products/{product['id']}/generate-ai", headers=get_headers())
                                if res.status_code == 200:
                                    st.success("AI Generation Started! Check back in 3 seconds.")
                                    time.sleep(3) # Wait for the background task
                                    st.rerun()
                                else:
                                    st.error(f"Failed to start AI: {res.json()}")
                    
                    elif status == "ai_failed":
                        st.markdown(f"Status: <span class='status-failed'>FAILED</span>", unsafe_allow_html=True)
                        st.error("The AI failed to generate a description. Groq might be down.")
                        if st.button("🔄 Retry AI", key=f"retry_btn_{product['id']}"):
                            requests.post(f"{API_URL}/products/{product['id']}/generate-ai", headers=get_headers())
                            st.rerun()
                            
                    st.markdown('</div>', unsafe_allow_html=True)
