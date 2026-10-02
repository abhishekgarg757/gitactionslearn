# github-actions-demo

A tiny Python project used to teach GitHub Actions live in a classroom.

It is deliberately small: three functions, three tests, one Dockerfile, and two
workflows. Everything here is real — the workflows run on GitHub exactly as
written.

---

## 1. What the project does

`src/app.py` has three functions:

| Function              | Example          | Result |
| --------------------- | ---------------- | ------ |
| `add(a, b)`           | `add(2, 3)`      | `5`    |
| `multiply(a, b)`      | `multiply(2, 3)` | `6`    |
| `is_even(number)`     | `is_even(4)`     | `True` |

The app has no web server, no database, and no dependencies — it is just
something small that can be tested and shipped in a container.

---

## 2. Repository structure

```text
.
├── .github/
│   └── workflows/
│       ├── ci.yml            # tests + build (push + PR)
│       └── docker.yml        # tests → build → push to Docker Hub
├── src/
│   ├── __init__.py
│   └── app.py                # the three functions + main()
├── tests/
│   └── test_app.py           # pytest tests
├── conftest.py               # lets `pytest` import from `src` (see note)
├── Dockerfile
├── requirements.txt          # runtime dependencies (empty)
├── requirements-dev.txt      # adds pytest
├── .gitignore
└── README.md
```

---

## 3. Run the Python app locally

```bash
python -m src.app
```

Output:

```text
add(2, 3)      = 5
multiply(2, 3) = 6
is_even(4)     = True
is_even(7)     = False
```

---

## 4. Run the tests

```bash
pip install -r requirements-dev.txt
pytest
```

> **Note on `conftest.py`** — it is an empty file that exists only so `pytest`
> can find the `src` package. Running `python -m pytest` works without it, but
> the plain `pytest` command does not, so both the local and CI commands use it.

---

## 5. Build and run with Docker

```bash
docker build -t github-actions-demo .
docker run --rm github-actions-demo
```

The container prints the same output as step 3.

---

## 6. What each workflow does

### `.github/workflows/ci.yml` — CI

Runs on **push to `main`** and on **pull requests targeting `main`**.

```text
Checkout → Setup Python → Install deps → Run pytest → Build Docker image
```

It builds the image but never pushes it. PRs get a fast "does it still work?"
check without touching Docker Hub.

### `.github/workflows/docker.yml` — Docker

Runs on **push to `main`** and on **manual dispatch**.

Two jobs:

- `test` — installs dependencies and runs pytest
- `build-and-push` — `needs: test`, then builds and pushes to Docker Hub

---

## 7. Push vs Pull Request vs manual trigger

| Trigger           | What causes it                                   | Workflows that run   |
| ----------------- | ------------------------------------------------ | -------------------- |
| `push`            | You push a commit to `main`                      | `ci.yml`, `docker.yml` |
| `pull_request`    | You open or update a PR into `main`              | `ci.yml` only        |
| `workflow_dispatch` | You click **Run workflow** in the Actions tab  | `docker.yml` only    |

The reason PRs run CI but not Docker: you don't want a PR to publish an image.
Only code that has landed on `main` is allowed to publish.

---

## 8. Secrets

Secrets are encrypted values stored in GitHub, not in your code. They are
exposed to workflows only at run time, and GitHub masks them in the logs.

You can read one in a workflow with `${{ secrets.NAME }}`.

This project uses two:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

**Never write a token into a workflow, a Dockerfile, or any file in the repo.**

---

## 9. Environment

The push job uses:

```yaml
environment: production
```

`production` is a **GitHub Environment**, a separate layer on top of a
repository. It can have:

- **Protection rules** — require approval before the job starts
- **Required reviewers** — a person must approve a run
- **Environment secrets** — secrets scoped only to this environment
- **Environment variables** — variables scoped only to this environment
- **Deployment protection rules** — wait for a timer or an external check

Because the image push is a real publish, gating it behind an environment is the
right place for a human "yes, ship it" step.

Create it at: **GitHub → your repo → Settings → Environments → New environment**.

