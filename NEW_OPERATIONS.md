# New Operations Added: ttnn.mul & ttnn.divide

## ✅ Successfully Added

Two new operation aliases have been added to make the calculator more intuitive!

---

## 🆕 Added Operations

### 1. `ttnn.mul`
- **Alias for**: `ttnn.multiply`
- **Category**: Pointwise Binary
- **Description**: Element-wise multiplication
- **Inputs**: 2 tensors or tensor + scalar
- **PyTorch Equivalent**: ✅ Supported

### 2. `ttnn.divide`
- **Alias for**: `ttnn.div`
- **Category**: Pointwise Binary
- **Description**: Element-wise division
- **Inputs**: 2 tensors or tensor + scalar
- **PyTorch Equivalent**: ✅ Supported

---

## 🧪 Test Results

### Test 1: ttnn.mul
```
Operation: ttnn.mul
Input 1: 6.0
Input 2: 7.0
TTNN Result: 42
PyTorch Result: 42
Match: ✅ Yes
```

### Test 2: ttnn.divide
```
Operation: ttnn.divide
Input 1: 20.0
Input 2: 4.0
TTNN Result: 5
PyTorch Result: 5
Match: ✅ Yes
```

---

## 📝 Why These Aliases?

### Shorter & More Common
- `mul` is shorter than `multiply` (3 chars saved)
- `divide` is more intuitive than `div` (clearer intent)
- Many users search for these common names

### Better Autocomplete
Now when you type:
- **"mul"** → Shows: `mul`, `multiply`, `addcmul`, `multigammaln`
- **"div"** → Shows: `div`, `divide`, `div_no_nan`, `floor_div`, `addcdiv`

More options = easier to find what you need!

---

## 🔧 Complete Division Operations

The calculator now supports all these division variants:

1. **`ttnn.div`** - Standard division
2. **`ttnn.divide`** ⭐ NEW - Alias for div
3. **`ttnn.div_no_nan`** - Division with NaN handling
4. **`ttnn.floor_div`** - Integer division (floor)

---

## 🔢 Complete Multiplication Operations

The calculator now supports:

1. **`ttnn.mul`** ⭐ NEW - Short form
2. **`ttnn.multiply`** - Full form
3. **`ttnn.addcmul`** - Fused add + multiply
4. **`ttnn.multigammaln`** - Multivariate log-gamma

---

## 🎮 Try Them Now!

### Using ttnn.mul
1. Open: http://localhost:5000
2. Type: **"mul"**
3. Select: `ttnn.mul`
4. Input 1: 8, Input 2: 7
5. Result: **56**

### Using ttnn.divide
1. Open: http://localhost:5000
2. Type: **"divide"**
3. Select: `ttnn.divide`
4. Input 1: 100, Input 2: 4
5. Result: **25**

---

## 📊 Operation Count Update

**Before**: 152 operations
**After**: 154 operations ✨

### Breakdown:
- Pointwise Unary: 80+ operations
- Pointwise Binary: 52+ operations (was 50+)
- Pointwise Ternary: 5 operations

---

## 🎯 Autocomplete Improvements

### Searching "mul"
```
ttnn.mul (Pointwise Binary) ⭐ NEW
ttnn.multiply (Pointwise Binary)
ttnn.addcmul (Pointwise Ternary)
ttnn.multigammaln (Pointwise Unary)
```

### Searching "div"
```
ttnn.div (Pointwise Binary)
ttnn.divide (Pointwise Binary) ⭐ NEW
ttnn.div_no_nan (Pointwise Binary)
ttnn.floor_div (Pointwise Binary)
ttnn.addcdiv (Pointwise Ternary)
```

---

## ✅ Features

Both new operations support:
- ✅ Tensor × Tensor
- ✅ Tensor × Scalar
- ✅ Multiple data types (bfloat16, float32, int32, uint32)
- ✅ PyTorch comparison
- ✅ Clean number formatting
- ✅ Autocomplete search

---

## 🚀 Ready to Use!

The operations are **live** and available now at:
**http://localhost:5000**

Start typing "mul" or "divide" to see them in action! 🎉
