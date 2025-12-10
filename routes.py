from flask import render_template, request, jsonify, redirect, url_for, flash, session
from app import app, hardware
from database import get_db_connection
import random
import string
from datetime import datetime, timedelta

# --- Helpers ---

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

def get_locker_status(locker_id):
    conn = get_db_connection()
    locker = conn.execute('SELECT * FROM lockers WHERE id = ?', (locker_id,)).fetchone()
    conn.close()
    return locker

def update_locker_status(locker_id, is_occupied=None, door_closed=None, otp_code=None):
    conn = get_db_connection()
    query = 'UPDATE lockers SET updated_at = CURRENT_TIMESTAMP'
    params = []
    
    if is_occupied is not None:
        query += ', is_occupied = ?'
        params.append(is_occupied)
    if door_closed is not None:
        query += ', door_closed = ?'
        params.append(door_closed)
    if otp_code is not None:
        query += ', otp_code = ?'
        params.append(otp_code)
        
    query += ' WHERE id = ?'
    params.append(locker_id)
    
    conn.execute(query, params)
    conn.commit()
    conn.close()

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in ['fr', 'ar']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

@app.route('/delivery/login', methods=['GET', 'POST'])
def delivery_login():
    if request.method == 'POST':
        pin = request.form.get('pin')
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM delivery_users WHERE pin_code = ?', (pin,)).fetchone()
        conn.close()
        
        if user:
            return redirect(url_for('delivery_dashboard'))
        else:
            flash('Invalid PIN', 'error')
            
    return render_template('delivery_login.html')

@app.route('/delivery/dashboard')
def delivery_dashboard():
    conn = get_db_connection()
    lockers = conn.execute('SELECT * FROM lockers ORDER BY id').fetchall()
    conn.close()
    
    # Sync with hardware state (optional, but good for consistency)
    hw_states = hardware.get_all_lockers_states()
    # Note: In a real system, we might want to update DB based on HW state here
    
    return render_template('delivery_dashboard.html', lockers=lockers, hw_states=hw_states)

@app.route('/configuration', methods=['GET', 'POST'])
def configuration():
    conn = get_db_connection()
    
    if request.method == 'POST':
        # Update locker configurations
        for locker_id in range(1, 33):
            hw_type = request.form.get(f'hw_type_{locker_id}', 'pi')
            gpio_pin = request.form.get(f'gpio_pin_{locker_id}')
            sensor_pin = request.form.get(f'sensor_pin_{locker_id}')
            special_code = request.form.get(f'special_code_{locker_id}', '').strip()
            
            try:
                gpio_pin = int(gpio_pin) if gpio_pin else None
                sensor_pin = int(sensor_pin) if sensor_pin else None
            except:
                gpio_pin = None
                sensor_pin = None
            
            conn.execute('''UPDATE lockers 
                SET hardware_type = ?, gpio_pin = ?, sensor_pin = ?, special_code = ?
                WHERE id = ?''', 
                (hw_type, gpio_pin, sensor_pin, special_code or None, locker_id))
        
        conn.commit()
        conn.close()
        
        # Reload hardware configuration
        from app import load_locker_config, USE_MOCK_HARDWARE
        from hardware import HybridHardware
        import app as app_module
        if not USE_MOCK_HARDWARE:
            try:
                new_config = load_locker_config()
                app_module.hardware = HybridHardware(locker_config=new_config)
                hardware = app_module.hardware
            except Exception as e:
                print(f"Failed to reload hardware: {e}")
        
        flash('Configuration saved successfully', 'success')
        return redirect(url_for('configuration'))
    
    lockers = conn.execute('SELECT * FROM lockers ORDER BY id').fetchall()
    conn.close()
    return render_template('configuration.html', lockers=lockers)

@app.route('/customer/pickup', methods=['GET', 'POST'])
def customer_pickup():
    if request.method == 'POST':
        code = request.form.get('otp', '').strip()
        conn = get_db_connection()
        
        # First try OTP code
        locker = conn.execute('SELECT * FROM lockers WHERE otp_code = ?', (code,)).fetchone()
        
        # If not found, try special code
        if not locker:
            locker = conn.execute('SELECT * FROM lockers WHERE special_code = ?', (code,)).fetchone()
        
        if locker:
            # Valid code (OTP or special)
            locker_id = locker['id']
            
            # Open Locker
            hardware.open_locker(locker_id)
            
            # Clear OTP and mark as empty (assuming customer takes package)
            # In a real system, we might wait for door close to mark empty.
            # But for simplicity, we mark it empty now or when door closes.
            # Let's mark it empty now to prevent reuse of OTP immediately.
            update_locker_status(locker_id, is_occupied=0, otp_code=None)
            
            # Log code usage (only if it was an OTP, not special code)
            if locker.get('otp_code') == code:
                conn.execute('INSERT INTO otp_codes (locker_id, code, used, expires_at) VALUES (?, ?, 1, CURRENT_TIMESTAMP)', 
                             (locker_id, code))
                conn.commit()
            
            conn.close()
            
            return render_template('status.html', message='Locker Opened!', sub_message='Please take your package and close the door.', locker_id=locker_id)
        else:
            conn.close()
            flash('Invalid Code', 'error')
            
    return render_template('customer_otp.html')

# --- API Endpoints (for JS/Async) ---

@app.route('/api/open_locker/<int:locker_id>', methods=['POST'])
def api_open_locker(locker_id):
    # This is for Delivery Guy to open an empty locker
    conn = get_db_connection()
    locker = conn.execute('SELECT * FROM lockers WHERE id = ?', (locker_id,)).fetchone()
    
    if not locker:
        return jsonify({'success': False, 'error': 'Locker not found'}), 404
        
    # Open hardware
    hardware.open_locker(locker_id)
    
    # Generate OTP for this locker (since delivery guy is putting something in)
    new_otp = generate_otp()
    
    # Update DB: Occupied, OTP set
    update_locker_status(locker_id, is_occupied=1, otp_code=new_otp)
    
    conn.close()
    
    return jsonify({
        'success': True, 
        'message': f'Locker {locker_id} opened',
        'otp': new_otp
    })

@app.route('/api/status')
def api_status():
    # Return status of all lockers
    conn = get_db_connection()
    lockers = conn.execute('SELECT * FROM lockers').fetchall()
    conn.close()
    
    # Get hardware states
    hw_states = hardware.get_all_lockers_states()
    
    data = []
    for l in lockers:
        data.append({
            'id': l['id'],
            'is_occupied': bool(l['is_occupied']),
            'otp_code': l['otp_code'],
            'door_closed': hw_states.get(l['id'], True) # Use HW state if available
        })
        
    return jsonify({'lockers': data})

@app.route('/api/mock/close_door/<int:locker_id>', methods=['POST'])
def api_mock_close_door(locker_id):
    # Helper to close door in mock mode
    if hasattr(hardware, 'mock_close_door'):
        hardware.mock_close_door(locker_id)
        # Update DB to reflect closed door
        update_locker_status(locker_id, door_closed=1)
        return jsonify({'success': True, 'message': f'Locker {locker_id} closed (Mock)'})
    return jsonify({'success': False, 'error': 'Not in mock mode'}), 400
