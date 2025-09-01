#!/usr/bin/env python3
"""
Demo script for Bitcoin testnet transfer transaction parser
This script demonstrates the usage of the custom transfer parser
"""

import os
import sys
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo_parser_usage():
    """Demonstrate how to use the transfer parser"""
    
    print("Bitcoin Testnet Transfer Transaction Parser Demo")
    print("=" * 60)
    print()
    
    print("1. Basic Usage:")
    print("   bitcoinetl parse_transfer_transactions --start-block 2400000 --end-block 2400010")
    print()
    
    print("2. With custom RPC endpoint:")
    print("   bitcoinetl parse_transfer_transactions \\")
    print("       --start-block 2400000 \\")
    print("       --end-block 2400010 \\")
    print("       --provider-uri http://your_user:your_pass@localhost:18332")
    print()
    
    print("3. With output file:")
    print("   bitcoinetl parse_transfer_transactions \\")
    print("       --start-block 2400000 \\")
    print("       --end-block 2400010 \\")
    print("       --output-file transfer_logs.txt")
    print()
    
    print("4. With debug logging:")
    print("   bitcoinetl parse_transfer_transactions \\")
    print("       --start-block 2400000 \\")
    print("       --end-block 2400010 \\")
    print("       --log-level DEBUG")
    print()
    
    print("5. High performance mode:")
    print("   bitcoinetl parse_transfer_transactions \\")
    print("       --start-block 2400000 \\")
    print("       --end-block 2400100 \\")
    print("       --batch-size 10 \\")
    print("       --max-workers 10")
    print()


def demo_output_format():
    """Show the expected output format"""
    
    print("Expected Output Format:")
    print("=" * 60)
    print()
    
    print("2024-01-15 10:30:15 - Starting to parse transfer transactions from block 2400000 to 2400010")
    print("====================================================================================================")
    print("2024-01-15 10:30:15 - TRANSFER TRANSACTION LOG FORMAT:")
    print("2024-01-15 10:30:15 - Block Height | Block Hash | Transaction Hash | From Address | To Address | Amount (BTC) | Fee (BTC)")
    print("====================================================================================================")
    print("2024-01-15 10:30:16 - Processing block 2400000 (000000000000...) at 2024-01-15 10:30:16")
    print("2024-01-15 10:30:16 - Block contains 150 transactions")
    print("2024-01-15 10:30:16 - TRANSFER: 2400000 | 000000000000... | abc123def456... | From: tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh | To: tb1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh | Amount: 0.00100000 BTC | Fee: 0.00001000 BTC")
    print("2024-01-15 10:30:16 - Block 2400000: 45 transfer transactions, volume: 12.34567890 BTC")
    print("--------------------------------------------------------------------------------")
    print("...")
    print("====================================================================================================")
    print("2024-01-15 10:30:20 - PARSING SUMMARY:")
    print("2024-01-15 10:30:20 - Total blocks processed: 11")
    print("2024-01-15 10:30:20 - Total transactions: 1650")
    print("2024-01-15 10:30:20 - Transfer transactions: 495")
    print("2024-01-15 10:30:20 - Coinbase transactions: 11")
    print("2024-01-15 10:30:20 - Total transfer volume: 123.45678900 BTC")
    print("2024-01-15 10:30:20 - Average volume per transfer: 0.24940765 BTC")
    print("====================================================================================================")
    print()


def demo_configuration():
    """Show configuration examples"""
    
    print("Configuration Examples:")
    print("=" * 60)
    print()
    
    print("1. Bitcoin testnet node configuration (~/.bitcoin/bitcoin.conf):")
    print("   testnet=1")
    print("   server=1")
    print("   rpcuser=your_username")
    print("   rpcpassword=your_password")
    print("   rpcallowip=127.0.0.1")
    print("   rpcport=18332")
    print("   txindex=1")
    print("   daemon=1")
    print()
    
    print("2. Environment variables (optional):")
    print("   export BITCOINETL_BITCOIN_PROVIDER_URI=http://user:pass@localhost:18332")
    print()
    
    print("3. Python script usage:")
    print("   from bitcoinetl.cli.parse_transfer_transactions import parse_transfer_transactions")
    print("   ")
    print("   parse_transfer_transactions.callback(")
    print("       start_block=2400000,")
    print("       end_block=2400010,")
    print("       provider_uri='http://user:pass@localhost:18332',")
    print("       output_file='transfers.log',")
    print("       log_level='INFO'")
    print("   )")
    print()


def demo_troubleshooting():
    """Show troubleshooting tips"""
    
    print("Troubleshooting:")
    print("=" * 60)
    print()
    
    print("1. Connection Issues:")
    print("   - Ensure Bitcoin testnet node is running")
    print("   - Check RPC credentials in bitcoin.conf")
    print("   - Verify RPC port (18332 for testnet)")
    print("   - Test connection: bitcoin-cli -testnet getblockchaininfo")
    print()
    
    print("2. Block Range Issues:")
    print("   - Ensure blocks exist on your node")
    print("   - Check node sync status")
    print("   - Use smaller block ranges for testing")
    print()
    
    print("3. Performance Issues:")
    print("   - Increase --max-workers for better performance")
    print("   - Adjust --batch-size based on available memory")
    print("   - Use --log-level DEBUG for detailed information")
    print()
    
    print("4. Output Issues:")
    print("   - Check file permissions for output files")
    print("   - Use --output-file - for stdout only")
    print("   - Verify log level settings")
    print()


def main():
    """Main demo function"""
    
    demo_parser_usage()
    demo_output_format()
    demo_configuration()
    demo_troubleshooting()
    
    print("For more information, see TRANSFER_PARSER_README.md")
    print("To run tests: python3 test_transfer_parser.py")
    print("To run example: python3 example_parse_transfers.py")


if __name__ == "__main__":
    main() 