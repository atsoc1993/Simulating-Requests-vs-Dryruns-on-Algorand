from algosdk.v2client.algod import AlgodClient
from algosdk import atomic_transaction_composer
from algosdk.v2client.models import simulate_request
from algosdk.transaction import AssetCreateTxn, AssetTransferTxn
from algosdk.util import microalgos_to_algos
from dotenv import load_dotenv
import os

load_dotenv()

algod_token = os.getenv('NODE_TOKEN')
algod_port = os.getenv('NODE_PORT')
algod_client = AlgodClient(algod_token, algod_port)
account_private_key = os.getenv('PRIVATE_KEY')
account_address = os.getenv('ADDRESS')

params = algod_client.suggested_params()

asset_creation_tx = AssetCreateTxn(
    sp = params,
    sender=account_address,
    decimals=0,
    default_frozen=False,
    total=1,
    manager=account_address,
    asset_name='Test',
    unit_name='T1',
)


signer = atomic_transaction_composer.AccountTransactionSigner(account_private_key)
tws = atomic_transaction_composer.TransactionWithSigner(asset_creation_tx, signer)

atc = atomic_transaction_composer.AtomicTransactionComposer()
atc.add_transaction(tws)

simreq = simulate_request.SimulateRequest(
    txn_groups=[asset_creation_tx],
    
)
simres = atc.simulate(algod_client, simreq)
asset_id = simres.simulate_response.get('txn-groups')[0]['txn-results'][0]['txn-result']['asset-index']

'''
ASSET ID OBTAINED
'''

asset_creation_tx = AssetCreateTxn(
    sp = params,
    sender=account_address,
    decimals=0,
    default_frozen=False,
    total=1,
    manager=account_address,
    asset_name='Test',
    unit_name='T1',
)

asset_transfer_txn = AssetTransferTxn(
    sp = params,
    sender=account_address,
    receiver=account_address,
    amt=1,
    index=asset_id,
)

signer = atomic_transaction_composer.AccountTransactionSigner(account_private_key)
ac_ws = atomic_transaction_composer.TransactionWithSigner(asset_creation_tx, signer)
at_ws = atomic_transaction_composer.TransactionWithSigner(asset_transfer_txn, signer)

atc = atomic_transaction_composer.AtomicTransactionComposer()
atc.add_transaction(ac_ws)
atc.add_transaction(at_ws)

grp = atc.build_group()

simreq = simulate_request.SimulateRequest(
    txn_groups=[grp],
    
)
sim_response = atc.simulate(algod_client, simreq)
#print(sim_response)
print(sim_response.simulate_response)