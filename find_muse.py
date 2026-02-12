import asyncio
from bleak import BleakScanner

async def scan_for_muse():
    print("Scanning for Bluetooth devices... (this may take a few seconds)")
    
    # Scan for 5 seconds
    devices = await BleakScanner.discover(timeout=5.0)
    
    muse_devices = []
    
    for d in devices:
        # Check if "Muse" is in the name (handles "Muse-2016", "Muse-01", etc.)
        if d.name and "muse" in d.name.lower():
            muse_devices.append(d)
            
    if not muse_devices:
        print("\n❌ No Muse devices found.")
        print("Tips:")
        print("1. Ensure your Muse is charged and in pairing mode (lights blinking).")
        print("2. Ensure your computer's Bluetooth is ON.")
        print("3. Keep the Muse close to your computer.")
    else:
        print(f"\n✅ Found {len(muse_devices)} Muse device(s):")
        print("-" * 40)
        for d in muse_devices:
            print(f"Name: {d.name}")
            print(f"Address: {d.address}")
            print(f"RSSI: {d.rssi} dBm")
            print("-" * 40)
            
        print("\nCopy the 'Address' above and paste it into main.py")

if __name__ == "__main__":
    try:
        asyncio.run(scan_for_muse())
    except Exception as e:
        print(f"Error during scan: {e}")