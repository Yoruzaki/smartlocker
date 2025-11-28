# Raspberry Pi 3 Deployment Guide

Step-by-step instructions to go from a fresh Raspberry Pi 3 to running the Smart Locker Delivery System in kiosk mode.

## 0. Prerequisites

Hardware:
- Raspberry Pi 3 Model B/B+ with official 5 V/2.5 A PSU
- microSD card (16 GB+ recommended) and card reader
- 7" Raspberry Pi touchscreen (DSI) or HDMI display, plus keyboard/mouse for initial setup
- Network connectivity (Wi-Fi or Ethernet)
- 2× MCP23017 I/O expanders (one dedicated to relays, one to sensors)
- 16-channel relay board rated for your locker actuators (5 V coils, opto-isolated preferred)
- 16 door sensors (magnetic reed or microswitch) wired as normally-closed to ground
- Wiring harness: 22 AWG stranded for signal, 18 AWG for actuator power runs, Dupont or JST connectors
- 5 V power supply sized for all relays/solenoids (often separate from Pi PSU) with common ground
- Mounting hardware, DIN rails, enclosure with airflow

Tools / Software:
- Raspberry Pi Imager
- Small screwdriver set, wire stripper, crimp tool, multimeter
- Heat-shrink tubing or electrical tape, zip ties, labels for cable management
- Access to this repository (git or ZIP)

## 1. Flash Raspberry Pi OS

1. Download **Raspberry Pi Imager** from raspberrypi.org.
2. Insert the microSD card and open the Imager.
3. Choose **Raspberry Pi OS (32-bit)** (Desktop makes kiosk setup easier).
4. Click the gear icon (advanced options) and:
   - Set hostname (e.g., `smartlocker`).
   - Enable SSH and configure Wi-Fi (optional but convenient).
   - Set username/password (default is `pi`/`raspberry` if unchanged).
5. Flash the image and safely eject the card.

## 2. First Boot Setup

1. Insert the card into the Pi, connect display, keyboard, and power on.
2. Complete the Raspberry Pi OS first-boot wizard if using Desktop.
3. Update firmware and packages:
   ```bash
   sudo apt update
   sudo apt full-upgrade -y
   sudo reboot
   ```
4. After reboot, run the configuration tool:
   ```bash
   sudo raspi-config
   ```
   - Change password if not done.
   - Set locale, timezone, keyboard layout.
   - Interface Options → enable **I2C**.
   - Finish and reboot when prompted.

## 3. Install System Dependencies

```bash
sudo apt install -y python3 python3-pip python3-flask python3-smbus \
    i2c-tools git chromium-browser unclutter xdotool
```

Verify I2C bus detects both MCP23017 chips (addresses 0x20 & 0x21):

```bash
sudo i2cdetect -y 1
# You should see "20" and "21" in the grid.
```

## 4. Deploy the Application

1. Choose the install directory (`/home/pi/smartlocker` assumed by the service file).
2. Get the project onto the Pi, for example:
   ```bash
   cd /home/pi
   git clone <YOUR_REPOSITORY_URL> smartlocker
   ```
   If you only have a ZIP, copy it via SCP or USB and extract it to `/home/pi/smartlocker`.
3. Ensure ownership is `pi:pi`:
   ```bash
   sudo chown -R pi:pi /home/pi/smartlocker
   ```

## 5. Configure the App

1. Edit `app.py` and set real-hardware mode:
   ```python
   USE_MOCK_HARDWARE = False
   ```
2. (Optional) Update translations or PIN values in `routes.py` as needed.
3. Initialize the database by running the app once:
   ```bash
   cd /home/pi/smartlocker
   python3 app.py
   ```
   Stop it with `Ctrl+C` after you confirm it starts without errors (this creates `smartlocker.db`).

## 6. Wire the Hardware

### 6.1 Addressing & Power
1. Set I2C addresses with the A0/A1/A2 pins:
   - **MCP23017 #1 (relays)**: leave A0–A2 tied to GND → address `0x20`.
   - **MCP23017 #2 (sensors)**: tie A0 to VCC, A1/A2 to GND → address `0x21`.
2. Power both chips from 5 V (pin VDD) and connect VSS to ground.
3. Tie Pi 3.3 V logic reference to the MCP23017 via the SDA/SCL pull-ups (the chip is 5 V tolerant on I2C as long as pull-ups go to 3.3 V). If your relay board expects 5 V logic, keep the MCP at 5 V and add transistor/optocoupler stages already present on most boards.
4. Run SDA to Pi pin 3 (GPIO2) and SCL to Pi pin 5 (GPIO3). Add 4.7 kΩ pull-ups to 3.3 V if the relay board does not include them.

