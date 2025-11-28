"""
TTNN Operation Calculator Web Application
A Flask-based web interface for testing ttnn operations
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import ttnn
import torch
import traceback
import json
import hashlib
import secrets
import os
import threading
import subprocess
from datetime import timedelta, datetime

# Try to import resend, but make it optional
try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False
    print("⚠️  Resend not installed. Bug report feature will be disabled.")

app = Flask(__name__)
# Generate a secure secret key for sessions
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))
# Session timeout: 30 minutes of inactivity
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

# Securely hash the password (SHA256)
# The actual password is not stored anywhere in the code
PASSWORD_HASH = "fb4d52ec15fde028f3574bfb1a313020e1d5127851353194e84978f788ada6b3"

# Resend API configuration
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
CONTACT_EMAIL = "contact@aswincloud.com"
BUG_REPORT_EMAIL = "contact@aswincloud.com"

# Login attempt tracking (in-memory, resets on server restart)
login_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)

# Device access lock - ensures only one request uses device at a time
device_lock = threading.Lock()
device_queue_stats = {
    'total_requests': 0,
    'currently_waiting': 0,
    'max_wait_time': 0.0
}

def check_password(password):
    """Check if provided password matches the hash"""
    return hashlib.sha256(password.encode()).hexdigest() == PASSWORD_HASH

def is_locked_out(ip_address):
    """Check if an IP address is currently locked out"""
    if ip_address in login_attempts:
        attempt_data = login_attempts[ip_address]
        if attempt_data['count'] >= MAX_ATTEMPTS:
            lockout_time = attempt_data['lockout_until']
            if datetime.now() < lockout_time:
                return True, lockout_time
            else:
                # Lockout expired, reset attempts
                del login_attempts[ip_address]
    return False, None

def record_failed_attempt(ip_address):
    """Record a failed login attempt"""
    if ip_address not in login_attempts:
        login_attempts[ip_address] = {
            'count': 1,
            'first_attempt': datetime.now(),
            'lockout_until': None
        }
    else:
        login_attempts[ip_address]['count'] += 1
    
    # If max attempts reached, set lockout
    if login_attempts[ip_address]['count'] >= MAX_ATTEMPTS:
        login_attempts[ip_address]['lockout_until'] = datetime.now() + LOCKOUT_DURATION

def reset_attempts(ip_address):
    """Reset login attempts for an IP after successful login"""
    if ip_address in login_attempts:
        del login_attempts[ip_address]

def login_required(f):
    """Decorator to protect routes with password"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def open_device_for_computation():
    """Open device for a single computation (lock must be acquired first)"""
    try:
        device = ttnn.open_device(device_id=0)
        print(f"✅ Device opened for computation: {device}")
        return device
    except Exception as e:
        print(f"❌ Failed to open device: {e}")
        raise

def close_device_after_computation(device):
    """Close device after computation is complete (lock will be released by caller)"""
    if device is not None:
        try:
            ttnn.close_device(device)
            print("✅ Device closed after computation")
        except Exception as e:
            print(f"❌ Failed to close device: {e}")

def get_queue_stats():
    """Get current queue statistics"""
    return {
        'total_requests': device_queue_stats['total_requests'],
        'currently_waiting': device_queue_stats['currently_waiting'],
        'max_wait_time_seconds': round(device_queue_stats['max_wait_time'], 3)
    }

# Operations that have optional scalar parameters
OPERATIONS_WITH_PARAMS = {
    'addalpha': {'param_name': 'alpha', 'default': 1.0, 'description': 'Scalar multiplier for second input'},
    'subalpha': {'param_name': 'alpha', 'default': 1.0, 'description': 'Scalar multiplier for second input'},
    'addcmul': {'param_name': 'value', 'default': 1.0, 'description': 'Scalar multiplier for product'},
    'addcdiv': {'param_name': 'value', 'default': 1.0, 'description': 'Scalar multiplier for division'},
    'elu': {'param_name': 'alpha', 'default': 1.0, 'description': 'Alpha value for ELU activation'},
    'threshold': {'param_name': 'threshold', 'default': 0.0, 'description': 'Threshold value', 'has_second_param': True, 'second_param_name': 'value', 'second_param_default': 0.0, 'second_param_description': 'Replacement value'},
    'heaviside': {'param_name': 'value', 'default': 0.0, 'description': 'Value when input is zero'},
    'prelu': {'param_name': 'weight', 'default': 0.25, 'description': 'Negative slope coefficient'},
}

