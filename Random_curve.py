import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.backends.backend_agg import RendererAgg
import threading

# Lock to prevent Matplotlib's threading issues
_lock = threading.Lock()

# Function to generate the randomized sine wave
def generate_randomized_wave(length=100, cycles=3, peak=300, randomness_level=5, min_fraction=0.25):
    """
    Generates a randomized wave with a minimum Y value (controlled by `min_fraction`).

    Args:
    - length (int): Total number of records.
    - cycles (int): Number of cycles in the wave.
    - peak (int): Peak value to be touched in each cycle.
    - randomness_level (int): Controls the randomness (1 = minimal, 10 = maximal).
    - min_fraction (float): The minimum fraction of the peak that the wave can go down to.

    Returns:
    - x (numpy array): The x-axis values (e.g., days).
    - y (numpy array): The randomized wave values.
    """
    records_per_cycle = length // cycles
    x = np.arange(length)  # Generate x values (e.g., days)
    y = np.zeros(length)  # Initialize wave values
    min_value = peak * min_fraction  # Set the minimum y-value

    for i in range(cycles):
        start = i * records_per_cycle
        end = start + records_per_cycle
        cycle_length = end - start

        # Ensure increments and decrements sum to cycle_length
        half_cycle = cycle_length // 2
        increments = np.abs(np.random.normal(loc=peak / cycle_length, scale=randomness_level, size=half_cycle))
        decrements = -np.abs(np.random.normal(loc=peak / cycle_length, scale=randomness_level, size=cycle_length - half_cycle))

        # Combine increments and decrements
        cycle = np.cumsum(np.concatenate([increments, decrements]))
        cycle = cycle - cycle.min()  # Normalize to start from 0
        cycle = cycle * ((peak - min_value) / cycle.max()) + min_value  # Scale between min_value and peak
        cycle[np.argmax(cycle)] = peak  # Ensure peak is touched

        # Add some noise (ensure size matches `cycle_length`)
        noise = np.random.uniform(-randomness_level, randomness_level, size=cycle_length)
        cycle += noise
        cycle = np.clip(cycle, min_value, peak)  # Ensure values are within bounds

        y[start:end] = cycle  # Insert the cycle into the main wave

    return x, y


# Streamlit app
def main():
    st.title("Randomized Wave Generator")

    # User inputs
    st.sidebar.header("Configuration")
    length = st.sidebar.number_input("Total Number of Records", min_value=50, max_value=1000, value=100, step=10)
    cycles = st.sidebar.number_input("Number of Cycles", min_value=1, max_value=10, value=3, step=1)
    peak = st.sidebar.number_input("Peak Value", min_value=100, max_value=1000, value=300, step=10)
    randomness_level = st.sidebar.slider("Randomness Level", min_value=1, max_value=10, value=5)

    # Add a slider for minimum fraction in the Streamlit sidebar
    min_fraction = st.sidebar.slider(
        "Minimum Fraction of Peak (Lowest Y Value)", min_value=0.1, max_value=0.5, value=0.25, step=0.05
    )

    # Generate the wave
    x, y = generate_randomized_wave(
        length=length, cycles=cycles, peak=peak, randomness_level=randomness_level, min_fraction=min_fraction
    )

    # Plot the wave
    with _lock:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(x, y, label="Randomized Wave", color="blue", marker="o")
        ax.axhline(peak, color="orange", linestyle="--", label=f"Peak ({peak})")
        ax.fill_between(x, y, where=(y == peak), color="red", alpha=0.5, label="Touched Peak")
        ax.set_title("Randomized Wave with Peaks")
        ax.set_xlabel("X (Days)")
        ax.set_ylabel("Y (Value)")
        ax.legend()
        ax.grid(True)

        # Show the plot in Streamlit
        st.pyplot(fig)

if __name__ == "__main__":
    main()
