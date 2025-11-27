# TTNN Web Calculator - Demo Guide

## 🎉 Quick Start

The TTNN Web Calculator is now **running** at: **http://localhost:5000**

### What You Can Do

1. **Open Your Browser**: Navigate to `http://localhost:5000`
2. **Select an Operation**: Choose from 150+ ttnn operations organized by category
3. **Configure Inputs**: Set values, types (tensor/scalar), and data types
4. **Get Instant Results**: View comprehensive statistics and output

---

## 📊 Test Results

All operations tested successfully! ✅

### Test 1: Binary Addition (ttnn.add)
- **Input 1**: Tensor with value 5.0 (bfloat16)
- **Input 2**: Tensor with value 3.0 (bfloat16)
- **Result**: 8.0 ✅
- **Shape**: [2, 2, 32, 32]

### Test 2: Binary Multiplication (ttnn.multiply)
- **Input 1**: Tensor with value 4.0 (bfloat16)
- **Input 2**: Tensor with value 2.5 (bfloat16)
- **Result**: 10.0 ✅
- **Shape**: [2, 2, 32, 32]

### Test 3: Unary Operation (ttnn.sqrt)
- **Input**: Tensor with value 16.0 (bfloat16)
- **Result**: 4.0 ✅
- **Shape**: [2, 2, 32, 32]

### Test 4: Ternary Operation (ttnn.where)
- **Input 1**: Tensor with value 1.0 (bfloat16) - condition
- **Input 2**: Tensor with value 5.0 (bfloat16) - true value
- **Input 3**: Tensor with value 3.0 (bfloat16) - false value
- **Result**: 5.0 ✅
- **Shape**: [2, 2, 32, 32]

---

## 🎨 UI Features

### Modern Design
- 🎨 Gradient background with purple theme
- 📱 Responsive layout
- ✨ Smooth animations and transitions
- 🔄 Real-time loading indicators

### Operation Categories
1. **Pointwise Unary** (80+ ops): abs, sin, cos, exp, log, relu, gelu, etc.
2. **Pointwise Binary** (50+ ops): add, multiply, subtract, div, pow, etc.
3. **Pointwise Ternary** (5 ops): where, lerp, addcmul, etc.

### Input Configuration
- **Type Selection**: Choose Tensor or Scalar
- **Value Input**: Set custom numeric values
- **Data Type**: Select from bfloat16, float32, int32, uint32

### Result Display
- Shape information
- Data type
- Min/Max/Mean statistics
- Sample values (first 10 elements)
- Error messages with stack traces for debugging

---

## 🚀 Usage Examples

### Example 1: Test ReLU Activation
1. Select: `ttnn.relu`
2. Input 1: Type=Tensor, Value=-5.0, dtype=bfloat16
3. Click "Calculate Result"
4. Expected: All values should be 0.0 (ReLU clips negative values)

### Example 2: Test Division
1. Select: `ttnn.div`
2. Input 1: Type=Tensor, Value=10.0, dtype=bfloat16
3. Input 2: Type=Tensor, Value=2.0, dtype=bfloat16
4. Click "Calculate Result"
5. Expected: All values should be 5.0

### Example 3: Test Exponential
1. Select: `ttnn.exp`
2. Input 1: Type=Tensor, Value=2.0, dtype=bfloat16
3. Click "Calculate Result"
4. Expected: All values should be ~7.389 (e^2)

---

## 🔧 Technical Details

### Backend (Flask + ttnn)
- Automatic device initialization on first request
- Efficient tensor creation with tile-aligned shapes
- Proper memory management with device cleanup
- Comprehensive error handling with stack traces

### Frontend (HTML/CSS/JavaScript)
- Pure vanilla JavaScript (no frameworks needed)
- Asynchronous API calls with fetch
- Dynamic input generation based on operation type
- Real-time result visualization

### Tensor Configuration
- Default shape: (2, 2, 32, 32) - optimized for tile layout
- Layout: TILE_LAYOUT for device compatibility
- Device placement: Automatic transfer to device

---

## 📁 Project Structure

```
ttnn-web-calculator/
├── app.py                 # Flask backend with ttnn integration
├── templates/
│   └── index.html        # Frontend UI (HTML + CSS + JS)
├── static/               # Static assets directory
├── requirements.txt      # Python dependencies
├── start.sh             # Quick start script
├── README.md            # Full documentation
└── DEMO.md              # This demo guide
```

---

## 🎯 Next Steps

### To Stop the Server
Press `Ctrl+C` in the terminal where Flask is running

### To Restart
```bash
cd /home/aswin/ttnn-web-calculator
./start.sh
```

### To Extend
- Add more operation categories (Convolution, Pooling, etc.)
- Support custom tensor shapes
- Add visualization graphs
- Export results to CSV/JSON
- Add operation performance metrics

---

## 🐛 Troubleshooting

### Server Not Starting
```bash
# Check if port 5000 is already in use
lsof -i :5000

# Kill existing process if needed
kill -9 <PID>

# Restart
./start.sh
```

### Device Initialization Issues
- Ensure ttnn device is available
- Check device drivers are loaded
- Verify Python environment is activated

### Import Errors
```bash
# Reinstall dependencies
cd /home/aswin/tt-metal
source python_env/bin/activate
cd /home/aswin/ttnn-web-calculator
pip install -r requirements.txt
```

---

## 📞 Support

For issues or feature requests:
1. Check the README.md for detailed documentation
2. Review error messages in the web interface
3. Check Flask server logs in the terminal

Enjoy testing ttnn operations! 🎉