# Operation categories and their operations
OPERATIONS = {
    "Pointwise Unary": [
        "abs", "acos", "acosh", "asin", "asinh", "atan", "atanh",
        "cbrt", "ceil", "celu", "clamp", "clip", "clone", "cos", "cosh",
        "deg2rad", "elu", "eqz", "erf", "erfc", "erfinv", "exp", "exp2", "expm1",
        "floor", "frac", "gelu", "gez", "gtz", "hardsigmoid", "hardswish", "hardtanh",
        "heaviside", "i0", "identity", "isfinite", "isinf", "isnan", "isneginf", "isposinf",
        "leaky_relu", "lez", "lgamma", "log", "log10", "log1p", "log2", "log_sigmoid",
        "logical_not", "logit", "ltz", "mish", "neg", "nez",
        "prelu", "rad2deg", "reciprocal", "relu", "relu6", "round", "rsqrt",
        "selu", "sigmoid", "sigmoid_accurate", "sign", "signbit", "silu", "sin", "sinh",
        "softplus", "softshrink", "softsign", "sqrt", "square",
        "swish", "tan", "tanh", "tanhshrink", "tril", "triu", "trunc"
    ],
    "Pointwise Binary": [
        "add", "addalpha", "subalpha", "mul", "multiply", "subtract", "div", "divide", "div_no_nan",
        "floor_div", "remainder", "fmod", "gcd", "lcm",
        "logical_and", "logical_or", "logical_xor",
        "bitwise_and", "bitwise_or", "bitwise_xor",
        "logaddexp", "logaddexp2", "hypot", "xlogy", "squared_difference",
        "gt", "lt", "ge", "le", "eq", "ne", "isclose",
        "maximum", "minimum", "pow", "atan2"
    ],
    "Pointwise Ternary": [
        "addcdiv", "addcmul", "mac", "where", "lerp"
    ]
}

# Data type mapping
DTYPE_MAP = {
    "uint8": ttnn.uint8,
    "uint16": ttnn.uint16,
    "int32": ttnn.int32,
    "uint32": ttnn.uint32,
    "float32": ttnn.float32,
    "bfloat16": ttnn.bfloat16,
    "bfloat8_b": ttnn.bfloat8_b,
    "bfloat4_b": ttnn.bfloat4_b,
}

