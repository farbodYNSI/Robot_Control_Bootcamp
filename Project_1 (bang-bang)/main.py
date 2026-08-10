from heat_simulation import Simulator

def main() -> None:
    sim = Simulator()
    heat = False
    try:
        while True:
            # write your code here
            temp = sim.current_temp()

            
            key = sim.run(heat) #True for turning on the heating element, False for turning it off
            if key in (ord("q"), 27):  # 'q' or Esc to quit
                break
    finally:
        sim.close()


if __name__ == "__main__":
    main()
