import threading, time
from datetime import datetime, timedelta

HOLDS_CACHE = {}   # id_hold → {"expira": datetime, "timer": Timer}
LOCK = threading.Lock()
