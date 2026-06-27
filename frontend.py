import streamlit as st
import requests
import time

# API Base URL
API_URL = "http://127.0.0.1:8000"

# --- Styling & Config ---
st.set_page_config(page_title="ZenStore Admin", page_icon="🛒", layout="wide")

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
        auth_mode = st.radio("Choose Action", ["Login", "Register"])
        
        if auth_mode == "Login":
            st.write("Log in to your store.")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            if st.button("Login"):
                with st.spinner("Authenticating..."):
                    data = {"username": email, "password": password}
                    res = requests.post(f"{API_URL}/auth/login", data=data)
                    if res.status_code == 200:
                        st.session_state.token = res.json()["access_token"]
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
                        
        else:
            st.write("Create a new account.")
            new_name = st.text_input("Full Name")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            
            if st.button("Register"):
                with st.spinner("Creating account..."):
                    payload = {"email": new_email, "password": new_password, "full_name": new_name}
                    res = requests.post(f"{API_URL}/auth/register", json=payload)
                    if res.status_code == 201:
                        st.success("Account created! Please switch to Login.")
                    else:
                        st.error(f"Registration failed: {res.text}")
    else:
        st.success("✅ Logged In")
        if st.button("Logout"):
            st.session_state.token = None
            st.rerun()

# --- Main Dashboard ---
st.title("🛒 ZenStore Admin Dashboard")

if st.session_state.token is None:
    st.info("👈 Please log in or register using the sidebar to view your dashboard.")
else:
    # --- TOP ACTIONS ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ➕ Add Single Product")
        with st.expander("Click to add a single product"):
            with st.form("single_product_form"):
                new_name = st.text_input("Product Name")
                new_price = st.number_input("Price ($)", min_value=0.0, format="%.2f")
                new_stock = st.number_input("Stock Quantity", min_value=0, step=1)
                new_desc = st.text_area("Raw Description")
                
                if st.form_submit_button("Create Product"):
                    payload = {
                        "name": new_name,
                        "price": new_price,
                        "stock": new_stock,
                        "raw_description": new_desc
                    }
                    res = requests.post(f"{API_URL}/products/", json=payload, headers=get_headers())
                    if res.status_code == 201:
                        st.success("Product created! Generating AI description in background...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to create product.")
                        
    with col2:
        st.markdown("### 📤 Bulk Upload CSV")
        with st.expander("Click to upload a CSV file"):
            uploaded_csv = st.file_uploader("Drag and drop a CSV file", type=["csv"])
            if uploaded_csv is not None:
                if st.button("Upload CSV"):
                    files = {"file": (uploaded_csv.name, uploaded_csv.getvalue(), "text/csv")}
                    res = requests.post(f"{API_URL}/products/bulk-upload", headers=get_headers(), files=files)
                    if res.status_code == 202:
                        st.success(f"Upload accepted! Background Job ID: {res.json()['job_id']}")
                        time.sleep(1)
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
        cols = st.columns(3)
        for index, product in enumerate(products):
            col = cols[index % 3] 
            
            with col:
                with st.container():
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    
                    st.subheader(product["name"])
                    st.write(f"**Price:** ${product['price']} | **Stock:** {product['stock']}")
                    
                    if product.get("image_path"):
                        try:
                            st.image(product["image_path"], use_container_width=True)
                        except Exception:
                            st.caption(f"🖼️ Image attached: {product['image_metadata']['original_name']}")
                    else:
                        img_upload = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], key=f"img_{product['id']}")
                        if img_upload:
                            if st.button("Save Image", key=f"save_img_{product['id']}"):
                                with st.spinner("Compressing with Pillow..."):
                                    files = {"file": (img_upload.name, img_upload.getvalue(), "image/jpeg")}
                                    res = requests.post(f"{API_URL}/products/{product['id']}/image", headers=get_headers(), files=files)
                                    if res.status_code == 200:
                                        st.success("Image saved!")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("Failed to save image.")
                    
                    st.markdown("---")
                    status = product["status"]
                    if status == "ready":
                        st.markdown(f"Status: <span class='status-ready'>READY</span>", unsafe_allow_html=True)
                        st.info(f"**Category:** {product.get('category')}\n\n**Marketing:** {product.get('ai_description')}")
                    
                    elif status == "pending" or status == "processing":
                        st.markdown(f"Status: <span class='status-pending'>{status.upper()}</span>", unsafe_allow_html=True)
                        st.warning("No AI description generated yet.")
                        
                        if st.button("✨ Generate AI Description", key=f"ai_btn_{product['id']}"):
                            with st.spinner("Telling Llama-3.1 to write magic..."):
                                res = requests.post(f"{API_URL}/products/{product['id']}/generate-ai", headers=get_headers())
                                if res.status_code == 200:
                                    st.success("AI Generation Started! Check back in 3 seconds.")
                                    time.sleep(3)
                                    st.rerun()
                                else:
                                    st.error(f"Failed to start AI: {res.json()}")
                    
                    elif status == "ai_failed":
                        st.markdown(f"Status: <span class='status-failed'>FAILED</span>", unsafe_allow_html=True)
                        st.error("The AI failed to generate a description.")
                        if st.button("🔄 Retry AI", key=f"retry_btn_{product['id']}"):
                            requests.post(f"{API_URL}/products/{product['id']}/generate-ai", headers=get_headers())
                            st.rerun()
                            
                    st.markdown('</div>', unsafe_allow_html=True)
