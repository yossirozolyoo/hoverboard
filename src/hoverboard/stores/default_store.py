import os
from .store import BinaryStore


default_path = os.path.join(os.path.dirname(__file__), '_default')
if not os.path.isdir(default_path):
    os.mkdir(default_path)

default = BinaryStore(default_path)
