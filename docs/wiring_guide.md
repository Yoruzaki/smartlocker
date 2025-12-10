# Smart Locker System - Complete Wiring Guide

This guide provides detailed instructions for wiring the Smart Locker Delivery System hardware components to a Raspberry Pi 4 (or Pi 3).

## Table of Contents
1. [Components Required](#components-required)
2. [Overview](#overview)
3. [Raspberry Pi Pinout](#raspberry-pi-pinout)
4. [Hybrid Hardware Architecture](#hybrid-hardware-architecture)
5. [Raspberry Pi GPIO Wiring (Lockers 1-22)](#raspberry-pi-gpio-wiring-lockers-1-22)
6. [MCP23017 I2C Expander Setup (Lockers 23-32)](#mcp23017-i2c-expander-setup-lockers-23-32)
7. [Relay Board Wiring (Outputs)](#relay-board-wiring-outputs)
8. [Door Sensor Wiring (Inputs)](#door-sensor-wiring-inputs)
9. [Power Distribution](#power-distribution)
10. [Complete Wiring Diagram](#complete-wiring-diagram)
11. [Configuration System](#configuration-system)
12. [Testing & Verification](#testing--verification)
13. [Troubleshooting](#troubleshooting)

---

## Components Required

### Essential Components
- **Raspberry Pi 4** (or Pi 3) with microSD card
- **1× MCP23017 I/O Expander IC** (16-bit GPIO expander) - for lockers 23-32
- **32× Relay Module** (5V, single-pole single-throw or double-throw)
- **32× Door Sensors** (Reed switches or magnetic sensors)
- **32× Lock Actuators** (Solenoids, electric strikes, or magnetic locks)
- **Power Supply**: 5V, 10A+ for relays/locks (separate from Pi recommended)
- **Breadboard or PCB** for MCP23017 breakout board
- **Jumper wires** (male-to-female, male-to-male)
- **Dupont connectors** or soldering equipment

### Additional Components
- **4.7kΩ resistors** (2× for I2C pull-ups, if not on relay board)
- **10kΩ resistors** (32× for sensor pull-ups, if not using internal pull-ups)
- **Flyback diodes** (32×, if not built into relay board)
- **Fuse holder and fuse** (5A-10A, depending on total current)
- **Wire strippers, crimping tools**
- **Multimeter** for testing
- **Heat shrink tubing** for insulation

---

## Overview

The system uses a **hybrid architecture** to control 32 lockers:

- **Raspberry Pi GPIOs (Lockers 1-22)**: Direct GPIO control for 22 lockers
  - Uses 22 GPIO pins for relay outputs
  - Uses 22 GPIO pins for door sensor inputs
- **MCP23017 (Lockers 23-32)**: I2C expander for 10 additional lockers
  - Port A (8 pins): Relay outputs
  - Port B (2 pins): Additional relay outputs
  - Port B can also be used for sensors (10 total pins available)

### System Architecture
```
Raspberry Pi 4
    │
    ├── GPIO Pins (22 lockers: 1-22)
    │   ├── GPIO 4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 2, 3, 14, 15, 8
    │   │   → 22 Relay Outputs → 22 Lock Actuators
    │   └── GPIO 7, 8, 9, 10, 11, 14, 15, 2, 3, 4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23
    │       ← 22 Sensor Inputs ← 22 Door Sensors
    │
    ├── I2C Bus (SDA/SCL)
    │   │
    │   └── MCP23017 (0x20) → 10 Relay Outputs → 10 Lock Actuators (Lockers 23-32)
    │                    → 10 Sensor Inputs ← 10 Door Sensors
    │
    └── Power: 5V/GND shared across all components
```

**Note**: The assignment of lockers to Pi GPIO vs MCP23017 is **configurable** through the web interface. By default:
- Lockers 1-22 use Raspberry Pi GPIOs
- Lockers 23-32 use MCP23017

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
- **Pin 3**: SDA (GPIO 2) - I2C data
- **Pin 5**: SCL (GPIO 3) - I2C clock
- **Pin 2 or 4**: 5V (for MCP23017 power, optional)
- **Pin 1 or 17**: 3.3V (for pull-up resistors, recommended for MCP23017)
- **Pin 6**: GND (reference ground)
- **GPIO 4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 2, 3, 14, 15, 8**: Available for lockers 1-22

---

## Hybrid Hardware Architecture

The system supports **32 lockers** using a combination of:
1. **Raspberry Pi GPIOs** (22 lockers: 1-22)
2. **MCP23017 I2C Expander** (10 lockers: 23-32)

### Default Pin Assignment

**Raspberry Pi GPIO Lockers (1-22):**
- **Relay Outputs**: GPIO 4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 2, 3, 14, 15, 8
- **Sensor Inputs**: GPIO 7, 8, 9, 10, 11, 14, 15, 2, 3, 4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23

**MCP23017 Lockers (23-32):**
- **Relay Outputs**: Port A (GPA0-GPA7) + Port B (GPB0-GPB1) = 10 pins
- **Sensor Inputs**: Port B (GPB0-GPB7) = 8 pins (can be shared or use different pins)

**Important**: Pin assignments are **configurable** through the web interface at `/configuration`. You can reassign any locker to use Pi GPIO or MCP23017 as needed.

---

## Raspberry Pi GPIO Wiring (Lockers 1-22)

### GPIO Pin Selection

**Available GPIO Pins** (avoid reserved pins):
- **Reserved**: GPIO 0, 1 (I2C), GPIO 14, 15 (UART), GPIO 7 (SPI)
- **Recommended for outputs**: GPIO 4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 2, 3, 8
- **Recommended for inputs**: GPIO 7, 8, 9, 10, 11, 14, 15, 2, 3, 4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23

### Wiring Raspberry Pi GPIO to Relays

**For each locker using Pi GPIO (1-22):**

| Locker ID | GPIO Pin (Output) | Physical Pin | Relay Module Input |
|-----------|-------------------|--------------|-------------------|
| 1         | GPIO 4            | Pin 7        | IN1               |
| 2         | GPIO 5            | Pin 29       | IN2               |
| 3         | GPIO 6            | Pin 31       | IN3               |
| ...       | ...               | ...          | ...               |
| 22        | GPIO 8            | Pin 24       | IN22              |

**Wiring Steps:**
1. Connect GPIO pin → Relay Module INx
2. Use appropriate wire gauge (22-24 AWG for signal)
3. Keep wires short to reduce interference
4. Use twisted-pair if wires are longer than 30cm

### Wiring Raspberry Pi GPIO to Sensors

**For each locker using Pi GPIO (1-22):**

| Locker ID | GPIO Pin (Input) | Physical Pin | Sensor Connection |
|-----------|------------------|--------------|-------------------|
| 1         | GPIO 7           | Pin 26       | Sensor 1          |
| 2         | GPIO 8           | Pin 24       | Sensor 2          |
| ...       | ...              | ...          | ...               |

**Sensor Wiring:**
```
GPIO Pin → Reed Switch Terminal 1
Reed Switch Terminal 2 → GND
10kΩ Resistor: 3.3V → GPIO Pin (pull-up)
```

**Code Configuration:**
- GPIO pins are configured with internal pull-up resistors (PUD_UP)
- When door closed: Switch closes → GPIO reads LOW (0)
- When door open: Switch open → GPIO reads HIGH (1)

---

## MCP23017 I2C Expander Setup (Lockers 23-32)

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
- **MCP23017 (Lockers 23-32)**: A0=GND, A1=GND, A2=GND → **Address 0x20**
  - Port A (GPA0-GPA7): 8 relay outputs
  - Port B (GPB0-GPB1): 2 additional relay outputs
  - Port B (GPB0-GPB7): 8 sensor inputs (can share with relay outputs or use separately)

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

**Complete MCP23017 (0x20) Wiring:**
```
MCP23017:
  VDD (Pin 28) → Pi Pin 1 or 17 (3.3V) [Recommended] OR Pin 2/4 (5V)
  VSS (Pin 27) → Pi Pin 6 (GND)
  SDA (Pin 3) → Pi Pin 3 (GPIO 2)
  SCL (Pin 4) → Pi Pin 5 (GPIO 3)
  RESET (Pin 18) → Pi Pin 1 or 17 (3.3V) [Keep HIGH]
  A0 (Pin 25) → GND (via jumper or wire)
  A1 (Pin 24) → GND
  A2 (Pin 23) → GND
```

**Power Options:**
- **3.3V (Recommended)**: VDD → Pi 3.3V (Pin 1 or 17) - Safer, direct compatibility
- **5V (Alternative)**: VDD → Pi 5V (Pin 2 or 4) - Higher drive current, but I2C pull-ups must be 3.3V

---

## Relay Board Wiring (Outputs)

### Complete Pin Mapping for 32 Lockers

**Raspberry Pi GPIO Lockers (1-22):**

| Locker ID | GPIO Pin | Physical Pin | Relay Module Input |
|-----------|----------|--------------|-------------------|
| 1         | GPIO 4   | Pin 7        | IN1               |
| 2         | GPIO 5   | Pin 29       | IN2               |
| 3         | GPIO 6   | Pin 31       | IN3               |
| 4         | GPIO 12  | Pin 32       | IN4               |
| 5         | GPIO 13  | Pin 33       | IN5               |
| 6         | GPIO 16  | Pin 36       | IN6               |
| 7         | GPIO 17  | Pin 11       | IN7               |
| 8         | GPIO 18  | Pin 12       | IN8               |
| 9         | GPIO 19  | Pin 35       | IN9               |
| 10        | GPIO 20  | Pin 38       | IN10              |
| 11        | GPIO 21  | Pin 40       | IN11              |
| 12        | GPIO 22  | Pin 15       | IN12              |
| 13        | GPIO 23  | Pin 16       | IN13              |
| 14        | GPIO 24  | Pin 18       | IN14              |
| 15        | GPIO 25  | Pin 22       | IN15              |
| 16        | GPIO 26  | Pin 37       | IN16              |
| 17        | GPIO 27  | Pin 13       | IN17              |
| 18        | GPIO 2   | Pin 3        | IN18              |
| 19        | GPIO 3   | Pin 5        | IN19              |
| 20        | GPIO 14  | Pin 8        | IN20              |
| 21        | GPIO 15  | Pin 10       | IN21              |
| 22        | GPIO 8   | Pin 24       | IN22              |

**MCP23017 Lockers (23-32):**

| Locker ID | MCP23017 Pin | Port | Bit | Relay Module Input |
|-----------|--------------|------|-----|-------------------|
| 23        | GPA0         | A    | 0   | IN23              |
| 24        | GPA1         | A    | 1   | IN24              |
| 25        | GPA2         | A    | 2   | IN25              |
| 26        | GPA3         | A    | 3   | IN26              |
| 27        | GPA4         | A    | 4   | IN27              |
| 28        | GPA5         | A    | 5   | IN28              |
| 29        | GPA6         | A    | 6   | IN29              |
| 30        | GPA7         | A    | 7   | IN30              |
| 31        | GPB0         | B    | 0   | IN31              |
| 32        | GPB1         | B    | 1   | IN32              |

### Relay Module Connections

**Typical 32-Channel Relay Module (or multiple smaller modules):**
- **VCC**: Connect to 5V power supply (NOT Pi 5V if using separate PSU)
- **GND**: Connect to common ground (Pi GND + PSU GND)
- **IN1-IN22**: Connect to Raspberry Pi GPIO outputs
- **IN23-IN32**: Connect to MCP23017 outputs (GPA0-GPA7, GPB0-GPB1)

**Wiring Steps:**
1. **Pi GPIO Lockers (1-22):**
   - Connect GPIO 4 → Relay Module IN1
   - Connect GPIO 5 → Relay Module IN2
   - Continue sequentially up to GPIO 8 → IN22
2. **MCP23017 Lockers (23-32):**
   - Connect MCP23017 GPA0 → Relay Module IN23
   - Connect MCP23017 GPA1 → Relay Module IN24
   - Continue sequentially up to GPB1 → IN32
3. Use twisted-pair wires for longer runs to reduce EMI
4. Label all connections for easy troubleshooting

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

### Example Wiring

**Locker 1 (Pi GPIO):**
```
Raspberry Pi GPIO 4 → Relay Module IN1
Relay Module COM → Lock Actuator Positive
Relay Module NO → 5V Power Supply Positive
Lock Actuator Negative → Power Supply Ground
```

**Locker 23 (MCP23017):**
```
MCP23017 GPA0 → Relay Module IN23
Relay Module COM → Lock Actuator Positive
Relay Module NO → 5V Power Supply Positive
Lock Actuator Negative → Power Supply Ground
```

---

## Door Sensor Wiring (Inputs)

### Complete Sensor Pin Mapping for 32 Lockers

**Raspberry Pi GPIO Lockers (1-22):**

| Locker ID | GPIO Pin | Physical Pin | Sensor Connection |
|-----------|----------|--------------|-------------------|
| 1         | GPIO 7   | Pin 26       | Sensor 1          |
| 2         | GPIO 8   | Pin 24       | Sensor 2          |
| 3         | GPIO 9   | Pin 21       | Sensor 3          |
| 4         | GPIO 10  | Pin 19       | Sensor 4          |
| 5         | GPIO 11  | Pin 23       | Sensor 5          |
| ...       | ...      | ...          | ...               |
| 22        | GPIO 23  | Pin 16       | Sensor 22         |

**MCP23017 Lockers (23-32):**

| Locker ID | MCP23017 Pin | Port | Bit | Sensor Connection |
|-----------|--------------|------|-----|-------------------|
| 23        | GPB0         | B    | 0   | Sensor 23         |
| 24        | GPB1         | B    | 1   | Sensor 24         |
| 25        | GPB2         | B    | 2   | Sensor 25         |
| 26        | GPB3         | B    | 3   | Sensor 26         |
| 27        | GPB4         | B    | 4   | Sensor 27         |
| 28        | GPB5         | B    | 5   | Sensor 28         |
| 29        | GPB6         | B    | 6   | Sensor 29         |
| 30        | GPB7         | B    | 7   | Sensor 30         |
| 31        | GPA0         | A    | 0   | Sensor 31 (if using A port) |
| 32        | GPA1         | A    | 1   | Sensor 32 (if using A port) |

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

### Example Sensor Wiring

**Locker 1 (Pi GPIO):**
```
Raspberry Pi GPIO 7 → Reed Switch Terminal 1
Reed Switch Terminal 2 → GND
Internal Pull-up: 3.3V → GPIO 7 (enabled in code)
```

**Locker 23 (MCP23017):**
```
MCP23017 GPB0 → Reed Switch Terminal 1
Reed Switch Terminal 2 → GND
Internal Pull-up: Enabled via GPPUB register
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
| Raspberry Pi 4 | 5V | ~3A (peak) | 3A |
| MCP23017 | 3.3V or 5V | ~1mA | 1mA |
| Relay Module (idle) | 5V | ~50mA | 50mA |
| Relay Module (active) | 5V | ~70mA per relay | ~2.2A (32×) |
| Lock Actuator | 5V-12V | 100mA-500mA each | 3.2A-16A (32×) |

**Total System Current:**
- **Logic/Control**: ~3.1A (Pi + MCP + relays)
- **Lock Actuators**: 3.2A-16A (depends on actuator type)
- **Recommended PSU**: 5V, 15A+ (or 12V with voltage regulator for actuators)

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
                    Raspberry Pi 4
                         │
        ┌────────────────┼────────────────┐
        │                │                │
     GPIO Pins        I2C Bus          Power
   (22 lockers)    (SDA/SCL)         (5V/3.3V)
        │                │                │
        │                │                │
    ┌───▼────────────┐   │                │
    │ 22 GPIO Pins   │   │                │
    │ (Lockers 1-22) │   │                │
    │                │   │                │
    │ Outputs:       │   │                │
    │ GPIO 4,5,6...  │   │                │
    │                │   │                │
    │ Inputs:        │   │                │
    │ GPIO 7,8,9...  │   │                │
    └───┬────────────┘   │                │
        │                │                │
        │            ┌───▼────────────┐   │
        │            │  MCP23017      │   │
        │            │  Address:0x20 │   │
        │            │  (Lockers 23-32)│   │
        │            │                │   │
        │            │ Port A: Relays │   │
        │            │ Port B: Sensors│   │
        │            └───┬────────────┘   │
        │                │                │
    ┌───┴────────────────┴────────────────┴───┐
    │      32-Channel Relay Module             │
    │  IN1-IN22 ← Pi GPIO outputs             │
    │  IN23-IN32 ← MCP23017 outputs           │
    │  VCC ← 5V PSU                           │
    │  GND ← Common Ground                    │
    └───┬─────────────────────────────────────┘
        │
        │ (Relay Contacts: COM/NO)
        │
    ┌───▼─────────────────────────────────────┐
    │     32 Lock Actuators                   │
    │  (Solenoids/Magnetic Locks)             │
    └─────────────────────────────────────────┘

    Sensor Inputs (32 total)
    ├── Pi GPIO Sensors (Lockers 1-22)
    └── MCP23017 Sensors (Lockers 23-32)
                 │
        ┌────────┼────────┐
        │        │        │
    ┌───▼───┐ ┌──▼───┐ ┌──▼───┐
    │Sensor │ │Sensor│ │Sensor│
    │   1   │ │  2   │ │ ...32│
    └───────┘ └──────┘ └──────┘
    (Reed Switches)
```

### Connection Summary Table

| From | To | Wire Count | Notes |
|------|----|-----------|-------|
| Pi GPIO 4-8, 12-27, 2-3, 14-15 | Relay IN1-IN22 | 22 | Pi GPIO relay control |
| Pi GPIO 7-11, 14-15, 2-6, 12-13, 16-23 | Sensors 1-22 | 22 | Pi GPIO sensor inputs |
| Pi Pin 3 | MCP SDA | 1 | I2C data line |
| Pi Pin 5 | MCP SCL | 1 | I2C clock line |
| Pi Pin 1/17 | MCP VDD | 1 | 3.3V power (recommended) |
| Pi Pin 6 | All GNDs | Multiple | Common ground |
| MCP GPA0-GPA7, GPB0-GPB1 | Relay IN23-IN32 | 10 | MCP relay control |
| MCP GPB0-GPB7 | Sensors 23-32 | 8-10 | MCP sensor inputs |
| Relay COM/NO | Lock Actuators | 32×2 | Power to locks |
| Sensors | GND | 32 | Sensor return |
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
20: 20 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
```

You should see **20** in the grid (only one MCP23017 chip for lockers 23-32).

### Step 2: Test Raspberry Pi GPIOs

**Using Python:**
```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Test GPIO 4 (Locker 1 output)
GPIO.setup(4, GPIO.OUT)
GPIO.output(4, GPIO.HIGH)
time.sleep(1)
GPIO.output(4, GPIO.LOW)
print("GPIO 4 test complete")

# Test GPIO 7 (Locker 1 sensor input)
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
state = GPIO.input(7)
print(f"GPIO 7 sensor state: {state} (0=closed, 1=open)")
```

**Listen for relay click** - you should hear an audible "click" when the relay activates.

### Step 3: Test MCP23017 (Lockers 23-32)

**Using Python:**
```python
import smbus
import time

bus = smbus.SMBus(1)
addr = 0x20  # MCP23017

# Configure Port A as outputs (relays)
bus.write_byte_data(addr, 0x00, 0x00)  # IODIRA = all outputs
bus.write_byte_data(addr, 0x12, 0x00)  # GPIOA = all low

# Configure Port B as inputs (sensors) with pull-ups
bus.write_byte_data(addr, 0x01, 0xFF)  # IODIRB = all inputs
bus.write_byte_data(addr, 0x0D, 0xFF)  # GPPUB = enable pull-ups

# Test relay (Locker 23 = GPA0)
bus.write_byte_data(addr, 0x12, 0x01)  # GPIOA = bit 0 high
time.sleep(1)
bus.write_byte_data(addr, 0x12, 0x00)  # GPIOA = bit 0 low

# Test sensor (Locker 23 = GPB0)
val = bus.read_byte_data(addr, 0x13)  # Read GPIOB
sensor = (val >> 0) & 1
print(f"Locker 23 sensor state: {sensor} (0=closed, 1=open)")
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
2. Login as delivery (PIN: check `routes.py` or default: 1234)
3. Click a locker button (test both Pi GPIO and MCP lockers)
4. Verify:
   - Relay clicks
   - Lock actuator activates
   - OTP displays
   - Door sensor updates when door closes
5. Test configuration page: `http://localhost:5000/configuration`
   - Assign lockers to Pi GPIO or MCP
   - Set special codes
   - Verify changes take effect

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

## Configuration System

The system includes a web-based configuration interface to assign lockers to hardware.

### Accessing Configuration

1. Navigate to: `http://[PI_IP]:5000/configuration`
2. Or click the "Configuration" button on the home page

### Configuration Options

For each locker (1-32), you can configure:

1. **Hardware Type:**
   - **Raspberry Pi GPIO**: Uses direct Pi GPIO pins
   - **MCP23017**: Uses the I2C expander chip

2. **GPIO Pin:**
   - For Pi GPIO lockers: Specify which GPIO pin to use (e.g., 4, 5, 6, etc.)
   - For MCP lockers: Specify MCP pin index (0-9)

3. **Sensor Pin:**
   - For Pi GPIO lockers: Specify which GPIO pin for the sensor input
   - For MCP lockers: Usually same as relay pin or different Port B pin

4. **Special Code:**
   - Set a permanent access code for this locker
   - Works alongside OTP codes for customer pickup
   - Useful for maintenance or special access

### Default Configuration

- **Lockers 1-22**: Raspberry Pi GPIO
  - Relay outputs: GPIO 4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 2, 3, 14, 15, 8
  - Sensor inputs: GPIO 7, 8, 9, 10, 11, 14, 15, 2, 3, 4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23

- **Lockers 23-32**: MCP23017
  - Relay outputs: Port A (GPA0-GPA7) + Port B (GPB0-GPB1)
  - Sensor inputs: Port B (GPB0-GPB7)

### After Configuration Changes

1. Save the configuration
2. The system will automatically reload hardware settings
3. Restart the service if needed: `sudo systemctl restart smartlocker.service`

---

## Safety Reminders

⚠️ **CRITICAL SAFETY WARNINGS:**

1. **Always disconnect power** before making wiring changes
2. **Double-check all connections** before powering on
3. **Use appropriate fuses** to prevent overcurrent damage
4. **Never mix AC and DC** in the same wire bundle
5. **Verify polarity** on all power connections
6. **Test with multimeter** before connecting to Pi
7. **Start with one locker** - verify it works before wiring all 32
8. **Use the configuration page** - assign lockers to hardware as you wire them
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

**Last Updated**: 2025-12-04  
**Version**: 2.0

**Changes in v2.0:**
- Updated for hybrid hardware system (32 lockers)
- Added Raspberry Pi GPIO wiring (22 lockers)
- Updated MCP23017 setup (10 lockers instead of 16)
- Added configuration system documentation
- Updated power requirements for 32 lockers

