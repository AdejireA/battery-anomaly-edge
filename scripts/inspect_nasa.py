from pathlib import Path
import scipy.io

DATA_PATH = Path("data/raw/nasa/B0005.mat")

print(f"Loading: {DATA_PATH}")
print(f"File exists: {DATA_PATH.exists()}")

mat = scipy.io.loadmat(DATA_PATH)

print("\n=== TOP-LEVEL MATLAB KEYS ===")
for key in mat.keys():
    if not key.startswith("__"):
        print(f"{key}: {type(mat[key])}")

battery = mat["B0005"]

print("\n=== B0005 STRUCTURE ===")
print("Shape:", battery.shape)
print("Dtype:", battery.dtype)
print("Fields:", battery.dtype.names)

cycle = battery["cycle"][0, 0]

print("\n=== CYCLE STRUCTURE ===")
print("Shape:", cycle.shape)
print("Dtype:", cycle.dtype)
print("Fields:", cycle.dtype.names)
print("Number of operation records:", cycle.size)

# ---------------------------------------------------------
# Count operation types
# ---------------------------------------------------------

from collections import Counter

operation_types = []

for record in cycle.flat:
    operation_type = record["type"]

    # MATLAB string -> Python string
    operation_type = operation_type[0]

    operation_types.append(operation_type)

counts = Counter(operation_types)

print("\n=== OPERATION TYPE COUNTS ===")
for operation_type, count in counts.items():
    print(f"{operation_type}: {count}")


# ---------------------------------------------------------
# Inspect the first discharge operation
# ---------------------------------------------------------

for record in cycle.flat:
    operation_type = record["type"][0]

    if operation_type == "discharge":

        print("\n=== FIRST DISCHARGE RECORD ===")

        print("Type:", operation_type)
        print("Ambient temperature:", record["ambient_temperature"])
        print("Start time:", record["time"])

        data = record["data"][0, 0]

        print("\nDischarge data fields:")
        print(data.dtype.names)

        print("\nField shapes:")

        for field in data.dtype.names:
            value = data[field]

            print(
                f"{field}: "
                f"shape={value.shape}, "
                f"dtype={value.dtype}"
            )

        break