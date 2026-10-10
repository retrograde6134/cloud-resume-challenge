import os

# The function module reads this at import time. A syntactically valid
# dummy value is enough — the actual TableClient is mocked in tests.
os.environ.setdefault(
    "COSMOS_CONNECTION_STRING",
    "DefaultEndpointsProtocol=https;"
    "AccountName=testaccount;"
    "AccountKey=dGVzdGtleQ==;"
    "TableEndpoint=https://testaccount.table.cosmos.azure.com:443/;",
)