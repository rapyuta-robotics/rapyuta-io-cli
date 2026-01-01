# Prints this help message
default:
    @just --list

RIO := "timeout 5 uv run rio"
PYTEST := "uv run pytest"
DIR := justfile_directory() + "/tests"
VERBOSE := "false"
COVERAGE := "false"


# Run all tests sequentially to avoid resource conflicts  
run-all COVERAGE="false":
    #!/bin/bash
    set -euo pipefail
    echo "Running all tests sequentially to prevent resource conflicts..."
    
    # Set coverage flags if requested
    COVERAGE_FLAGS=""
    if [ "{{COVERAGE}}" = "true" ]; then
        COVERAGE_FLAGS="--cov=riocli --cov-report=html --cov-report=term-missing"
        echo "Coverage reporting enabled"
    fi
    
    # Run tests in a specific order to manage dependencies
    echo "=== Running Authentication Tests ==="
    {{PYTEST}} {{DIR}}/main/test_auth.py -v $COVERAGE_FLAGS
    
    echo "=== Running Project Tests ==="  
    {{PYTEST}} {{DIR}}/main/test_project.py -v $COVERAGE_FLAGS
    
    echo "=== Running Package Tests ==="
    {{PYTEST}} {{DIR}}/main/test_packages.py -v $COVERAGE_FLAGS
    
    echo "=== Running Secret Tests ==="
    {{PYTEST}} {{DIR}}/main/test_secrets.py -v $COVERAGE_FLAGS
    
    echo "=== Running Static Route Tests ==="
    {{PYTEST}} {{DIR}}/main/test_staticroute.py -v $COVERAGE_FLAGS
    
    echo "=== Running Service Account Tests ==="
    {{PYTEST}} {{DIR}}/main/test_service_accounts.py -v $COVERAGE_FLAGS
    
    echo "=== Running Deployment Tests ==="
    {{PYTEST}} {{DIR}}/main/test_deployment.py -v $COVERAGE_FLAGS
    
    echo "=== Running Usergroup Tests ==="
    {{PYTEST}} {{DIR}}/main/test_usergroup.py -v $COVERAGE_FLAGS
    
    echo "All tests completed successfully!"
    if [ "{{COVERAGE}}" = "true" ]; then
        echo "Coverage report generated in htmlcov/ directory"
    fi

# Run tests for a specific resource type
run RESOURCE COVERAGE="false":
    #!/bin/bash
    set -euo pipefail
    
    # Set coverage flags if requested
    COVERAGE_FLAGS=""
    if [ "{{COVERAGE}}" = "true" ]; then
        COVERAGE_FLAGS="--cov=riocli --cov-report=html --cov-report=term-missing"
        echo "Coverage reporting enabled"
    fi
    
    case "{{RESOURCE}}" in
        "auth"|"authentication")
            echo "Running Authentication tests..."
            {{PYTEST}} {{DIR}}/main/test_auth.py -v $COVERAGE_FLAGS
            ;;
        "project"|"projects")
            echo "Running Project tests..."
            {{PYTEST}} {{DIR}}/main/test_project.py -v $COVERAGE_FLAGS
            ;;
        "package"|"packages")
            echo "Running Package tests..."
            {{PYTEST}} {{DIR}}/main/test_packages.py -v $COVERAGE_FLAGS
            ;;
        "secret"|"secrets")
            echo "Running Secret tests..."
            {{PYTEST}} {{DIR}}/main/test_secrets.py -v $COVERAGE_FLAGS
            ;;
        "staticroute"|"static-route"|"static_route")
            echo "Running Static Route tests..."
            {{PYTEST}} {{DIR}}/main/test_staticroute.py -v $COVERAGE_FLAGS
            ;;
        "service-account"|"service_account"|"serviceaccount"|"sa")
            echo "Running Service Account tests..."
            {{PYTEST}} {{DIR}}/main/test_service_accounts.py -v $COVERAGE_FLAGS
            ;;
        "deployment"|"deployments")
            echo "Running Deployment tests..."
            {{PYTEST}} {{DIR}}/main/test_deployment.py -v $COVERAGE_FLAGS
            ;;
        "usergroup"|"usergroups"|"user-group"|"user_group")
            echo "Running Usergroup tests..."
            {{PYTEST}} {{DIR}}/main/test_usergroup.py -v $COVERAGE_FLAGS
            ;;
        "all")
            just run-all {{COVERAGE}}
            ;;
        *)
            echo "Unknown resource type: {{RESOURCE}}"
            echo "Available resources: auth, project, package, secret, staticroute, service-account, deployment, usergroup"
            echo "Use 'just run all' to run all tests"
            echo "Add 'true' as second argument to enable coverage: just run <resource> true"
            exit 1
            ;;
    esac
    
    if [ "{{COVERAGE}}" = "true" ]; then
        echo "Coverage report generated in htmlcov/ directory"
    fi

# Run uv sync --upgrade and rio --help for multiple Python versions
sync-and-help:
    #!/bin/bash
    set -euo pipefail

    PY_VERSIONS=("3.10" "3.11" "3.12" "3.13")
    for PY_VER in "${PY_VERSIONS[@]}"; do
        echo "=== Using Python $PY_VER ==="
        echo "-- Running: uv sync --upgrade"
        uv sync --upgrade -p $PY_VER || echo "uv sync failed for Python $PY_VER"

        echo "-- Running: rio --help"
        rio --help || echo "rio --help failed for Python $PY_VER"
        echo
    done