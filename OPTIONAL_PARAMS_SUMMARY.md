# Optional Parameters Feature - Summary

## Overview
Extended the TTNN Web Calculator to support operations with optional scalar parameters. The system now supports 8 operations with configurable parameters.

## Supported Operations with Optional Parameters

### Binary Operations (2 inputs + 1 parameter)

1. **addalpha(input, other, alpha=1.0)**
   - Formula: `input + alpha * other`
   - Parameter: `alpha` (scalar multiplier for second input)
   - Default: 1.0
   - Example: `addalpha(1, 2, alpha=3) = 1 + 3*2 = 7`

2. **subalpha(input, other, alpha=1.0)**
   - Formula: `input - alpha * other`
   - Parameter: `alpha` (scalar multiplier for second input)
   - Default: 1.0
   - Example: `subalpha(10, 2, alpha=3) = 10 - 3*2 = 4`

### Ternary Operations (3 inputs + 1 parameter)

3. **addcmul(input, tensor1, tensor2, value=1.0)**
   - Formula: `input + value * (tensor1 * tensor2)`
   - Parameter: `value` (scalar multiplier for product)
   - Default: 1.0
   - Example: `addcmul(1, 2, 3, value=5) = 1 + 5*(2*3) = 31`

4. **addcdiv(input, tensor1, tensor2, value=1.0)**
   - Formula: `input + value * (tensor1 / tensor2)`
   - Parameter: `value` (scalar multiplier for division)
   - Default: 1.0
   - Example: `addcdiv(10, 6, 2, value=2) = 10 + 2*(6/2) = 16`

### Unary Operations (1 input + 1 parameter)

5. **elu(input, alpha=1.0)**
   - Formula: `x if x > 0 else alpha * (exp(x) - 1)`
   - Parameter: `alpha` (alpha value for ELU activation)
   - Default: 1.0
   - Example: `elu(-1, alpha=2) ≈ -1.265625`

6. **prelu(input, weight=0.25)**
   - Formula: `x if x >= 0 else weight * x`
   - Parameter: `weight` (negative slope coefficient)
   - Default: 0.25
   - Example: `prelu(-2, weight=0.5) = -1.0`

7. **heaviside(input, value=0.0)**
   - Formula: `0 if x < 0, value if x == 0, 1 if x > 0`
   - Parameter: `value` (value when input is zero)
   - Default: 0.0
   - Example: `heaviside(0, value=0.5) = 0.5`

### Unary Operations (1 input + 2 parameters)

8. **threshold(input, threshold=0.0, value=0.0)**
   - Formula: `x if x > threshold else value`
   - Parameters:
     - `threshold` (threshold value)
     - `value` (replacement value)
   - Defaults: 0.0, 0.0
   - Example: `threshold(0.5, threshold=1.0, value=99.0) = 99.0`

## Implementation Details

### Backend Changes (app.py)

1. **OPERATIONS_WITH_PARAMS Dictionary**
   - Maps operation names to their parameter metadata
   - Includes parameter name, default value, and description
   - Supports operations with two parameters (threshold)

2. **New API Endpoint**
   - `/api/operations/params` - Returns metadata about operations with optional parameters

3. **Updated execute_operation Function**
   - Accepts `optional_param` and `optional_param_2` from request
   - Passes parameters to TTNN operations using keyword arguments
   - Handles both single and dual-parameter operations

4. **Updated compute_torch_equivalent Function**
   - Accepts optional parameters
   - Maps TTNN operation parameters to PyTorch equivalents
   - Ensures accurate comparison between TTNN and PyTorch results

### Frontend Changes (index.html)

1. **Dynamic Parameter Fields**
   - Automatically displays parameter input fields when an operation with optional parameters is selected
   - Shows parameter name, description, and default value
   - Supports two parameter fields for operations like threshold
   - Fields have a distinctive yellow background to distinguish from regular inputs

2. **Parameter Loading**
   - Fetches parameter metadata from `/api/operations/params` on page load
   - Stores in `OPERATIONS_WITH_PARAMS` JavaScript object

3. **Calculate Function Updates**
   - Collects values from `optional-param` and `optional-param-2` input fields
   - Includes them in the API request to `/api/execute`

## Testing

All 8 operations have been tested with:
- ✅ TTNN execution
- ✅ PyTorch equivalent calculation
- ✅ Result comparison (TTNN vs PyTorch)
- ✅ Expected value validation

Test results: **8/8 passed** (100% success rate)

## Usage Example

### Via Web Interface:
1. Select an operation (e.g., "addcmul")
2. Fill in the required tensor/scalar inputs
3. Adjust the optional parameter (e.g., change "value" from 1.0 to 5.0)
4. Click "Calculate"
5. View both TTNN and PyTorch results with parameter values displayed

### Via API:
```python
import requests

response = requests.post('http://localhost:5000/api/execute', json={
    "operation": "addcmul",
    "inputs": [
        {"type": "tensor", "value": 1, "dtype": "bfloat16", "shape": "1,1,32,32"},
        {"type": "tensor", "value": 2, "dtype": "bfloat16", "shape": "1,1,32,32"},
        {"type": "tensor", "value": 3, "dtype": "bfloat16", "shape": "1,1,32,32"}
    ],
    "optional_param": 5.0  # Custom value parameter
})

data = response.json()
print(f"TTNN Result: {data['value']}")      # 31.0
print(f"PyTorch Result: {data['torch_value']}")  # 31.0
```

## Future Enhancements

Potential additions:
- Support for more operations with optional parameters (e.g., softplus with beta parameter)
- Validation of parameter ranges (e.g., weight in [0, 1] for lerp)
- Presets for common parameter values
- Parameter tooltips with mathematical formulas
- Visual parameter sliders for real-time updates

