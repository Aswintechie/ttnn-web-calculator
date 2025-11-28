# On-Demand Device Management

## Overview
The TTNN Web Calculator uses an **on-demand device management** strategy where the device is opened only during computation and closed immediately after, ensuring efficient resource usage.

## Architecture

### Before (Persistent Device) ❌
```python
# Device opened once at startup
device = ttnn.open_device(device_id=0)

# Device stays open for entire app lifetime
# ... hours/days later ...

# Device closed only on shutdown
ttnn.close_device(device)
```

**Problems:**
- 🔴 Device locked even when idle
- 🔴 Memory accumulation over time
- 🔴 Other processes can't use device
- 🔴 Resource waste during idle periods
- 🔴 Stale state between operations

### After (On-Demand) ✅
```python
# Per-request lifecycle
def execute_operation():
    device = None
    try:
        # 1. Open device
        device = open_device_for_computation()
        
        # 2. Perform computation
        result = ttnn.add(tensor1, tensor2)
        
        # 3. Return result
        return result
    finally:
        # 4. Always close device
        close_device_after_computation(device)
```

**Benefits:**
- ✅ Device open only when needed
- ✅ Automatic cleanup guaranteed
- ✅ No idle resource consumption
- ✅ Device available for other processes
- ✅ Fresh state every computation

## Implementation Details

### Core Functions

#### `open_device_for_computation()`
Opens the device for a single computation.

```python
def open_device_for_computation():
    """Open device for a single computation"""
    try:
        device = ttnn.open_device(device_id=0)
        print(f"✅ Device opened for computation: {device}")
        return device
    except Exception as e:
        print(f"❌ Failed to open device: {e}")
        raise
```

**When called:** Start of every `/api/execute` request  
**Returns:** Device handle for immediate use  
**Time:** ~50-100ms typical

#### `close_device_after_computation(device)`
Closes the device after computation completes.

```python
def close_device_after_computation(device):
    """Close device after computation is complete"""
    if device is not None:
        try:
            ttnn.close_device(device)
            print("✅ Device closed after computation")
        except Exception as e:
            print(f"❌ Failed to close device: {e}")
```

**When called:** End of every `/api/execute` request (in `finally` block)  
**Guarantees:** Device always closes, even on errors  
**Time:** ~50-100ms typical

### Request Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    HTTP Request Arrives                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  execute_operation() starts                                 │
│  device = None                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  TRY BLOCK                                                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │  1. device = open_device_for_computation()         │    │
│  │     [Device opens - ~50-100ms]                     │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                 │
│                           ▼                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │  2. Create tensors and move to device              │    │
│  │     ttnn.from_torch(..., device=device)            │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                 │
│                           ▼                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │  3. Execute operation                              │    │
│  │     result = ttnn.add(tensor1, tensor2)            │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                 │
│                           ▼                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │  4. Convert result back to PyTorch                 │    │
│  │     result_torch = ttnn.to_torch(result)           │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                 │
│                           ▼                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │  5. Return JSON response                           │    │
│  │     return jsonify(result_data)                    │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  FINALLY BLOCK (always executes)                           │
│  ┌────────────────────────────────────────────────────┐    │
│  │  close_device_after_computation(device)            │    │
│  │  [Device closes - ~50-100ms]                       │    │
│  │  ✅ Guaranteed cleanup even if errors occurred     │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Device is now free for other use               │
└─────────────────────────────────────────────────────────────┘
```

### Timeline Example

```
Time    Event                          Device State
------  ---------------------------    -------------
0.0s    Request arrives                CLOSED
0.0s    execute_operation() called     CLOSED
0.05s   open_device_for_computation()  OPENING...
0.15s   Device opened                  OPEN ✅
0.16s   Create tensors                 OPEN (working)
0.20s   Execute ttnn.add()             OPEN (computing)
0.25s   Convert result                 OPEN (converting)
0.26s   Prepare JSON response          OPEN (idle)
0.26s   Enter finally block            OPEN
0.28s   close_device()                 CLOSING...
0.38s   Device closed                  CLOSED ✅
0.38s   Return response                CLOSED

Total operation time: ~380ms
Device open time: ~230ms (only when needed!)
Idle time: Device available for others
```

## Resource Comparison

### Persistent Device (Old)
```
App Lifetime: 24 hours
Device Open: 24 hours (86,400 seconds)
Actual Compute: 100 operations × 0.1s = 10 seconds
Idle Time: 86,390 seconds (99.98% wasted!)
Resource Efficiency: 0.01%
```

### On-Demand Device (New)
```
App Lifetime: 24 hours
Device Open: 100 operations × 0.2s = 20 seconds
Actual Compute: 100 operations × 0.1s = 10 seconds
Idle Time: 0 seconds (device closed!)
Resource Efficiency: 50% (overhead vs compute)
```

**Improvement:** From 0.01% to 50% efficiency = **5,000x better!**

## Performance Impact

### Overhead Per Operation
- Device open: ~50-100ms
- Device close: ~50-100ms
- Total overhead: ~100-200ms per operation

### When This Is Good (Most Web Scenarios)
✅ **Sporadic requests** (seconds/minutes between operations)
- User thinking time: 5-30 seconds
- Overhead: 200ms
- Impact: Negligible (~1% of user time)

✅ **Low frequency** (few operations per minute)
- Overhead per operation: 200ms
- Frequency: 1-10 ops/minute
- Device availability: 99%+ for other processes

✅ **Multiple users/processes sharing device**
- Device released after each operation
- Fair sharing between processes
- No blocking or waiting

### When This Might Be Slow (Not Web Scenarios)
❌ **Batch processing** (thousands of operations)
- 10,000 operations × 200ms overhead = 2,000 seconds wasted
- Better: Keep device open for batch duration

❌ **Real-time streaming** (sub-second latency requirements)
- 200ms overhead unacceptable for <100ms latency targets
- Better: Persistent device with dedicated process

❌ **Single-user, single-process, continuous use**
- If only one user constantly using the app
- Better: Persistent device might be simpler

**Verdict:** For web calculator use case, on-demand is clearly better! ✅

## Error Handling

### Automatic Cleanup on Errors

```python
device = None
try:
    device = open_device_for_computation()
    
    # If ANY of these fail:
    tensor = ttnn.from_torch(...)      # ❌ Error here
    result = ttnn.add(...)              # Or here
    torch_result = ttnn.to_torch(...)   # Or here
    
    return jsonify(...)
    
