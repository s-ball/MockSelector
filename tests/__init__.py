import os
import sys

current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.extend((current_path, os.path.dirname(current_path)))
