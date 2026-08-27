# 🎯 PID Teaching Simulator

A simple real-time rotational control simulator designed for teaching **P, PD, PI, and PID controllers step by step**.

The simulator handles the plant dynamics, GUI, target motion, error derivative, and error integral internally so students can focus only on the controller equation.

## 🛠️ Features
- Real-time rotational system visualization using OpenCV
- Stationary and moving targets
- Angular acceleration and angular velocity input modes
- Built-in error, derivative of error, and integral of error
- Constant actuator disturbance for demonstrating steady-state error
- Simple student-facing `main.py`
- Progressive teaching from P to PD, PID, and PI tracking

## 📋 Requirements
- **Python 3.10 or higher**
- **OpenCV** (`opencv-python`)
- **NumPy** (`numpy`)

## 🚀 Installation

1. Clone or download this repository.

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

## ▶️ Usage

Run the main script:

```bash
python main.py
```

## 🎓 Student Interface

Students mainly work inside this section of `main.py`:

```python
error = sim.get_error()
error_dot = sim.get_error_derivative()
error_integral = sim.get_error_integral()

# ==========================================
# WRITE YOUR CODE HERE
# ==========================================

control = 0.0

# ==========================================
```

### P Controller

```python
kp = 4.0
control = kp * error
```

### PD Controller

```python
kp = 4.0
kd = 2.5
control = kp * error + kd * error_dot
```

### PID Controller

```python
kp = 4.0
kd = 2.5
ki = 1.0

control = (
    kp * error
    + kd * error_dot
    + ki * error_integral
)
```

The simulator calculates the derivative and integral internally, so students do not need to implement numerical differentiation or integration yet.

## 🎮 Controls
- Press `q` or `Esc` to quit.
- Press `r` to reset.
- Press 'n' to change target.

## 📁 Project Structure

```text
.
├── pid_simulator.py      # Simulator physics, target motion, PID signals, and GUI
├── main.py               # Student-facing control loop
├── teacher_examples.py   # Instructor reference examples
├── fire.png              # Optional visual asset
├── requirements.txt      # Project dependencies
└── README.md             # This file
```
