from collections import deque

import cv2
import numpy as np


class Simulator:
    def __init__(
        self,
        width: int = 400,
        height: int = 200,
        env_temp: float = 25.0,
        initial_temp: float = 25.0,
        heating_rate: float = 1.0,
        cooling_coeff: float = 0.08,
        setpoint_low: float | None = None,
        setpoint_high: float | None = None,
        history_len: int = 300,
    ):
        self.width = width
        self.height = height
        self.env_temp = env_temp
        self.current_temp = initial_temp
        self.heating_on = False

        self.heating_rate = heating_rate
        self.cooling_coeff = cooling_coeff

        # Optional threshold lines drawn on the strip chart, purely visual.
        self.setpoint_low = setpoint_low
        self.setpoint_high = setpoint_high

        self.history = deque(maxlen=history_len)
        self.window_name = "Bang-Bang Heater Controller"
        cv2.namedWindow(self.window_name)

    def update_temperature(self, heating_on: bool) -> None:
        """Advance the plant model by one tick."""
        self.heating_on = heating_on
        if heating_on:
            self.current_temp += self.heating_rate
        else:
            self.current_temp += (self.env_temp - self.current_temp) * self.cooling_coeff

    # -- drawing helpers -----------------------------------------------

    def _draw_thermometer(self) -> np.ndarray:
        panel_w = self.width // 3 + 20
        img = np.full((self.height + 40, panel_w, 3), 25, dtype=np.uint8)

        temp_value = int(np.clip(self.current_temp, 0, 100) / 100 * self.height)

        cv2.rectangle(img, (5, self.height + 5), (self.width // 3 + 5, 15), (60, 60, 60), -1)
        color = (
            0,
            int((1 - np.clip(self.current_temp, 0, 100) / 100) * 255),
            int(np.clip(self.current_temp, 0, 100) / 100 * 255),
        )
        cv2.rectangle(img, (10, self.height), (self.width // 3, self.height - temp_value + 10), color, -1)

        if self.heating_on:
            cv2.ellipse(img, (72, 220), (60, 8), 0, 0, 360, (0, 10, 255), 2)
            cv2.ellipse(img, (72, 220), (40, 4), 0, 0, 360, (0, 10, 255), 2)

        font = cv2.FONT_HERSHEY_SIMPLEX
        text = f"{self.current_temp:.1f} C"
        cv2.putText(img, text, (8, self.height + 35), font, 0.7, (255, 255, 255), 2)

        status = "HEATER ON" if self.heating_on else "heater off"
        status_color = (0, 0, 255) if self.heating_on else (150, 150, 150)
        cv2.putText(img, status, (8, 25), font, 0.5, status_color, 1)

        return img

    def _draw_strip_chart(self) -> np.ndarray:
        chart_w = self.width
        chart_h = self.height + 40
        img = np.full((chart_h, chart_w, 3), 15, dtype=np.uint8)

        top_margin, bottom_margin = 20, 20
        plot_h = chart_h - top_margin - bottom_margin
        lo, hi = 20.0, 90.0  # fixed y-axis range so the plot doesn't jitter

        def y_of(temp: float) -> int:
            frac = (temp - lo) / (hi - lo)
            return int(chart_h - bottom_margin - np.clip(frac, 0, 1) * plot_h)

        # Threshold reference lines
        for thresh, label in ((self.setpoint_low, "low"), (self.setpoint_high, "high")):
            if thresh is not None:
                y = y_of(thresh)
                cv2.line(img, (0, y), (chart_w, y), (90, 90, 90), 1, cv2.LINE_AA)
                cv2.putText(img, f"{label} {thresh:g}", (chart_w - 70, y - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (120, 120, 120), 1)

        # Heater-on shading + temperature trace
        n = len(self.history)
        if n > 1:
            step = chart_w / (self.history.maxlen - 1)
            start_x = chart_w - step * (n - 1)
            pts = []
            for i, (temp, heating) in enumerate(self.history):
                x = int(start_x + step * i)
                y = y_of(temp)
                pts.append((x, y))
                if heating:
                    cv2.line(img, (x, top_margin), (x, chart_h - bottom_margin), (0, 0, 60), 1)
            for p1, p2 in zip(pts, pts[1:]):
                cv2.line(img, p1, p2, (0, 200, 255), 2, cv2.LINE_AA)

        cv2.putText(img, "temperature over time", (8, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        return img

    def draw_temperature_bar(self) -> np.ndarray:
        """Kept for backwards compatibility: just the thermometer panel."""
        return self._draw_thermometer()

    # -- main loop step --------------------------------------------------

    def run(self, heat: bool, delay_ms: int = 100) -> int:
        """Advance the simulation one tick, render it, and return the
        key code pressed (or -1 if none). Caller should check for a
        quit key, e.g. `if key in (ord('q'), 27): break`.
        """
        self.update_temperature(heat)
        self.history.append((self.current_temp, self.heating_on))

        thermometer = self._draw_thermometer()
        chart = self._draw_strip_chart()
        # pad thermometer to match chart height if needed and stack side by side
        combined = np.hstack([thermometer, chart])

        cv2.imshow(self.window_name, combined)
        return cv2.waitKey(delay_ms) & 0xFF

    def close(self) -> None:
        cv2.destroyWindow(self.window_name)