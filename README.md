# ID Card Generator - Reorganized

This project has been reorganized into a clean **Frontend-Backend** architecture. The core logic remains untouched but is now accessible via a modern web interface.

## Project Structure

```
📁 project-root/
│
├── 📁 backend/
│   ├── id_gen.py          # Original logic (AS-IS)
│   ├── index.py           # Original entry (AS-IS)
│   ├── app.py             # New Flask API wrapper
│   └── requirements.txt   # Backend dependencies
│
├── 📁 frontend/
│   ├── index.html         # Modern UI Structure
│   ├── style.css          # Premium Styling
│   └── script.js          # Logic & API Integration
│
└── README.md              # Setup Instructions
```

## Setup & Running

### 1. Backend Setup
The backend provides the API that generates the ID card images using the original Python logic.

1. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the API server:
   ```bash
   python app.py
   ```
   *The server will run on `http://localhost:5000`.*

### 2. Frontend Setup (React)
The frontend is built with React and Vite.

1. Navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   *The frontend will run on `http://localhost:5173`.*

## Features
- **React + Vite**: Fast, modern development environment.
- **Tailwind CSS**: Professional styling with dark mode support.
- **Framer Motion**: Smooth animations for a premium feel.
- **In-Browser Camera**: Capture photo directly from the browser.
- **Live Preview**: Real-time generation and download of front/back ID cards.

## Note on Original Logic
The original `id_gen.py` and `index.py` (PyQt5 version) are still fully functional and can be run separately if needed. The new `app.py` simply imports the rendering methods from `id_gen.py` to serve them over the web.
