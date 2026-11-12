---
trigger: always_on
description: "Google Cloud authentication (ADC-only), dynamic project resolution, client isolation, and container parity standards."
---

# Google Cloud & Infrastructure Standards

Applies whenever this project interacts with Google Cloud services, SDKs, or containers. Delete this rule file if the project never touches Google Cloud.

## 1. Authentication: Application Default Credentials (ADC) Only

* **Zero Service Account Keys:** Never create, store, or load Service Account JSON key files, `--key-file` flags, `gcloud auth activate-service-account`, or `GOOGLE_APPLICATION_CREDENTIALS` key paths. *(Enforced by `.agents/hooks/guard_secrets.py` and `.gitignore`.)*
* **Seamless Credential Inheritance:** Authenticate locally via `gcloud auth application-default login` and initialize GCP client libraries with default credentials (`google.auth.default()`) so identical code runs locally via ADC and in cloud runtimes via attached service accounts.

## 2. Project ID & Environment Isolation

* **Never Hardcode Real Project IDs:** Always use `"your-gcp-project-id"` as the placeholder in tracked source files, tests, docs, and committed notebook outputs.
* **Dynamic Runtime Resolution:** Resolve the active project ID at runtime in priority order: explicit caller argument -> `GOOGLE_CLOUD_PROJECT` environment variable -> local gitignored `.env` -> `google.auth.default()[1]` -> `"your-gcp-project-id"`.
* **CI Safety:** Skip live ADC smoke tests automatically when running on unauthenticated CI runners (`GITHUB_ACTIONS == "true"` without credentials).

## 3. Cloud Clients & Containers

* **Isolated Leaf Clients:** Keep GCP client instantiations in dedicated leaf modules so unit tests can mock them cleanly without network access.
* **Zero-Drift Containers:** Build Dockerfiles (Cloud Run, Vertex AI, Airflow, KFP) directly from `pyproject.toml` and `uv.lock` using `uv sync --frozen`.
