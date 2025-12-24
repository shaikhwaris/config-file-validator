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
valid, errors = validator.validate_file('docker-compose.yml')
if not valid:
    for error in errors:
        print(f"Error: {error}")

# Validate a directory
valid, errors = validator.validate_directory('./configs/')
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

