# 🛒 ZenStore E-Commerce API & Admin Dashboard

ZenStore is a robust, production-ready backend built with **FastAPI**. It serves as the core infrastructure for an e-commerce platform, featuring fully authenticated routes, background data processing, secure image handling, and automatic AI product description generation.

It also includes a pure Python **Streamlit Admin Dashboard** to visualize products, trigger AI jobs, and upload CSVs seamlessly.

---

## ✨ Key Features

1. **Secure Authentication:** JWT (JSON Web Token) based login and registration with Bcrypt password hashing.
2. **Generative AI Integration:** Uses the **Groq API (Llama-3.1-8b-instant)** to automatically write marketing descriptions and categorize products in the background.
3. **Resilient Background Workers:** Dedicated ThreadPool execution prevents server freezing during heavy synchronous tasks.
4. **Image Processing Pipeline:** Protects server hard drives using UUID filename sanitization, transparency stripping, and automatic dimension compression via `Pillow`.
5. **Fault-Tolerant CSV Bulk Uploads:** Asynchronously parses hundreds of products at once. Bad rows are gracefully logged to a `BatchJob` status tracker without crashing the server.
6. **Smart Caching:** In-memory dictionary cache with TTL and immediate cache invalidation to prevent database overload and race conditions.
7. **Custom Performance Profiler:** A dynamic `@time_logger` decorator that accurately tracks execution time for both synchronous and asynchronous functions using `inspect`.
8. **Admin Dashboard:** A fully interactive frontend UI built with Streamlit that consumes the REST API.

---

## 🛠️ Technology Stack
*   **Backend:** FastAPI, Python 3.11
*   **Database:** SQLite, SQLAlchemy (ORM)
*   **Data Validation:** Pydantic
*   **Frontend UI:** Streamlit
*   **AI Provider:** Groq
*   **Image Processing:** Pillow

---

## 🚀 Getting Started

### 1. Setup the Environment
Clone the repository and create a virtual environment:
```bash
git clone https://github.com/starboy1402/Zenstore.git
cd Zenstore
python -m venv venv
```

Activate the virtual environment:
*   **Windows:** `.\venv\Scripts\activate`
*   **Mac/Linux:** `source venv/bin/activate`

### 2. Install Dependencies
```bash
pip install fastapi uvicorn sqlalchemy pydantic passlib bcrypt==3.2.2 python-jose python-multipart groq pillow streamlit requests
```
*(Note: bcrypt is explicitly downgraded to 3.2.2 to prevent passlib compatibility crashes).*

### 3. Configure API Keys
Create a `.env` file in the root directory and add your Groq API key:
```env
GROQ_API_KEY=your_api_key_here
```
*(If no key is provided, the AI worker will safely fall back to Mock Mode).*

---

## 💻 Running the Application

This project requires **two** terminal windows to run both the API and the UI simultaneously.

**Terminal 1: Start the FastAPI Backend**
```bash
uvicorn main:app --reload
```
*   The API will be live at: `http://127.0.0.1:8000`
*   Swagger Interactive Docs: `http://127.0.0.1:8000/docs`

**Terminal 2: Start the Streamlit Admin Dashboard**
```bash
python -m streamlit run frontend.py
```
*   The Dashboard will automatically open in your browser at: `http://localhost:8501`

