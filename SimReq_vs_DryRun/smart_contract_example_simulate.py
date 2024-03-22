
from pyteal import *


router = Router(
    "Testing",
    
    BareCallActions(
        no_op=OnCompleteAction.create_only(Approve()),
        opt_in=OnCompleteAction.call_only(Approve()),
        close_out=OnCompleteAction.call_only(Approve()),
    ),
    clear_state=Approve(),
)
@router.method
def print_ten():
    return Seq([
        Log(Itob(Int(10))),
    ])
    
@router.method
def call_and_zero_pay():
    #Add 1 to these indexes to simulate instead of dryrun and allow room for app creation transaction
    #app_call_index = 0
    #payment_index = 1
    app_call_index = 1 
    payment_index = 2
    payment_txn_amount = Itob(Gtxn[payment_index].amount())
    return Seq([
        Assert(Gtxn[app_call_index].type_enum() == TxnType.ApplicationCall),
        Assert(Gtxn[app_call_index].sender() == Addr("ZNOS2OA62XTLQRNOD4GKDHA4V4QTNHQEEY7YDDVJRINGAGAOZZDSSFHVME")), 
        Assert(Gtxn[app_call_index].application_args[1] == Bytes("TESTING")),
        Assert(Gtxn[app_call_index].note() == Bytes("TESTINGNOTE")),
        Assert(Gtxn[payment_index].type_enum() == TxnType.Payment),
        Assert(Gtxn[payment_index].amount() == Int(0)),
        Log(payment_txn_amount),
    ])

    

if __name__ == "__main__":
    import os
    import json

    path = os.path.dirname(os.path.abspath(__file__))
    approval, clear, contract = router.compile_program(version=8)
    
    os.makedirs(os.path.join(path, "simulate/artifacts"), exist_ok=True)

    with open(os.path.join(path, "simulate/artifacts/contract.json"), "w") as f:
        f.write(json.dumps(contract.dictify(), indent=2))

    with open(os.path.join(path, "simulate/artifacts/approval.teal"), "w") as f:
        f.write(approval)

    with open(os.path.join(path, "simulate/artifacts/clear.teal"), "w") as f:
        f.write(clear)