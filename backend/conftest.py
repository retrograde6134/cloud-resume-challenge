import os

os.environ.setdefault(
    "COSMOS_CONNECTION_STRING",
    "DefaultEndpointsProtocol=https;"
    "AccountName=testaccount;"
    "AccountKey=dGVzdGtleQ==;"
    "TableEndpoint=https://testaccount.table.cosmos.azure.com:443/;",
)