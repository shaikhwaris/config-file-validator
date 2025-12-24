#!/usr/bin/env python3
"""
Tests for Config File Validator
"""

import json
import unittest
import tempfile
import os
from pathlib import Path
from validator import ConfigValidator


class TestConfigValidator(unittest.TestCase):
    """Test cases for ConfigValidator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.validator = ConfigValidator()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_temp_file(self, content: str, filename: str) -> str:
        """Create a temporary file with content"""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def test_validate_valid_yaml(self):
        """Test validation of valid YAML"""
        content = """
key1: value1
key2: value2
nested:
  key3: value3
"""
        file_path = self.create_temp_file(content, 'test.yaml')
        valid, errors = self.validator.validate_yaml(file_path)
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_invalid_yaml(self):
        """Test validation of invalid YAML"""
        content = """
key1: value1
  invalid_indent: value2
"""
        file_path = self.create_temp_file(content, 'test.yaml')
        valid, errors = self.validator.validate_yaml(file_path)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_valid_json(self):
        """Test validation of valid JSON"""
        content = '{"key1": "value1", "key2": "value2"}'
        file_path = self.create_temp_file(content, 'test.json')
        valid, errors = self.validator.validate_json(file_path)
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_invalid_json(self):
        """Test validation of invalid JSON"""
        content = '{"key1": "value1", "key2": }'
        file_path = self.create_temp_file(content, 'test.json')
        valid, errors = self.validator.validate_json(file_path)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_valid_docker_compose(self):
        """Test validation of valid Docker Compose file"""
        content = """
version: '3.8'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
  db:
    image: postgres:13
"""
        file_path = self.create_temp_file(content, 'docker-compose.yml')
        valid, errors = self.validator.validate_docker_compose(file_path)
        self.assertTrue(valid, f"Errors: {errors}")
        self.assertEqual(len(errors), 0)
    
    def test_validate_docker_compose_v2(self):
        """Test validation of Docker Compose v2 (no version)"""
        content = """
services:
  web:
    image: nginx:latest
"""
        file_path = self.create_temp_file(content, 'compose.yml')
        valid, errors = self.validator.validate_docker_compose(file_path)
        self.assertTrue(valid, f"Errors: {errors}")
        self.assertEqual(len(errors), 0)
    
    def test_validate_invalid_docker_compose(self):
        """Test validation of invalid Docker Compose file"""
        content = """
version: '3.8'
services:
  web:
    # Missing image or build
"""
        file_path = self.create_temp_file(content, 'docker-compose.yml')
        valid, errors = self.validator.validate_docker_compose(file_path)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_valid_kubernetes_manifest(self):
        """Test validation of valid Kubernetes manifest"""
        content = """
apiVersion: v1
kind: Pod
metadata:
  name: test-pod
spec:
  containers:
    - name: test-container
      image: nginx:latest
