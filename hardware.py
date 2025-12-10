import time
import random

# Try to import smbus for real hardware, handle failure for non-Pi environments
try:
    import smbus
    HAS_SMBUS = True
except ImportError:
    HAS_SMBUS = False

# Try to import RPi.GPIO for Raspberry Pi GPIO control
try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except ImportError:
    HAS_GPIO = False

class HardwareInterface:
    def open_locker(self, locker_id):
        raise NotImplementedError

    def read_door_state(self, locker_id):
        raise NotImplementedError

    def get_all_lockers_states(self):
        raise NotImplementedError

class RealMCP23017(HardwareInterface):
    def __init__(self, address_relays=0x20, address_sensors=0x21, bus_num=1):
        if not HAS_SMBUS:
            raise RuntimeError("smbus not found. Cannot use RealMCP23017.")
        
        self.bus = smbus.SMBus(bus_num)
        self.addr_relays = address_relays
        self.addr_sensors = address_sensors

        # Configuration constants
        self.IODIRA = 0x00 # I/O Direction Register A
        self.IODIRB = 0x01 # I/O Direction Register B
        self.GPIOA = 0x12  # GPIO Port A
        self.GPIOB = 0x13  # GPIO Port B
        self.OLATA = 0x14  # Output Latch A
        self.OLATB = 0x15  # Output Latch B

        # Initialize Relays (Outputs) - Chip 1
        # Set all pins to OUTPUT (0x00)
        self.bus.write_byte_data(self.addr_relays, self.IODIRA, 0x00)
        self.bus.write_byte_data(self.addr_relays, self.IODIRB, 0x00)
        # Turn off all relays initially (assuming Active LOW or HIGH, let's assume Active LOW for relays usually, but here 0=OFF, 1=ON for simplicity logic, will invert if needed)
        # Actually, let's assume writing 0 to GPIO turns it OFF, 1 turns it ON.
        self.bus.write_byte_data(self.addr_relays, self.GPIOA, 0x00)
        self.bus.write_byte_data(self.addr_relays, self.GPIOB, 0x00)

        # Initialize Sensors (Inputs) - Chip 2
        # Set all pins to INPUT (0xFF)
        self.bus.write_byte_data(self.addr_sensors, self.IODIRA, 0xFF)
        self.bus.write_byte_data(self.addr_sensors, self.IODIRB, 0xFF)
        # Enable Pull-ups if needed (GPPUA/GPPUB), skipping for now unless specified.

    def _set_relay(self, pin_index, state):
        # pin_index 0-15. 0-7 is Port A, 8-15 is Port B.
        # We need to read current state, modify bit, write back.
        # Or keep a local state cache. For robustness, read-modify-write.
        
        port = self.GPIOA if pin_index < 8 else self.GPIOB
        pin = pin_index if pin_index < 8 else pin_index - 8
        
        current = self.bus.read_byte_data(self.addr_relays, port)
        if state:
            new_val = current | (1 << pin)
        else:
            new_val = current & ~(1 << pin)
            
        self.bus.write_byte_data(self.addr_relays, port, new_val)

    def open_locker(self, locker_id):
        # locker_id 1-16 -> pin_index 0-15
        pin_index = locker_id - 1
        print(f"[Hardware] Opening locker {locker_id} (Pin {pin_index})")
        self._set_relay(pin_index, True) # ON
        time.sleep(1) # Keep open for 1 second (solenoid pulse)
        self._set_relay(pin_index, False) # OFF

    def read_door_state(self, locker_id):
        # locker_id 1-16 -> pin_index 0-15
        pin_index = locker_id - 1
        port = self.GPIOA if pin_index < 8 else self.GPIOB
        pin = pin_index if pin_index < 8 else pin_index - 8
        
        val = self.bus.read_byte_data(self.addr_sensors, port)
        # Return True if Closed, False if Open.
        # Usually sensors are switches. Let's assume 1 = Closed, 0 = Open (or vice versa).
        # Assuming Pull-up: Open switch = 1, Closed switch = 0 (GND).
        # Let's assume 0 means Closed (GND) for now.
        is_closed = not ((val >> pin) & 1) 
        return is_closed

    def get_all_lockers_states(self):
        states = {}
        # Read all at once for efficiency
        val_a = self.bus.read_byte_data(self.addr_sensors, self.GPIOA)
        val_b = self.bus.read_byte_data(self.addr_sensors, self.GPIOB)
        
        for i in range(16):
            locker_id = i + 1
            if i < 8:
                is_closed = not ((val_a >> i) & 1)
            else:
                is_closed = not ((val_b >> (i-8)) & 1)
            states[locker_id] = is_closed
        return states

