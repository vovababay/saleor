import requests
from hashlib import sha256

text_data = "100000testTokenExampleTinkoffBankTestTinkoffBankTest"
result = sha256(text_data.encode("utf-8")).hexdigest()
print(result)
