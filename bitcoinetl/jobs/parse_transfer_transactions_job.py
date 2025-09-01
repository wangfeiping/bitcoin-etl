# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev, evge.medvedev@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import logging
from datetime import datetime
from collections import defaultdict

from bitcoinetl.mappers.block_mapper import BtcBlockMapper
from bitcoinetl.mappers.transaction_mapper import BtcTransactionMapper
from bitcoinetl.service.btc_service import BtcService
from blockchainetl.executors.batch_work_executor import BatchWorkExecutor
from blockchainetl.jobs.base_job import BaseJob
from blockchainetl.utils import validate_range


# Parse and log transfer transactions
class ParseTransferTransactionsJob(BaseJob):
    def __init__(
            self,
            start_block,
            end_block,
            batch_size,
            bitcoin_rpc,
            max_workers,
            chain,
            logger):
        validate_range(start_block, end_block)
        self.start_block = start_block
        self.end_block = end_block

        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self.logger = logger

        self.btc_service = BtcService(bitcoin_rpc, chain)
        self.block_mapper = BtcBlockMapper()
        self.transaction_mapper = BtcTransactionMapper()
        
        # Statistics
        self.stats = {
            'total_blocks': 0,
            'total_transactions': 0,
            'transfer_transactions': 0,
            'coinbase_transactions': 0,
            'total_volume_btc': 0.0
        }

    def _start(self):
        self.logger.info(f"Starting to parse transfer transactions from block {self.start_block} to {self.end_block}")
        self.logger.info("=" * 100)
        self.logger.info("TRANSFER TRANSACTION LOG FORMAT:")
        self.logger.info("Block Height | Block Hash | Transaction Hash | From Address | To Address | Amount (BTC) | Fee (BTC)")
        self.logger.info("=" * 100)

    def _export(self):
        self.batch_work_executor.execute(
            range(self.start_block, self.end_block + 1),
            self._export_batch,
            total_items=self.end_block - self.start_block + 1
        )

    def _export_batch(self, block_number_batch):
        blocks = self.btc_service.get_blocks(block_number_batch, export_transactions=True)

        for block in blocks:
            self._parse_block_transactions(block)

    def _parse_block_transactions(self, block):
        """Parse transactions in a block and log transfer transactions"""
        block_height = block.number
        block_hash = block.hash
        block_timestamp = datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        self.stats['total_blocks'] += 1
        
        self.logger.info(f"Processing block {block_height} ({block_hash[:16]}...) at {block_timestamp}")
        self.logger.info(f"Block contains {len(block.transactions)} transactions")
        
        block_transfer_count = 0
        block_volume = 0.0
        
        for tx in block.transactions:
            self.stats['total_transactions'] += 1
            transfer_info = self._parse_transfer_transaction(tx, block_height, block_hash)
            if transfer_info:
                block_transfer_count += 1
                block_volume += transfer_info.get('total_amount', 0.0)
        
        if block_transfer_count > 0:
            self.logger.info(f"Block {block_height}: {block_transfer_count} transfer transactions, volume: {block_volume:.8f} BTC")
        
        self.logger.info("-" * 80)

    def _parse_transfer_transaction(self, transaction, block_height, block_hash):
        """Parse a single transaction and log transfer details"""
        tx_hash = transaction.hash
        
        # Skip coinbase transactions
        if transaction.is_coinbase:
            self.stats['coinbase_transactions'] += 1
            self.logger.debug(f"Skipping coinbase transaction {tx_hash}")
            return None
        
        # Parse inputs to get from addresses and total input value
        from_addresses = []
        total_input_value = 0
        
        for input_tx in transaction.inputs:
            if input_tx.addresses:
                from_addresses.extend(input_tx.addresses)
            if input_tx.value is not None:
                total_input_value += input_tx.value
        
        # Parse outputs to get to addresses and amounts
        transfer_details = []
        total_output_value = 0
        
        for output in transaction.outputs:
            if output.addresses and output.value is not None:
                total_output_value += output.value
                # Convert satoshis to BTC
                amount_btc = output.value / 100000000.0
                for address in output.addresses:
                    transfer_details.append({
                        'to_address': address,
                        'amount_btc': amount_btc
                    })
        
        # Calculate fee
        fee_satoshi = total_input_value - total_output_value
        fee_btc = fee_satoshi / 100000000.0 if fee_satoshi > 0 else 0.0
        
        # Log transfer transactions
        if from_addresses and transfer_details:
            self.stats['transfer_transactions'] += 1
            total_amount = sum(detail['amount_btc'] for detail in transfer_details)
            self.stats['total_volume_btc'] += total_amount
            
            for detail in transfer_details:
                from_addr_str = ', '.join(from_addresses) if len(from_addresses) > 1 else from_addresses[0]
                self.logger.info(
                    f"TRANSFER: {block_height} | {block_hash[:16]}... | {tx_hash[:16]}... | "
                    f"From: {from_addr_str} | To: {detail['to_address']} | "
                    f"Amount: {detail['amount_btc']:.8f} BTC | Fee: {fee_btc:.8f} BTC"
                )
            
            return {
                'total_amount': total_amount,
                'fee': fee_btc,
                'from_addresses': from_addresses,
                'to_addresses': [detail['to_address'] for detail in transfer_details]
            }
        else:
            self.logger.debug(f"No clear transfer details for transaction {tx_hash}")
            return None

    def _end(self):
        self.batch_work_executor.shutdown()
        
        # Print summary statistics
        self.logger.info("=" * 100)
        self.logger.info("PARSING SUMMARY:")
        self.logger.info(f"Total blocks processed: {self.stats['total_blocks']}")
        self.logger.info(f"Total transactions: {self.stats['total_transactions']}")
        self.logger.info(f"Transfer transactions: {self.stats['transfer_transactions']}")
        self.logger.info(f"Coinbase transactions: {self.stats['coinbase_transactions']}")
        self.logger.info(f"Total transfer volume: {self.stats['total_volume_btc']:.8f} BTC")
        self.logger.info(f"Average volume per transfer: {self.stats['total_volume_btc'] / max(self.stats['transfer_transactions'], 1):.8f} BTC")
        self.logger.info("=" * 100)
        self.logger.info(f"Finished parsing transfer transactions from block {self.start_block} to {self.end_block}") 