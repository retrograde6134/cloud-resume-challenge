# Cloud Resume Challenge (Azure)

Resume site with a visitor counter. [alexlittle.dev](https://alexlittle.dev).

The counter is a Python function on Azure Functions that reads and increments a row in Cosmos DB. The rest is static HTML, CSS, and JS.

## Architecture

```
Browser
  │
  ▼
Static Web Apps (CDN + HTTPS + custom domain)
  │  POST /api/visitor
  ▼
Azure Functions (Python 3.12, Consumption, Linux)
  │
  ▼
Cosmos DB (Table API, serverless)
```

Two workflows in GitHub Actions. One builds the frontend and deploys it to Static Web Apps on push to `main`. The other runs pytest and deploys the function if the tests pass. Backend deploys use OIDC, so no Azure credential is stored anywhere.

Infrastructure is Bicep, under `infra/`.

## Local

Frontend:

```
cd frontend
python3 -m http.server 8000
```

The counter won't work until the backend is reachable. Either run it locally or change `API_BASE_URL` in `script.js` to point at the deployed one.

Backend:

```
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
func start
```

Needs `COSMOS_CONNECTION_STRING` in `local.settings.json` and Azurite running for `AzureWebJobsStorage`.

```
python -m pytest -v
```

Infra:

```
az deployment group what-if \
  --resource-group cloud-resume-rg \
  --template-file infra/main.bicep \
  --parameters infra/main.parameters.json
```

Run what-if first.

## Notes

Cosmos DB accounts have two locations that mean different things. The top-level `location` is metadata and it's fixed at creation. The `properties.locations` array is where data actually lives. Mine are `canadacentral` and `westus2` respectively, and ARM rejected the first Bicep deploy because I had them confused.

Function App CORS is configured at the host, not in your function code. The Functions runtime intercepts OPTIONS before your handler runs. If the app's CORS list is empty you get a 404 with no headers, which the browser reports as a CORS failure. `az functionapp cors add` is the fix.

GitHub's OIDC subject claim for a job with an `environment:` is `repo:owner/repo:environment:name`, not the branch ref. They also started embedding immutable owner and repo IDs into the subject string. If the federated credential doesn't match exactly what Azure reports in the error, login fails.

`serverFarmId` comes back empty for Linux Consumption apps. The plan exists, the API just doesn't expose it. Referencing it with `existing` in Bicep still works.

`az functionapp cors add` overwrites the list if you pass `--allowed-origins` more than once. Pass every origin in one flag, space separated.

## Scope

Bicep covers Cosmos, Storage, and the Function App. The Static Web App isn't included. Adding it means passing a GitHub PAT as a secure deployment parameter, and that's circular: the CI/CD that would hold the secret depends on the SWA already existing. Not worth solving for one environment.

## Contact

[LinkedIn](https://www.linkedin.com/in/aclittle) · [GitHub](https://github.com/retrograde6134)