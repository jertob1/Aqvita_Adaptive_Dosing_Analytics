import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from scipy.interpolate import LinearNDInterpolator
from dataFile import get_trainingData
import json

# === Load Data ===
X, TDS = get_trainingData()
interpolator = LinearNDInterpolator(X, TDS)

# === Parameters ===
VALVE_MIN = 25
VALVE_STEP = 3
VALVE_MAX = 300
CUMULATIVE_MIN = 625
CUMULATIVE_STEP = 75
CUMULATIVE_MAX = 42000

# === Generate grid for ESP32 header (valve_times and times)
valve_times_grid = np.arange(VALVE_MIN, VALVE_MAX, VALVE_STEP)
cumulative_times_grid = np.arange(CUMULATIVE_MIN, CUMULATIVE_MAX, CUMULATIVE_STEP)

def generate_lookup_table():
    """Generate C++ header file with interpolated TDS values."""
    header_lines = [
        f"const int VALVE_MIN = {VALVE_MIN};",
        f"const int VALVE_STEP = {VALVE_STEP};",
        f"const int CUMULATIVE_MIN = {CUMULATIVE_MIN};",
        f"const int CUMULATIVE_STEP = {CUMULATIVE_STEP};",
        f"const float TDS_LOOKUP[{len(valve_times_grid)}][{len(cumulative_times_grid)}] = {{"
    ]

    for vt in valve_times_grid:
        row = []
        for ct in cumulative_times_grid:
            tds = interpolator(vt, ct)
            if tds is None or np.isnan(tds):
                row.append("-1.0")
            else:
                row.append(f"{tds:.2f}")
        header_lines.append("    {" + ", ".join(row) + "},")
    header_lines.append("};")

    with open("TDS_Lookup.h", "w") as f:
        f.write("\n".join(header_lines))


def main():
    print("Generating TDS Lookup Header...")
    generate_lookup_table()

    # Initial conditions
    valveTime = 25
    cumulativeTime = valveTime * 25  # First cycle
    tds = interpolator(valveTime, cumulativeTime)

    # Store results
    matches = []
    cumulative_times = []

    # Define search range
    valve_times = np.arange(25, 300, 3)
    target_min, target_max = 90, 120
    target_tds = 100

    while tds is not None and target_min <= tds <= target_max:
        cumulative_times.append(cumulativeTime)
        matches.append((valveTime, cumulativeTime, tds))

        # Step 1: Find best next valve time
        best_vt = valveTime
        min_diff = float('inf')

        #===== Adaptive Dosing routine
        for vt in valve_times:
            next_time = cumulativeTime + vt * 25  # Next full injection cycle
            temp_tds = interpolator(vt, next_time)
            if temp_tds is not None:
                diff = abs(temp_tds - target_tds)
                if diff < min_diff:
                    min_diff = diff
                    best_vt = vt
        
        # Step 2: Update valveTime and cumulativeTime
        valveTime = best_vt
        cumulativeTime += valveTime * 25
        tds = interpolator(valveTime, cumulativeTime)

    #=== 6. Show the result (example print)
    # print(len(matches))
    # for (vt, ct, tds) in matches:
    #    print(f"Valve time: {vt} ms, Cumulative time: {ct} ms → TDS₀ ≈ {tds:.2f} ppm")

    # === Plotting
    plt.figure(figsize=(12, 6))

    valve_times_to_plot = np.arange(25, 301, 20)
    timePlot = np.arange(625, 45000, 100)

    for (vt, a, b) in matches:
        tds_values = [interpolator(vt, ct) for ct in timePlot]
        if all(t is not None for t in tds_values):  # Avoid broken lines
            plt.plot(timePlot, tds_values, label=f'{vt} ms')

    plt.xlabel("Cumulative Valve Open Time (ms)")
    plt.ylabel("Predicted TDS₀ (ppm)")
    plt.title("Interpolated TDS₀ vs. Cumulative Time\n(Every 10ms Valve Time Step from 25ms to 300ms)")
    plt.legend(loc='upper right', fontsize='small', ncol=2)
    plt.grid(True)
    plt.tight_layout()
    # plt.show()

if __name__ == "__main__":
    main()
