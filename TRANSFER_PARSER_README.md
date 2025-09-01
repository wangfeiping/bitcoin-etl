# Bitcoin Testnet Transfer Transaction Parser

这个自定义功能扩展了bitcoin-etl项目，专门用于解析和记录Bitcoin测试网的转账交易信息。

## 功能特性

- 解析指定区块范围内的所有转账交易
- 记录详细的交易信息：区块高度、区块哈希、交易哈希、发送方地址、接收方地址、转账金额、手续费
- 支持多种输出格式：控制台输出、文件日志
- 提供统计信息：总交易数、转账交易数、总转账量等
- 自动跳过coinbase交易
- 支持多线程处理以提高性能

## 安装和设置

1. 确保已安装bitcoin-etl项目：
```bash
pip install bitcoin-etl
```

2. 或者从源码安装：
```bash
git clone <repository-url>
cd bitcoin-etl
pip install -e .
```

3. 确保你有运行中的Bitcoin测试网节点，并配置了RPC访问权限。

## 使用方法

### 命令行使用

基本用法：
```bash
bitcoinetl parse_transfer_transactions --start-block 2400000 --end-block 2400010
```

完整参数示例：
```bash
bitcoinetl parse_transfer_transactions \
    --start-block 2400000 \
    --end-block 2400010 \
    --provider-uri http://user:pass@localhost:18332 \
    --output-file transfer_logs.txt \
    --log-level INFO \
    --batch-size 1 \
    --max-workers 5
```

### 参数说明

- `--start-block`: 起始区块高度
- `--end-block`: 结束区块高度（必需）
- `--provider-uri`: Bitcoin测试网节点RPC地址（默认：http://user:pass@localhost:18332）
- `--output-file`: 输出日志文件路径（可选，默认输出到控制台）
- `--log-level`: 日志级别（DEBUG, INFO, WARNING, ERROR，默认：INFO）
- `--batch-size`: 批处理大小（默认：1）
- `--max-workers`: 最大工作线程数（默认：5）
- `--chain`: 区块链类型（默认：bitcoin）

### 使用示例脚本

运行提供的示例脚本：
```bash
python example_parse_transfers.py
```

## 输出格式

### 控制台输出示例

```
2024-01-15 10:30:15 - Starting to parse transfer transactions from block 2400000 to 2400010
====================================================================================================
2024-01-15 10:30:15 - TRANSFER TRANSACTION LOG FORMAT:
2024-01-15 10:30:15 - Block Height | Block Hash | Transaction Hash | From Address | To Address | Amount (BTC) | Fee (BTC)
====================================================================================================
2024-01-15 10:30:16 - Processing block 2400000 (000000000000...) at 2024-01-15 10:30:16
2024-01-15 10:30:16 - Block contains 150 transactions
2024-01-15 10:30:16 - TRANSFER: 2400000 | 000000000000... | abc123def456... | From: tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh | To: tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh | Amount: 0.00100000 BTC | Fee: 0.00001000 BTC
2024-01-15 10:30:16 - Block 2400000: 45 transfer transactions, volume: 12.34567890 BTC
--------------------------------------------------------------------------------
2024-01-15 10:30:17 - Processing block 2400001 (000000000000...) at 2024-01-15 10:30:17
...
====================================================================================================
2024-01-15 10:30:20 - PARSING SUMMARY:
2024-01-15 10:30:20 - Total blocks processed: 11
2024-01-15 10:30:20 - Total transactions: 1650
2024-01-15 10:30:20 - Transfer transactions: 495
2024-01-15 10:30:20 - Coinbase transactions: 11
2024-01-15 10:30:20 - Total transfer volume: 123.45678900 BTC
2024-01-15 10:30:20 - Average volume per transfer: 0.24940765 BTC
====================================================================================================
2024-01-15 10:30:20 - Finished parsing transfer transactions from block 2400000 to 2400010
```

### 日志文件格式

如果指定了输出文件，日志会同时输出到控制台和文件：
```
2024-01-15 10:30:16 - TRANSFER: 2400000 | 000000000000... | abc123def456... | From: tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh | To: tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh | Amount: 0.00100000 BTC | Fee: 0.00001000 BTC
```

## 配置Bitcoin测试网节点

### 1. 安装Bitcoin Core

```bash
# Ubuntu/Debian
sudo apt-get install bitcoin-qt

# 或者从源码编译
git clone https://github.com/bitcoin/bitcoin.git
cd bitcoin
./autogen.sh
./configure
make
sudo make install
```

### 2. 配置测试网

创建配置文件 `~/.bitcoin/bitcoin.conf`：
```ini
# 启用测试网
testnet=1

# RPC设置
server=1
rpcuser=your_username
rpcpassword=your_password
rpcallowip=127.0.0.1
rpcport=18332

# 启用交易索引（用于获取输入地址信息）
txindex=1

# 其他设置
daemon=1
datadir=/path/to/testnet/data
```

### 3. 启动测试网节点

```bash
bitcoind -testnet
```

### 4. 等待同步

```bash
bitcoin-cli -testnet getblockchaininfo
```

## 故障排除

### 常见问题

1. **连接错误**: 确保Bitcoin测试网节点正在运行且RPC配置正确
2. **认证失败**: 检查RPC用户名和密码
3. **区块不存在**: 确保指定的区块范围在节点中可用
4. **权限错误**: 确保有足够的权限访问节点数据

### 调试模式

使用DEBUG日志级别获取更详细的信息：
```bash
bitcoinetl parse_transfer_transactions --start-block 2400000 --end-block 2400001 --log-level DEBUG
```

### 性能优化

- 增加 `--max-workers` 参数以提高处理速度
- 调整 `--batch-size` 参数以优化内存使用
- 对于大量区块，考虑分批处理

## 扩展功能

### 自定义解析器

你可以扩展 `ParseTransferTransactionsJob` 类来添加更多功能：

```python
class CustomTransferParser(ParseTransferTransactionsJob):
    def _parse_transfer_transaction(self, transaction, block_height, block_hash):
        # 添加自定义逻辑
        result = super()._parse_transfer_transaction(transaction, block_height, block_hash)
        
        # 添加额外的处理逻辑
        if result:
            # 例如：过滤特定金额的交易
            if result['total_amount'] > 1.0:
                self.logger.info(f"Large transfer detected: {result['total_amount']} BTC")
        
        return result
```

### 数据导出

你可以修改代码来导出数据到其他格式（CSV、JSON等）：

```python
import json

# 在 _parse_transfer_transaction 方法中添加
transfer_data = {
    'block_height': block_height,
    'block_hash': block_hash,
    'tx_hash': tx_hash,
    'from_addresses': from_addresses,
    'to_addresses': [detail['to_address'] for detail in transfer_details],
    'amounts': [detail['amount_btc'] for detail in transfer_details],
    'fee': fee_btc
}

# 写入JSON文件
with open('transfers.json', 'a') as f:
    json.dump(transfer_data, f)
    f.write('\n')
```

## 许可证

本项目遵循MIT许可证。详见LICENSE文件。 