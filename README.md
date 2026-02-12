# Muse Real-Time Brainwave Visualizer

A lightweight, high-performance Python interface for the Interaxon Muse headband. This tool connects via Bluetooth Low Energy (BLE), processes raw EEG data in real-time using the Welch method, and visualizes the five major brainwave bands (Delta, Theta, Alpha, Beta, Gamma).

Unlike complex BCI suites, this project focuses on a "plug-and-play" experience for researchers and developers who need immediate access to live brainwave data and CSV logging.


##  Features

* **Real-time Visualization:** Smooth, multi-threaded plotting of band power using `pyqtgraph`.
* **Automatic Device Discovery:** Includes a helper script to find your Muse's MAC address instantly.
* **Signal Processing:** Implements a sliding buffer and Welch's Power Spectral Density (PSD) to extract frequency bands.
* **Data Logging:** Automatically saves session data (Timestamp + Band Powers) to the `data/` folder for post-analysis.
* **Stable Connection:** Uses a robust proxy to handle Bluetooth dropouts and reconnections.

##  Project Structure

```text
Muse-Realtime-Monitor/
├── data/                  # Stores your recorded CSV session files
├── proxies/               # Core connection logic for the Muse headband
│   └── MuseProxy.py       
├── find_muse.py           # Helper script to scan for your device
├── main.py                # Main application script
├── requirements.txt       # List of dependencies
├── LICENSE                # MIT License
└── README.md              # Documentation

```

##  Prerequisites

* **Hardware:** A Muse Headband (Muse 2 or Muse S recommended).
* **OS:** Windows, macOS, or Linux with Bluetooth Low Energy (BLE) support.
* **Python:** Version 3.8 or higher.

##  Installation

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/Muse-Realtime-Monitor.git
cd Muse-Realtime-Monitor

```


2. **Install dependencies:**
```bash
pip install -r requirements.txt

```



##  Configuration & Usage

### Step 1: Find your Device

If you don't know your Muse's MAC address, turn on your headband and run the helper script:

```bash
python find_muse.py

```

*Copy the address it finds (e.g., `00:55:DA:B9:9C:EE`).*

### Step 2: Run the Monitor

Open `main.py` and replace the `MUSE_MAC_ADDRESS` variable at the top with your address.

Alternatively, you can pass the address directly as an argument:

```bash
python main.py 00:55:DA:B9:9C:EE

```

### Step 3: Controls

* The connection process will start automatically.
* Once connected, a window will appear displaying the 5 live brainwave bands.
* **To Stop:** Close the visualization window or press `Ctrl+C` in the terminal.
* **Data:** Your session is automatically saved to `data/brainwaves_YYYY-MM-DD_...csv`.

##  The Frequency Bands

This tool visualizes the following standard EEG bands:

| Band | Frequency Range | Associated State |
| :--- | :--- | :--- |
| **Delta** | 0.5 - 4 Hz | Deep sleep, unconsciousness |
| **Theta** | 4 - 8 Hz | Meditation, drowsiness, creativity |
| **Alpha** | 8 - 13 Hz | Relaxation, closed eyes, calm |
| **Beta** | 13 - 30 Hz | Active thinking, focus, alertness |
| **Gamma** | 30 - 100 Hz | High-level cognitive processing |

##  Contributing

Contributions are welcome! If you have a bug fix or a new feature (like Neurofeedback audio), please fork the repository and submit a pull request.

##  Disclaimer

This software is for educational and research purposes only. It is not a medical device and should not be used for diagnosis, treatment, or prevention of any health condition.

## Acknowledgements

Author: Rubathiyagish 
(rubathiyagish@gmail.com)

Mentor/Guide: Prof.Sandeep Budde

Institution: NITTE School of Architecture Planning and Design (NITTE SAPD), Bengaluru

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
