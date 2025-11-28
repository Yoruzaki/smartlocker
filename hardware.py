import time
import random

# Try to import smbus for real hardware, handle failure for non-Pi environments
try:
    import smbus
    HAS_SMBUS = True
except ImportError:
    HAS_SMBUS = False

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
        print("[MockHardware] Initialized 16 lockers.")
        self.relays = [False] * 16
        # True = Closed, False = Open
        self.sensors = [True] * 16 

    def open_locker(self, locker_id):
        idx = locker_id - 1
        if 0 <= idx < 16:
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
        if 0 <= idx < 16:
            return self.sensors[idx]
        return False

    def get_all_lockers_states(self):
        states = {}
        for i in range(16):
            states[i+1] = self.sensors[i]
        return states
    
    # Helper for testing
    def mock_close_door(self, locker_id):
        idx = locker_id - 1
        if 0 <= idx < 16:
            print(f"[MockHardware] Slam! Locker {locker_id} closed.")
            self.sensors[idx] = True

def get_hardware(use_mock=True):
    if use_mock:
        return MockMCP23017()
    else:
        try:
            return RealMCP23017()
        except Exception as e:
            print(f"Failed to init real hardware: {e}. Falling back to Mock.")
            return MockMCP23017()
