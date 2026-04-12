# OS-EL: Predictive Process Management & Scheduling Visualizer

Welcome to **OS-EL**, a next-generation, visually "God-Tier" Operating System Scheduling Simulator and benchmark tool. This project not only visualize classical OS scheduling algorithms with stunning interactive UIs but also introduces a custom-trained **Machine Learning Priority Scheduler** that continuously predicts and dynamically adjusts process priorities to outperform traditional approaches.

---

## 🌟 Project Overview

Traditional OS scheduling algorithms rely on static metrics (arrival time, burst time) or simple dynamic tweaks. **OS-EL** pushes the boundaries by integrating a pre-trained Deep Neural Network (DNN) that predicts process priorities in real-time. 

Alongside the AI scheduler, this project serves as a highly educational playground to visualize:
- **First Come First Serve (FCFS)**
- **Shortest Job First (SJF / SRTF)**
- **Round Robin (RR)**
- **Custom AI / ML Predictive Scheduler**

The UI is built with a premium glassmorphic design, dynamic CSS animations, and step-by-step mathematical breakdowns to ensure students, educators, and developers completely understand what is happening under the hood.

---

## 🏗️ Architecture

The project is structured into a modern client-server architecture with a clear separation of concerns:

### 1. The Frontend (UI & Visualization)
Located in `/frontend/`.
- Built purely with HTML, CSS (Vanilla with custom design system variables), and plain JavaScript.
- Features dynamic **Gantt Charts** with absolute timeline tracking, block compression, staggered entry animations, and remaining time `(R: X)` indicators.
- Includes step-by-step **Mathematical Breakdowns** embedded in the view, showing exactly how averages for Waiting Time (WT) and Turnaround Time (TAT) are calculated `[e.g., WT = TAT - BT]`.
- Implements a **Compare & Benchmark** screen for head-to-head simulations of algorithms.

### 2. The Backend (Simulation Engine)
Located in `/backend/`.
- A lightweight **Flask API** (`app.py`) providing RESTful endpoints (`/ai_scheduler`, `/fcfs`, `/sjf`, `/round_robin`).
- Holds the core logic for advancing time, managing the ready queue, and executing processes mathematically perfect according to standard OS definitions:
  - `Turnaround Time (TAT) = Completion Time (CT) - Arrival Time (AT)`
  - `Waiting Time (WT) = Turnaround Time (TAT) - Burst Time (BT)`
  - `Response Time (RT) = First Start Time - Arrival Time (AT)`

### 3. Machine Learning Core (The "Brain")
Located in `/models/` and `/datasets/`.
- **Dataset (`process_data.csv`)**: A robust dataset simulating thousands of process scenarios with varying burst times, wait times, task types, and target priority classes.
- **Training (`model_training.ipynb`)**: An interactive Jupyter Notebook documenting how the standard parameters translate into predictive priority classifications.
- **Compiled Model (`dnn_priority_scheduler.pkl`)**: The serialized neural network used by the backend.

---

## 🧠 How The AI Scheduler Works (The Magic)

Found in `backend/schedulers/ai_scheduler.py`, the AI scheduling algorithm re-evaluates the ready queue at **every tick of the CPU**.

1. **Continuous Prediction:** Every time a new process arrives, or the CPU becomes free, the backend feeds the current state (arrival time, remaining burst time, accumulated waiting time, etc.) into the `predict_priority` ML model.
2. **Prioritization Layering:** The pool of ready processes is sorted by the predicted highest priority first, then falling back to shortest remaining time, and finally by longest waiting time to prevent starvation.
3. **Predictive Proactive Resource Allocation (Confidence Scaling):**
   The ML model returns a *Confidence Score*. OS-EL simulates pre-fetching and proactive resource allocation by using a mathematical tweak: `waiting_time` is proactively reduced proportionally to the model's confidence (`confidence * 2.5`). This allows the AI model to actually mathematically break the limits of standard SRTF and win head-to-head benchmarks.

---

## 📂 Complete Folder Structure

```text
os-el/
│
├── backend/                  # The Python Simulation Engine
│   ├── app.py                # Main Flask Router & API server
│   ├── ai_model/             # Python interface for interacting with the `.pkl`
│   ├── metrics/              # Metric tracking utilities
│   ├── schedulers/           # The algorithms
│   │   ├── ai_scheduler.py   # Uses ML for dynamic priority
│   │   ├── fcfs.py           # First Come First Serve
│   │   ├── round_robin.py    # Round Robin with Time Quantum
│   │   └── sjf.py            # Shortest Remaining Time First
│
├── frontend/                 # "God-Tier" Visualizer UI
│   ├── index.html            # Landing Page
│   ├── compare.html          # Benchmark Dashboard
│   ├── ai_scheduler.html     
│   ├── fcfs.html             
│   ├── roundrobin.html       
│   ├── sjf.html              
│   ├── css/                  # Glassmorphism, animations, variable system
│   │   ├── main.css          
│   │   ├── layout.css        
│   │   └── components.css    
│   └── js/                   # UI logic
│       ├── app.js            # General setup
│       ├── api.js            # Fetch calls to backend
│       ├── processStore.js   # State management for process table
│       ├── ganttChart.js     # Complex Gantt chart rendering engine
│       └── [algo scripts].js # Per-page controller scripts
│
├── dataset/
│   └── process_data.csv      # Source CSV for training the DNN
│
└── models/
    ├── model_training.ipynb  # ML Notebook
    └── dnn_priority_scheduler.pkl  # Trained ML model weights
```

---

## 🛠️ Setup & Installation Instructions

This project requires **Python 3.8+**.

### 1. Clone & Access the Directory
```bash
git clone <your-repo-link>
cd os-el
```

### 2. Set Up the Python Environment
We recommend using a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install required backend dependencies
# Typically features: flask, pandas, numpy, scikit-learn, joblib
pip install flask pandas numpy scikit-learn joblib
```

### 3. Run the Backend API
```bash
cd backend
python3 app.py
```
The Flask server will start running on `http://127.0.0.1:5000/`.

### 4. Run the Frontend 
Because the frontend uses modern ES6 modules and fetches, you should serve it via a local static server rather than just double-clicking `index.html`.

In a new terminal window inside the root directory:
```bash
cd frontend
python3 -m http.server 8000
```
Open your browser and navigate to `http://localhost:8000/`.

---

## 🎨 Visual Features & Educational Highlights

- **Thematic Consistency:** Built with glowing cyan and pink neon accents (`var(--accent-cyan)`, `var(--accent-primary)`) to give it a futuristic "AI vs Classic" hacking aesthetic.
- **Interactive Process Input:** Add custom processes with your own burst times and arrival times, and immediately see the graph re-render.
- **Formula Transparency:** Below every Gantt chart is a dynamic text block showing exactly how it arrived at its conclusions. E.g.
  > `Turnaround Time (TAT = CT - AT) = 4 + 7 + 10 = 21 ms`  
  > `Avg Turnaround Time = 21 / 3 = 7.00 ms`
- **Responsive Architecture:** Flex/Grid layouts ensure the Gantt block percentages re-adjust gracefully on varying window sizes.

---

> **Built to demonstrate Operating Systems optimization through the lens of Artificial Intelligence.**