---

## 10. Environment variables

`env`, `vars`, and `secrets` look similar but are different:

| | Written in | Visible in logs | For |
| --- | --- | --- | --- |
| `env` | The workflow YAML | Yes | Non-sensitive values for this run |
| `vars` | Repo/Environment settings | Yes | Config you want to change without editing YAML |
| `secrets` | Repo/Environment settings | Masked | Passwords, tokens, keys |

This project sets a plain environment variable:

```yaml
env:
  APP_NAME: github-actions-demo
```

`vars` is the one to reach for when a value should live in the GitHub UI rather
than in the file. Both are readable in YAML; only `secrets` is hidden.

---

## 11. `needs`

```yaml
build-and-push:
  needs: test
```

`needs` declares a dependency between jobs. The job that declares it waits for
the named job to finish, and if that job fails, it is **skipped entirely**.

So if the tests fail, no image is built and nothing is pushed to Docker Hub.

---

## 12. How to configure Docker Hub

1. Create a free account at <https://hub.docker.com>.
2. In your Docker Hub account, open **Account Settings → Access tokens**.
3. Click **Generate new token**, choose **Read & Write**, and copy the token.

Keep it somewhere safe — Docker Hub shows it only once.

---

## 13. Add the secrets

Go to:

```text
GitHub → your repo → Settings → Secrets and variables → Actions
```

Under **Secrets** → **New repository secret**, add:

| Name | Value |
| ---- | ----- |
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN`   | The access token from step 12 |

The workflow builds the image name as:

```text
<DOCKERHUB_USERNAME>/github-actions-demo:latest
```

No username or token is hard-coded anywhere in this repository.

---

## 14. Running the demo

Push the repo to GitHub, then walk through these.

**Demo 1 — Push code → workflow runs**

```bash
echo "# demo 1" >> README.md
git add README.md
git commit -m "demo 1"
git push
```

Open the **Actions** tab. Both `CI` and `Docker` start.

**Demo 2 — Create a Pull Request → CI runs**

```bash
git checkout -b feature-branch
echo "# demo 2" >> README.md
git add README.md
git commit -m "demo 2"
git push -u origin feature-branch
```

Open a PR from `feature-branch` into `main`. Only `CI` runs.

**Demo 3 — Break a test → CI fails**

On the PR branch, edit `tests/test_app.py`:

```python
assert add(2, 3) == 6   # wrong on purpose
```

Push. `CI` fails at **Run tests**. The Docker image is never built.

**Demo 4 — Fix the test → CI passes**

```python
assert add(2, 3) == 5   # correct again
```

Push. `CI` goes green.

**Demo 5 — Push to main → image is pushed to Docker Hub**

```bash
git checkout main
git merge feature-branch
git push
```

`CI` and `Docker` both run. The `test` job runs pytest, then
`build-and-push` logs in and pushes to Docker Hub. Check your tags at
<https://hub.docker.com/r/\<DOCKERHUB_USERNAME\>/github-actions-demo>.

**Demo 6 — Run the workflow manually**

Go to **Actions → Docker → Run workflow → Run workflow** (with `main` selected).

That is `workflow_dispatch`. It reruns the whole test → build → push flow
without any code change.

**Extra — show the `production` environment**

Go to **Settings → Environments**. Rename it or add a required reviewer, then
rerun Demo 6. The push job now pauses until the reviewer approves it.

---

## Glossary

| Term | Meaning |
| ---- | ------- |
| `on` | When the workflow runs (push, pull_request, workflow_dispatch) |
| `jobs` | The separate units of work in a workflow |
| `steps` | The individual tasks inside a job, run in order |
| `runs-on` | Which machine the job runs on |
| `uses` | Run a pre-built action, e.g. `actions/checkout@v4` |
| `run` | Run a shell command |
| `with` | Inputs passed to an action |
| `env` | Environment variables for the job |
| `secrets` | Encrypted values, masked in logs |
| `needs` | Wait for another job, and skip this one if it failed |
| `environment` | Run the job inside a named GitHub Environment |
