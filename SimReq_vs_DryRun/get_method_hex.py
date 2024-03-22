from algosdk.abi import Method

signature1 = "print_ten()void" #a8cf85fe
signature2 = "call_and_zero_pay()void" #979d1f8b

print(Method.from_signature(signature1).get_selector().hex())
print(Method.from_signature(signature2).get_selector().hex())

