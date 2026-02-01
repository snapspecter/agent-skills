#!/bin/bash
# map_context.sh - Provides a token-efficient view of the project

OUTPUT="_artifacts/project_map.md"
mkdir -p _artifacts

echo "# Project Mapper" > $OUTPUT
echo "Generated: $(date)" >> $OUTPUT
echo "" >> $OUTPUT

echo "## File Structure" >> $OUTPUT
echo '```text' >> $OUTPUT
# Use tree if available, otherwise fallback to find
if command -v tree >/dev/null 2>&1; then
  tree -I "node_modules|.git|__pycache__|dist|build|.next|*.pyc" -L 3 >> $OUTPUT
else
  find . -maxdepth 3 -not -path '*/.*' | sed -e "s/[^-][^\/]*\// |/g" -e "s/|\([^ ]\)/|-\1/" >> $OUTPUT
fi
echo '```' >> $OUTPUT

echo "## Core Dependencies" >> $OUTPUT
echo '```json' >> $OUTPUT
if [ -f "package.json" ]; then
  if command -v jq >/dev/null 2>&1; then
    jq '{dependencies, devDependencies}' package.json >> $OUTPUT
  else
    cat package.json >> $OUTPUT
  fi
elif [ -f "pyproject.toml" ]; then
  cat pyproject.toml | grep -A 10 "dependencies" >> $OUTPUT
fi
echo '```' >> $OUTPUT

echo "## 🛠 Available Skills" >> $OUTPUT
ls .agent/skills/*.skill | sed 's/.*\///' >> $OUTPUT

echo "Map saved to $OUTPUT"