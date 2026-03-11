# CLI Integration Tests

This directory contains integration and unit tests for the rapyuta.io CLI.

## Test Setup

### Prerequisites

1. **Python Environment**: Ensure you have Python 3.8+ installed
2. **Dependencies**: Install test dependencies using `uv` or `pip`
   ```bash
   uv sync
   # or
   pip install -e ".[dev]"
   ```

### Configuration Files

The test suite requires two configuration files:

#### 1. `.test.config.json`

This file contains the rapyuta.io platform configuration and authentication details.

**Location**: `tests/.test.config.json`

⚠️ **Note**: This file is committed to the repository with basic environment configuration. You must add your authentication details locally before running tests.

**Committed Fields** (environment URLs):
```json
{
  "environment": "your-environment-name",
  "catalog_host": "https://...",
  "core_api_host": "https://...",
  "rip_host": "https://...",
  "v2api_host": "https://..."
}
```

**Additional Fields Required** (add these locally):
```json
{
  "email_id": "your-test-user@example.com",
  "auth_token": "your-auth-token",
  "organization_name": "YourOrgName",
  "project_name": "your-test-project",
}
```

**Setup**:
1. The file already exists with environment URLs
2. Add the authentication fields listed above with your credentials
3. Do not commit these changes (authentication fields should remain local)

#### 2. `.password`

This file contains passwords for test user accounts and is **not** committed to git.

**Location**: `tests/.password`

**Format**: Key-value pairs (one per line)
```
DEFAULT_PASSWORD=your-default-password
HWIL_USERNAME=your-hwil-username
HWIL_PASSWORD=your-hwil-password
```

**Setup**: Create this file from the example template:
```bash
cp tests/.password.example tests/.password
# Edit tests/.password with your actual credentials
```

⚠️ **Security**: The `.password` file is in `.gitignore` and should never be committed.

### Test Users

The test suite uses the following user accounts:

| User Account | Purpose | Password Source |
|-------------|---------|-----------------|
| `cli.superuser@rapyuta-robotics.com` | Super user with full permissions | `DEFAULT_PASSWORD` |
| `cli.test1@rapyuta-robotics.com` | Test user with limited permissions | `DEFAULT_PASSWORD` |
| `cli.test2@rapyuta-robotics.com` | Test user with different permissions | `DEFAULT_PASSWORD` |
| HWIL User | Hardware-in-the-Loop virtual device creation | `HWIL_USERNAME` + `HWIL_PASSWORD` |

**Organization**: All test users belong to the `CliTest` organization.

### Test Projects

Tests use the following projects (must exist in your organization):
- `test-project1`
- `test-project2`

### HWIL Requirement for File Upload Tests

⚠️ **Important**: File upload tests require HWIL (Hardware-in-the-Loop) access to create virtual devices.

**Prerequisites**:
- Valid HWIL credentials (`HWIL_USERNAME` and `HWIL_PASSWORD` in `.password` file)
- HWIL auth token in `.test.config.json`
- Access to HWIL service for virtual device creation

If HWIL credentials are not available, file upload tests will be skipped automatically.

## Running Tests

### Run All Tests
```bash
uv run pytest tests/
```

### Run Specific Test File
```bash
uv run pytest tests/main/test_fileupload.py
```

### Run Specific Test Class
```bash
uv run pytest tests/main/test_fileupload.py::TestFileUpload
```

### Run Specific Test Method
```bash
uv run pytest tests/main/test_fileupload.py::TestFileUpload::test_01_create_success_file_upload
```

### Run with Markers
```bash
# Run only integration tests
uv run pytest -m integration

# Run only slow tests
uv run pytest -m slow

# Skip slow tests
uv run pytest -m "not slow"
```

### Verbose Output
```bash
uv run pytest -v tests/
```

## Test Structure

### Fixtures (`conftest.py`)

The test suite uses pytest fixtures for:

- **CLI Runner**: `cli_runner` - Click's CliRunner for invoking CLI commands
- **Test Users**: `super_user`, `test_user_11`, `test_user_12` - Pre-configured user accounts
- **Test Projects**: `test_projects` - List of test project names
- **HWIL Login**: `hwil_login` - Authenticates with HWIL for virtual device operations
- **Device Setup**: `test_device_setup` - Creates a virtual device with pre-created files for testing
- **File Factory**: `device_file_factory` - Creates files on devices for testing

### Device Setup for File Upload Tests

The `test_device_setup` fixture:
1. Logs in as super user
2. Creates a virtual HWIL device (`test-upload-device`)
3. Waits for device to be online
4. Creates two test files on the device:
   - `small_file`: `/tmp/test-upload.txt` (100 bytes)
   - `large_file`: `/tmp/large-upload.txt` (20KB)
5. Returns device name and file paths for use in tests
6. Cleanup: Deletes all file uploads (device is preserved for faster re-runs)

## Test Workflow

Tests use `cli_runner.invoke()` to run CLI commands without spawning subprocesses:

```python
result = cli_runner.invoke(cli, ["device", "uploads", "list", device_name])
assert result.exit_code == 0
assert "expected-output" in result.output
```

This approach:
- Uses local code from your workspace
- Runs faster than subprocess execution
- Captures stdout, stderr, and exit codes
- No global CLI installation required

## Credentials Required

### For Basic Tests
- Email and password for test user accounts
- rapyuta.io platform auth token
- Organization and project details

### For File Upload Tests (Additional)
- HWIL username and password (for virtual device creation)
- HWIL auth token in `.test.config.json`


**Setup Workflow**:
1. Clone the repository (`.test.config.json` comes with environment URLs)
2. Add authentication fields to `.test.config.json` locally
3. Create `.password` file from `.password.example`
4. Never commit authentication credentials or the `.password` file

## Troubleshooting

### Tests Fail with Authentication Errors
- Verify `.test.config.json` has correct auth tokens
- Check that `.password` file exists and has correct passwords
- Ensure test user accounts exist in the organization

### Device Creation Fails
- Verify HWIL credentials are correct
- Check HWIL service is available
- Ensure you have permissions to create virtual devices

### File Upload Tests Fail
- Check that the virtual device is online
- Verify file paths exist on the device
- Ensure sufficient storage space on device
