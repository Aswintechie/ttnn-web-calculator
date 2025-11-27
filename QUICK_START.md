# 🚀 TTNN Web Calculator - Quick Start Guide

## Current Status: ✅ RUNNING

**Server URL**: http://localhost:5000

---

## 🎯 Latest Features

### 1. **Smart Autocomplete Search** (NEW! 🆕)
- Type operation names to filter instantly
- Keyboard navigation with arrow keys
- Highlighted matching text
- Category labels for each operation

### 2. **Clean Number Display**
- Integer values: `15` (not `15.000000`)
- Zero values: `0` (not `0.000000`)
- Decimals: `1.414063` (trailing zeros removed)

### 3. **PyTorch Comparison**
- Side-by-side TTNN vs PyTorch results
- Match indicator (✅ or ⚠️)
- Instant verification

---

## 📖 How to Use

### Step 1: Type Operation Name
In the search box, start typing:
- `add` → Shows addition operations
- `relu` → Shows ReLU activation
- `sqrt` → Shows square root operations

### Step 2: Select Operation
Either:
- **Click** on an operation from the list
- Use **↓/↑ arrows** + **Enter** to select
- Type exact name + **Enter**

### Step 3: Configure Inputs
For each input:
- **Type**: Tensor or Scalar
- **Value**: The number value
- **Data Type**: bfloat16, float32, etc.

### Step 4: Calculate
Click "Calculate Result" button

### Step 5: View Results
See:
- **TTNN Result**: Value from ttnn
- **PyTorch Result**: Value from PyTorch
- **Match**: ✅ if they agree

---

## 🎮 Try These Examples

### Example 1: Simple Addition
1. Type: `add`
2. Select: `ttnn.add`
3. Input 1: Tensor, 10.0, bfloat16
4. Input 2: Tensor, 5.0, bfloat16
5. Click Calculate
6. Result: **15** (both TTNN and PyTorch)

### Example 2: ReLU Activation
1. Type: `relu`
2. Select: `ttnn.relu`
3. Input 1: Tensor, -5.0, bfloat16
4. Click Calculate
5. Result: **0** (negative values clipped)

### Example 3: Square Root
1. Type: `sqrt`
2. Select: `ttnn.sqrt`
3. Input 1: Tensor, 25.0, bfloat16
4. Click Calculate
5. Result: **5** (perfect square)

### Example 4: Multiplication
1. Type: `mul`
2. Select: `ttnn.multiply`
3. Input 1: Tensor, 7.0, bfloat16
4. Input 2: Tensor, 8.0, bfloat16
5. Click Calculate
6. Result: **56**

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Type in search | Filter operations |
| ↓ | Move down in list |
| ↑ | Move up in list |
| Enter | Select operation |
| Esc | Close dropdown |
| Tab | Next field |

---

## 🎨 UI Features

### Search Box
- Placeholder: "Type to search..."
- Real-time filtering
- Shows up to 10 results
- Matches anywhere in name

### Results Display
- Purple border: TTNN result
- Green border: PyTorch result
- Color-coded match indicator

### Operation Labels
- Shows operation category
- Example: `ttnn.add (Pointwise Binary)`

---

## 📊 Supported Operations

- **80+** Pointwise Unary operations
- **50+** Pointwise Binary operations
- **5** Pointwise Ternary operations
- **150+ total** operations available

### Popular Operations
- **Arithmetic**: add, subtract, multiply, div, pow
- **Activations**: relu, sigmoid, tanh, gelu, silu
- **Math**: sqrt, exp, log, sin, cos, abs
- **Comparison**: gt, lt, eq, ne, maximum, minimum

---

## 🔧 Server Management

### Check Status
```bash
curl http://localhost:5000/api/device/status
```

### Restart Server
```bash
pkill -f "python app.py"
cd /home/aswin/ttnn-web-calculator
./start.sh
```

### View Logs
```bash
tail -f /tmp/ttnn-server.log
```

---

## 📁 Project Files

```
/home/aswin/ttnn-web-calculator/
├── app.py                      # Flask backend
├── templates/index.html        # Frontend with autocomplete
├── start.sh                   # Quick start script
├── README.md                  # Full documentation
├── AUTOCOMPLETE_FEATURE.md    # Autocomplete docs
├── FORMAT_EXAMPLES.md         # Number formatting
└── QUICK_START.md            # This file!
```

---

## 💡 Tips & Tricks

### Fast Operation Selection
- Type first few letters: `add`, `mul`, `sq`
- Press Enter immediately if exact match
- Use arrows for similar operations

### Testing Multiple Operations
- Change operation in search box
- Inputs auto-update based on operation type
- Values persist between operations

### Understanding Results
- If TTNN ≠ PyTorch: Check input types
- Match indicator shows ✅ for agreement
- Values displayed with minimal decimals

---

## 🎉 Ready to Go!

**Open your browser**: http://localhost:5000

Start typing operation names and see the magic happen! ✨

The autocomplete makes finding operations **10x faster** than scrolling through dropdowns.

Happy computing! 🚀