def compute_torch_equivalent(operation_name, inputs, target_dtype, optional_param=None, optional_param_2=None):
    """Compute the equivalent result using pure PyTorch for comparison"""
    try:
        # Map ttnn dtype to torch dtype
        dtype_map = {
            'bfloat16': torch.bfloat16,
            'float32': torch.float32,
            'int32': torch.int32,
            'uint32': torch.int32,  # torch doesn't have uint32, use int32
            'uint8': torch.uint8,
            'uint16': torch.int16,  # torch doesn't have uint16, use int16
        }
        
        # Create torch tensors from input specifications
        torch_inputs = []
        for inp in inputs:
            input_type = inp.get('type')
            value = inp.get('value')
            shape_str = inp.get('shape', '1,1,32,32')
            dtype_str = inp.get('dtype', 'bfloat16')
            
            if input_type == 'scalar':
                torch_inputs.append(float(value))
            else:
                # Parse shape from string
                try:
                    shape = [int(s.strip()) for s in shape_str.split(',')]
                    if len(shape) < 2:
                        shape = [1, 1, 32, 32]
                except:
                    shape = [1, 1, 32, 32]
                
                # Get torch dtype matching the input
                torch_dtype = dtype_map.get(dtype_str, torch.float32)
                
                # Create torch tensor with the same shape and dtype
                torch_tensor = torch.full(tuple(shape), float(value), dtype=torch_dtype)
                torch_inputs.append(torch_tensor)
        
        # Map ttnn operations to torch operations
        op_map = {
            'add': lambda a, b: torch.add(a, b),
            'subtract': lambda a, b: torch.subtract(a, b),
            'mul': lambda a, b: torch.mul(a, b),
            'multiply': lambda a, b: torch.multiply(a, b),
            'div': lambda a, b: torch.div(a, b),
            'divide': lambda a, b: torch.div(a, b),
            'pow': lambda a, b: torch.pow(a, b),
            'sqrt': lambda a: torch.sqrt(a),
            'exp': lambda a: torch.exp(a),
            'log': lambda a: torch.log(a),
            'sin': lambda a: torch.sin(a),
            'cos': lambda a: torch.cos(a),
            'tan': lambda a: torch.tan(a),
            'abs': lambda a: torch.abs(a),
            'neg': lambda a: torch.neg(a),
            'relu': lambda a: torch.relu(a),
            'sigmoid': lambda a: torch.sigmoid(a),
            'tanh': lambda a: torch.tanh(a),
            'elu': lambda a, alpha=1.0: torch.nn.functional.elu(a, alpha=alpha),
            'prelu': lambda a, weight=0.25: torch.nn.functional.prelu(a, torch.tensor(weight, dtype=a.dtype)),
            'threshold': lambda a, threshold=0.0, value=0.0: torch.threshold(a, threshold, value),
            'heaviside': lambda a, value=0.0: torch.heaviside(a, torch.full_like(a, value)),
            'floor': lambda a: torch.floor(a),
            'ceil': lambda a: torch.ceil(a),
            'round': lambda a: torch.round(a),
            'square': lambda a: torch.square(a),
            'rsqrt': lambda a: torch.rsqrt(a),
            'reciprocal': lambda a: torch.reciprocal(a),
            'maximum': lambda a, b: torch.maximum(a, b),
            'minimum': lambda a, b: torch.minimum(a, b),
            'addalpha': lambda a, b, alpha=1: torch.add(a, b, alpha=alpha),
            'subalpha': lambda a, b, alpha=1: torch.sub(a, b, alpha=alpha),
            'where': lambda a, b, c: torch.where(a.bool(), b, c),
            'addcmul': lambda a, b, c, value=1: torch.addcmul(a, b, c, value=value),
            'addcdiv': lambda a, b, c, value=1: torch.addcdiv(a, b, c, value=value),
            'lerp': lambda a, b, weight: torch.lerp(a, b, weight),
            'mac': lambda a, b, c: a + b * c,
            'gt': lambda a, b: torch.gt(a, b),
            'lt': lambda a, b: torch.lt(a, b),
            'ge': lambda a, b: torch.ge(a, b),
            'le': lambda a, b: torch.le(a, b),
            'eq': lambda a, b: torch.eq(a, b),
            'ne': lambda a, b: torch.ne(a, b),
        }
        
        if operation_name in op_map:
            # Check if operation needs optional parameter
            if optional_param is not None and operation_name in OPERATIONS_WITH_PARAMS:
                param_info = OPERATIONS_WITH_PARAMS[operation_name]
                param_name = param_info['param_name']
                
                # Handle operations with single optional parameter
                if operation_name in ['addalpha', 'subalpha']:
                    result = op_map[operation_name](*torch_inputs, alpha=float(optional_param))
                elif operation_name in ['addcmul', 'addcdiv']:
                    result = op_map[operation_name](*torch_inputs, value=float(optional_param))
                elif operation_name == 'elu':
                    result = op_map[operation_name](*torch_inputs, alpha=float(optional_param))
                elif operation_name == 'prelu':
                    result = op_map[operation_name](*torch_inputs, weight=float(optional_param))
                elif operation_name == 'heaviside':
                    result = op_map[operation_name](*torch_inputs, value=float(optional_param))
                elif operation_name == 'threshold':
                    # Threshold has two parameters
                    value_param = float(optional_param_2) if optional_param_2 is not None else 0.0
                    result = op_map[operation_name](*torch_inputs, threshold=float(optional_param), value=value_param)
                else:
                    result = op_map[operation_name](*torch_inputs)
            else:
                result = op_map[operation_name](*torch_inputs)
            return result
        else:
            return None
            
    except Exception as e:
        print(f"Could not compute torch equivalent: {e}")
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with lockout protection"""
    ip_address = request.remote_addr
    
    if request.method == 'POST':
        # Check if IP is locked out
        locked_out, lockout_until = is_locked_out(ip_address)
        if locked_out:
            remaining_time = (lockout_until - datetime.now()).total_seconds() / 60
            return render_template('login.html', 
                error=f'Too many failed attempts. Account locked for {int(remaining_time)} more minutes.',
                lockout=True)
        
        password = request.form.get('password')
        if check_password(password):
            session.permanent = True  # Enable session timeout
            session['authenticated'] = True
            reset_attempts(ip_address)  # Clear failed attempts on success
            return redirect(url_for('index'))
        else:
            record_failed_attempt(ip_address)
            attempts_left = MAX_ATTEMPTS - login_attempts.get(ip_address, {}).get('count', 0)
            
            if attempts_left > 0:
                return render_template('login.html', 
                    error=f'Invalid password. {attempts_left} attempts remaining.',
                    attempts_left=attempts_left)
            else:
                return render_template('login.html', 
                    error=f'Too many failed attempts. Account locked for {LOCKOUT_DURATION.seconds // 60} minutes.',
                    lockout=True)
    
    # Check lockout status on GET request too
    locked_out, lockout_until = is_locked_out(ip_address)
    if locked_out:
        remaining_time = (lockout_until - datetime.now()).total_seconds() / 60
        return render_template('login.html', 
            error=f'Account locked. Please try again in {int(remaining_time)} minutes.',
            lockout=True)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Render the main page"""
    return render_template('index.html', operations=OPERATIONS)