"""
        file_path = self.create_temp_file(content, 'pod.yaml')
        valid, errors = self.validator.validate_kubernetes_manifest(file_path)
        self.assertTrue(valid, f"Errors: {errors}")
        self.assertEqual(len(errors), 0)
    
    def test_validate_kubernetes_with_group(self):
        """Test validation of Kubernetes manifest with API group"""
        content = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-deployment
spec:
  replicas: 3
"""
        file_path = self.create_temp_file(content, 'deployment.yaml')
        valid, errors = self.validator.validate_kubernetes_manifest(file_path)
        self.assertTrue(valid, f"Errors: {errors}")
        self.assertEqual(len(errors), 0)
    
    def test_validate_invalid_kubernetes_manifest(self):
        """Test validation of invalid Kubernetes manifest"""
        content = """
kind: Pod
# Missing apiVersion and metadata
spec:
  containers: []
"""
        file_path = self.create_temp_file(content, 'pod.yaml')
        valid, errors = self.validator.validate_kubernetes_manifest(file_path)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_valid_terraform(self):
        """Test validation of valid Terraform file"""
        content = """
resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
  
  tags = {
    Name = "ExampleInstance"
  }
}
"""
        file_path = self.create_temp_file(content, 'main.tf')
        valid, errors = self.validator.validate_terraform(file_path)
        self.assertTrue(valid, f"Errors: {errors}")
        self.assertEqual(len(errors), 0)
    
    def test_validate_invalid_terraform_braces(self):
        """Test validation of Terraform file with unbalanced braces"""
        content = """
resource "aws_instance" "example" {
  ami = "ami-12345678"
  # Missing closing brace
"""
        file_path = self.create_temp_file(content, 'main.tf')
        valid, errors = self.validator.validate_terraform(file_path)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_terraform_no_blocks(self):
        """Test validation of file with no Terraform blocks"""
        content = """
# This is just a comment
some_random_text = "value"
"""
        file_path = self.create_temp_file(content, 'main.tf')
        valid, errors = self.validator.validate_terraform(file_path)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_detect_file_type_yaml(self):
        """Test file type detection for YAML"""
        content = "key: value"
        file_path = self.create_temp_file(content, 'config.yaml')
        file_type = self.validator.detect_file_type(file_path)
        self.assertEqual(file_type, 'yaml')
    
    def test_detect_file_type_json(self):
        """Test file type detection for JSON"""
        content = '{"key": "value"}'
        file_path = self.create_temp_file(content, 'config.json')
        file_type = self.validator.detect_file_type(file_path)
        self.assertEqual(file_type, 'json')
    
    def test_detect_file_type_docker_compose(self):
        """Test file type detection for Docker Compose"""
        content = """
services:
  web:
    image: nginx
"""
        file_path = self.create_temp_file(content, 'docker-compose.yml')
        file_type = self.validator.detect_file_type(file_path)
        self.assertEqual(file_type, 'docker-compose')
    
    def test_detect_file_type_kubernetes(self):
        """Test file type detection for Kubernetes"""
        content = """
apiVersion: v1
kind: Pod
metadata:
  name: test
"""
        file_path = self.create_temp_file(content, 'k8s-pod.yaml')
        file_type = self.validator.detect_file_type(file_path)
        self.assertEqual(file_type, 'kubernetes')
    
    def test_detect_file_type_terraform(self):
        """Test file type detection for Terraform"""
        content = 'resource "aws_instance" "test" {}'
        file_path = self.create_temp_file(content, 'main.tf')
        file_type = self.validator.detect_file_type(file_path)
        self.assertEqual(file_type, 'terraform')
    
    def test_validate_file_not_found(self):
        """Test validation of non-existent file"""
        file_path = os.path.join(self.temp_dir, 'nonexistent.yaml')
        valid, errors, file_type = self.validator.validate_file(file_path)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
        self.assertEqual(file_type, 'unknown')
    
    def test_validate_json_schema_valid(self):
        """Test JSON schema validation with valid data"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name"]
        }
        data = {"name": "John", "age": 30}
        
        schema_path = self.create_temp_file(
            json.dumps(schema, indent=2), 'schema.json'
        )
        data_path = self.create_temp_file(
            json.dumps(data, indent=2), 'data.json'
        )
        
        valid, errors = self.validator.validate_json_schema(data_path, schema_path)
        self.assertTrue(valid, f"Errors: {errors}")
        self.assertEqual(len(errors), 0)
    
    def test_validate_json_schema_invalid(self):
        """Test JSON schema validation with invalid data"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name"]
        }
        data = {"age": 30}  # Missing required 'name'
        
        schema_path = self.create_temp_file(
            json.dumps(schema, indent=2), 'schema.json'
        )
        data_path = self.create_temp_file(
            json.dumps(data, indent=2), 'data.json'
        )
        
        valid, errors = self.validator.validate_json_schema(data_path, schema_path)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_directory(self):
        """Test directory validation"""
        # Create valid files
        valid_yaml = "key: value"
        valid_json = '{"key": "value"}'
        
        self.create_temp_file(valid_yaml, 'config.yaml')
        self.create_temp_file(valid_json, 'config.json')
        
        valid, errors, file_types = self.validator.validate_directory(self.temp_dir)
        self.assertTrue(valid, f"Errors: {errors}")
        self.assertEqual(len(errors), 0)
        self.assertGreater(len(file_types), 0)
    
    def test_validate_directory_with_errors(self):
        """Test directory validation with invalid files"""
        # Create invalid files
        invalid_yaml = "key: value\n  invalid_indent: value2"
        invalid_json = '{"key": }'
        
        self.create_temp_file(invalid_yaml, 'config.yaml')
        self.create_temp_file(invalid_json, 'config.json')
        
        valid, errors, file_types = self.validator.validate_directory(self.temp_dir)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)
        self.assertGreater(len(file_types), 0)


if __name__ == '__main__':
    unittest.main()

