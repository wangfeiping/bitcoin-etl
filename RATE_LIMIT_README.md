# Bitcoin ETL Rate Limiting Feature

## Overview

This feature adds rate limiting capability to the Bitcoin ETL streaming functionality to control the frequency of RPC calls to Bitcoin nodes.

## New Parameter

### `--request-per-second`

- **Type**: float
- **Default**: 0 (no limit)
- **Description**: Maximum number of RPC requests per second. When set to 0, no rate limiting is applied.

## Usage Examples

### Basic Usage

```bash
# Limit to 5 requests per second
docker run bitcoin-etl-stream:test stream --request-per-second 5 --provider-uri http://user:pass@localhost:8332

# Limit to 2.5 requests per second (one request every 400ms)
docker run bitcoin-etl-stream:test stream --request-per-second 2.5 --provider-uri http://user:pass@localhost:8332

# No rate limiting (default behavior)
docker run bitcoin-etl-stream:test stream --provider-uri http://user:pass@localhost:8332
```

### Complete Example with All Parameters

```bash
docker run bitcoin-etl-stream:test stream \
  --request-per-second 3 \
  --provider-uri http://user:pass@localhost:8332 \
  --period-seconds 10 \
  --batch-size 2 \
  --block-batch-size 10 \
  --max-workers 5 \
  --lag 0
```

## How It Works

1. **Rate Limiter**: A thread-safe rate limiter is created when `--request-per-second` is greater than 0
2. **RPC Calls**: All Bitcoin RPC calls go through the rate limiter, which ensures the specified request frequency is maintained
3. **Thread Safety**: The rate limiter uses locks to ensure thread safety across multiple worker threads
4. **Precise Timing**: Uses high-precision timing to maintain accurate request intervals

## Implementation Details

- **File**: `bitcoinetl/rpc/request.py` - Contains the `RateLimiter` class
- **File**: `bitcoinetl/rpc/bitcoin_rpc.py` - Modified to accept and use rate limiter
- **File**: `bitcoinetl/cli/stream.py` - Added command line parameter

## Benefits

1. **Node Protection**: Prevents overwhelming Bitcoin nodes with too many requests
2. **Rate Compliance**: Ensures compliance with node rate limiting policies
3. **Stable Performance**: Maintains consistent performance without hitting rate limits
4. **Configurable**: Easy to adjust based on node capabilities and requirements

## Considerations

- Setting a very low rate (e.g., 0.1 requests/second) will significantly slow down the streaming process
- The rate limiter adds minimal overhead when enabled
- When disabled (default), performance is identical to the original implementation
- The rate limiter is applied per RPC call, not per batch of calls

## Testing

You can test the rate limiting functionality using the provided test script:

```bash
python3 test_rate_limit.py
```

This will verify that the rate limiter correctly enforces the specified request frequency. 