# SignGuard AI 🔏

> **AI-powered Handwritten Signature Verification with Retrieval-Augmented Generation (RAG)**

A full-stack student portfolio project that verifies handwritten signatures as **Genuine** or **Forged** using a custom ML model, then answers user questions about the result through a RAG-powered chatbot.

---

## ✨ Features

- 📤 **Drag-and-drop signature upload** with live image preview
- 🤖 **ML prediction** — SVM pipeline trained on 9 hand-crafted image features
- 📊 **Animated confidence score** displayed after each prediction
- 💬 **RAG chatbot** — answers questions grounded in your research paper
- 🧠 **Context-aware responses** — chatbot automatically knows the latest prediction
- 🚫 **No hallucination** — chatbot says "I couldn't find that" if answer is not in the PDF
- 📱 **Responsive UI** — two-column desktop, single-column mobile

---

## 🏗️ Architecture

```
User
 │
 ├─ Upload Image → POST /upload
 │                    │
 │              preprocess.py (RGB→Grey→Otsu→crop)
 │              feature_extract.py (9 features)
 │              predict.py (SVM model.pkl)
 │                    │
 │              { prediction, confidence }
 │
 └─ Ask Question → POST /chat
                       │
                 ChromaDB retriever (top-4 chunks)
                 Groq LLM (llama-3.1-8b-instant)
                 Prediction context injected into prompt
                       │
                 { answer }
```

---

## 📁 Folder Structure

```
SignguardRag/
├── backend/
│   ├── app.py                  ← FastAPI entry point
│   ├── config.py               ← Central config (paths, env vars)
│   ├── requirements.txt
│   ├── .env.example
│   ├── routes/
│   │   ├── upload.py           ← POST /upload
│   │   └── chat.py             ← POST /chat
│   ├── ml/
│   │   ├── preprocess.py       ← Image preprocessing (from notebook)
│   │   ├── feature_extract.py  ← 9-feature extraction (from notebook)
│   │   ├── train_model.py      ← One-time training script
│   │   └── predict.py          ← predict_signature() function
│   ├── rag/
│   │   ├── build_vector_db.py  ← One-time DB build script
│   │   ├── retriever.py        ← ChromaDB retriever
│   │   ├── chatbot.py          ← RAG chain (create_retrieval_chain)
│   │   └── prompt_template.py  ← Context-aware prompt builder
│   ├── knowledge/
│   │   └── SignGuard_Research_Paper.pdf   ← PLACE YOUR PDF HERE
│   ├── chroma_db/              ← Generated vector store (auto-created)
│   └── uploads/                ← Temp upload folder (auto-cleaned)
│
├── frontend/
│   ├── src/
│   │   ├── api/api.js          ← Axios API layer
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── UploadSignature.jsx
│   │   │   ├── PredictionCard.jsx
│   │   │   ├── ChatBot.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   └── pages/Home.jsx
│   ├── index.html
│   └── package.json
│
└── README.md
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- A free Groq API key → [https://console.groq.com](https://console.groq.com)

---

### 1. Place your Research Paper PDF

Copy your PDF into the backend knowledge folder and rename it:

```
backend/knowledge/SignGuard_Research_Paper.pdf
```

> Your existing file `reaserch_papers_signguard.pdf` is at the workspace root.
> Just copy and rename it:
>
> ```powershell
> Copy-Item ".\reaserch_papers_signguard.pdf" ".\backend\knowledge\SignGuard_Research_Paper.pdf"
> ```

---

### 2. Set Up the Backend

```powershell
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt
```

#### Configure environment variables

```powershell
Copy-Item .env.example .env
```

Edit `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

### 3. Train the ML Model

> **Skip this if you already have `backend/ml/model.pkl`.**

Download a signature dataset ([CEDAR](http://www.cedar.buffalo.edu/NIJ/data/) or [Kaggle](https://www.kaggle.com/datasets/robinreni/signature-verification-dataset)) and run:

```powershell
# From inside backend/
python ml/train_model.py --genuine path\to\genuine\ --forged path\to\forged\
```

This generates `backend/ml/model.pkl`.

---

### 4. Build the ChromaDB Vector Store

```powershell
# From inside backend/
python rag/build_vector_db.py
```

This embeds your PDF using `all-MiniLM-L6-v2` (downloads ~90 MB on first run) and stores chunks in `backend/chroma_db/`.

---

### 5. Run the Backend

```powershell
# From inside backend/
uvicorn app:app --reload --port 8000
```

API docs available at [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 6. Run the Frontend

```powershell
cd frontend
npm run dev
```

App available at [http://localhost:5173](http://localhost:5173)

---

## 🔑 Environment Variables

| Variable | Description | Default |
|---|---|---|
| `GROQ_API_KEY` | Your Groq API key | — |
| `HUGGINGFACEHUB_API_TOKEN` | Your Hugging Face Hub token (Used if Groq key is absent) | — |

Frontend (in `frontend/.env`):

| Variable | Description | Default |
|---|---|---|
| `VITE_API_URL` | Backend base URL | `http://localhost:8000` |

---

## 📡 API Endpoints

### `POST /upload`

Upload a signature image for prediction.

**Request:** `multipart/form-data` with `file` field (PNG/JPG/BMP/TIFF)

**Response:**
```json
{
  "prediction": "Genuine",
  "confidence": 94,
  "filename": "signature.png"
}
```

---

### `POST /chat`

Ask the RAG chatbot a question.

**Request:**
```json
{
  "question": "Why is this forged?",
  "prediction": "Forged",
  "confidence": 94
}
```

**Response:**
```json
{
  "answer": "Based on the research paper, forged signatures often exhibit..."
}
```

---

## 🛠️ Technologies Used

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite, Tailwind CSS 3, Axios, Lucide React |
| **Backend** | FastAPI, Uvicorn, Python-dotenv |
| **ML** | scikit-learn (SVM), scikit-image, SciPy, NumPy, joblib |
| **RAG** | LangChain, langchain-groq, langchain-huggingface |
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 (local) |
| **Vector DB** | ChromaDB |
| **LLM** | Groq API — llama-3.1-8b-instant |

---

## 🔮 Future Improvements

- [ ] Support multiple persons with person-specific models
- [ ] Add signature drawing canvas (draw instead of upload)
- [ ] Export prediction report as PDF
- [ ] Batch verification of multiple signatures
- [ ] Deploy backend to Render / Railway, frontend to Vercel
- [ ] Add dark mode toggle
- [ ] Support more image formats (HEIC, WebP)