def send_status_update(status_message):
    """Helper to send status updates (for future SSE implementation)"""
    print(f"📊 Status: {status_message}")
    # Future: Could stream to client via SSE

@app.route('/api/execute', methods=['POST'])
@login_required
def execute_operation():
    """Execute a ttnn operation and return the result (serialized access)"""
    device = None
    lock_acquired = False
    wait_start = None
    status_log = []
    
    try:
        data = request.json
        operation_name = data.get('operation')
        inputs = data.get('inputs', [])
        
        # Track queue statistics
        device_queue_stats['total_requests'] += 1
        device_queue_stats['currently_waiting'] += 1
        wait_start = datetime.now()
        
        queue_position = device_queue_stats['currently_waiting']
        status_log.append(f"⏳ In queue (position: {queue_position})")
        send_status_update(f"In queue (position: {queue_position})")
        
        # Acquire lock - only one request can use device at a time
        print(f"🔒 Request waiting for device lock... (queue: {queue_position})")
        device_lock.acquire()
        lock_acquired = True
        
        # Calculate wait time
        wait_time = (datetime.now() - wait_start).total_seconds()
        device_queue_stats['currently_waiting'] -= 1
        if wait_time > device_queue_stats['max_wait_time']:
            device_queue_stats['max_wait_time'] = wait_time
        
        print(f"✅ Lock acquired! Waited {wait_time:.3f}s")
        status_log.append(f"🔓 Lock acquired (waited {wait_time:.3f}s)")
        
        # Open device for this computation
        status_log.append("🔌 Opening device...")
        send_status_update("Opening device...")
        device = open_device_for_computation()
        status_log.append("✅ Device opened")
        
        # Prepare input tensors
        status_log.append(f"🔨 Creating {len(inputs)} tensor(s)...")
        send_status_update(f"Creating {len(inputs)} tensor(s)...")
        ttnn_inputs = []
        for inp in inputs:
            input_type = inp.get('type')  # 'tensor' or 'scalar'
            value = inp.get('value')
            dtype_str = inp.get('dtype', 'bfloat16')
            shape_str = inp.get('shape', '1,1,32,32')
            
            if input_type == 'scalar':
                # For scalar, just use the value directly
                ttnn_inputs.append(float(value))
            else:
                # For tensor, create a tensor with the value
                dtype = DTYPE_MAP.get(dtype_str, ttnn.bfloat16)
                
                # Parse shape from string (e.g., "1,1,32,32" -> [1,1,32,32])
                try:
                    shape = [int(s.strip()) for s in shape_str.split(',')]
                    if len(shape) < 2:
                        shape = [1, 1, 32, 32]  # Fallback to default
                except:
                    shape = [1, 1, 32, 32]  # Fallback on error
                
                # Create a torch tensor with the value and specified shape
                torch_tensor = torch.full(tuple(shape), float(value))
                
                # Convert to ttnn tensor and move to device
                ttnn_tensor = ttnn.from_torch(
                    torch_tensor, 
                    dtype=dtype,
                    device=device,
                    layout=ttnn.TILE_LAYOUT
                )
                ttnn_inputs.append(ttnn_tensor)
        status_log.append("✅ Tensors created")
        
        # Get the operation function
        if not hasattr(ttnn, operation_name):
            return jsonify({
                'success': False,
                'error': f'Operation "{operation_name}" not found in ttnn'
            })
        
        operation_func = getattr(ttnn, operation_name)
        
        # Check if operation has optional parameters
        optional_param = data.get('optional_param')
        optional_param_2 = data.get('optional_param_2')
        
        # Execute the operation
        status_log.append(f"⚡ Computing ttnn.{operation_name}...")
        send_status_update(f"Computing ttnn.{operation_name}...")
        if optional_param is not None and operation_name in OPERATIONS_WITH_PARAMS:
            param_info = OPERATIONS_WITH_PARAMS[operation_name]
            param_name = param_info['param_name']
            
            # Handle operations with two parameters (like threshold)
            if optional_param_2 is not None and param_info.get('has_second_param'):
                second_param_name = param_info['second_param_name']
                result = operation_func(*ttnn_inputs, **{
                    param_name: float(optional_param),
                    second_param_name: float(optional_param_2)
                })
            else:
                result = operation_func(*ttnn_inputs, **{param_name: float(optional_param)})
        else:
            result = operation_func(*ttnn_inputs)
        status_log.append("✅ TTNN computation complete")
        
        # Convert result back to torch tensor
        status_log.append("🔄 Converting to PyTorch...")
        send_status_update("Converting to PyTorch...")
        if isinstance(result, ttnn.Tensor):
            result_torch = ttnn.to_torch(result)
            status_log.append("✅ Converted to PyTorch")
            
            # Also compute using pure PyTorch for comparison
            status_log.append("🔬 Computing PyTorch equivalent...")
            send_status_update("Computing PyTorch equivalent...")
            torch_result = compute_torch_equivalent(operation_name, inputs, result_torch.dtype, optional_param, optional_param_2)
            status_log.append("✅ PyTorch computation complete")
            
            # Get statistics about the result
            status_log.append("📊 Preparing results...")
            result_data = {
                'success': True,
                'shape': list(result_torch.shape),
                'dtype': str(result_torch.dtype),
                'ttnn_dtype': str(result.dtype) if hasattr(result, 'dtype') else str(result_torch.dtype),
                'value': float(result_torch.flatten()[0].item()),  # Single value since all are same
                'sample_values': result_torch.flatten()[:10].tolist(),  # First 10 values
                'torch_value': float(torch_result.flatten()[0].item()) if torch_result is not None else None,
                'torch_dtype': str(torch_result.dtype) if torch_result is not None else None,
                'torch_shape': list(torch_result.shape) if torch_result is not None else None,
                'full_output': None,  # Could add full tensor if needed
                'status_log': status_log  # Include status log in response
            }
            status_log.append("✅ Complete!")
        else:
            # For non-tensor results
            status_log.append("✅ Complete!")
            result_data = {
                'success': True,
                'result': str(result),
                'type': str(type(result)),
                'status_log': status_log
            }
        
        send_status_update("Complete!")
        return jsonify(result_data)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ Error executing operation: {error_trace}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_trace
        })
    finally:
        # Always close device after computation, even if there was an error
        status_log.append("🔌 Closing device...")
        send_status_update("Closing device...")
        close_device_after_computation(device)
        status_log.append("✅ Device closed")
        
        # Release lock to allow next request to proceed
        if lock_acquired:
            device_lock.release()
            print("🔓 Lock released - next request can proceed")
        
        # Clean up wait counter if we failed before acquiring lock
        if wait_start and not lock_acquired:
            device_queue_stats['currently_waiting'] -= 1

