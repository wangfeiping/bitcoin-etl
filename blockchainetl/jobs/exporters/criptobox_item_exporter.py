import json
import logging
from datetime import datetime


class CriptoboxItemExporter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.stats = {
            'total_blocks': 0,
            'total_transactions': 0,
            'transfer_transactions': 0,
            'coinbase_transactions': 0
        }

    def open(self):
        self.logger.info("开始解析转账交易...")
        self.logger.info("=" * 80)
        self.logger.info("转账交易日志格式:")
        self.logger.info("区块高度 | 区块哈希 | 交易哈希 | 发送方地址 | 接收方地址")
        self.logger.info("=" * 80)

    def export_items(self, items):
        for item in items:
            self.export_item(item)

    def export_item(self, item):
        """导出单个项目，如果是区块则解析其中的转账交易"""
        if hasattr(item, 'transactions') and hasattr(item, 'number'):
            # 这是一个区块对象
            self._parse_block_transactions(item)
        # else:
        #     # 其他类型的项目，按原样输出
        #     print(json.dumps(item, separators=(',', ':')))

    def _parse_block_transactions(self, block):
        """解析区块中的转账交易"""
        block_height = block.number
        block_hash = getattr(block, 'hash', 'unknown')
        block_timestamp = getattr(block, 'timestamp', None)
        
        if block_timestamp:
            timestamp_str = datetime.fromtimestamp(block_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        else:
            timestamp_str = 'unknown'
        
        self.stats['total_blocks'] += 1
        transactions = getattr(block, 'transactions', [])
        self.stats['total_transactions'] += len(transactions)
        
        self.logger.info(f"处理区块 {block_height} (哈希: {block_hash[:16]}...) 时间: {timestamp_str}")
        self.logger.info(f"区块包含 {len(transactions)} 笔交易")
        
        block_transfer_count = 0
        
        for tx in transactions:
            transfer_info = self._parse_transfer_transaction(tx, block_height, block_hash)
            if transfer_info:
                block_transfer_count += 1
        
        if block_transfer_count > 0:
            self.logger.info(f"区块 {block_height}: 发现 {block_transfer_count} 笔转账交易")
        
        self.logger.info("-" * 80)

    def _parse_transfer_transaction(self, transaction, block_height, block_hash):
        """解析单笔转账交易"""
        tx_hash = getattr(transaction, 'hash', 'unknown')
        
        # 跳过coinbase交易
        if getattr(transaction, 'is_coinbase', False):
            self.stats['coinbase_transactions'] += 1
            return None
        
        # 获取输入地址（发送方）
        from_addresses = []
        inputs = getattr(transaction, 'inputs', [])
        for input_tx in inputs:
            addresses = getattr(input_tx, 'addresses', [])
            if addresses:
                from_addresses.extend(addresses)
        
        # 获取输出地址（接收方）
        to_addresses = []
        outputs = getattr(transaction, 'outputs', [])
        for output in outputs:
            addresses = getattr(output, 'addresses', [])
            if addresses:
                to_addresses.extend(addresses)
        
        # 如果是转账交易（有发送方和接收方地址）
        if from_addresses and to_addresses:
            self.stats['transfer_transactions'] += 1
            
            # 输出转账信息
            from_addr_str = ', '.join(from_addresses) if len(from_addresses) > 1 else from_addresses[0]
            to_addr_str = ', '.join(to_addresses) if len(to_addresses) > 1 else to_addresses[0]
            
            self.logger.info(
                f"转账交易: 区块 {block_height} | "
                f"区块哈希: {block_hash[:16]}... | "
                f"交易哈希: {tx_hash[:16]}... | "
                f"发送方: {from_addr_str} | "
                f"接收方: {to_addr_str}"
            )
            
            return {
                'block_height': block_height,
                'block_hash': block_hash,
                'tx_hash': tx_hash,
                'from_addresses': from_addresses,
                'to_addresses': to_addresses
            }
        
        return None

    def close(self):
        """关闭导出器并显示统计信息"""
        self.logger.info("=" * 80)
        self.logger.info("解析完成统计:")
        self.logger.info(f"总处理区块数: {self.stats['total_blocks']}")
        self.logger.info(f"总交易数: {self.stats['total_transactions']}")
        self.logger.info(f"转账交易数: {self.stats['transfer_transactions']}")
        self.logger.info(f"Coinbase交易数: {self.stats['coinbase_transactions']}")
        self.logger.info("=" * 80)
        self.logger.info("转账交易解析完成")
