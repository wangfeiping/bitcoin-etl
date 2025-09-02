# Changes Summary for Rate Limiting Feature

## Overview
Added a new `--request-per-second` parameter to the Bitcoin ETL stream command to control RPC request frequency.

## Files Modified

### 1. `bitcoinetl/rpc/request.py`
- Added `RateLimiter` class for controlling request frequency
- Added `make_post_request_with_rate_limit` function
- Implemented thread-safe rate limiting with precise timing control

### 2. `bitcoinetl/rpc/bitcoin_rpc.py`
- Modified `BitcoinRpc.__init__` to accept optional `rate_limiter` parameter
- Updated `batch` method to use rate-limited requests when rate_limiter is provided
- Maintains backward compatibility (rate_limiter defaults to None)

### 3. `bitcoinetl/cli/stream.py`
- Added `--request-per-second` command line option
- Integrated rate limiter creation and passing to BitcoinRpc
- Parameter type: float, default: 0 (no limit)

## New Features

### Rate Limiter Class
- **Thread-safe**: Uses locks to ensure thread safety across multiple workers
- **Precise timing**: High-precision timing for accurate request intervals
- **Configurable**: Supports fractional requests per second (e.g., 2.5 req/sec)
- **Efficient**: Minimal overhead when enabled, zero overhead when disabled

### Command Line Interface
- **New parameter**: `--request-per-second <float>`
- **Default behavior**: No rate limiting (same as before)
- **Flexible values**: Supports any positive float value
- **Help text**: Clear description of parameter usage

## Usage Examples

```bash
# Limit to 5 requests per second
docker run bitcoin-etl-stream:test stream --request-per-second 5

# Limit to 2.5 requests per second
docker run bitcoin-etl-stream:test stream --request-per-second 2.5

# No rate limiting (default)
docker run bitcoin-etl-stream:test stream
```

## Backward Compatibility
- All existing functionality remains unchanged
- When `--request-per-second` is not specified, behavior is identical to before
- Existing scripts and commands continue to work without modification
- Rate limiter is only created when explicitly requested

## Benefits
1. **Node Protection**: Prevents overwhelming Bitcoin nodes
2. **Rate Compliance**: Ensures compliance with node policies
3. **Stable Performance**: Maintains consistent performance
4. **Easy Configuration**: Simple parameter to control request frequency

## Testing
- Created and tested rate limiter functionality
- Verified thread safety and timing accuracy
- Confirmed backward compatibility
- All existing tests should continue to pass 