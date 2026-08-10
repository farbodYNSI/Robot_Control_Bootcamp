# 🌡️ Bang-Bang Heater Controller Simulation

A real-time thermal simulation that demonstrates a bang-bang controller. Visualized via a thermometer and a live strip chart using OpenCV.

## 🛠️ Features
- Real-time temperature visualization (Thermometer & Strip Chart)
- Heater status overlay and historical temperature tracing
- Customizable environment temperature, heating rates, and cooling coefficients

## 📋 Requirements
- **Python 3.10 or higher** (The code uses modern `float | None` type hint syntax)
- **OpenCV** (`opencv-python`)
- **NumPy** (`numpy`)

## 🚀 Installation

1. **Clone or download this repository.**

2. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```


## Usage

Run the main script from your terminal:
  ```bash
  python main.py
  ```

## Controls
- Press q or Esc to quit the simulation.

## Project Structure

```text
.
├── heat_simulation.py   # Contains the Simulator class, physics, and OpenCV rendering
├── main.py              # Entry point, contains the control logic loop
├── requirements.txt     # Project dependencies
└── README.md            # This file