@app.route('/api/operations')
@login_required
def get_operations():
    """Get list of available operations"""
    return jsonify(OPERATIONS)

@app.route('/api/operations/params')
@login_required
def get_operations_params():
    """Get operations that have optional parameters"""
    return jsonify(OPERATIONS_WITH_PARAMS)

@app.route('/api/device/queue')
@login_required
def device_queue_status():
    """Get device queue statistics"""
    return jsonify(get_queue_stats())

@app.route('/api/device/status')
@login_required
def device_status():
    """Get device status - devices are opened per computation"""
    try:
        # Try to open device to check if it's available (without blocking other requests)
        # We briefly acquire the lock to test device availability
        acquired = device_lock.acquire(blocking=False)
        if acquired:
            try:
                test_device = ttnn.open_device(device_id=0)
                ttnn.close_device(test_device)
                device_lock.release()
                return jsonify({
                    'available': True,
                    'mode': 'serialized',
                    'message': 'Device opens per computation, one request at a time',
                    'queue_stats': get_queue_stats()
                })
            except Exception as e:
                device_lock.release()
                raise
        else:
            # Lock is held, device is currently in use
            return jsonify({
                'available': True,
                'mode': 'serialized',
                'message': 'Device currently in use by another request',
                'in_use': True,
                'queue_stats': get_queue_stats()
            })
    except Exception as e:
        return jsonify({
            'available': False,
            'mode': 'serialized',
            'error': str(e)
        })

