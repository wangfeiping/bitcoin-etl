#!/usr/bin/env python3
"""
Example script for parsing Bitcoin testnet transfer transactions
This script demonstrates how to use the custom transfer transaction parser
"""

import os
import sys
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bitcoinetl.cli.parse_transfer_transactions import parse_transfer_transactions


def main():
    """Main function to demonstrate transfer transaction parsing"""
    
    print("Bitcoin Testnet Transfer Transaction Parser")
    print("=" * 50)
    
    # Example configuration for Bitcoin testnet
    # You can modify these parameters as needed
    
    # Testnet RPC endpoint (modify with your testnet node details)
    provider_uri = "http://user:pass@localhost:18332"
    
    # Block range to parse (modify as needed)
    start_block = 2400000  # Example start block
    end_block = 2400010    # Example end block (10 blocks)
    
    # Output file for logs
    output_file = "transfer_transactions.log"
    
    # Log level
    log_level = "INFO"
    
    print(f"Configuration:")
    print(f"  Provider URI: {provider_uri}")
    print(f"  Start Block: {start_block}")
    print(f"  End Block: {end_block}")
    print(f"  Output File: {output_file}")
    print(f"  Log Level: {log_level}")
    print()
    
    try:
        # Call the parse_transfer_transactions function
        parse_transfer_transactions.callback(
            start_block=start_block,
            end_block=end_block,
            batch_size=1,
            provider_uri=provider_uri,
            max_workers=1,
            output_file=output_file,
            chain="bitcoin",
            log_level=log_level
        )
        
        print(f"\nParsing completed! Check the log file: {output_file}")
        
    except Exception as e:
        print(f"Error during parsing: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure your Bitcoin testnet node is running")
        print("2. Verify the RPC credentials in provider_uri")
        print("3. Check that the block range exists on your node")
        print("4. Ensure you have the required dependencies installed")


if __name__ == "__main__":
    main() 