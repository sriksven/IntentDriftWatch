from pathlib import Path

print("This file:", Path(__file__).resolve())
print("Project root (1 levels up):", Path(__file__).resolve().parents[1])
