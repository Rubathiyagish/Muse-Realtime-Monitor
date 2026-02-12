import sys
import csv
import atexit
import numpy as np
from time import time, sleep
import signal
from multiprocessing import Process, Queue, Event
from datetime import datetime
from scipy.signal import welch


import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets


from proxies.MuseProxy import MuseProxy

MUSE_MAC_ADDRESS = "00:55:DA:B9:9C:EE"
FS = 256  


BANDS = {
    "Delta": (0.5, 4),
    "Theta": (4, 8),
    "Alpha": (8, 13),
    "Beta":  (13, 30),
    "Gamma": (30, 100)
}



now = datetime.now()
timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
filename = f"brainwaves_{timestamp_str}.csv"



try:
    file_obj = open(f"data/{filename}", "w", newline="")
except FileNotFoundError:
    
    file_obj = open(f"{filename}", "w", newline="")

writer = csv.writer(file_obj)

writer.writerow(["Timestamp", "Delta", "Theta", "Alpha", "Beta", "Gamma"])

def close_file():
    try:
        file_obj.close()
        print(f"File closed: {filename}")
    except:
        pass

atexit.register(close_file)



class Buffer:
    """
    Stores raw EEG data until we have enough to calculate the waves.
    """
    def __init__(self, buffer_duration=1.0, overlap=0.2):
        self.buffer_len = int(FS * buffer_duration)
        self.data_buffer = np.zeros((self.buffer_len, 4)) 
        self.ptr = 0
        self.timestamps = np.zeros(self.buffer_len)

    def add(self, timestamps, data):
        """
        Add new data. If buffer is full, returns True and the full buffer.
        """
        n_samples = data.shape[0]
        
       
        if self.ptr + n_samples > self.buffer_len:
            shift = (self.ptr + n_samples) - self.buffer_len
            self.data_buffer = np.roll(self.data_buffer, -shift, axis=0)
            self.timestamps = np.roll(self.timestamps, -shift)
            self.ptr -= shift
            if self.ptr < 0: self.ptr = 0

      
        end_idx = min(self.ptr + n_samples, self.buffer_len)
        len_to_add = end_idx - self.ptr
        
        if len_to_add > 0:
            self.data_buffer[self.ptr:end_idx, :] = data[:len_to_add]
            self.timestamps[self.ptr:end_idx] = timestamps[:len_to_add]
            self.ptr = end_idx

     
        return self.ptr >= self.buffer_len, self.data_buffer, self.timestamps[-1]

eeg_buffer = Buffer(buffer_duration=1.0) 
viz_queue = Queue()



def compute_band_powers(eeg_data, fs):
    """
    Takes raw EEG (samples x channels), calculates PSD, 
    and returns average power for Alpha, Beta, etc. across all channels.
    """
  

    freqs, psd = welch(eeg_data, fs=fs, nperseg=fs, axis=0)

  

    avg_psd = np.mean(psd, axis=1)

    powers = {}
    for band, (low, high) in BANDS.items():
        
        idx_band = np.logical_and(freqs >= low, freqs <= high)
        # Mean of the power in this band
        band_power = np.mean(avg_psd[idx_band]) if np.any(idx_band) else 0
        powers[band] = band_power
    
    return powers

# ------------------------------
# Callback
# ------------------------------
def eeg_callback(timestamps, data):
    """
    1. Collect raw data.
    2. When buffer is full, compute waves.
    3. Save to CSV and send to Viz.
    """
    is_ready, buffered_data, latest_ts = eeg_buffer.add(timestamps, data)
    
    if is_ready:
        # Calculate wave powers
        powers = compute_band_powers(buffered_data, FS)
        
        # Prepare row: [Timestamp, Delta, Theta, Alpha, Beta, Gamma]
        row = [latest_ts] + [powers[b] for b in ["Delta", "Theta", "Alpha", "Beta", "Gamma"]]
        
        # Save to CSV
        try:
            writer.writerow(row)
        except ValueError:
            pass # Handle occasional file I/O issues gently
        
        # Send to Visualizer
        viz_queue.put(powers)

# ------------------------------
# Visualization Process (PyQtGraph)
# ------------------------------
def visualizer_process(input_queue, stop_event):
    # FIX: Use pg.mkQApp() to handle Qt version differences automatically
    app = pg.mkQApp("Brainwave Monitor")
    
    # Setup Window
    win = pg.GraphicsLayoutWidget(title="Realtime Brainwaves")
    win.resize(1000, 800)
    win.setWindowTitle('Muse Brainwave Monitor')
    win.show()

    # Create 5 distinct plots vertically
    curves = {}
    data_buffers = {} 
    band_names = ["Delta", "Theta", "Alpha", "Beta", "Gamma"]
    
    # Colors: Red, Orange, Yellow, Green, Blue
    colors = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255)] 

    for i, band in enumerate(band_names):
        # Add plot to layout (i is the row number)
        p = win.addPlot(row=i, col=0, title=f"{band} Band")
        p.showGrid(x=True, y=True)
        p.setLabel('left', 'Power', units='uV^2')
        
        # Create curve
        curves[band] = p.plot(pen=colors[i])
        
        # Initialize buffer with zeros (display last 200 updates)
        data_buffers[band] = np.zeros(200)

    def update():
        # Process all items currently in the queue
        while not input_queue.empty():
            try:
                new_data = input_queue.get(block=False)
                if new_data is None: 
                    return

                for band in band_names:
                    # Shift buffer left
                    data_buffers[band][:-1] = data_buffers[band][1:]
                    # Add new value to end
                    data_buffers[band][-1] = new_data[band]
                    # Update the line on the graph
                    curves[band].setData(data_buffers[band])
            except:
                pass

        # Check if main process wants us to stop
        if stop_event.is_set():
            app.quit()

    # Set update timer (run every 50ms)
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(50)

    # Start the Qt event loop
    print("Visualizer process started.")
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        app.exec() 

# ------------------------------
# Main Execution
# ------------------------------
shutdown_event = Event()

def signal_handler(sig, frame):
    print("\n[INFO] Ctrl+C received. Initiating shutdown...")
    shutdown_event.set()

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    # Start Viz in separate process
    vis_process = Process(target=visualizer_process, args=(viz_queue, shutdown_event))
    vis_process.start()

    try:
        # Connect to Muse
        print(f"Attempting to connect to Muse: {MUSE_MAC_ADDRESS}")
        proxy = MuseProxy(MUSE_MAC_ADDRESS, eeg_callback)
        proxy.waitForConnected()
        
        print("Connected. Stabilizing signal...")
        sleep(2)
        print("Starting Recording (5 Minutes)...")
        
        # Run for 5 minutes (300 seconds)
        start_time = time()
        while time() - start_time < 300:
            if shutdown_event.is_set():
                break
            sleep(1)
            
        print("5 minutes complete.")

    except KeyboardInterrupt:
        print("Stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("[MAIN] Cleaning up...")
        shutdown_event.set()
        
        try:
            proxy.disconnect()
        except:
            pass
            
        viz_queue.put(None)
        vis_process.terminate() # Ensure viz process closes
        vis_process.join()
        close_file()
        print("Data saved to CSV. Goodbye.")