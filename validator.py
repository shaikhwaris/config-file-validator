#!/usr/bin/env python3
"""
Config File Validator
Validates YAML/JSON config files against schemas for Docker Compose, Kubernetes, Terraform, etc.
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import yaml
import jsonschema
from jsonschema import validate, ValidationError


class ConfigValidator:
    """Validates various configuration file formats"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_yaml(self, file_path: str) -> Tuple[bool, List[str]]:
        """Validate YAML syntax"""
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            return True, errors
        except yaml.YAMLError as e:
            errors.append(f"YAML syntax error in {file_path}: {str(e)}")
            return False, errors
        except Exception as e:
            errors.append(f"Error reading {file_path}: {str(e)}")
            return False, errors
    
    def validate_json(self, file_path: str) -> Tuple[bool, List[str]]:
        """Validate JSON syntax"""
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True, errors
        except json.JSONDecodeError as e:
            errors.append(f"JSON syntax error in {file_path}: {str(e)}")
            return False, errors
        except Exception as e:
            errors.append(f"Error reading {file_path}: {str(e)}")
            return False, errors
    
    def validate_docker_compose(self, file_path: str) -> Tuple[bool, List[str]]:
        """Validate Docker Compose file"""
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            if not isinstance(content, dict):
                errors.append(f"{file_path}: Root must be a dictionary")
                return False, errors
            
            # Check for required top-level keys
            if 'version' not in content and 'services' not in content:
                # Docker Compose v2 format (no version field)
                if 'services' not in content:
                    errors.append(f"{file_path}: Missing 'services' key")
                    return False, errors
            
            # Validate services structure
            if 'services' in content:
                services = content['services']
                if not isinstance(services, dict):
                    errors.append(f"{file_path}: 'services' must be a dictionary")
                    return False, errors
                
                for service_name, service_config in services.items():
                    if not isinstance(service_config, dict):
                        errors.append(f"{file_path}: Service '{service_name}' must be a dictionary")
                        continue
                    
                    # Check for image or build
                    if 'image' not in service_config and 'build' not in service_config:
                        errors.append(
                            f"{file_path}: Service '{service_name}' must have either 'image' or 'build'"
                        )
            
            return len(errors) == 0, errors
            
        except yaml.YAMLError as e:
            errors.append(f"YAML error in {file_path}: {str(e)}")
            return False, errors
        except Exception as e:
            errors.append(f"Error validating Docker Compose file {file_path}: {str(e)}")
            return False, errors
    
    def validate_kubernetes_manifest(self, file_path: str) -> Tuple[bool, List[str]]:
        """Validate Kubernetes manifest"""
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            if not isinstance(content, dict):
                errors.append(f"{file_path}: Root must be a dictionary")
                return False, errors
            
            # Required Kubernetes fields
            required_fields = ['apiVersion', 'kind', 'metadata']
            for field in required_fields:
                if field not in content:
                    errors.append(f"{file_path}: Missing required field '{field}'")
            
            # Validate metadata
            if 'metadata' in content:
                metadata = content['metadata']
                if not isinstance(metadata, dict):
                    errors.append(f"{file_path}: 'metadata' must be a dictionary")
                elif 'name' not in metadata:
                    errors.append(f"{file_path}: 'metadata.name' is required")
            
            # Validate apiVersion format
            if 'apiVersion' in content:
                api_version = content['apiVersion']
                if not isinstance(api_version, str) or '/' not in api_version:
                    # Some apiVersions like 'v1' don't have '/', but most do
                    if api_version != 'v1':
                        errors.append(
                            f"{file_path}: 'apiVersion' should follow format 'group/version' or 'v1'"
                        )
            
            return len(errors) == 0, errors
            
        except yaml.YAMLError as e:
            errors.append(f"YAML error in {file_path}: {str(e)}")
            return False, errors
        except Exception as e:
            errors.append(f"Error validating Kubernetes manifest {file_path}: {str(e)}")
            return False, errors
    
    def validate_terraform(self, file_path: str) -> Tuple[bool, List[str]]:
        """Validate Terraform HCL file (basic validation)"""
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic Terraform validation
            # Check for balanced braces
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces != close_braces:
                errors.append(
                    f"{file_path}: Unbalanced braces ({{: {open_braces}, }}: {close_braces})"
                )
            
            # Check for balanced brackets
            open_brackets = content.count('[')
            close_brackets = content.count(']')
            if open_brackets != close_brackets:
                errors.append(
                    f"{file_path}: Unbalanced brackets ([: {open_brackets}, ]: {close_brackets})"
                )
            
            # Check for basic Terraform block structure
            if not any(keyword in content for keyword in ['resource', 'data', 'variable', 'output', 'provider', 'module', 'terraform']):
                errors.append(
                    f"{file_path}: No Terraform blocks found (resource, data, variable, output, provider, module, or terraform)"
                )
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Error validating Terraform file {file_path}: {str(e)}")
            return False, errors
    
    def validate_json_schema(self, file_path: str, schema_path: Optional[str] = None) -> Tuple[bool, List[str]]:
        """Validate JSON file against a JSON Schema"""
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if schema_path:
                if not os.path.exists(schema_path):
                    errors.append(f"Schema file not found: {schema_path}")
                    return False, errors
                
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                
                try:
                    validate(instance=data, schema=schema)
                except ValidationError as e:
                    errors.append(f"{file_path}: Schema validation error: {e.message}")
                    if e.path:
                        errors.append(f"  Path: {'.'.join(str(p) for p in e.path)}")
            
            return len(errors) == 0, errors
            
        except json.JSONDecodeError as e:
            errors.append(f"JSON syntax error in {file_path}: {str(e)}")
            return False, errors
        except Exception as e:
            errors.append(f"Error validating JSON schema for {file_path}: {str(e)}")
            return False, errors
    
    def detect_file_type(self, file_path: str) -> str:
        """Detect the type of config file based on filename and content"""
        path = Path(file_path)
        filename = path.name.lower()
        
        # Skip non-config file types
        if filename.endswith('.md') or filename.endswith('.markdown'):
            return 'markdown'
        elif filename.endswith('.txt') or filename.endswith('.log'):
            return 'text'
        elif filename.endswith('.py') or filename.endswith('.pyc'):
            return 'python'
        elif filename.endswith('.sh') or filename.endswith('.bash'):
            return 'shell'
        
        # Check filename patterns
        if 'docker-compose' in filename or filename == 'compose.yml' or filename == 'compose.yaml':
            return 'docker-compose'
        elif filename.endswith('.tf') or filename.endswith('.tf.json'):
            return 'terraform'
        elif 'k8s' in filename or 'kubernetes' in filename or path.parent.name == 'k8s':
            return 'kubernetes'
        elif filename.endswith('.json'):
            return 'json'
        elif filename.endswith('.yaml') or filename.endswith('.yml'):
            # Try to detect by content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                    if isinstance(content, dict):
                        if 'apiVersion' in content and 'kind' in content:
                            return 'kubernetes'
                        elif 'services' in content or 'version' in content:
                            return 'docker-compose'
            except:
                pass
            return 'yaml'
        
        return 'unknown'
    
    def validate_file(self, file_path: str, file_type: Optional[str] = None) -> Tuple[bool, List[str], str]:
        """Validate a config file
        
        Returns:
            Tuple of (is_valid, errors_list, detected_file_type)
        """
        if not os.path.exists(file_path):
            return False, [f"File not found: {file_path}"], 'unknown'
        
        if file_type is None:
            file_type = self.detect_file_type(file_path)
        
        # Skip non-config file types (markdown, text, etc.)
        if file_type in ['markdown', 'text', 'python', 'shell']:
            return True, [], file_type  # Return valid but skip actual validation
        
        errors = []
        
        # First validate syntax
        if file_type in ['yaml', 'docker-compose', 'kubernetes']:
            valid, yaml_errors = self.validate_yaml(file_path)
            errors.extend(yaml_errors)
            if not valid:
                return False, errors, file_type
        elif file_type == 'json':
            valid, json_errors = self.validate_json(file_path)
            errors.extend(json_errors)
            if not valid:
                return False, errors, file_type
        
        # Then validate structure
        if file_type == 'docker-compose':
            valid, struct_errors = self.validate_docker_compose(file_path)
            errors.extend(struct_errors)
        elif file_type == 'kubernetes':
            valid, struct_errors = self.validate_kubernetes_manifest(file_path)
            errors.extend(struct_errors)
        elif file_type == 'terraform':
            valid, struct_errors = self.validate_terraform(file_path)
            errors.extend(struct_errors)
        
        return len(errors) == 0, errors, file_type
    
    def validate_directory(self, directory: str, patterns: Optional[List[str]] = None) -> Tuple[bool, List[str], Dict[str, str]]:
        """Validate all config files in a directory
        
        Returns:
            Tuple of (is_valid, errors_list, file_types_dict mapping file_path -> file_type)
        """
        if patterns is None:
            patterns = ['*.yaml', '*.yml', '*.json', '*.tf', 'docker-compose*.yml', 'docker-compose*.yaml']
        
        all_errors = []
        files_validated = 0
        file_types = {}
        
        for pattern in patterns:
            for file_path in Path(directory).rglob(pattern):
                if file_path.is_file():
                    files_validated += 1
                    file_path_str = str(file_path)
                    valid, errors, file_type = self.validate_file(file_path_str)
                    file_types[file_path_str] = file_type
                    # Only report errors for config file types, skip markdown/text files
                    if not valid and file_type not in ['markdown', 'text', 'python', 'shell']:
                        all_errors.extend(errors)
        
        return len(all_errors) == 0, all_errors, file_types


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate configuration files')
    parser.add_argument('paths', nargs='+', help='Files or directories to validate')
    parser.add_argument('--type', choices=['yaml', 'json', 'docker-compose', 'kubernetes', 'terraform', 'auto'],
                       default='auto', help='File type (default: auto-detect)')
    parser.add_argument('--schema', help='JSON Schema file for JSON validation')
    
    args = parser.parse_args()
    
    validator = ConfigValidator()
    all_errors = []
    files_checked = 0
    file_info = []  # Store (file_path, file_type, is_valid) tuples
    
    for path_str in args.paths:
        path = Path(path_str)
        
        if not path.exists():
            all_errors.append(f"Path not found: {path_str}")
            continue
        
        if path.is_file():
            files_checked += 1
            file_type = None if args.type == 'auto' else args.type
            if args.schema and args.type == 'json':
                valid, errors = validator.validate_json_schema(str(path), args.schema)
                detected_type = 'json'
            else:
                valid, errors, detected_type = validator.validate_file(str(path), file_type)
            
            file_info.append((str(path), detected_type, valid))
            if not valid:
                all_errors.extend(errors)
        elif path.is_dir():
            valid, errors, file_types = validator.validate_directory(str(path))
            files_checked += len(file_types)
            for file_path, file_type in file_types.items():
                # Check if this file had errors
                file_has_errors = any(file_path in error for error in errors)
                file_info.append((file_path, file_type, not file_has_errors))
            if not valid:
                all_errors.extend(errors)
    
    # Print results
    if all_errors:
        print("Validation failed!\n", file=sys.stderr)
        for error in all_errors:
            print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
    else:
        # Separate config files from non-config files
        config_files = []
        skipped_files = []
        
        for file_path, file_type, is_valid in file_info:
            if file_type in ['markdown', 'text', 'python', 'shell']:
                skipped_files.append((file_path, file_type))
            else:
                config_files.append((file_path, file_type, is_valid))
        
        # Print results
        if config_files:
            print(f"[PASS] Validation passed! Checked {len(config_files)} config file(s).\n")
            # Print config files
            for file_path, file_type, is_valid in config_files:
                status = "[OK]" if is_valid else "[FAIL]"
                print(f"  {status} {file_path} ({file_type})")
        else:
            print(f"[INFO] No config files to validate. Checked {files_checked} file(s).\n")
        
        # Print skipped files (non-config files)
        if skipped_files:
            print(f"\n  Skipped {len(skipped_files)} non-config file(s):")
            for file_path, file_type in skipped_files:
                print(f"    [SKIP] {file_path} ({file_type})")
        
        sys.exit(0)


if __name__ == '__main__':
    main()

