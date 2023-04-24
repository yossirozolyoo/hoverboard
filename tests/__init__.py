import sys
import os

MODULE_NAME = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(MODULE_NAME, '..', 'src'))

sys.path.insert(0, SRC_DIR)
