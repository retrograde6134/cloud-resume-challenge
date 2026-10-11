# Cloud Resume Challenge — Azure

My take on the [Cloud Resume Challenge](https://cloudresumechallenge.dev/), Azure track.

**Live:** [alexlittle.dev](https://alexlittle.dev)

## What this is

A static resume site with a visitor counter. The counter is a serverless
Python function that reads and increments a row in Cosmos DB — it exists so
the project has something running in Azure beyond static hosting.

## Architecture

    Browser
      │
      ▼
    Azure Static Web App  (global CDN, managed HTTPS, custom domain)
      │
      │  fetch POST /api/visitor
      ▼
    Azure Function  (Python 3.12, Consumption plan, HTTP trigger)
      │
      ▼
    Cosmos DB  (Table API, serverless capacity)

Two GitHub Actions workflows:

- **Frontend** — builds and deploys the Static Web App on push to `main`
- **Backend** — runs pytest, then deploys the Function App only if tests pass

Backend deploys use OIDC federated credentials. There's no stored Azure
secret in the repo.

## Stack

| Layer | Service | Notes |
|---|---|---|
| Frontend | Azure Static Web Apps | Free tier, auto-deploy from GitHub |
| API | Azure Functions | Python 3.12, Consumption plan, Linux |
| Database | Cosmos DB | Table API, serverless — pennies per month |
| IaC | Bicep | Cosmos, Storage, Function App |
| CI/CD | GitHub Actions | Separate workflows for frontend and backend |

## Running it locally

### Frontend

```bash
cd frontend
python3 -m http.server 8000
```

Then open http://localhost:8000. The visitor counter will fail until you point
`API_BASE_URL` in `script.js` at a running backend (or the deployed one).

### Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Add COSMOS_CONNECTION_STRING to local.settings.json (see backend/.gitignore)
# You'll also need Azurite for local AzureWebJobsStorage:
#   npm install -g azurite && azurite --location ~/azurite &

func start
```

Tests:

```bash
python -m pytest -v
```

### Infrastructure

```bash
az deployment group what-if \
  --resource-group cloud-resume-rg \
  --template-file infra/main.bicep \
  --parameters infra/main.parameters.json
```

Always run `what-if` first. It'll catch anything that would replace a live
resource rather than update it.

## Things that bit me

A few that aren't obvious from the docs, in case they save you an afternoon:

- **Cosmos DB has two locations.** The top-level `location` on the account is
  metadata and can't be changed after creation. The `properties.locations`
  array is where the data actually lives. These are usually different, and
  ARM will reject a deployment if you mix them up.

- **Function App CORS is host-level.** Setting `Access-Control-Allow-Origin`
  in your function code isn't enough for preflight requests. The Functions
  host intercepts `OPTIONS` before your handler runs, and if the app's CORS
  settings are empty, it returns 404 with no headers. Configure via
  `az functionapp cors add`.

- **GitHub OIDC subject claims changed.** If your workflow uses an
  `environment:`, the subject is
  `repo:owner/repo:environment:name`, not `:ref:refs/heads/main`. GitHub also
  now embeds immutable owner/repo IDs in the subject. Match the exact string
  Azure reports in the error, or the federated credential won't validate.

- **Linux Consumption plans don't expose `serverFarmId`.** Referencing a plan
  with `existing` in Bicep works, but the property comes back empty when you
  query the app. Not a misconfiguration — the dynamic plan is abstracted.

- **`az functionapp cors add` replaces the list.** Passing `--allowed-origins`
  twice in one command only keeps the last value. Pass both in one flag,
  space-separated.

## Notes on scope

The Bicep template covers the backend infrastructure. The Static Web App is
intentionally not in it — managing it via Bicep requires passing a GitHub PAT
as a secure parameter, which creates a bootstrapping problem when the CI/CD
that would hold that secret depends on the SWA existing in the first place.
For a single-environment portfolio project, the trade-off isn't worth it.

## Contact

- [LinkedIn](https://www.linkedin.com/in/aclittle)
- [GitHub](https://github.com/retrograde6134)