#!/usr/bin/env python3
"""
Fix Unicode arrows in the notebook
"""
import json
import re

# Read the notebook
with open('plot_metrics.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Fix Unicode arrows in all cells
for cell in notebook['cells']:
    if 'source' in cell:
        if isinstance(cell['source'], list):
            # Fix each line in the source
            for i, line in enumerate(cell['source']):
                cell['source'][i] = re.sub(r'→', '->', line)
        elif isinstance(cell['source'], str):
            cell['source'] = re.sub(r'→', '->', cell['source'])

# Write the fixed notebook
with open('plot_metrics.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print("✅ Fixed Unicode arrows in notebook")