except Exception as e:
    # Error logged, response returned
    return jsonify({'error': str(e)})
    
finally:
    # ✅ Device STILL gets closed!
    close_device_after_computation(device)
```

### Benefits of `finally` Block
1. **Guaranteed Cleanup**: Device closes even if computation fails
2. **No Leaks**: Can't forget to close device
3. **Exception Safety**: Errors don't leave device hanging
4. **Clean State**: Next operation starts fresh

## Device Status API

The `/api/device/status` endpoint now reflects on-demand behavior:

```python
@app.route('/api/device/status')
def device_status():
    """Check if device is available (without keeping it open)"""
    try:
        # Quick test: open and immediately close
        test_device = ttnn.open_device(device_id=0)
        ttnn.close_device(test_device)
        
        return jsonify({
            'available': True,
            'mode': 'on-demand',
            'message': 'Device opens for each computation and closes after'
        })
    except Exception as e:
        return jsonify({
            'available': False,
            'mode': 'on-demand',
            'error': str(e)
        })
```

**Response:**
```json
{
    "available": true,
    "mode": "on-demand",
    "message": "Device opens for each computation and closes after"
}
```

## Best Practices

### ✅ DO

1. **Let the framework manage device lifecycle**
   - Don't try to optimize by keeping device open
   - Trust the on-demand pattern for web workloads

2. **Report errors to users**
   - Device open failures are caught and reported
   - Users get clear error messages

3. **Use the API as designed**
   - Each operation is independent
   - No need to "warm up" or "prepare" device

### ❌ DON'T

1. **Don't try to cache the device**
   - Defeats the purpose of on-demand management
   - Causes resource leaks

2. **Don't manually open/close device**
   - The framework handles this automatically
   - Manual intervention can cause double-close errors

3. **Don't worry about overhead**
   - 200ms is negligible in web context
   - User think time >> device overhead

## Monitoring & Debugging

### Log Messages

**Successful Operation:**
```
✅ Device opened for computation: <Device object>
✅ Device closed after computation
```

**Device Open Failure:**
```
❌ Failed to open device: [error details]
```

**Device Close Failure (rare):**
```
❌ Failed to close device: [error details]
```

### What to Monitor

1. **Device open failures**
   - Indicates hardware/driver issues
   - Check device availability

2. **Frequent close failures**
   - Could indicate driver bugs
   - May need system reboot

3. **Slow open times (>500ms)**
   - Device might be warming up from cold state
   - Could indicate hardware issues

### Troubleshooting

**Problem:** "Device already in use" errors

**Solution:**
- This should not happen with on-demand management
- If it does, check for leaked device handles
- Kill other processes holding device

**Problem:** Operations very slow

**Check:**
```bash
# See if device is healthy
tt-smi

# Reset device if needed
tt-smi -r 0
```

## Migration Notes

If upgrading from persistent device version:

### What Changed
- Global `device` variable removed
- `initialize_device()` → `open_device_for_computation()`
- `cleanup_device()` → `close_device_after_computation()`
- No startup/shutdown device management needed

### What Stayed Same
- API endpoints unchanged
- Request/response format unchanged
- Frontend unchanged
- Operation semantics unchanged

### Breaking Changes
None! This is purely an internal optimization.

## Future Enhancements

Potential improvements:

### Device Pool (for high throughput)
```python
# For high-frequency workloads
device_pool = [ttnn.open_device(i) for i in range(4)]

def get_device():
    return device_pool[current_request_id % len(device_pool)]
```

### Lazy Close (delay closing)
```python
# Close device after 5 seconds of inactivity
@app.after_request
def schedule_device_close(response):
    schedule_after(5, close_device_after_computation)
    return response
```

### Smart Caching (for burst traffic)
```python
# Keep device open if requests are frequent
if requests_in_last_minute > 10:
    keep_device_open = True
```

**Note:** Current on-demand approach is simpler and sufficient for typical web workloads.

## Summary

### Before ❌
- Device always open
- Resource waste during idle
- 0.01% efficiency
- Device blocking other processes

### After ✅
- Device opens per-computation
- No idle resource consumption
- 50% efficiency (5,000x improvement!)
- Device available when not in use

### Key Metrics
- Overhead per operation: ~200ms
- User think time: 5-30 seconds
- Impact: <1% of user time
- Resource savings: 99.98%

### Conclusion
**On-demand device management is the right choice for web applications!**

🚀 Efficient • 🔒 Safe • ♻️ Resource-friendly • ⚡ Fast enough

