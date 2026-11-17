# I developed this file with Codex assistance; see PROCESS_LOG.md.
"""Project-scoped prerequisite provisioning; never deploy or handle application secrets."""

import argparse
import json
import subprocess  # nosec B404
from pathlib import Path

PROJECT = "assignment3-515003"
NUMBER = "1043695272988"
REGION = "us-central1"
BUCKET = PROJECT + "-a3-state"
RUNTIME = "a3-runtime@" + PROJECT + ".iam.gserviceaccount.com"
DEPLOY = "a3-deploy@" + PROJECT + ".iam.gserviceaccount.com"
POOL = "projects/" + NUMBER + "/locations/global/workloadIdentityPools/a3-github"
CONDITION = (
    "assertion.repository_id == '1460469388' && "
    "assertion.repository_owner_id == '77002960' && "
    "assertion.ref == 'refs/heads/main' && "
    "assertion.sub == 'repo:Arya-Wadhwani07@77002960/personal_agent@1460469388:environment:production' && "
    "assertion.workflow_ref == 'Arya-Wadhwani07/personal_agent/.github/workflows/release.yml@refs/heads/main'"
)


def commands():
    # Creates only named assignment resources. Execute once; an existing-resource error
    # stops the sequence for inspection rather than overwriting its policy.
    commands = [
        ["iam", "service-accounts", "create", "a3-runtime", "--display-name=A3 runtime"],
        ["iam", "service-accounts", "create", "a3-deploy", "--display-name=A3 release"],
        [
            "artifacts",
            "repositories",
            "create",
            "a3",
            "--repository-format=docker",
            "--location=" + REGION,
        ],
        [
            "storage",
            "buckets",
            "create",
            "gs://" + BUCKET,
            "--location=" + REGION,
            "--uniform-bucket-level-access",
            "--public-access-prevention",
            "--soft-delete-duration=0",
        ],
        [
            "storage",
            "buckets",
            "add-iam-policy-binding",
            "gs://" + BUCKET,
            "--member=serviceAccount:" + RUNTIME,
            "--role=roles/storage.objectAdmin",
        ],
        ["iam", "workload-identity-pools", "create", "a3-github", "--location=global"],
        [
            "iam",
            "workload-identity-pools",
            "providers",
            "create-oidc",
            "github",
            "--location=global",
            "--workload-identity-pool=a3-github",
            "--issuer-uri=https://token.actions.githubusercontent.com",
            "--attribute-mapping=google.subject=assertion.sub,attribute.repository_id=assertion.repository_id",
            "--attribute-condition=" + CONDITION,
        ],
        [
            "iam",
            "service-accounts",
            "add-iam-policy-binding",
            DEPLOY,
            "--role=roles/iam.workloadIdentityUser",
            "--member=principalSet://iam.googleapis.com/"
            + POOL
            + "/attribute.repository_id/1460469388",
        ],
        [
            "iam",
            "service-accounts",
            "add-iam-policy-binding",
            RUNTIME,
            "--role=roles/iam.serviceAccountUser",
            "--member=serviceAccount:" + DEPLOY,
        ],
        [
            "artifacts",
            "repositories",
            "add-iam-policy-binding",
            "a3",
            "--location=" + REGION,
            "--role=roles/artifactregistry.writer",
            "--member=serviceAccount:" + DEPLOY,
        ],
        [
            "iam",
            "roles",
            "create",
            "a3InstanceDeployer",
            "--title=A3 Instance deployer",
            "--permissions=run.instances.create,run.instances.get,run.instances.list,run.instances.update,run.instances.getIamPolicy,run.instances.setIamPolicy,run.operations.get,run.operations.list,run.locations.list,resourcemanager.projects.get",
            "--stage=GA",
        ],
        [
            "projects",
            "add-iam-policy-binding",
            PROJECT,
            "--member=serviceAccount:" + DEPLOY,
            "--role=projects/" + PROJECT + "/roles/a3InstanceDeployer",
            "--condition=None",
        ],
    ]
    return [["gcloud", *c, "--project=" + PROJECT, "--quiet", "--format=json"] for c in commands]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--start", type=int, default=0)
    args = parser.parse_args()
    if not 0 <= args.start < len(commands()):
        raise SystemExit("Invalid reviewed step")
    if not args.execute:
        print(json.dumps(commands(), indent=2))
        return
    out = Path(".cache/cloud")
    out.mkdir(parents=True, exist_ok=True)
    for index, command in enumerate(commands()):
        if index < args.start:
            continue
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)  # noqa: S603  # nosec B603
        record = out / ("provision-" + str(index) + ".json")
        record.write_text(
            json.dumps(
                {
                    "step": index,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            )
        )
        record.chmod(0o600)
        print(
            "Cloud prerequisite step",
            index,
            "passed" if result.returncode == 0 else "FAILED",
            flush=True,
        )
        if result.returncode:
            raise SystemExit("Inspect the private record before continuing")


if __name__ == "__main__":
    main()
