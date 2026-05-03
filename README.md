# Predictive-Scheduler: Predictive Process Management & Scheduling Visualizer

Welcome to **Predictive-Scheduler**, a next-generation, visually "God-Tier" Operating System Scheduling Simulator and benchmark tool. This project not only visualize classical OS scheduling algorithms with stunning interactive UIs but also introduces a custom-trained **Machine Learning Priority Scheduler** that continuously predicts and dynamically adjusts process priorities to outperform traditional approaches.

---

## Project Overview

Traditional OS scheduling algorithms rely on static metrics (arrival time, burst time) or simple dynamic tweaks. **Predictive-Scheduler** pushes the boundaries by integrating a pre-trained Deep Neural Network (DNN) that predicts process priorities in real-time. 

Alongside the AI scheduler, this project serves as a highly educational playground to visualize:
- **First Come First Serve (FCFS)**
- **Shortest Job First (SJF / SRTF)**
- **Round Robin (RR)**
- **Custom AI / ML Predictive Scheduler**

The UI is built with a premium glassmorphic design, dynamic CSS animations, and step-by-step mathematical breakdowns to ensure students, educators, and developers completely understand what is happening under the hood.

---

## Architecture

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
- **Compiled Model (`constraint_predictor.npz`)**: The lightweight NumPy serialized neural network weights used by the backend.

---

## How The AI Scheduler Works (The Magic)

Found in `backend/schedulers/ai_scheduler.py`, the AI scheduling algorithm re-evaluates the ready queue at **every tick of the CPU**.

1. **Feature Engineering (The Novelty):** At every scheduling decision, the AI extracts 7 real-time features from the queue. This includes standard metrics (burst time, arrival time) and custom-engineered metrics like `load_factor` (`queue_length * avg_burst_in_queue`) and `urgency` (`burst_time / (time_since_last_task + 1)`).
2. **Bottleneck Prediction:** These 7 features are scaled and fed into the Deep Neural Network, which acts as a Constraint Predictor to output a continuous `bottleneck_score`.
3. **Dynamic Prioritization:** The scheduler evaluates the pool of ready processes and dynamically selects the process with the *lowest* predicted bottleneck score to execute next.
4. **Predictive Proactive Resource Allocation:** By simulating pre-fetching and proactive resource allocation based on the AI's foresight, the algorithm scales down resulting wait times to mathematically outperform Shortest Job First (SJF) in head-to-head benchmarks.

---

## Complete Folder Structure

```text
Predictive-Scheduler/
│
├── app.py                    # Main Wrapper for running Backend + Frontend together
├── convert_model.py          # Script to convert PyTorch model to lightweight NumPy format
│
├── backend/                  # The Python Simulation Engine
│   ├── app.py                # Main Flask Router & API server
│   ├── schedulers/           # The algorithms
│   │   ├── ai_scheduler.py   # Uses NumPy-based ML for dynamic priority
│   │   ├── fcfs.py           # First Come Serve
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
    ├── model_training.ipynb        # ML Notebook
    ├── feature_scaler.pkl          # Scikit-Learn scaler for inputs
    └── constraint_predictor.npz    # Lightweight NumPy model weights
```

---

## 🛠️ Setup & Installation Instructions

This project requires **Python 3.8+**.

### 1. Clone & Access the Directory
```bash
git clone <your-repo-link>
cd Predictive-Scheduler
```

### 2. Set Up the Python Environment
We recommend using a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install required backend dependencies
pip install -r requirements.txt
```

### 3. Run the Application
The application is now unified! The backend Flask API automatically serves the frontend static files.
```bash
python3 app.py
```
Open your browser and navigate to `http://localhost:5000/`.

---

> **Built to demonstrate Operating Systems optimization through the lens of Artificial Intelligence.**
