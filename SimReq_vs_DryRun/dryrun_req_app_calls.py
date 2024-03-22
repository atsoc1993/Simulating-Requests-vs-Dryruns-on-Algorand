from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.models import DryrunRequest, DryrunSource, Application, ApplicationParams
from algosdk.transaction import ApplicationCallTxn, PaymentTxn, OnComplete
import os
import base64

algod_token = os.getenv('NODE_TOKEN')
algod_port = os.getenv('NODE_PORT')
algod_client = AlgodClient(algod_token, algod_port)
account_private_key = os.getenv('PRIVATE_KEY')
account_address = os.getenv('ADDRESS')


with open('dryrun/artifacts/approval.teal', 'r') as f:
    approval_teal_source = f.read()

app_id = 123
approval_result = algod_client.compile(approval_teal_source)
approval_program = base64.b64decode(approval_result['result'])

app = Application(id=app_id, params=ApplicationParams(approval_program=approval_program))

method_call = 0x979d1f8b.to_bytes(4, 'big') 
testing_arg = "TESTING".encode()
note = "TESTINGNOTE"
params = algod_client.suggested_params()

app_call_txn = ApplicationCallTxn(
    sender=account_address,
    sp=params,
    index=123,
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


signed_app_call_txn = app_call_txn.sign(account_private_key)
signed_payment_txn = payment_txn.sign(account_private_key)
#No group assignment needed for dryruns, just pass in list of signed transactions to DryRunRequest txns key
group = [signed_app_call_txn, signed_payment_txn]

source = DryrunSource(field_name="approv", source=approval_teal_source)
request = DryrunRequest(
    txns=group,
    sources=[source],
    apps=[app]
)

dryrun_response = algod_client.dryrun(request)
print(dryrun_response)
print(int.from_bytes(base64.b64decode(dryrun_response['txns'][0]['logs'][0]), 'big'))
