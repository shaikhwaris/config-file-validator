# Config File Validator

A comprehensive Python tool for validating YAML/JSON configuration files against schemas for Docker Compose, Kubernetes manifests, Terraform, and other common configuration formats.

## Features

- ✅ **YAML/JSON Syntax Validation** - Validates basic syntax correctness
- 🐳 **Docker Compose Validation** - Validates Docker Compose v1 and v2 formats
- ☸️ **Kubernetes Manifest Validation** - Validates K8s YAML manifests
- 🏗️ **Terraform Validation** - Basic HCL validation for Terraform files
- 📋 **JSON Schema Validation** - Validate JSON files against JSON Schema
- 🔍 **Auto-detection** - Automatically detects file types based on filename and content
- 🚀 **CI/CD Ready** - GitHub Actions workflows included

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### GitHub Action

This repository can be used as a GitHub Action in your workflows:

```yaml
name: Validate Config Files

on:
  pull_request:
    paths:
      - '**.yaml'
      - '**.yml'
      - '**.json'
      - '**.tf'
      - 'docker-compose*.yml'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Validate config files
        uses: ./  # Use local action
        # Or use: your-org/config-file-validator@v1
        with:
          files: |
            docker-compose.yml
            k8s/*.yaml
            config/*.json
          file-type: 'auto'  # auto, yaml, json, docker-compose, kubernetes, terraform
          fail-on-error: 'true'
      
      - name: Check validation results
        if: always()
        run: |
          echo "Valid: ${{ steps.validate.outputs.valid }}"
          echo "Files checked: ${{ steps.validate.outputs.files-checked }}"
          echo "Files passed: ${{ steps.validate.outputs.files-passed }}"
          echo "Files failed: ${{ steps.validate.outputs.files-failed }}"
```

**Action Inputs:**
- `files` (required): Comma-separated list of files or directories to validate. Supports glob patterns.
- `file-type` (optional): File type to validate (`yaml`, `json`, `docker-compose`, `kubernetes`, `terraform`, `auto`). Default: `auto`
- `schema` (optional): Path to JSON Schema file for JSON validation
- `fail-on-error` (optional): Whether to fail the action if validation errors are found. Default: `true`
- `working-directory` (optional): Working directory for file paths. Default: `.`

**Action Outputs:**
- `valid`: Whether all files passed validation
- `errors`: Validation errors found (if any)
- `files-checked`: Number of files checked
- `files-passed`: Number of files that passed validation
- `files-failed`: Number of files that failed validation

### Command Line

```bash
# Validate a single file (auto-detect type)
python validator.py config.yaml

# Validate a specific file type
python validator.py docker-compose.yml --type docker-compose

# Validate multiple files
python validator.py file1.yaml file2.json file3.tf

# Validate a directory
python validator.py /path/to/configs/

# Validate JSON against a schema
python validator.py config.json --schema schema.json
```

### Python API

```python
from validator import ConfigValidator

validator = ConfigValidator()

# Validate a file
valid, errors, file_type = validator.validate_file('docker-compose.yml')
if not valid:
    for error in errors:
        print(f"Error: {error}")

# Validate a directory
valid, errors, file_types = validator.validate_directory('./configs/')
```

## Supported File Types

- **YAML** (`.yaml`, `.yml`) - Basic YAML syntax validation
- **JSON** (`.json`) - JSON syntax validation
- **Docker Compose** (`docker-compose.yml`, `compose.yml`) - Structure validation
- **Kubernetes** (detected by content or filename) - Manifest validation
- **Terraform** (`.tf`, `.tf.json`) - Basic HCL validation

## Examples

### Valid Docker Compose File

```yaml
version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
```

### Valid Kubernetes Manifest

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
    - name: nginx
      image: nginx:latest
```

### Valid Terraform File

```hcl
resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License

