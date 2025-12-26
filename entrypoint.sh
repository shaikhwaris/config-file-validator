#!/bin/bash
set -euo pipefail

# Parse inputs
FILES="${INPUT_FILES}"
FILE_TYPE="${INPUT_FILE_TYPE:-auto}"
SCHEMA="${INPUT_SCHEMA:-}"
FAIL_ON_ERROR="${INPUT_FAIL_ON_ERROR:-true}"
ACTION_PATH="${GITHUB_ACTION_PATH:-.}"

# Convert files input (can be comma-separated or newline-separated) to array
VALIDATION_ARGS=()

# Handle both comma-separated and newline-separated inputs
while IFS= read -r line; do
  # Split by comma if line contains commas
  IFS=',' read -ra PARTS <<< "$line"
  for part in "${PARTS[@]}"; do
    # Trim whitespace
    file_pattern=$(echo "$part" | xargs)
    
    # Skip empty patterns
    [ -z "$file_pattern" ] && continue
    
    # Expand glob patterns if they exist
    if [[ "$file_pattern" == *"*"* ]] || [[ "$file_pattern" == *"?"* ]]; then
      # Use find to expand glob patterns
      while IFS= read -r -d '' file; do
        VALIDATION_ARGS+=("$file")
      done < <(find . -path "$file_pattern" -type f -print0 2>/dev/null || true)
    else
      # Check if file/directory exists
      if [ -e "$file_pattern" ]; then
        VALIDATION_ARGS+=("$file_pattern")
      else
        echo "::warning::File or directory not found: $file_pattern"
      fi
    fi
  done
done <<< "$FILES"

# If no files found, exit with error
if [ ${#VALIDATION_ARGS[@]} -eq 0 ]; then
  echo "::error::No files found matching the provided patterns: $FILES"
  echo "valid=false" >> $GITHUB_OUTPUT
  echo "errors=No files found matching patterns" >> $GITHUB_OUTPUT
  echo "files-checked=0" >> $GITHUB_OUTPUT
  echo "files-passed=0" >> $GITHUB_OUTPUT
  echo "files-failed=0" >> $GITHUB_OUTPUT
  if [ "$FAIL_ON_ERROR" = "true" ]; then
    exit 1
  else
    exit 0
  fi
fi

# Build command
CMD="python3 \"$ACTION_PATH/validator.py\""

# Add file type if specified
if [ "$FILE_TYPE" != "auto" ]; then
  CMD="$CMD --type \"$FILE_TYPE\""
fi

# Add schema if specified
if [ -n "$SCHEMA" ]; then
  CMD="$CMD --schema \"$SCHEMA\""
fi

# Add files
for file in "${VALIDATION_ARGS[@]}"; do
  CMD="$CMD \"$file\""
done

# Run validation and capture output
echo "::group::Validating config files"
echo "Files to validate: ${VALIDATION_ARGS[*]}"
echo "File type: $FILE_TYPE"
if [ -n "$SCHEMA" ]; then
  echo "Schema: $SCHEMA"
fi
echo ""

VALIDATION_EXIT_CODE=0
VALIDATION_OUTPUT=$(eval "$CMD" 2>&1) || VALIDATION_EXIT_CODE=$?

echo "$VALIDATION_OUTPUT"
echo "::endgroup::"

# Parse results (basic parsing - validator.py outputs [PASS] or ERROR:)
FILES_CHECKED=0
FILES_PASSED=0
FILES_FAILED=0
VALID="true"
ERRORS=""

# Check if validation failed
if [ "$VALIDATION_EXIT_CODE" != "0" ] || echo "$VALIDATION_OUTPUT" | grep -q "ERROR:" || echo "$VALIDATION_OUTPUT" | grep -q "\[FAIL\]"; then
  VALID="false"
  # Extract errors
  if echo "$VALIDATION_OUTPUT" | grep -q "ERROR:"; then
    ERRORS=$(echo "$VALIDATION_OUTPUT" | grep "ERROR:" | sed 's/ERROR: //' | tr '\n' '; ' | sed 's/; $//')
  fi
fi

# Count files from output
if echo "$VALIDATION_OUTPUT" | grep -q "Checked"; then
  FILES_CHECKED=$(echo "$VALIDATION_OUTPUT" | grep -oP 'Checked \K\d+' | head -1 || echo "0")
fi

if echo "$VALIDATION_OUTPUT" | grep -q "\[OK\]"; then
  FILES_PASSED=$(echo "$VALIDATION_OUTPUT" | grep -o "\[OK\]" | wc -l | tr -d ' ')
fi

if echo "$VALIDATION_OUTPUT" | grep -q "\[FAIL\]"; then
  FILES_FAILED=$(echo "$VALIDATION_OUTPUT" | grep -o "\[FAIL\]" | wc -l | tr -d ' ')
fi

# Set outputs
echo "valid=$VALID" >> $GITHUB_OUTPUT
echo "errors=$ERRORS" >> $GITHUB_OUTPUT
echo "files-checked=$FILES_CHECKED" >> $GITHUB_OUTPUT
echo "files-passed=$FILES_PASSED" >> $GITHUB_OUTPUT
echo "files-failed=$FILES_FAILED" >> $GITHUB_OUTPUT

# Exit based on fail-on-error setting
if [ "$VALIDATION_EXIT_CODE" != "0" ] && [ "$FAIL_ON_ERROR" = "true" ]; then
  echo "::error::Validation failed. See output above for details."
  exit $VALIDATION_EXIT_CODE
elif [ "$VALIDATION_EXIT_CODE" != "0" ]; then
  echo "::warning::Validation failed but fail-on-error is disabled."
  exit 0
fi

exit 0

