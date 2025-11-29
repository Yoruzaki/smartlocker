# Smart Locker System - Complete Wiring Guide

This guide provides detailed instructions for wiring the Smart Locker Delivery System hardware components to a Raspberry Pi 3.

## Table of Contents
1. [Components Required](#components-required)
2. [Overview](#overview)
3. [Raspberry Pi Pinout](#raspberry-pi-pinout)
4. [MCP23017 I2C Expander Setup](#mcp23017-i2c-expander-setup)
5. [Relay Board Wiring (Outputs)](#relay-board-wiring-outputs)
6. [Door Sensor Wiring (Inputs)](#door-sensor-wiring-inputs)
7. [Power Distribution](#power-distribution)
8. [Complete Wiring Diagram](#complete-wiring-diagram)
9. [Testing & Verification](#testing--verification)
10. [Troubleshooting](#troubleshooting)

---

## Components Required

### Essential Components
- **Raspberry Pi 3 Model B/B+** with microSD card
- **2× MCP23017 I/O Expander ICs** (16-bit GPIO expanders)
- **16× Relay Module** (5V, single-pole single-throw or double-throw)
- **16× Door Sensors** (Reed switches or magnetic sensors)
- **16× Lock Actuators** (Solenoids, electric strikes, or magnetic locks)
- **Power Supply**: 5V, 3A+ for relays/locks (separate from Pi)
- **Breadboard or PCB** for MCP23017 breakout boards
- **Jumper wires** (male-to-female, male-to-male)
- **Dupont connectors** or soldering equipment

### Additional Components
- **4.7kΩ resistors** (2× for I2C pull-ups, if not on relay board)
- **10kΩ resistors** (16× for sensor pull-ups, if not using internal MCP pull-ups)
- **Flyback diodes** (16×, if not built into relay board)
- **Fuse holder and fuse** (2A-5A, depending on total current)
- **Wire strippers, crimping tools**
- **Multimeter** for testing
- **Heat shrink tubing** for insulation

---

## Overview

The system uses **two MCP23017 chips** to control 16 lockers:

- **MCP23017 #1 (Address 0x20)**: Controls 16 relay outputs → Opens/closes lockers
- **MCP23017 #2 (Address 0x21)**: Reads 16 door sensor inputs → Detects door open/closed state

### System Architecture
```
Raspberry Pi 3
    │
    ├── I2C Bus (SDA/SCL)
    │   │
    │   ├── MCP23017 #1 (0x20) → 16 Relay Outputs → 16 Lock Actuators
    │   └── MCP23017 #2 (0x21) → 16 Sensor Inputs ← 16 Door Sensors
    │
    └── Power: 5V/GND shared across all components
```

---

## Raspberry Pi Pinout

### I2C Pins (Required)
| Function | GPIO | Physical Pin | Notes |
|----------|------|--------------|-------|
| **SDA** (I2C Data) | GPIO 2 | Pin 3 | Data line |
| **SCL** (I2C Clock) | GPIO 3 | Pin 5 | Clock line |
| **5V Power** | 5V | Pin 2 or 4 | For MCP23017 chips |
| **3.3V Power** | 3.3V | Pin 1 or 17 | For pull-up resistors |
| **Ground** | GND | Pin 6, 9, 14, 20, 25, 30, 34, 39 | Multiple GND pins available |

### Physical Pin Layout (40-pin header)
```
    3.3V  [1]  [2]  5V
   GPIO2  [3]  [4]  5V
   GPIO3  [5]  [6]  GND
   GPIO4  [7]  [8]  GPIO14
     GND  [9]  [10] GPIO15
  GPIO17  [11] [12] GPIO18
  GPIO27  [13] [14] GND
  GPIO22  [15] [16] GPIO23
    3.3V  [17] [18] GPIO24
  GPIO10  [19] [20] GND
   GPIO9  [21] [22] GPIO25
  GPIO11  [23] [24] GPIO8
     GND  [25] [26] GPIO7
   GPIO0  [27] [28] GPIO1
   GPIO5  [29] [30] GND
   GPIO6  [31] [32] GPIO12
  GPIO13  [33] [34] GND
  GPIO19  [35] [36] GPIO16
  GPIO26  [37] [38] GPIO20
     GND  [39] [40] GPIO21
```

**Key Pins for This Project:**
- **Pin 3**: SDA (GPIO 2)
- **Pin 5**: SCL (GPIO 3)
- **Pin 2 or 4**: 5V (for MCP23017 power)
- **Pin 6**: GND (reference ground)

---

## MCP23017 I2C Expander Setup

### MCP23017 Pinout
```
        ┌─────────────┐
   GPA0 │1          28│ VDD (5V)
   GPA1 │2          27│ VSS (GND)
   GPA2 │3          26│ RESET
   GPA3 │4          25│ A0 (Address bit 0)
   GPA4 │5          24│ A1 (Address bit 1)
   GPA5 │6          23│ A2 (Address bit 2)
   GPA6 │7          22│ INTA
   GPA7 │8          21│ INTB
   VSS   │9          20│ SCL (I2C Clock)
   SDA   │10         19│ SCL (I2C Clock) - alternate
   GPB0  │11         18│ GPB7
   GPB1  │12         17│ GPB6
   GPB2  │13         16│ GPB5
   GPB3  │14         15│ GPB4
        └─────────────┘
```

### Setting I2C Addresses

The MCP23017 has 3 address pins (A0, A1, A2) that determine its I2C address:
- **Base address**: 0x20 (binary: 0100000)
- **Address bits**: A2, A1, A0 (bits 1, 2, 3)

| A2 | A1 | A0 | I2C Address | Binary |
|----|----|----|-------------|--------|
| 0  | 0  | 0  | **0x20**    | 0100000 |
| 0  | 0  | 1  | **0x21**    | 0100001 |
| 0  | 1  | 0  | 0x22        | 0100010 |
| ... | ... | ... | ... | ... |

**For This Project:**
- **MCP23017 #1 (Relays)**: A0=GND, A1=GND, A2=GND → **Address 0x20**
- **MCP23017 #2 (Sensors)**: A0=VCC, A1=GND, A2=GND → **Address 0x21**

### Wiring MCP23017 to Raspberry Pi

**For Each MCP23017 Chip:**

| MCP23017 Pin | Raspberry Pi Connection | Notes |
|--------------|-------------------------|-------|
| **VDD** (Pin 28) | **5V** (Pin 2 or 4) | Power supply |
| **VSS** (Pin 27) | **GND** (Pin 6) | Ground reference |
| **SDA** (Pin 3) | **GPIO 2 / Pin 3** | I2C Data line |
| **SCL** (Pin 4) | **GPIO 3 / Pin 5** | I2C Clock line |
| **RESET** (Pin 18) | **3.3V** (Pin 1) | Keep high (active low) |
| **A0, A1, A2** | See addressing table above | Address configuration |

**I2C Pull-up Resistors:**
- Add **4.7kΩ resistors** from SDA to 3.3V
- Add **4.7kΩ resistors** from SCL to 3.3V
- *Note: Many relay boards include these pull-ups. Check your board first.*

**Complete MCP23017 #1 (Relays - 0x20) Wiring:**
```
MCP23017 #1:
  VDD → Pi Pin 2 (5V)
  VSS → Pi Pin 6 (GND)
  SDA → Pi Pin 3 (GPIO 2)
  SCL → Pi Pin 5 (GPIO 3)
  RESET → Pi Pin 1 (3.3V)
  A0 → GND (via jumper or wire)
  A1 → GND
  A2 → GND
```

**Complete MCP23017 #2 (Sensors - 0x21) Wiring:**
```
MCP23017 #2:
  VDD → Pi Pin 2 (5V) [shared with Chip #1]
  VSS → Pi Pin 6 (GND) [shared with Chip #1]
  SDA → Pi Pin 3 (GPIO 2) [shared with Chip #1]
  SCL → Pi Pin 5 (GPIO 3) [shared with Chip #1]
  RESET → Pi Pin 1 (3.3V) [shared with Chip #1]
  A0 → 5V (via jumper or wire) ← DIFFERENT!
  A1 → GND
  A2 → GND
```

---

## Relay Board Wiring (Outputs)

### MCP23017 #1 Pin Mapping to Lockers

| Locker ID | MCP23017 Pin | Port | Bit | Relay Module Input |
|-----------|--------------|------|-----|-------------------|
| 1         | GPA0         | A    | 0   | IN1               |
| 2         | GPA1         | A    | 1   | IN2               |
| 3         | GPA2         | A    | 2   | IN3               |
| 4         | GPA3         | A    | 3   | IN4               |
| 5         | GPA4         | A    | 4   | IN5               |
| 6         | GPA5         | A    | 5   | IN6               |
| 7         | GPA6         | A    | 6   | IN7               |
| 8         | GPA7         | A    | 7   | IN8               |
| 9         | GPB0         | B    | 0   | IN9               |
| 10        | GPB1         | B    | 1   | IN10              |
| 11        | GPB2         | B    | 2   | IN11              |
| 12        | GPB3         | B    | 3   | IN12              |
| 13        | GPB4         | B    | 4   | IN13              |
| 14        | GPB5         | B    | 5   | IN14              |
| 15        | GPB6         | B    | 6   | IN15              |
| 16        | GPB7         | B    | 7   | IN16              |

### Relay Module Connections

**Typical 16-Channel Relay Module:**
- **VCC**: Connect to 5V power supply (NOT Pi 5V if using separate PSU)
- **GND**: Connect to common ground (Pi GND + PSU GND)
- **IN1-IN16**: Connect to MCP23017 #1 outputs (GPA0-GPB7)

**Wiring Steps:**
1. Connect MCP23017 #1 GPA0 → Relay Module IN1
2. Connect MCP23017 #1 GPA1 → Relay Module IN2
3. Continue sequentially up to GPB7 → IN16
4. Use twisted-pair wires for longer runs to reduce EMI

**Relay Output to Lock Actuator:**
- **COM** (Common): Connect to lock actuator positive terminal
- **NO** (Normally Open): Connect to power supply positive (when relay closes, power flows)
- **NC** (Normally Closed): Usually not used for this application
- **Lock Actuator Negative**: Connect to power supply ground

**Important Notes:**
- Most relay modules are **active LOW** (0V = relay ON, 5V = relay OFF)
- The code writes `1` to turn relay ON - if your board is active LOW, you may need to invert logic
- Check your relay board datasheet for active HIGH vs LOW
- Use appropriate wire gauge for lock actuators (typically 18-22 AWG for low current, 14-16 AWG for high current)

### Example: Locker 1 Complete Wiring
```
MCP23017 #1 GPA0 → Relay Module IN1
Relay Module COM → Lock Actuator Positive
Relay Module NO → 5V Power Supply Positive
Lock Actuator Negative → Power Supply Ground
```

---

## Door Sensor Wiring (Inputs)

### MCP23017 #2 Pin Mapping to Sensors

| Locker ID | MCP23017 Pin | Port | Bit | Sensor Connection |
|-----------|--------------|------|-----|-------------------|
| 1         | GPA0         | A    | 0   | Sensor 1          |
| 2         | GPA1         | A    | 1   | Sensor 2          |
| 3         | GPA2         | A    | 2   | Sensor 3          |
| 4         | GPA3         | A    | 3   | Sensor 4          |
| 5         | GPA4         | A    | 4   | Sensor 5          |
| 6         | GPA5         | A    | 5   | Sensor 6          |
| 7         | GPA6         | A    | 6   | Sensor 7          |
| 8         | GPA7         | A    | 7   | Sensor 8          |
| 9         | GPB0         | B    | 0   | Sensor 9          |
| 10        | GPB1         | B    | 1   | Sensor 10         |
| 11        | GPB2         | B    | 2   | Sensor 11         |
| 12        | GPB3         | B    | 3   | Sensor 12         |
| 13        | GPB4         | B    | 4   | Sensor 13         |
| 14        | GPB5         | B    | 5   | Sensor 14         |
| 15        | GPB6         | B    | 6   | Sensor 15         |
| 16        | GPB7         | B    | 7   | Sensor 16         |

### Reed Switch Sensor Wiring

**Reed Switch Basics:**
- **Normally Open (NO)**: Contacts close when magnet is near (door closed)
- **Normally Closed (NC)**: Contacts open when magnet is near (door closed)
- For this project, we assume **NO reed switches**

**Two Wiring Options:**

#### Option 1: Pull-up to 5V (Recommended)
```
MCP23017 #2 GPA0 → Reed Switch Terminal 1
Reed Switch Terminal 2 → GND
10kΩ Resistor: 5V → MCP23017 #2 GPA0
```
- When door **closed**: Switch closes → GPA0 pulled LOW (0V) → Code reads `0` = closed
- When door **open**: Switch open → GPA0 pulled HIGH (5V) → Code reads `1` = open

#### Option 2: Internal MCP Pull-up (Alternative)
- Enable internal pull-up resistors in code (GPPUA/GPPUB registers)
- Wire: MCP23017 GPA0 → Reed Switch Terminal 1
- Wire: Reed Switch Terminal 2 → GND
- No external resistor needed

**Code Logic:**
The code inverts the reading: `is_closed = not ((val >> pin) & 1)`
- If sensor reads `0` (LOW) → door is closed
- If sensor reads `1` (HIGH) → door is open

### Example: Locker 1 Sensor Wiring
```
MCP23017 #2 GPA0 → Reed Switch Terminal 1
Reed Switch Terminal 2 → GND
10kΩ Resistor: 5V → MCP23017 #2 GPA0 (pull-up)
```

**For Long Wire Runs:**
- Use **twisted-pair cables** to reduce EMI
- Consider **shielded cables** in noisy environments
- Keep sensor wires away from AC power lines
- Maximum recommended distance: 10-15 meters (33-50 feet)

---

## Power Distribution

### Power Requirements

| Component | Voltage | Current (per unit) | Total Current |
|-----------|---------|-------------------|---------------|
| Raspberry Pi 3 | 5V | ~2.5A (peak) | 2.5A |
| MCP23017 #1 | 5V | ~1mA | 1mA |
| MCP23017 #2 | 5V | ~1mA | 1mA |
| Relay Module (idle) | 5V | ~50mA | 50mA |
| Relay Module (active) | 5V | ~70mA per relay | ~1.1A (16×) |
| Lock Actuator | 5V-12V | 100mA-500mA each | 1.6A-8A (16×) |

**Total System Current:**
- **Logic/Control**: ~2.6A (Pi + MCPs + relays)
- **Lock Actuators**: 1.6A-8A (depends on actuator type)
- **Recommended PSU**: 5V, 10A+ (or 12V with voltage regulator for actuators)

### Power Supply Setup

**Option 1: Single 5V Supply (Simple)**
```
5V, 10A Power Supply
  ├── Raspberry Pi (via microUSB or GPIO)
  ├── MCP23017 #1 VDD
  ├── MCP23017 #2 VDD
  ├── Relay Module VCC
  └── Lock Actuators (via relay contacts)
  
All GNDs connected together (common ground)
```

**Option 2: Separate Supplies (Recommended for High Current)**
```
5V, 3A Supply → Raspberry Pi + MCP23017 chips
5V or 12V, 10A Supply → Relay Module + Lock Actuators
  └── Tie grounds together (critical!)
```

### Safety Features

1. **Fuse Protection:**
   - Place a **2A-5A fuse** between PSU and relay board
   - Use a **3A fuse** for Raspberry Pi power line
   - Fast-blow fuses recommended

2. **Grounding:**
   - **Always** connect all grounds together (Pi, MCPs, PSU, relay board)
   - Use a **star ground** configuration (all grounds meet at one point)
   - Never leave floating grounds

3. **Isolation:**
   - Keep high-voltage AC wiring (if any) separate from low-voltage DC
   - Use separate conduits or raceways
   - Maintain minimum 6mm (0.25") clearance between AC and DC wires

4. **Wire Gauge:**
   - **Signal wires** (I2C, sensor): 22-24 AWG
   - **Power to Pi**: 20-22 AWG
   - **Power to relay board**: 18-20 AWG
   - **Lock actuator wires**: 14-18 AWG (depends on current)

---

## Complete Wiring Diagram

### Text-Based Diagram

```
                    Raspberry Pi 3
                         │
        ┌────────────────┼────────────────┐
        │                │                │
     Pin 3            Pin 5           Pin 2/4
     (SDA)           (SCL)            (5V)
        │                │                │
        └────────┬───────┴────────┬───────┘
                 │                │
        ┌────────▼────────┐ ┌─────▼─────────┐
        │  MCP23017 #1    │ │  MCP23017 #2   │
        │  Address: 0x20  │ │  Address: 0x21│
        │  (RELAYS)       │ │  (SENSORS)     │
        └────────┬────────┘ └─────┬─────────┘
                 │                │
    ┌────────────┼────────────┐   │
    │            │            │   │
GPA0-GPA7    GPB0-GPB7    GND │   │
    │            │            │   │
    │            │            │   │
┌───▼────────────▼────────────▼───▼───┐
│     16-Channel Relay Module         │
│  IN1-IN16 ← MCP23017 #1 outputs    │
│  VCC ← 5V PSU                       │
│  GND ← Common Ground                │
└───┬─────────────────────────────────┘
    │
    │ (Relay Contacts: COM/NO)
    │
┌───▼─────────────────────────────────┐
│     16 Lock Actuators              │
│  (Solenoids/Magnetic Locks)        │
└────────────────────────────────────┘

        MCP23017 #2 Inputs
        GPA0-GPA7, GPB0-GPB7
                 │
        ┌────────┼────────┐
        │        │        │
    ┌───▼───┐ ┌──▼───┐ ┌──▼───┐
    │Sensor │ │Sensor│ │Sensor│
    │   1   │ │  2   │ │ ...  │
    └───────┘ └──────┘ └──────┘
    (Reed Switches)
```

### Connection Summary Table

| From | To | Wire Count | Notes |
|------|----|-----------|-------|
| Pi Pin 3 | MCP #1 SDA, MCP #2 SDA | 1 (shared) | I2C data line |
| Pi Pin 5 | MCP #1 SCL, MCP #2 SCL | 1 (shared) | I2C clock line |
| Pi Pin 2/4 | MCP #1 VDD, MCP #2 VDD | 1 (shared) | 5V power |
| Pi Pin 6 | All GNDs | Multiple | Common ground |
| MCP #1 GPA0-GPB7 | Relay IN1-IN16 | 16 | Relay control |
| Relay COM/NO | Lock Actuators | 16×2 | Power to locks |
| MCP #2 GPA0-GPB7 | Sensors | 16 | Door sensors |
| Sensors | GND | 16 | Sensor return |
| 5V PSU | Relay VCC, Lock Actuators | Multiple | High current power |

---

## Testing & Verification

### Step 1: Verify I2C Communication

**Before connecting relays/sensors, test I2C:**

```bash
# Enable I2C (if not already done)
sudo raspi-config
# Interface Options → I2C → Enable

# Install tools
sudo apt install -y i2c-tools

# Detect I2C devices
sudo i2cdetect -y 1
```

**Expected Output:**
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: 20 21 -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
```

You should see **20** and **21** in the grid.

### Step 2: Test MCP23017 Outputs (Relays)

**Using Python:**
```python
import smbus
import time

bus = smbus.SMBus(1)
addr = 0x20  # MCP23017 #1

# Configure all pins as outputs
bus.write_byte_data(addr, 0x00, 0x00)  # IODIRA = all outputs
bus.write_byte_data(addr, 0x01, 0x00)  # IODIRB = all outputs

# Turn on relay 1 (GPA0)
bus.write_byte_data(addr, 0x12, 0x01)  # GPIOA = bit 0 high
time.sleep(1)
# Turn off relay 1
bus.write_byte_data(addr, 0x12, 0x00)  # GPIOA = bit 0 low
```

**Listen for relay click** - you should hear an audible "click" when the relay activates.

### Step 3: Test MCP23017 Inputs (Sensors)

**Using Python:**
```python
import smbus

bus = smbus.SMBus(1)
addr = 0x21  # MCP23017 #2

# Configure all pins as inputs
bus.write_byte_data(addr, 0x00, 0xFF)  # IODIRA = all inputs
bus.write_byte_data(addr, 0x01, 0xFF)  # IODIRB = all inputs

# Read sensor 1 (GPA0)
val = bus.read_byte_data(addr, 0x12)  # Read GPIOA
sensor1 = (val >> 0) & 1
print(f"Sensor 1 state: {sensor1} (1=open, 0=closed)")
```

**Manually open/close door** and verify the reading changes.

### Step 4: Test Complete System

**Run the application:**
```bash
cd /home/pi/smartlocker
python3 app.py
```

**Test flow:**
1. Open browser to `http://localhost:5000`
2. Login as delivery (PIN: check `routes.py`)
3. Click a locker button
4. Verify:
   - Relay clicks
   - Lock actuator activates
   - OTP displays
   - Door sensor updates when door closes

### Step 5: Continuity & Short Testing

**Before powering on:**
```bash
# Use multimeter to check:
# 1. No short between 5V and GND
# 2. Continuity on all connections
# 3. Correct resistance values on pull-up resistors
```

---

## Troubleshooting

### Problem: I2C devices not detected

**Solutions:**
- Verify I2C is enabled: `sudo raspi-config` → Interface Options → I2C
- Check wiring: SDA to Pin 3, SCL to Pin 5
- Verify pull-up resistors (4.7kΩ on SDA/SCL to 3.3V)
- Check power: MCP23017 VDD to 5V, VSS to GND
- Try: `sudo i2cdetect -y 1` (should show 20 and 21)

### Problem: Relays not activating

**Solutions:**
- Verify MCP23017 #1 address is 0x20 (A0=A1=A2=GND)
- Check relay module power (VCC to 5V)
- Verify relay module is active HIGH or LOW (may need code inversion)
- Test relay directly: connect IN1 to 5V, should click
- Check wire connections: MCP GPA0 → Relay IN1, etc.

### Problem: Sensors always read same value

**Solutions:**
- Verify pull-up resistors (10kΩ to 5V) or enable internal pull-ups
- Check sensor wiring: MCP pin → Sensor → GND
- Test sensor with multimeter: should show continuity when door closed
- Verify MCP23017 #2 address is 0x21 (A0=5V, A1=A2=GND)
- Check code logic: may need to invert reading

### Problem: System resets or unstable

**Solutions:**
- Check power supply capacity (may be insufficient)
- Verify all grounds are connected (common ground issue)
- Check for loose connections
- Add decoupling capacitors (100µF) near MCP23017 VDD pins
- Separate high-current wiring from signal wiring

### Problem: False sensor readings

**Solutions:**
- Add shielding to sensor wires
- Use twisted-pair cables
- Increase pull-up resistor value (try 47kΩ)
- Add 0.1µF capacitor from sensor pin to GND (debouncing)
- Keep sensor wires away from AC power lines

### Problem: Lock actuator doesn't work

**Solutions:**
- Verify relay contacts are making connection (test with multimeter)
- Check actuator power supply (may need 12V instead of 5V)
- Verify actuator polarity (if DC)
- Check wire gauge (may be too thin for current)
- Test actuator directly (bypass relay)

---

## Safety Reminders

⚠️ **CRITICAL SAFETY WARNINGS:**

1. **Always disconnect power** before making wiring changes
2. **Double-check all connections** before powering on
3. **Use appropriate fuses** to prevent overcurrent damage
4. **Never mix AC and DC** in the same wire bundle
5. **Verify polarity** on all power connections
6. **Test with multimeter** before connecting to Pi
7. **Start with one locker** - verify it works before wiring all 16
8. **Document your wiring** - label every wire and connection
9. **Use proper wire gauge** - undersized wires can overheat
10. **Keep wiring organized** - use cable management, labels, and color coding

---

## Additional Resources

- **MCP23017 Datasheet**: Search for "MCP23017 datasheet" online
- **Raspberry Pi GPIO Pinout**: https://pinout.xyz
- **I2C Protocol**: https://www.i2c-bus.org/
- **Relay Module Guides**: Check your specific relay board documentation

---

**Last Updated**: 2025-11-28  
**Version**: 1.0

