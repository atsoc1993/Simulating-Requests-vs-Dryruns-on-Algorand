from algosdk.v2client.algod import AlgodClient
from algosdk import atomic_transaction_composer
from algosdk.v2client.models import simulate_request
from algosdk.transaction import ApplicationCreateTxn, ApplicationCallTxn, PaymentTxn, StateSchema, OnComplete
from dotenv import load_dotenv
import base64
import os

load_dotenv()

algod_token = os.getenv('NODE_TOKEN')
algod_port = os.getenv('NODE_PORT')
algod_client = AlgodClient(algod_token, algod_port)
account_private_key = os.getenv('PRIVATE_KEY')
account_address = os.getenv('ADDRESS')


with open('simulate/artifacts/approval.teal', 'r') as f:
    approval_teal_source = f.read()

with open('simulate/artifacts/clear.teal', 'r') as f:
    clear_teal_source = f.read()

approval_result = algod_client.compile(approval_teal_source)
approval_program = base64.b64decode(approval_result['result'])

clear_result = algod_client.compile(clear_teal_source)
clear_program = base64.b64decode(clear_result['result'])

global_schema = StateSchema(num_uints=1, num_byte_slices=1)
local_schema = StateSchema(num_uints=1, num_byte_slices=1)

params = algod_client.suggested_params()

app_create_txn = ApplicationCreateTxn(
    account_address,
    params,
    OnComplete.NoOpOC,
    approval_program=approval_program,
    clear_program=clear_program,
    global_schema=global_schema,
    local_schema=local_schema,
)

signer = atomic_transaction_composer.AccountTransactionSigner(account_private_key)
tws = atomic_transaction_composer.TransactionWithSigner(app_create_txn, signer)

atc = atomic_transaction_composer.AtomicTransactionComposer()
atc.add_transaction(tws)

simreq = simulate_request.SimulateRequest(
    txn_groups=[app_create_txn],
)

'''
APP ID OBTAINED
''' 

simres = atc.simulate(algod_client, simreq)
response = simres.simulate_response
asset_id = response['txn-groups'][0]['txn-results'][0]['txn-result']['application-index']
method_call = 0x979d1f8b.to_bytes(4, 'big') 
testing_arg = "TESTING".encode()
note = "TESTINGNOTE"

app_create_txn = ApplicationCreateTxn(
    account_address,
    params,
    OnComplete.NoOpOC,
    approval_program=approval_program,
    clear_program=clear_program,
    global_schema=global_schema,
    local_schema=local_schema,
)

app_call_txn = ApplicationCallTxn(
    sender=account_address,
    sp=params,
    index=asset_id,
    app_args=[method_call, testing_arg],
    on_complete=OnComplete.NoOpOC,
    note = "TESTINGNOTE",
)

payment_txn = PaymentTxn(
    sender=account_address,
    sp=params,
    receiver=account_address,
    amt=0,
)

signer = atomic_transaction_composer.AccountTransactionSigner(account_private_key)
app_create_tx_signed = atomic_transaction_composer.TransactionWithSigner(app_create_txn, signer)
app_call_tx_signed = atomic_transaction_composer.TransactionWithSigner(app_call_txn, signer)
payment_tx_signed = atomic_transaction_composer.TransactionWithSigner(payment_txn, signer)

atc = atomic_transaction_composer.AtomicTransactionComposer()
atc.add_transaction(app_create_tx_signed)
atc.add_transaction(app_call_tx_signed)
atc.add_transaction(payment_tx_signed)

grp = atc.build_group()


simreq = simulate_request.SimulateRequest(
    txn_groups=[grp],
)

simres = atc.simulate(algod_client, simreq)
response = simres.simulate_response
print(response)
print(int.from_bytes(base64.b64decode(response['txn-groups'][0]['txn-results'][1]['txn-result']['logs'][0]),'big'))
