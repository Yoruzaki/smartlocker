# Smart Locker Delivery System

A complete smart delivery locker system for Raspberry Pi with a 7-inch touchscreen.

## Features
- **Delivery Mode**: Secure login (PIN), view empty lockers, open locker, generate OTP.
- **Customer Mode**: Enter OTP to retrieve package.
- **Hardware Control**: Supports MCP23017 I/O expanders (Real & Mock modes).
- **Kiosk Interface**: Touch-friendly UI optimized for 800x480 resolution.

## Hardware Setup
The system requires **two** MCP23017 chips to control 16 lockers (32 GPIOs total).
- **Chip 1 (Address 0x20)**: Controls 16 Relays (Outputs)
- **Chip 2 (Address 0x21)**: Reads 16 Door Sensors (Inputs)

## Installation on Raspberry Pi

1. **Install Dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-flask python3-smbus i2c-tools chromium-browser unclutter
   ```

2. **Enable I2C**
   Run `sudo raspi-config` -> Interface Options -> I2C -> Enable.

3. **Deploy Code**
   Copy all files to `/home/pi/smartlocker`.

4. **Configure Hardware**
   Edit `app.py` and set `USE_MOCK_HARDWARE = False`.

5. **Setup Auto-Start (Systemd)**
   ```bash
   sudo cp smartlocker.service /etc/systemd/system/
   sudo systemctl enable smartlocker.service
   sudo systemctl start smartlocker.service
   ```

6. **Setup Kiosk Mode**
   Add the content of `start_kiosk.sh` to your desktop autostart or `.bashrc` (depending on your window manager, e.g., LXDE).
   Alternatively, copy `start_kiosk.sh` to `/home/pi/` and make it executable:
   ```bash
   chmod +x /home/pi/start_kiosk.sh
   ```
   Add to autostart: `echo "@/home/pi/start_kiosk.sh" >> /etc/xdg/lxsession/LXDE-pi/autostart`

## Testing on PC (Mock Mode)

1. **Install Python Dependencies**
   ```bash
   pip install flask
   ```

2. **Run Application**
   ```bash
   python app.py
   ```
   The app will start on `http://localhost:5000`.
   `USE_MOCK_HARDWARE = True` is set by default.

3. **Mock Logic**
   - **Delivery Login**: PIN is `1234`.
   - **Open Locker**: Click a locker in dashboard. It simulates opening and generates an OTP.
   - **Close Door**: In Mock mode, doors don't auto-close. You can use the API `/api/mock/close_door/<id>` or restart the server to reset. (Or add a dev button if needed).

## API Endpoints
- `GET /api/status`: Get state of all lockers.
- `POST /api/open_locker/<id>`: Open a locker (Delivery).
