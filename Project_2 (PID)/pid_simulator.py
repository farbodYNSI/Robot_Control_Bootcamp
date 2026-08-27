import math
from pathlib import Path

import cv2
import numpy as np


class PIDSimulator:
    def __init__(self, image_path="fire.png", dt=0.05,
                 control_mode="acceleration", max_command=2.0,
                 window_name="PID Teaching Simulator"):

        self.dt = float(dt)
        self.control_mode = control_mode
        self.max_command = float(max_command)
        self.window_name = window_name

        self.angle = math.pi / 2
        self.speed = 0.0
        self.acceleration = 0.0
        self.time = 0.0

        self.min_angle = 0.10
        self.max_angle = 3.04

        self.target_x = 300.0
        self.target_y = 650.0
        self.target_vx = 0.0
        self.target_vy = 0.0

        self.target_is_moving = False
        self.target_linear_speed = 250.0
        self.target_direction = 1.0
        self.target_x_min = -520.0
        self.target_x_max = 520.0

        self.actuator_disturbance = 0.0

        # Simulator calculates the integral for the student.
        self.error_integral = 0.0

        self.canvas_width = 1100
        self.canvas_height = 635
        self.pivot = (self.canvas_width // 2, 640)
        self.arm_length = 150 

        self.image = None
        image_file = Path(image_path)
        if image_file.exists():
            self.image = cv2.imread(str(image_file))

        self.running = True
        self.last_command = 0.0
        self.last_actual_command = 0.0

    # --------------------------------------------------------
    # Student-facing signals
    # --------------------------------------------------------

    def get_error(self):
        return self._wrap_angle(self.get_target_angle() - self.angle)

    def get_error_derivative(self):
        return self.get_target_angle_derivative() - self.speed

    def get_error_integral(self):
        return self.error_integral

    # --------------------------------------------------------
    # Target information
    # --------------------------------------------------------

    def get_target_angle(self):
        return math.atan2(self.target_y, self.target_x)

    def get_target_angle_derivative(self):
        denominator = self.target_x**2 + self.target_y**2

        if denominator < 1e-12:
            return 0.0

        return (
            self.target_x * self.target_vy
            - self.target_y * self.target_vx
        ) / denominator

    # --------------------------------------------------------
    # Teacher settings
    # --------------------------------------------------------

    def randomize_stationary_target(self):
        self.set_target_stationary(
            x=np.random.uniform(-500, 500),
            y=np.random.uniform(580, 720),
    )

    def set_control_mode(self, mode):
        if mode not in ("acceleration", "velocity"):
            raise ValueError("mode must be 'acceleration' or 'velocity'")

        self.control_mode = mode
        self.speed = 0.0
        self.acceleration = 0.0
        self.error_integral = 0.0

    def set_actuator_disturbance(self, disturbance):
        self.actuator_disturbance = float(disturbance)

    def set_target_stationary(self, x=300, y=650):
        self.target_is_moving = False
        self.target_x = float(x)
        self.target_y = float(y)
        self.target_vx = 0.0
        self.target_vy = 0.0
        self.error_integral = 0.0

    def set_target_moving(self, speed=250, x=-500, y=650):
        self.target_is_moving = True
        self.target_linear_speed = abs(float(speed))
        self.target_x = float(x)
        self.target_y = float(y)
        self.error_integral = 0.0

    def reset(self):
        self.angle = math.pi / 2
        self.speed = 0.0
        self.acceleration = 0.0
        self.time = 0.0
        self.error_integral = 0.0

    # --------------------------------------------------------
    # Simulation
    # --------------------------------------------------------

    def step(self, command):
        # Integral is calculated internally.
        error = self.get_error()
        self.error_integral += error * self.dt

        command = float(np.clip(command, -self.max_command, self.max_command))
        actual_command = command + self.actuator_disturbance

        if self.control_mode == "acceleration":
            self.acceleration = actual_command
            self.angle += (
                self.speed * self.dt
                + 0.5 * self.acceleration * self.dt**2
            )
            self.speed += self.acceleration * self.dt

        elif self.control_mode == "velocity":
            self.acceleration = 0.0
            self.speed = actual_command
            self.angle += self.speed * self.dt

        self._apply_angle_limits()
        self._update_target()

        self.last_command = command
        self.last_actual_command = actual_command
        self.time += self.dt

    def run(self, command):
        if not self.running:
            return False

        self.step(command)
        frame = self._draw()
        cv2.imshow(self.window_name, frame)

        key = cv2.waitKey(max(1, int(self.dt * 1000))) & 0xFF

        if key in (27, ord("q")):
            self.running = False

        elif key == ord("r"):
            self.reset()

        elif key == ord("n"):
            self.randomize_stationary_target()

        return self.running

    def close(self):
        cv2.destroyAllWindows()

    # --------------------------------------------------------
    # Internal helpers
    # --------------------------------------------------------

    def _update_target(self):
        if not self.target_is_moving:
            self.target_vx = 0.0
            self.target_vy = 0.0
            return

        self.target_vx = self.target_direction * self.target_linear_speed
        self.target_vy = 0.0
        self.target_x += self.target_vx * self.dt

        if self.target_x >= self.target_x_max:
            self.target_x = self.target_x_max
            self.target_direction = -1.0

        elif self.target_x <= self.target_x_min:
            self.target_x = self.target_x_min
            self.target_direction = 1.0

    def _apply_angle_limits(self):
        if self.angle <= self.min_angle:
            self.angle = self.min_angle
            if self.speed < 0:
                self.speed = 0.0

        elif self.angle >= self.max_angle:
            self.angle = self.max_angle
            if self.speed > 0:
                self.speed = 0.0

    @staticmethod
    def _wrap_angle(angle):
        return (angle + math.pi) % (2 * math.pi) - math.pi

    def _world_to_pixel(self, x, y):
        scale = 0.72
        return (
            int(self.pivot[0] + x * scale),
            int(self.pivot[1] - y * scale),
        )

    def _draw(self):
        frame = np.zeros(
            (self.canvas_height, self.canvas_width, 3),
            dtype=np.uint8,
        )

        target_px = self._world_to_pixel(self.target_x, self.target_y)
        cv2.circle(frame, target_px, 8, (0, 220, 0), -1)

        target_angle = self.get_target_angle()
        reference_end = (
            int(self.pivot[0] + self.arm_length * math.cos(target_angle)),
            int(self.pivot[1] - self.arm_length * math.sin(target_angle)),
        )
        cv2.line(frame, self.pivot, reference_end, (60, 60, 60), 2)

        arm_end = (
            int(self.pivot[0] + self.arm_length * math.cos(self.angle)),
            int(self.pivot[1] - self.arm_length * math.sin(self.angle)),
        )
        cv2.line(frame, self.pivot, arm_end, (0, 0, 180), 16)
        cv2.circle(frame, self.pivot, 34, (0, 0, 170), -1)

        self._draw_info(frame)
        return frame

    def _draw_info(self, frame):
        mode = "acceleration" if self.control_mode == "acceleration" else "velocity"

        lines = [
            f"Mode: {mode}",
            f"error = {self.get_error(): .3f}",
            f"error_dot = {self.get_error_derivative(): .3f}",
            f"error_integral = {self.get_error_integral(): .3f}",
            f"command = {self.last_command: .3f}",
            f"actual actuator = {self.last_actual_command: .3f}",
            f"constant disturbance = {self.actuator_disturbance: .3f}",
            "Q/ESC: quit   R: reset   N: new target",
        ]

        y = 30
        for line in lines:
            cv2.putText(
                frame, line, (20, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                (230, 230, 230), 1, cv2.LINE_AA
            )
            y += 28