class MockMCP23017(HardwareInterface):
    def __init__(self):
        print("[MockHardware] Initialized 32 lockers.")
        self.relays = [False] * 32
        # True = Closed, False = Open
        self.sensors = [True] * 32 

    def open_locker(self, locker_id):
        idx = locker_id - 1
        if 0 <= idx < 32:
            print(f"[MockHardware] Click! Locker {locker_id} opened.")
            self.relays[idx] = True
            self.sensors[idx] = False # Door opens
            
            # Simulate user closing door after 5 seconds (async in real life, but here we just toggle state logic)
            # For the sake of the mock, we leave it 'Open' until some other action closes it, 
            # OR we can say it stays open.
            # Let's keep it open. The user might need a "Close Door" button in Mock UI to test logic.
            # But the prompt says "After the door closes (sensor detects)..."
            # So we need a way to simulate closing.
            # For now, let's auto-close it after a delay in a background thread? 
            # Or just provide a helper to close it.
            pass
        else:
            print(f"[MockHardware] Invalid locker {locker_id}")

    def read_door_state(self, locker_id):
        idx = locker_id - 1
        if 0 <= idx < 32:
            return self.sensors[idx]
        return True  # Default: closed

    def get_all_lockers_states(self):
        states = {}
        for i in range(32):
            states[i+1] = self.sensors[i]
        return states
    
    # Helper for testing
    def mock_close_door(self, locker_id):
        idx = locker_id - 1
        if 0 <= idx < 16:
            print(f"[MockHardware] Slam! Locker {locker_id} closed.")
            self.sensors[idx] = True

