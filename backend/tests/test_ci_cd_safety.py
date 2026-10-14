"""SmartMail AI — Automated CI/CD Safety & Frontend API Configuration Tests.

Verifies:
1. CI workflow does NOT auto-deploy on ordinary git pushes.
2. Staging deployment requires explicit manual workflow_dispatch with deploy_to_staging=true.
3. Missing deployment inputs default to false (safe opt-in).
4. Production deployment requires separate workflow_dispatch with deploy_to_production=true.
5. Frontend consistently uses canonical VITE_API_BASE_URL (no VITE_API_URL mismatches).
6. Staging and production deployment paths remain strictly isolated.
7. Build-time validation prevents silent localhost fallback in production/staging builds.
"""

from pathlib import Path
import re
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CI_WORKFLOW_FILE = REPO_ROOT / ".github" / "workflows" / "ci-cd.yml"
APP_TSX_FILE = REPO_ROOT / "frontend" / "src" / "App.tsx"
VITE_CONFIG_FILE = REPO_ROOT / "frontend" / "vite.config.ts"
FRONTEND_DOCKERFILE = REPO_ROOT / "frontend" / "Dockerfile"
DOCKER_COMPOSE_FILE = REPO_ROOT / "docker-compose.yml"


@pytest.fixture(scope="module")
def workflow_content() -> str:
    """Load CI/CD workflow YAML text."""
    assert CI_WORKFLOW_FILE.is_file(), f"Missing CI workflow file at {CI_WORKFLOW_FILE}"
    return CI_WORKFLOW_FILE.read_text(encoding="utf-8")


def test_workflow_dispatch_defaults_to_no_deployment(workflow_content: str):
    """Ensure manual dispatch inputs default to false (zero accidental deployments)."""
    staging_default = re.search(r"deploy_to_staging:.*?default:\s*(false|true)", workflow_content, re.DOTALL)
    assert staging_default is not None, "deploy_to_staging input definition not found"
    assert staging_default.group(1) == "false", "deploy_to_staging MUST default to false"

    prod_default = re.search(r"deploy_to_production:.*?default:\s*(false|true)", workflow_content, re.DOTALL)
    assert prod_default is not None, "deploy_to_production input definition not found"
    assert prod_default.group(1) == "false", "deploy_to_production MUST default to false"


def test_deploy_staging_does_not_trigger_on_push(workflow_content: str):
    """Ensure deploy-staging does NOT automatically deploy on ordinary branch pushes."""
    # Find deploy-staging block
    staging_block_match = re.search(r"deploy-staging:\s*\n(.*?)(?=\n\s*deploy-production:|\Z)", workflow_content, re.DOTALL)
    assert staging_block_match is not None, "deploy-staging block not found"
    staging_block = staging_block_match.group(1)

    # Condition must require workflow_dispatch, NOT trigger on push
    if_line_match = re.search(r"if:\s*(.*)", staging_block)
    assert if_line_match is not None, "deploy-staging missing 'if:' condition"
    if_cond = if_line_match.group(1)

    assert "github.event_name == 'workflow_dispatch'" in if_cond, (
        "deploy-staging must require github.event_name == 'workflow_dispatch'"
    )
    assert "github.event.inputs.deploy_to_staging == 'true'" in if_cond, (
        "deploy-staging must require explicit deploy_to_staging == 'true'"
    )
    assert "github.event_name == 'push'" not in if_cond, (
        "deploy-staging must NOT execute on ordinary branch push"
    )


def test_deploy_production_requires_explicit_opt_in(workflow_content: str):
    """Ensure deploy-production is gated strictly behind explicit manual dispatch."""
    prod_block_match = re.search(r"deploy-production:\s*\n(.*)", workflow_content, re.DOTALL)
    assert prod_block_match is not None, "deploy-production block not found"
    prod_block = prod_block_match.group(1)

    if_line_match = re.search(r"if:\s*(.*)", prod_block)
    assert if_line_match is not None, "deploy-production missing 'if:' condition"
    if_cond = if_line_match.group(1)

    assert "github.event_name == 'workflow_dispatch'" in if_cond
    assert "github.event.inputs.deploy_to_production == 'true'" in if_cond
    assert "github.event_name == 'push'" not in if_cond


def test_ci_validation_jobs_configured_for_prs_and_pushes(workflow_content: str):
    """Ensure CI validation (backend tests, frontend build, terraform validate) runs on both PRs and pushes."""
    assert "push:" in workflow_content
    assert "pull_request:" in workflow_content

    for job in ["backend-test:", "frontend-build:", "terraform-validate:", "docker-validate:"]:
        assert job in workflow_content, f"Validation job {job} missing from workflow"


def test_canonical_vite_api_base_url_used_across_all_configs(workflow_content: str):
    """Verify that VITE_API_BASE_URL is canonical and deprecated VITE_API_URL is nowhere in CI."""
    assert "VITE_API_URL" not in workflow_content, (
        "Deprecated variable VITE_API_URL found in .github/workflows/ci-cd.yml; use VITE_API_BASE_URL"
    )

    # Check App.tsx
    app_tsx = APP_TSX_FILE.read_text(encoding="utf-8")
    assert "import.meta.env.VITE_API_BASE_URL" in app_tsx
    assert "import.meta.env.VITE_API_URL" not in app_tsx

    # Check Dockerfile
    dockerfile = FRONTEND_DOCKERFILE.read_text(encoding="utf-8")
    assert "VITE_API_BASE_URL" in dockerfile
    assert "VITE_API_URL" not in dockerfile

    # Check docker-compose.yml
    compose = DOCKER_COMPOSE_FILE.read_text(encoding="utf-8")
    assert "VITE_API_BASE_URL" in compose
    assert "VITE_API_URL" not in compose


def test_frontend_does_not_silently_fallback_to_localhost_in_production():
    """Verify App.tsx only falls back to localhost when running in development mode."""
    app_tsx = APP_TSX_FILE.read_text(encoding="utf-8")
    # Verify that 'http://localhost:5000' is protected by DEV check
    assert "import.meta.env.DEV ? 'http://localhost:5000'" in app_tsx or (
        "import.meta.env.DEV" in app_tsx and "localhost:5000" in app_tsx
    ), "App.tsx must not silently default to localhost in production mode"


def test_vite_config_enforces_strict_api_url_for_deploy_builds():
    """Verify frontend/vite.config.ts implements build-time check when STRICT_API_URL=true."""
    vite_config = VITE_CONFIG_FILE.read_text(encoding="utf-8")
    assert "STRICT_API_URL" in vite_config
    assert "VITE_API_BASE_URL" in vite_config
    assert "BUILD FAILURE" in vite_config


def test_staging_and_production_environments_distinct(workflow_content: str):
    """Verify that staging and production deployment jobs declare distinct environment scopes."""
    staging_env_match = re.search(r"deploy-staging:.*?environment:\s*\n\s*name:\s*([a-zA-Z0-9_-]+)", workflow_content, re.DOTALL)
    assert staging_env_match is not None
    assert staging_env_match.group(1) == "staging"

    prod_env_match = re.search(r"deploy-production:.*?environment:\s*\n\s*name:\s*([a-zA-Z0-9_-]+)", workflow_content, re.DOTALL)
    assert prod_env_match is not None
    assert prod_env_match.group(1) == "production"
