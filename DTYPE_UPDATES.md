# Data Type Updates - Smart Dtype Selection

## ✨ New Features

### 1. Dynamic Dtype Options
The dtype dropdown now **changes based on input type**!

#### When "Tensor" is selected:
Shows all TTNN data types:
- `bfloat16` - Brain floating point 16-bit
- `float32` - Standard 32-bit float
- `bfloat8_b` - Brain floating point 8-bit
- `bfloat4_b` - Brain floating point 4-bit
- `uint8` - Unsigned 8-bit integer
- `uint16` - Unsigned 16-bit integer
- `int32` - Signed 32-bit integer
- `uint32` - Unsigned 32-bit integer

#### When "Scalar" is selected:
Shows simplified scalar types:
- `float` - Floating point number
- `int` - Integer number

---

## 🎯 Why This Update?

### Before:
- Same dtype options for both tensors and scalars
- Confusing for users (scalars don't need bfloat16)
- Too many options when using scalars

### After:
✅ **Context-aware** dtype selection
✅ **Simpler** options for scalars (float or int)
✅ **Complete** options for tensors (8 types)
✅ **Dynamic** - changes automatically when you switch type

---

## 📊 Supported Data Types

### TTNN Tensor Types

| Type | Bits | Description | Use Case |
|------|------|-------------|----------|
| `bfloat16` | 16 | Brain float | Default, good balance |
| `float32` | 32 | Full precision | High accuracy needed |
| `bfloat8_b` | 8 | Compressed float | Memory saving |
| `bfloat4_b` | 4 | Ultra compressed | Extreme compression |
| `uint8` | 8 | Unsigned int | Small positive integers |
| `uint16` | 16 | Unsigned int | Larger positive integers |
| `int32` | 32 | Signed int | Full integer range |
| `uint32` | 32 | Unsigned int | Large positive integers |

### Scalar Types

| Type | Description |
|------|-------------|
| `float` | Maps to float32 |
| `int` | Maps to int32 |

---

## 🎮 How to Use

### Example 1: Tensor with bfloat16
1. Select operation: `ttnn.add`
2. Input 1:
   - Type: **Tensor**
   - Value: 5.0
   - Dtype: **bfloat16** (shows in dropdown)
3. Input 2:
   - Type: **Tensor**
   - Value: 3.0
   - Dtype: **bfloat16**

### Example 2: Scalar with simple types
1. Select operation: `ttnn.add`
2. Input 1:
   - Type: **Tensor**
   - Value: 10.0
   - Dtype: **float32** (8 options available)
3. Input 2:
   - Type: **Scalar** ⭐
   - Value: 5.0
   - Dtype: **float** (only 2 simple options: float or int)

### Example 3: Using uint8 for small integers
1. Select operation: `ttnn.add`
2. Input 1:
   - Type: **Tensor**
   - Value: 100
   - Dtype: **uint8** (perfect for 0-255 range)
3. Input 2:
   - Type: **Tensor**
   - Value: 50
   - Dtype: **uint8**

---

## 🔄 Dynamic Behavior

### Switching Type Changes Dtype Options

**Start with Tensor:**
```
Type: Tensor
Dtype options: [bfloat16, float32, bfloat8_b, bfloat4_b, uint8, uint16, int32, uint32]
```

**Switch to Scalar:**
```
Type: Scalar ← Changed!
Dtype options: [float, int] ← Auto-updated!
```

**Switch back to Tensor:**
```
Type: Tensor ← Changed back!
Dtype options: [bfloat16, float32, ...] ← Restored!
```

---

## 💡 Tips

### Choosing Data Types

**For Tensors:**
- **Default**: Use `bfloat16` (good performance)
- **High precision**: Use `float32`
- **Memory constrained**: Use `bfloat8_b` or `bfloat4_b`
- **Integer data**: Use `int32`, `uint8`, `uint16`, `uint32`

**For Scalars:**
- **Decimal values**: Use `float`
- **Whole numbers**: Use `int`

### When to Use Each Type

**bfloat16**: Most operations, default choice
**float32**: Need full precision (scientific computing)
**bfloat8_b/bfloat4_b**: Experimental, compressed models
**uint8**: Images, small positive numbers (0-255)
**uint16**: Larger positive numbers (0-65535)
**int32**: General integers with negatives
**uint32**: Large positive numbers

---

## 🧪 Testing Different Types

Try these combinations:

### Test 1: bfloat16 (default)
```
Operation: ttnn.add
Input 1: Tensor, 5.0, bfloat16
Input 2: Tensor, 3.0, bfloat16
Result: 8
```

### Test 2: float32 (high precision)
```
Operation: ttnn.mul
Input 1: Tensor, 3.14159, float32
Input 2: Tensor, 2.0, float32
Result: 6.28318
```

### Test 3: uint8 (small integers)
```
Operation: ttnn.add
Input 1: Tensor, 100, uint8
Input 2: Tensor, 50, uint8
Result: 150
```

### Test 4: Mixed (tensor + scalar)
```
Operation: ttnn.multiply
Input 1: Tensor, 10.0, bfloat16
Input 2: Scalar, 2.5, float
Result: 25
```

---

## 📋 Complete Type List

### In Backend (app.py)
```python
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
```

### In Frontend (dynamic)
**Tensor mode**: All 8 types
**Scalar mode**: float, int (2 types)

---

## 🚀 Try It Now!

**URL**: http://localhost:5000

1. Select any operation
2. Choose **Scalar** as input type
3. Watch dtype dropdown change to show only `float` and `int`
4. Switch back to **Tensor**
5. See all 8 TTNN types appear!

---

## ✅ Summary

✨ **8 TTNN data types** now supported
✨ **Dynamic dtype options** based on input type
✨ **Simplified scalar types** (float, int)
✨ **Complete tensor types** (8 options)
✨ **Better UX** - context-aware interface

The calculator is now more intuitive and supports all major TTNN data types! 🎉
