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
from datetime import timedelta

app = Flask(__name__)
# Generate a secure secret key for sessions
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))
# Session timeout: 30 minutes of inactivity
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

# Securely hash the password (SHA256)
# The actual password is not stored anywhere in the code
PASSWORD_HASH = "fb4d52ec15fde028f3574bfb1a313020e1d5127851353194e84978f788ada6b3"

def check_password(password):
    """Check if provided password matches the hash"""
    return hashlib.sha256(password.encode()).hexdigest() == PASSWORD_HASH

def login_required(f):
    """Decorator to protect routes with password"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Global device handle
device = None

def initialize_device():
    """Initialize ttnn device if not already initialized"""
    global device
    if device is None:
        try:
            device = ttnn.open_device(device_id=0)
            print(f"✅ Device initialized: {device}")
        except Exception as e:
            print(f"❌ Failed to initialize device: {e}")
            raise
    return device

def cleanup_device():
    """Cleanup device resources"""
    global device
    if device is not None:
        try:
            ttnn.close_device(device)
            device = None
            print("✅ Device closed")
        except Exception as e:
            print(f"❌ Failed to close device: {e}")

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
    """Login page"""
    if request.method == 'POST':
        password = request.form.get('password')
        if check_password(password):
            session.permanent = True  # Enable session timeout
            session['authenticated'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid password')
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

@app.route('/api/execute', methods=['POST'])
@login_required
def execute_operation():
    """Execute a ttnn operation and return the result"""
    try:
        data = request.json
        operation_name = data.get('operation')
        inputs = data.get('inputs', [])
        
        # Initialize device
        dev = initialize_device()
        
        # Prepare input tensors
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
                    device=dev,
                    layout=ttnn.TILE_LAYOUT
                )
                ttnn_inputs.append(ttnn_tensor)
        
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
        
        # Convert result back to torch tensor
        if isinstance(result, ttnn.Tensor):
            result_torch = ttnn.to_torch(result)
            
            # Also compute using pure PyTorch for comparison
            torch_result = compute_torch_equivalent(operation_name, inputs, result_torch.dtype, optional_param, optional_param_2)
            
            # Get statistics about the result
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
                'full_output': None  # Could add full tensor if needed
            }
        else:
            # For non-tensor results
            result_data = {
                'success': True,
                'result': str(result),
                'type': str(type(result))
            }
        
        return jsonify(result_data)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ Error executing operation: {error_trace}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_trace
        })

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

@app.route('/api/device/status')
@login_required
def device_status():
    """Get device status"""
    global device
    return jsonify({
        'initialized': device is not None,
        'device': str(device) if device else None
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

if __name__ == '__main__':
    try:
        print("🚀 Starting TTNN Operation Calculator...")
        print("📍 Navigate to http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        cleanup_device()