### 6.2 Relay Side (Outputs)
| Locker | MCP pin | Expander port | Relay input | Notes |
|--------|---------|---------------|-------------|-------|
| 1      | GPA0    | Chip #1       | Relay IN1   | Locker IDs map sequentially to pins |
| ...    | ...     | ...           | ...         | Continue up to locker 16 (GPB7) |

Steps:
1. Use twisted pairs: one conductor for the MCP output, one for ground/local reference (if relay board requires).
2. If your relay board is active-low, invert logic in hardware (tie IN to MCP output and GND) – current code assumes writing `1` energizes the relay. Adjust in `hardware.py` if necessary.
3. Route relay `COM` and `NO/NC` contacts to each solenoid/lock coil using appropriately gauged wire. Use flyback diodes if coils are not already protected.

### 6.3 Sensor Side (Inputs)
| Locker | MCP pin | Connection                                      |
|--------|---------|--------------------------------------------------|
| 1      | GPA0    | Sensor -> pulls to GND when door closed          |
| ...    | ...     | ...                                              |

Steps:
1. Wire one side of each reed switch to ground, the other to the MCP input.
2. Enable pull-ups: either through MCP’s internal pull-ups (configure in hardware) or via 10 kΩ resistors to 5 V. In code we assume `1 = open, 0 = closed`, so adjust wiring accordingly.
3. Shield long runs if the environment is noisy; twisted pairs help reject EMI.

### 6.4 Power Distribution & Safety
1. Use a separate 5 V supply for relays/locks if total current exceeds 2 A. Tie its ground to the Pi ground.
2. Place an inline fuse between PSU and relay board.
3. Keep high-voltage AC wiring isolated from low-voltage logic; use separate conduits or raceways.
4. Label every conductor and document the locker-to-relay mapping for maintenance.

### 6.5 Sanity Checks
1. Before connecting the Pi, validate continuity with a multimeter (no shorts between 5 V and GND).
2. Power up the Pi, run `sudo i2cdetect -y 1` to ensure addresses `20` and `21` appear.
3. Use `python3` REPL to instantiate `hardware.get_hardware(use_mock=False)` and manually trigger `hardware.open_locker(1)` while listening for the relay click.

## 7. Configure Systemd Service

1. Copy the included unit file:
   ```bash
   sudo cp /home/pi/smartlocker/smartlocker.service /etc/systemd/system/
   ```
2. Reload, enable, and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable smartlocker.service
   sudo systemctl start smartlocker.service
   ```
3. Verify status:
   ```bash
   sudo systemctl status smartlocker.service
   ```
   The Flask server should listen on `http://localhost:5000`.

## 8. Configure Kiosk Mode (Chromium)

1. Copy the kiosk launcher:
   ```bash
   cp /home/pi/smartlocker/start_kiosk.sh /home/pi/
   chmod +x /home/pi/start_kiosk.sh
   ```
2. Autostart it for the `pi` desktop session (LXDE):
   ```bash
   sudo mkdir -p /etc/xdg/lxsession/LXDE-pi
   echo "@/home/pi/start_kiosk.sh" | sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart
   ```
3. On next login, Chromium opens fullscreen at `http://localhost:5000`.

## 9. Test the System

1. Reboot (`sudo reboot`) to confirm both the service and kiosk start automatically.
2. Use the delivery login page:
   - Default PIN is defined in `routes.py` (search for `VALID_PIN` or similar variable).
3. Open a locker from the dashboard; verify relay clicks and locker door unlocks.
4. Confirm OTP modal displays and sensors update when doors close.
5. Test customer pickup flow with the generated OTP.

## 10. Maintenance & Troubleshooting

- **Logs**: `journalctl -u smartlocker.service -f`
- **Restart service**: `sudo systemctl restart smartlocker.service`
- **Network changes**: update `/etc/wpa_supplicant/wpa_supplicant.conf` or use `raspi-config`.
- **Hardware fallback**: if hardware init fails, the code falls back to mock mode; ensure MCP23017 chips show in `i2cdetect`.
- **Updates**: pull latest code and restart service:
  ```bash
  cd /home/pi/smartlocker
  git pull
  sudo systemctl restart smartlocker.service
  ```

Following these steps brings a fresh Raspberry Pi 3 from blank SD card to a locked-down smart locker kiosk running the provided system.

