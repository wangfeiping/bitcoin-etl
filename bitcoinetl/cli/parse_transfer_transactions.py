# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev, Omidiora Samuel evge.medvedev@gmail.com, samparsky@gmail.com
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


import click
import logging
import json
from datetime import datetime

from bitcoinetl.enumeration.chain import Chain
from bitcoinetl.jobs.parse_transfer_transactions_job import ParseTransferTransactionsJob
from bitcoinetl.rpc.bitcoin_rpc import BitcoinRpc
from blockchainetl.logging_utils import logging_basic_config
from blockchainetl.thread_local_proxy import ThreadLocalProxy

logging_basic_config()


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-s', '--start-block', default=0, type=int, help='Start block')
@click.option('-e', '--end-block', required=True, type=int, help='End block')
@click.option('-b', '--batch-size', default=1, type=int, help='The number of blocks to export at a time.')
@click.option('-p', '--provider-uri', default='http://user:pass@localhost:18332', type=str,
              help='The URI of the remote Bitcoin testnet node')
@click.option('-w', '--max-workers', default=5, type=int, help='The maximum number of workers.')
@click.option('--output-file', default=None, type=str,
              help='The output file for transfer transaction logs. Use "-" for stdout')
@click.option('-c', '--chain', default=Chain.BITCOIN, type=click.Choice(Chain.ALL),
              help='The type of chain')
@click.option('--log-level', default='INFO', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
              help='Log level')
def parse_transfer_transactions(start_block, end_block, batch_size, provider_uri,
                               max_workers, output_file, chain, log_level):
    """Parse and log transfer transactions from Bitcoin testnet."""
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, log_level))
    
    # Create custom logger for transfer transactions
    transfer_logger = logging.getLogger('transfer_transactions')
    transfer_logger.setLevel(logging.INFO)
    
    # Add file handler if output file is specified
    if output_file and output_file != '-':
        file_handler = logging.FileHandler(output_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(formatter)
        transfer_logger.addHandler(file_handler)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    console_handler.setFormatter(formatter)
    transfer_logger.addHandler(console_handler)
    
    job = ParseTransferTransactionsJob(
        start_block=start_block,
        end_block=end_block,
        batch_size=batch_size,
        bitcoin_rpc=ThreadLocalProxy(lambda: BitcoinRpc(provider_uri)),
        max_workers=max_workers,
        chain=chain,
        logger=transfer_logger)
    job.run() 