@app.route('/api/git/info')
@login_required
def git_info():
    """Get git commit information"""
    import subprocess
    try:
        # Get commit info from tt-metal repo
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%H|%h|%cr|%s'],
            cwd='/home/aswin/tt-metal',
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            parts = result.stdout.strip().split('|')
            if len(parts) >= 4:
                return jsonify({
                    'success': True,
                    'full_hash': parts[0],
                    'short_hash': parts[1],
                    'time_ago': parts[2],
                    'message': parts[3]
                })
        
        return jsonify({'success': False, 'error': 'Could not get git info'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/machine/info')
@login_required
def machine_info():
    """Get machine/device information"""
    return jsonify({
        'success': True,
        'machine_type': 'Wormhole N150',
        'device_id': 0
    })

@app.route('/api/device/reset', methods=['POST'])
@login_required
def reset_device():
    """Reset the device using tt-smi"""
    import subprocess
    try:
        # Close current device connection if open
        global device
        if device is not None:
            try:
                ttnn.close_device(device)
                device = None
            except:
                pass
        
        # Run tt-smi -r 0 to reset device
        result = subprocess.run(
            ['tt-smi', '-r', '0'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Device reset successfully',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Reset failed: {result.stderr}'
            })
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Reset command timed out'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/bug-report', methods=['POST'])
@login_required
def submit_bug_report():
    """Submit a bug report with current state via Resend API"""
    try:
        if not RESEND_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Bug report feature is not configured. Resend library not installed.'
            })
        
        if not RESEND_API_KEY:
            return jsonify({
                'success': False,
                'error': 'Bug report feature is not configured. RESEND_API_KEY environment variable not set.'
            })
        
        data = request.json
        report_data = data.get('report_data', {})
        user_description = data.get('description', 'No description provided')
        
        # Get git commit info
        try:
            git_result = subprocess.run(
                ['git', 'log', '-1', '--format=%H|%h|%cr|%s'],
                cwd='/home/aswin/tt-metal',
                capture_output=True,
                text=True,
                timeout=5
            )
            if git_result.returncode == 0:
                parts = git_result.stdout.strip().split('|')
                git_info = {
                    'commit': parts[1] if len(parts) > 1 else 'unknown',
                    'time': parts[2] if len(parts) > 2 else 'unknown',
                    'message': parts[3] if len(parts) > 3 else 'unknown'
                }
            else:
                git_info = {'commit': 'unknown', 'time': 'unknown', 'message': 'unknown'}
        except:
            git_info = {'commit': 'unknown', 'time': 'unknown', 'message': 'unknown'}
        
        # Get queue stats
        queue_stats = get_queue_stats()
        
        # Build email content
        email_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }}
                .section {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
                .label {{ font-weight: bold; color: #667eea; }}
                .code {{ background: #f0f0f0; padding: 10px; border-radius: 4px; font-family: monospace; }}
                .input-item {{ margin: 10px 0; padding: 10px; background: white; border-left: 4px solid #667eea; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🐛 Bug Report - TTNN Calculator</h2>
                <p>Received: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h3>📝 User Description</h3>
                <p>{user_description}</p>
            </div>
            
            <div class="section">
                <h3>⚙️ Operation Details</h3>
                <p><span class="label">Operation:</span> {report_data.get('operation', 'N/A')}</p>
                <p><span class="label">Number of Inputs:</span> {len(report_data.get('inputs', []))}</p>
                
                <h4>Inputs:</h4>
                {''.join([f'''
                <div class="input-item">
                    <p><span class="label">Input {i+1}:</span></p>
                    <p>Type: {inp.get('type', 'N/A')}</p>
                    <p>Value: {inp.get('value', 'N/A')}</p>
                    <p>Dtype: {inp.get('dtype', 'N/A')}</p>
                    {f"<p>Shape: {inp.get('shape', 'N/A')}</p>" if inp.get('type') == 'tensor' else ''}
                </div>
                ''' for i, inp in enumerate(report_data.get('inputs', []))])}
                
                {f"<p><span class='label'>Optional Param:</span> {report_data.get('optional_param', 'N/A')}</p>" if report_data.get('optional_param') else ''}
                {f"<p><span class='label'>Optional Param 2:</span> {report_data.get('optional_param_2', 'N/A')}</p>" if report_data.get('optional_param_2') else ''}
            </div>
            
            <div class="section">
                <h3>📊 Result Data</h3>
                {f"<p><span class='label'>Success:</span> {report_data.get('result', {}).get('success', 'N/A')}</p>" if report_data.get('result') else '<p>No result captured</p>'}
                {f"<p><span class='label'>TTNN Value:</span> {report_data.get('result', {}).get('value', 'N/A')}</p>" if report_data.get('result', {}).get('success') else ''}
                {f"<p><span class='label'>PyTorch Value:</span> {report_data.get('result', {}).get('torch_value', 'N/A')}</p>" if report_data.get('result', {}).get('success') else ''}
                {f"<p><span class='label'>Shape:</span> {report_data.get('result', {}).get('shape', 'N/A')}</p>" if report_data.get('result', {}).get('success') else ''}
                {f"<p><span class='label'>Error:</span> <code>{report_data.get('result', {}).get('error', 'N/A')}</code></p>" if report_data.get('result', {}).get('error') else ''}
            </div>
            
            <div class="section">
                <h3>🖥️ System Information</h3>
                <p><span class="label">Machine:</span> Wormhole N150</p>
                <p><span class="label">Git Commit:</span> {git_info['commit']}</p>
                <p><span class="label">Commit Time:</span> {git_info['time']}</p>
                <p><span class="label">Commit Message:</span> {git_info['message']}</p>
                <p><span class="label">Queue Stats:</span></p>
                <ul>
                    <li>Total Requests: {queue_stats['total_requests']}</li>
                    <li>Currently Waiting: {queue_stats['currently_waiting']}</li>
                    <li>Max Wait Time: {queue_stats['max_wait_time_seconds']}s</li>
                </ul>
            </div>
            
            <div class="section">
                <h3>🔍 Browser Info</h3>
                <p><span class="label">User Agent:</span> {request.headers.get('User-Agent', 'Unknown')}</p>
                <p><span class="label">IP Address:</span> {request.remote_addr}</p>
            </div>
        </body>
        </html>
        """
        
        # Send email via Resend
        resend.api_key = RESEND_API_KEY
        
        params = {
            "from": f"TTNN Bug Report <{CONTACT_EMAIL}>",
            "to": [BUG_REPORT_EMAIL],
            "subject": f"🐛 Bug Report: {report_data.get('operation', 'Unknown Operation')}",
            "html": email_html
        }
        
        email_result = resend.Emails.send(params)
        
        return jsonify({
            'success': True,
            'message': 'Bug report submitted successfully! We will review it shortly.',
            'email_id': email_result.get('id', 'unknown')
        })
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ Error sending bug report: {error_trace}")
        return jsonify({
            'success': False,
            'error': f'Failed to send bug report: {str(e)}'
        })

if __name__ == '__main__':
    print("🚀 Starting TTNN Operation Calculator...")
    print("💡 Device opens on-demand per computation (efficient resource usage)")
    print("📍 Navigate to http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
