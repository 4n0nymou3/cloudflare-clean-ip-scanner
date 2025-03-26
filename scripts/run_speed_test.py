import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.speed_tester import run_speed_test

if __name__ == "__main__":
    run_speed_test()
