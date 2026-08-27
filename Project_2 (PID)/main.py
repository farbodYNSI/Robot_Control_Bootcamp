from pid_simulator import PIDSimulator


sim = PIDSimulator()

sim.set_target_stationary(x=300, y=650)
sim.set_actuator_disturbance(0.0)

while True:

    error = sim.get_error()

    # ==========================================
    # WRITE YOUR CODE HERE:

    control = 0.0

    # ==========================================

    if not sim.run(control):
        break

sim.close()
