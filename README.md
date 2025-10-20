<h1 align="center">AI-Powered E-Commerce Product Recommender</h1>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Redis](https://img.shields.io/badge/Redis-Caching-red)
![MongoDB](https://img.shields.io/badge/MongoDB-Database-green)
![Gemini](https://img.shields.io/badge/Google%20Gemini-AI%20LLM-orange)
![Docker](https://img.shields.io/badge/Docker-Containerization-blue)
![Status](https://img.shields.io/badge/Status-Active-success)
![GitHub stars](https://img.shields.io/github/stars/sindhurmarella/ecommerce-recommender-llm?style=social)
![GitHub forks](https://img.shields.io/github/forks/sindhurmarella/ecommerce-recommender-llm?style=social)
![GitHub issues](https://img.shields.io/github/issues/sindhurmarella/ecommerce-recommender-llm)
![Last commit](https://img.shields.io/github/last-commit/sindhurmarella/ecommerce-recommender-llm)

</p>


<p align="center">
  <b>A high-performance hybrid product recommender built with FastAPI, Python, and Google's Gemini LLM.</b>
</p>

---

##  Overview

This project is a **high-performance E-Commerce Product Recommendation System** built with **Python**, **FastAPI**, and **Google’s Gemini LLM**.  
It combines intelligent recommendation algorithms with natural-language product explanations, architected for scalability and real-world use.

---

## ✨ Key Features

- **🧩 Hybrid Recommendation Model:**  
  Combines *Content-Based Filtering* (similar items) and *Collaborative Filtering* (similar users) for accurate, diverse results.

- **💬 LLM-Powered Explanations:**  
  Integrates **Google Gemini** to generate human-like, personalized explanations for each recommendation.

- **⚡ High-Performance Architecture:**  
  Offline batch processing + **Redis caching** ensures near-instant API responses.

- **🔥 Social Proof Integration:**  
  Dynamically displays popularity metrics (e.g., *“🔥 Popular! 17 users have purchased this item.”*).

- **🧪 Realistic Data Simulation:**  
  Generates realistic mock data for users, products, and interactions (with bestsellers, affinities, etc.).

- **💻 Modern API & Frontend:**  
  Clean, responsive frontend built with **HTML + Tailwind CSS** for a simple demonstration interface.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Backend** | Python, FastAPI |
| **Recommendation Engine** | Pandas, Scikit-Surprise |
| **Database** | MongoDB |
| **Caching** | Redis |
| **LLM Integration** | Google Gemini API |
| **Containerization** | Docker |
| **Frontend** | HTML, Tailwind CSS, JavaScript |

---

## 🚀 Project Evolution

| Milestone | Description |
|------------|-------------|
| Foundation & Backend MVP | Created mock data generation, core data models, and the first content-based recommender. |
| AI Integration | Integrated Gemini API to provide human-like product explanations. |
| UI & Data Refinement | Added frontend, improved product realism, refined data generation pipeline. |
| Advanced Logic & Scaling | Introduced hybrid logic, added social proof, and implemented Redis caching with batch pre-computation. |

---

## 🖼️ Project Preview

Product recommendations at the API endpoint

<p align="center">
  <img src="./demo_images/Screenshot 2025-10-20 185543.png" alt="Backend Response" width="700">
</p>

Production recommendations in the frontend page

<p align="center">
  <img src="./demo_images/Screenshot 2025-10-20 185616.png" alt="Frontend Response" width="700">
</p>

### System Architecture

<p align="center">
  <img src="./demo_images/Screenshot 2025-10-20 194251.png" alt="System Architecture" width="700">
</p>

---

## ⚙️ Setup and Installation

Follow these steps to run the project locally

### 1. Prerequisites

- Python 3.8+
- MongoDB instance
- Docker Desktop (for Redis)
- Node.js *(optional, for `npx gignore`)*

---

### 2. Clone the Repository

```bash
git clone https://github.com/SindhurMarella/ecommerce-recommender-llm.git
cd ecommerce-recommender-llm
```
---

### 3. Set Up Environment

Create and activate a virtual environment, then install dependencies:
```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Activate it (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
---

### 4. Configure Environment Variables

Create a .env file in the root directory and add your credentials:
```bash
# MongoDB Connection String
MDB_URI="mongodb+srv://..."

# Google Gemini API Key
GEMINI_API_KEY="AIzaSy..."
```
---

### 5. Start Services

Start Redis using Docker:

```bash
docker run --name recommender-redis -p 6379:6379 -d redis
```

(Use docker start recommender-redis for subsequent runs.)

Ensure your MongoDB database is running and accessible.

---

### 6. Generate Data & Pre-compute Recommendations

Populate MongoDB with mock data:

```bash
python generate_mock_data.py
```

Run the offline batch job to fill Redis cache:
```bash
python batch_recommender.py
```
---

### 7. Run the API Server
Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```
API available at:
👉 http://127.0.0.1:8000/

Documentation of API available at http://127.0.0.1:8000/docs

---

### 8. Use the Application
Open the frontend:
```bash
index.html
```
Interact with the recommender through the browser UI.

---

## 🧩 Example API Response
```bash
{
    "product_id": "P0027",
    "name": "Vintage Denim Jeans",
    "category": "Apparel",
    "price": 210.43,
    "description": "A high-quality, vintage denim jeans from our exclusive Apparel collection.",
    "explanation": "The AI recommendation explanation service is temporarily unavailable.",
    "social_proof": "Popular! 4 users have purchased this product."
  }
```
---


### 💡 Future Enhancements

Add real user authentication and recommendation feedback loops

Introduce multilingual explanations via Gemini

Expand frontend dashboard with interactive recommendation visualizations

---

### 🤝 Contributing

Contributions are welcome!
Feel free to fork the repo, open issues, or submit PRs to improve features or documentation.


