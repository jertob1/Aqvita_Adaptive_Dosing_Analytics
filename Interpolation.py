import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt


import numpy as np
from scipy.interpolate import griddata

# === Input features: [valve_time_ms, cumulative_open_time_ms]
X = np.array([
    # 25ms
    [25, 625], [25, 1250], [25, 1875], [25, 2500], [25, 3125],
    [25, 3750], [25, 4375], [25, 5000], [25, 5625], [25, 6250],
    [25, 6875], [25, 7500], [25, 8125], [25, 8750], [25, 9375],
    [25, 10000], [25, 10625], [25, 11250], [25, 11875], [25, 12500],
    [25, 13125], [25, 13750], [25, 14375], [25, 15000], [25, 15625],
    
    # 50ms
    [50, 1250], [50, 2500], [50, 3750], [50, 5000], [50, 6250],
    [50, 7500], [50, 8750], [50, 10000], [50, 11250], [50, 12500],
    [50, 13750], [50, 15000], [50, 16250], [50, 17500], [50, 18750],
    [50, 20000], [50, 21250], [50, 22500],

    # 75ms
    [75, 1875], [75, 3750], [75, 5625], [75, 7500], [75, 9375],
    [75, 11250], [75, 13125], [75, 15000], [75, 16875], [75, 18750],
    [75, 20625], [75, 22500], [75, 24375], [75, 26250], [75, 28125],

    # 100ms
    [100, 2500], [100, 5000], [100, 7500], [100, 10000], [100, 12500],
    [100, 15000], [100, 17500], [100, 20000], [100, 22500], [100, 25000],
    [100, 27500], [100, 30000], [100, 32500], [100, 35000], [100, 37500], [100, 40000],

    # 200ms
    [200, 5000], [200, 10000], [200, 15000], [200, 20000], [200, 25000],
    [200, 30000], [200, 35000], [200, 40000], [200, 45000], [200, 50000],

    # 300ms
    [300, 7500], [300, 15000], [300, 22500], [300, 30000], [300, 37500], [300, 45000]
])

# === Corresponding TDS₀ values
TDS = np.array([
    # 25ms
    102, 110, 103, 98, 92, 89, 81, 71, 68, 62,
    58, 54, 50, 46, 46, 42, 39, 39, 37, 34,
    35, 31, 30, 29, 28,

    # 50ms
    151, 142, 132, 114, 104, 94, 82, 74, 64, 60,
    54, 47, 47, 41, 41, 36, 32, 32,

    # 75ms
    183.83, 175.96, 154.32, 135.34, 118.69, 104.09, 91.29, 80.06,
    70.21, 61.58, 58.94, 56.4, 54.0, 51.69, 49.6,

    # 100ms
    199, 191, 158, 134, 108, 96, 76, 62, 52, 41,
    33, 29, 30, 27, 28, 27,

    # 200ms
    337, 264, 193, 157, 112, 84, 60, 42, 37, 38,

    # 300ms
    441, 276, 184, 107, 63, 34
])

# Generate new test points for interpolation
valve_times_new = np.array([25,40,50,100, 125, 175,200,300])  # ms
cumulative_times = np.arange(625, 45000, 625)  # ms

grid_new = np.array([[vt, ct] for vt in valve_times_new for ct in cumulative_times])

TDS_interp = griddata(X, TDS, grid_new, method='linear')  # or 'cubic' if enough data

# Plot TDS0 vs cumulative valve time for new interpolated valve times
for i, vt in enumerate(valve_times_new):
    tds_curve = TDS_interp[i * len(cumulative_times):(i + 1) * len(cumulative_times)]
    plt.plot(cumulative_times, tds_curve, label=f'{vt}ms')

def predict_tds(valve_time_ms, cumulative_open_time_ms, method='linear'):
    """
    Predict TDS₀ given valve time and cumulative valve open time.
    - valve_time_ms: e.g. 75
    - cumulative_open_time_ms: e.g. 6250
    - method: 'linear' or 'cubic' (linear is more robust if data is sparse)
    """
    point = np.array([[valve_time_ms, cumulative_open_time_ms]])
    tds_pred = griddata(X, TDS, point, method=method)
    return tds_pred[0]  # Return scalar

# Predict TDS₀ for 75ms valve time after 6250ms cumulative open time
tds_value = predict_tds(125, 10750)
print(f"Predicted TDS₀: {tds_value:.2f} ppm")
tds_value = predict_tds(125, 13875)
print(f"Predicted TDS₀: {tds_value:.2f} ppm")

plt.xlabel('Cumulative Valve Open Time (ms)')
plt.ylabel('TDS₀')
plt.title('Interpolated TDS₀ vs Cumulative Time for Valve Times')
plt.legend()
plt.grid()
plt.show()

