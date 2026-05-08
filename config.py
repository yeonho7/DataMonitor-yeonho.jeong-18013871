import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "DataPersistence"))

DATA_DIR = os.environ.get(
    "DATA_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"),
)
DATA_SAMPLES = os.path.join(DATA_DIR, "samples.json")
DATA_ORDERS = os.path.join(DATA_DIR, "orders.json")

MONITORED_STATUSES = ["RESERVED", "PRODUCING", "CONFIRMED", "RELEASED"]
ACTIVE_STATUSES = ["RESERVED", "PRODUCING", "CONFIRMED"]
