import json
import logging
import requests
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

    def export_items(self, items):
        for item in items:
            self.export_item(item)

    def export_item(self, item):
        """导出单个项目，支持对象和字典两种格式"""
        # 调试信息
        self.logger.debug(f"收到项目类型: {type(item)}")
        if hasattr(item, '__dict__'):
            self.logger.debug(f"项目属性: {list(item.__dict__.keys())}")
        elif isinstance(item, dict):
            self.logger.debug(f"字典键: {list(item.keys())}")
        
        # 检查是否为区块（对象格式）
        if hasattr(item, 'transactions') and hasattr(item, 'number'):
            self.logger.debug("检测到区块对象格式")
            self._parse_block_transactions(item)
        # 检查是否为区块（字典格式）
        elif isinstance(item, dict) and 'transactions' in item and 'number' in item:
            self.logger.debug("检测到区块字典格式")
            self._parse_block_dict_transactions(item)
        # 检查是否为交易（字典格式）
        elif isinstance(item, dict) and 'hash' in item and 'inputs' in item and 'outputs' in item:
            self.logger.debug("检测到交易字典格式")
            # 在streaming模式下，单独的交易可能没有区块信息
            # 尝试从交易数据中提取区块信息
            block_height = item.get('block_number') or item.get('blockNumber') or item.get('block_number')
            block_hash = item.get('block_hash') or item.get('blockHash') or item.get('block_hash')
            self._parse_transaction_dict(item, block_height, block_hash)
        # 检查是否为交易（对象格式）
        elif hasattr(item, 'hash') and hasattr(item, 'inputs') and hasattr(item, 'outputs'):
            self.logger.debug("检测到交易对象格式")
            # 尝试从交易对象中获取区块信息
            block_height = getattr(item, 'block_number', None) or getattr(item, 'blockNumber', None)
            block_hash = getattr(item, 'block_hash', None) or getattr(item, 'blockHash', None)
            self._parse_transaction_object(item, block_height, block_hash)
        else:
            # 其他类型的项目，记录但不处理
            self.logger.debug(f"跳过未知类型的项目: {type(item)}")
            if isinstance(item, dict):
                self.logger.debug(f"项目内容: {json.dumps(item, separators=(',', ':'))}")

    def _parse_block_dict_transactions(self, block_dict):
        """解析字典格式的区块中的转账交易"""
        block_height = block_dict.get('number', 'unknown')
        block_hash = block_dict.get('hash', 'unknown')
        block_timestamp = block_dict.get('timestamp', None)
        
        if block_timestamp:
            timestamp_str = datetime.fromtimestamp(block_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        else:
            timestamp_str = 'unknown'
        
        self.stats['total_blocks'] += 1
        transactions = block_dict.get('transactions', [])
        self.stats['total_transactions'] += len(transactions)
        
        self.logger.info(f"处理区块 {block_height} (哈希: {block_hash[:16]}...) 时间: {timestamp_str}")
        self.logger.info(f"区块包含 {len(transactions)} 笔交易")
        
        block_transfer_count = 0
        
        for tx in transactions:
            transfer_info = self._parse_transaction_dict(tx, block_height, block_hash)
            if transfer_info:
                block_transfer_count += 1
        
        if block_transfer_count > 0:
            self.logger.info(f"区块 {block_height}: 发现 {block_transfer_count} 笔转账交易")
        
        self.logger.info("-" * 80)

    def _parse_block_transactions(self, block):
        """解析区块对象中的转账交易"""
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
            transfer_info = self._parse_transaction_object(tx, block_height, block_hash)
            if transfer_info:
                block_transfer_count += 1
        
        if block_transfer_count > 0:
            self.logger.info(f"区块 {block_height}: 发现 {block_transfer_count} 笔转账交易")
        
        self.logger.info("-" * 80)

    def _parse_transaction_dict(self, transaction_dict, block_height=None, block_hash=None):
        """解析字典格式的交易"""
        tx_hash = transaction_dict.get('hash', 'unknown')
        
        # 跳过coinbase交易
        if transaction_dict.get('is_coinbase', False):
            self.stats['coinbase_transactions'] += 1
            self.logger.debug(f"跳过coinbase交易: {tx_hash}")
            return None
        
        # 获取输入地址（发送方）
        from_addresses = []
        inputs = transaction_dict.get('inputs', [])
        for input_tx in inputs:
            addresses = input_tx.get('addresses', [])
            if addresses:
                from_addresses.extend(addresses)
        
        # 获取输出地址（接收方）和对应的vout_n
        to_addresses_with_vout = []
        outputs = transaction_dict.get('outputs', [])
        for i, output in enumerate(outputs):
            addresses = output.get('addresses', [])
            if addresses:
                for address in addresses:
                    to_addresses_with_vout.append((address, i))  # (地址, vout_n)
        
        # 如果是转账交易（有发送方和接收方地址）
        if from_addresses and to_addresses_with_vout:
            self.stats['transfer_transactions'] += 1
            
            # 输出转账信息
            from_addr_str = ', '.join(from_addresses) if len(from_addresses) > 1 else from_addresses[0]
            
            # 为每个接收方地址输出对应的vout_n
            for address, vout_n in to_addresses_with_vout:
                self.logger.warning(
                    f"{block_height} from: {from_addr_str} to: {address} vout_n: {vout_n} {tx_hash}"
                )
                addrs = [from_addr_str, address]
                addrs = self._query_addrs(addrs)
                if len(addrs) > 0:
                    self.logger.warning(f"registered Tx: {tx_hash}")
            
            return {
                'block_height': block_height,
                'block_hash': block_hash,
                'tx_hash': tx_hash,
                'from_addresses': from_addresses,
                'to_addresses_with_vout': to_addresses_with_vout
            }
        
        return None

    def _parse_transaction_object(self, transaction, block_height=None, block_hash=None):
        """解析交易对象"""
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
        
        # 获取输出地址（接收方）和对应的vout_n
        to_addresses_with_vout = []
        outputs = getattr(transaction, 'outputs', [])
        for i, output in enumerate(outputs):
            addresses = getattr(output, 'addresses', [])
            if addresses:
                for address in addresses:
                    to_addresses_with_vout.append((address, i))  # (地址, vout_n)
        
        # 如果是转账交易（有发送方和接收方地址）
        if from_addresses and to_addresses_with_vout:
            self.stats['transfer_transactions'] += 1
            
            # 输出转账信息
            from_addr_str = ', '.join(from_addresses) if len(from_addresses) > 1 else from_addresses[0]
            
            block_info = f"区块 {block_height} | 区块哈希: {block_hash[:16]}..." if block_height and block_hash else ""
            
            # 为每个接收方地址输出对应的vout_n
            for address, vout_n in to_addresses_with_vout:
                self.logger.info(
                    f"转账交易: {block_info} | "
                    f"交易哈希: {tx_hash[:16]}... | "
                    f"发送方: {from_addr_str} | "
                    f"接收方: {address} | "
                    f"vout_n: {vout_n}"
                )
            
            return {
                'block_height': block_height,
                'block_hash': block_hash,
                'tx_hash': tx_hash,
                'from_addresses': from_addresses,
                'to_addresses_with_vout': to_addresses_with_vout
            }
        
        return None

    def _query_addrs(self, addresses, api_url="http://172.17.0.1:17004"):
        """
        查询地址信息
        
        Args:
            addresses (list): 要查询的地址列表
            api_url (str): API端点URL，默认为本地API
            
        Returns:
            list: 返回API响应中的地址数组，如果出错返回空列表
        """
        api_url = api_url+"/api/v1/bitcoin/addresses"
        try:
            # 准备请求数据
            payload = {"addresses": addresses}
            headers = {
                'accept': 'application/json',
                'content-type': 'application/json'
            }
            
            self.logger.debug(f"查询地址: {addresses}")
            self.logger.debug(f"API URL: {api_url}")
            
            # 发送POST请求
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()  # 检查HTTP错误
            
            # 解析响应
            result = response.json()
            
            # 检查API响应状态
            if result.get('success', False) and result.get('error_code', -1) == 0:
                addresses_result = result.get('result', [])
                self.logger.info(f"成功查询到 {len(addresses_result)} 个地址")
                self.logger.debug(f"查询结果: {addresses_result}")
                return addresses_result
            else:
                error_msg = result.get('error_message', 'Unknown error')
                error_desc = result.get('error_description', 'No description')
                self.logger.error(f"API返回错误: {error_msg} - {error_desc}")
                return []
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求错误: {str(e)}")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON解析错误: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"查询地址时发生未知错误: {str(e)}")
            return []

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