class HybridHardware(HardwareInterface):
    """
    Hybrid hardware supporting:
    - 22 Raspberry Pi GPIOs (lockers 1-22)
    - 10 MCP23017 pins (lockers 23-32)
    Total: 32 lockers
    """
    def __init__(self, mcp_address=0x20, bus_num=1, locker_config=None):
        """
        locker_config: dict mapping locker_id -> {'type': 'pi'|'mcp', 'pin': int, 'sensor_pin': int}
        If None, defaults: lockers 1-22 = Pi GPIO, 23-32 = MCP
        """
        self.locker_config = locker_config or self._default_config()
        self.pi_gpios = {}  # Store GPIO pin numbers for Pi lockers
        self.mcp_pins = {}  # Store MCP pin indices for MCP lockers
        
        # Initialize Pi GPIOs
        if HAS_GPIO:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            for locker_id, config in self.locker_config.items():
                if config['type'] == 'pi':
                    gpio_pin = config['pin']
                    GPIO.setup(gpio_pin, GPIO.OUT)
                    GPIO.output(gpio_pin, GPIO.LOW)
                    self.pi_gpios[locker_id] = gpio_pin
                    # Setup sensor pin if provided
                    if 'sensor_pin' in config:
                        GPIO.setup(config['sensor_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        else:
            print("[HybridHardware] Warning: RPi.GPIO not available, Pi GPIOs will not work")
        
        # Initialize MCP23017
        self.mcp_bus = None
        self.mcp_addr = None
        if HAS_SMBUS:
            try:
                self.mcp_bus = smbus.SMBus(bus_num)
                self.mcp_addr = mcp_address
                
                # MCP23017 constants
                self.IODIRA = 0x00
                self.IODIRB = 0x01
                self.GPIOA = 0x12
                self.GPIOB = 0x13
                self.GPPUA = 0x0C  # Pull-up register A
                self.GPPUB = 0x0D  # Pull-up register B
                
                # Configure Port A as outputs (for relays)
                self.mcp_bus.write_byte_data(self.mcp_addr, self.IODIRA, 0x00)
                self.mcp_bus.write_byte_data(self.mcp_addr, self.GPIOA, 0x00)
                
                # Configure Port B as inputs (for sensors) with pull-ups
                self.mcp_bus.write_byte_data(self.mcp_addr, self.IODIRB, 0xFF)
                self.mcp_bus.write_byte_data(self.mcp_addr, self.GPPUB, 0xFF)
                
                # Map MCP lockers to pin indices
                mcp_pin_index = 0
                for locker_id, config in sorted(self.locker_config.items()):
                    if config['type'] == 'mcp':
                        self.mcp_pins[locker_id] = mcp_pin_index
                        mcp_pin_index += 1
                        if mcp_pin_index >= 10:  # Only 10 MCP pins available
                            break
                
                print(f"[HybridHardware] Initialized: {len(self.pi_gpios)} Pi GPIOs, {len(self.mcp_pins)} MCP pins")
            except Exception as e:
                print(f"[HybridHardware] MCP23017 init failed: {e}")
                self.mcp_bus = None
        else:
            print("[HybridHardware] Warning: smbus not available, MCP23017 will not work")
    
    def _default_config(self):
        """Default configuration: lockers 1-22 = Pi GPIO, 23-32 = MCP"""
        config = {}
        # Pi GPIO pins (using available GPIOs, avoiding reserved ones)
        # Common available GPIOs: 4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27
        pi_gpios = [4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 2, 3, 14, 15, 8]
        pi_sensors = [7, 8, 9, 10, 11, 14, 15, 2, 3, 4, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 22, 23]
        
        for i in range(1, 23):  # Lockers 1-22
            config[i] = {
                'type': 'pi',
                'pin': pi_gpios[i-1] if i-1 < len(pi_gpios) else 4,
                'sensor_pin': pi_sensors[i-1] if i-1 < len(pi_sensors) else 7
            }
        
        for i in range(23, 33):  # Lockers 23-32
            config[i] = {
                'type': 'mcp',
                'pin': i - 23,  # MCP pin index 0-9
                'sensor_pin': i - 23  # Same pin for sensor (Port B)
            }
        
        return config
    
    def open_locker(self, locker_id):
        config = self.locker_config.get(locker_id)
        if not config:
            print(f"[HybridHardware] Locker {locker_id} not configured")
            return
        
        if config['type'] == 'pi':
            if HAS_GPIO and locker_id in self.pi_gpios:
                gpio_pin = self.pi_gpios[locker_id]
                print(f"[HybridHardware] Opening locker {locker_id} (Pi GPIO {gpio_pin})")
                GPIO.output(gpio_pin, GPIO.HIGH)
                time.sleep(1)
                GPIO.output(gpio_pin, GPIO.LOW)
            else:
                print(f"[HybridHardware] Pi GPIO not available for locker {locker_id}")
        elif config['type'] == 'mcp':
            if self.mcp_bus and locker_id in self.mcp_pins:
                pin_index = self.mcp_pins[locker_id]
                port = self.GPIOA if pin_index < 8 else self.GPIOB
                pin = pin_index if pin_index < 8 else pin_index - 8
                
                print(f"[HybridHardware] Opening locker {locker_id} (MCP pin {pin_index})")
                current = self.mcp_bus.read_byte_data(self.mcp_addr, port)
                new_val = current | (1 << pin)
                self.mcp_bus.write_byte_data(self.mcp_addr, port, new_val)
                time.sleep(1)
                new_val = current & ~(1 << pin)
                self.mcp_bus.write_byte_data(self.mcp_addr, port, new_val)
            else:
                print(f"[HybridHardware] MCP not available for locker {locker_id}")
    
    def read_door_state(self, locker_id):
        config = self.locker_config.get(locker_id)
        if not config:
            return True  # Default: closed
        
        if config['type'] == 'pi':
            if HAS_GPIO and 'sensor_pin' in config:
                sensor_pin = config['sensor_pin']
                state = GPIO.input(sensor_pin)
                # Assuming pull-up: LOW (0) = door closed, HIGH (1) = door open
                return state == GPIO.LOW
            return True  # Default: closed
        elif config['type'] == 'mcp':
            if self.mcp_bus and locker_id in self.mcp_pins:
                pin_index = self.mcp_pins[locker_id]
                port = self.GPIOB  # Sensors on Port B
                pin = pin_index if pin_index < 8 else pin_index - 8
                
                val = self.mcp_bus.read_byte_data(self.mcp_addr, port)
                is_closed = not ((val >> pin) & 1)
                return is_closed
            return True  # Default: closed
    
    def get_all_lockers_states(self):
        states = {}
        for locker_id in range(1, 33):  # 32 lockers
            states[locker_id] = self.read_door_state(locker_id)
        return states

def get_hardware(use_mock=True, locker_config=None):
    if use_mock:
        return MockMCP23017()
    else:
        try:
            return HybridHardware(locker_config=locker_config)
        except Exception as e:
            print(f"Failed to init real hardware: {e}. Falling back to Mock.")
            return MockMCP23017()
