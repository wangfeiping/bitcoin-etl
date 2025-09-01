#!/usr/bin/env python3
"""
Test script for the transfer transaction parser
This script tests the parser functionality without requiring a full Bitcoin node
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bitcoinetl.jobs.parse_transfer_transactions_job import ParseTransferTransactionsJob
from bitcoinetl.domain.transaction import BtcTransaction
from bitcoinetl.domain.transaction_input import BtcTransactionInput
from bitcoinetl.domain.transaction_output import BtcTransactionOutput


class TestTransferParser(unittest.TestCase):
    """Test cases for the transfer transaction parser"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_rpc = Mock()
        self.mock_logger = Mock()
        
        self.parser = ParseTransferTransactionsJob(
            start_block=1,
            end_block=10,
            batch_size=1,
            bitcoin_rpc=self.mock_rpc,
            max_workers=1,
            chain="bitcoin",
            logger=self.mock_logger
        )
    
    def test_parse_transfer_transaction_coinbase(self):
        """Test that coinbase transactions are skipped"""
        # Create a mock coinbase transaction
        tx = BtcTransaction()
        tx.hash = "coinbase_tx_hash"
        tx.is_coinbase = True
        
        result = self.parser._parse_transfer_transaction(tx, 1000, "block_hash")
        
        self.assertIsNone(result)
        self.assertEqual(self.parser.stats['coinbase_transactions'], 1)
    
    def test_parse_transfer_transaction_normal(self):
        """Test parsing of normal transfer transaction"""
        # Create a mock transaction with inputs and outputs
        tx = BtcTransaction()
        tx.hash = "normal_tx_hash"
        tx.is_coinbase = False
        
        # Add input
        input_tx = BtcTransactionInput()
        input_tx.addresses = ["tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"]
        input_tx.value = 100000000  # 1 BTC in satoshis
        tx.inputs.append(input_tx)
        
        # Add output
        output_tx = BtcTransactionOutput()
        output_tx.addresses = ["tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"]
        output_tx.value = 99990000  # 0.9999 BTC in satoshis (0.0001 BTC fee)
        tx.outputs.append(output_tx)
        
        result = self.parser._parse_transfer_transaction(tx, 1000, "block_hash")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['total_amount'], 0.9999)
        self.assertEqual(result['fee'], 0.0001)
        self.assertEqual(self.parser.stats['transfer_transactions'], 1)
        self.assertEqual(self.parser.stats['total_volume_btc'], 0.9999)
    
    def test_parse_transfer_transaction_multiple_outputs(self):
        """Test parsing transaction with multiple outputs"""
        tx = BtcTransaction()
        tx.hash = "multi_output_tx_hash"
        tx.is_coinbase = False
        
        # Add input
        input_tx = BtcTransactionInput()
        input_tx.addresses = ["tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"]
        input_tx.value = 200000000  # 2 BTC in satoshis
        tx.inputs.append(input_tx)
        
        # Add multiple outputs
        output1 = BtcTransactionOutput()
        output1.addresses = ["tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"]
        output1.value = 100000000  # 1 BTC
        tx.outputs.append(output1)
        
        output2 = BtcTransactionOutput()
        output2.addresses = ["tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"]
        output2.value = 99990000  # 0.9999 BTC
        tx.outputs.append(output2)
        
        result = self.parser._parse_transfer_transaction(tx, 1000, "block_hash")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['total_amount'], 1.9999)
        self.assertEqual(result['fee'], 0.0001)
    
    def test_parse_transfer_transaction_no_addresses(self):
        """Test transaction with no clear addresses"""
        tx = BtcTransaction()
        tx.hash = "no_address_tx_hash"
        tx.is_coinbase = False
        
        # Add input without addresses
        input_tx = BtcTransactionInput()
        input_tx.value = 100000000
        tx.inputs.append(input_tx)
        
        # Add output without addresses
        output_tx = BtcTransactionOutput()
        output_tx.value = 99990000
        tx.outputs.append(output_tx)
        
        result = self.parser._parse_transfer_transaction(tx, 1000, "block_hash")
        
        self.assertIsNone(result)
    
    def test_statistics_accumulation(self):
        """Test that statistics are properly accumulated"""
        # Create multiple transactions
        for i in range(3):
            tx = BtcTransaction()
            tx.hash = f"tx_hash_{i}"
            tx.is_coinbase = False
            
            input_tx = BtcTransactionInput()
            input_tx.addresses = ["tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"]
            input_tx.value = 100000000
            tx.inputs.append(input_tx)
            
            output_tx = BtcTransactionOutput()
            output_tx.addresses = ["tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"]
            output_tx.value = 99990000
            tx.outputs.append(output_tx)
            
            self.parser._parse_transfer_transaction(tx, 1000, "block_hash")
        
        self.assertEqual(self.parser.stats['transfer_transactions'], 3)
        self.assertEqual(self.parser.stats['total_volume_btc'], 2.9997)


def run_tests():
    """Run the test suite"""
    print("Running Transfer Parser Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTransferParser)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 