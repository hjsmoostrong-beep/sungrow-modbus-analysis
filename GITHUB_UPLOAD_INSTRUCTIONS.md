# GitHub Upload Instructions

## Step 1: Install Git

### Windows
Download and install from: https://git-scm.com/download/win

Verify installation:
```powershell
git --version
```

## Step 2: Configure Git (First Time)

```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 3: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `sungrow-modbus-analysis`
3. Description: "Modbus TCP capture analysis toolkit for Sungrow solar inverters"
4. Choose: **Public** (to share with community)
5. **Do NOT** initialize with README (we have one)
6. Click "Create repository"

## Step 4: Initialize Local Git Repository

```powershell
cd "C:\Users\Public\Videos\modbus"

# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Sungrow Modbus analysis toolkit with live capture and documentation"

# Add remote repository (replace YOUR_USERNAME and YOUR_TOKEN)
git remote add origin https://YOUR_USERNAME:YOUR_TOKEN@github.com/YOUR_USERNAME/sungrow-modbus-analysis.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 5: GitHub Personal Access Token

Instead of password, use Personal Access Token:

1. Go to GitHub Settings: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name: `sungrow-upload`
4. Expiration: 90 days
5. Scopes: Check `repo` (full control of private repositories)
6. Generate token
7. **Copy token** (you won't see it again)
8. Use token as password in git commands above

## Step 6: Push All Files

```powershell
cd "C:\Users\Public\Videos\modbus"

# Stage all files
git add -A

# Verify what will be uploaded
git status

# Commit
git commit -m "Complete Sungrow Modbus toolkit: capture, analysis, and documentation"

# Push to GitHub
git push -u origin main
```

## Step 7: Verify Upload

Visit your repository: `https://github.com/YOUR_USERNAME/sungrow-modbus-analysis`

You should see:
- ✓ All Python files
- ✓ All documentation
- ✓ README_GITHUB.md as main README
- ✓ LICENSE file
- ✓ .gitignore
- ✓ requirements.txt

## Step 8: Rename Main README (Optional)

If uploaded as README_GITHUB.md, rename it on GitHub:

1. Click on README_GITHUB.md
2. Click pencil icon (Edit)
3. Click "..." → "Rename"
4. Change to "README.md"
5. Commit changes

## Complete Command Sequence (All-in-One)

```powershell
cd "C:\Users\Public\Videos\modbus"

# Initialize
git init
git add -A
git commit -m "Initial commit: Sungrow Modbus analysis toolkit with live capture and documentation cross-reference"

# Configure remote
git remote add origin https://YOUR_USERNAME:YOUR_TOKEN@github.com/YOUR_USERNAME/sungrow-modbus-analysis.git

# Push
git branch -M main
git push -u origin main

# Verify
echo "Repository created at: https://github.com/YOUR_USERNAME/sungrow-modbus-analysis"
```

## Files Included in Upload

### Core Tools (10 files)
- analyze_json_output.py
- modbus_decoder.py
- sungrow_doc_mapper.py
- modbus_pipeline.py
- pcap_extractor.py
- test_harness.py
- test_data_generator.py
- example_usage.py
- extract_live_mapping.py
- modbus_live_analyzer.py

### Utilities (2 files)
- simple_frame_analyzer.py
- enhanced_frame_extractor.py

### Scripts (2 files)
- capture_modbus.bat
- workflow.bat

### Documentation (12 files)
- README_GITHUB.md (→ README.md)
- QUICK_REFERENCE.md
- EXECUTION_GUIDE.md
- IMPLEMENTATION_COMPLETE.md
- MAPPING_ANALYSIS_COMPLETE.md
- SUNGROW_DOCUMENTATION_CROSSREF.md
- INDEX.md
- Plus others...

### Configuration (3 files)
- .gitignore
- requirements.txt
- LICENSE

### Sample Outputs (7 files)
- sungrow_live_register_map.json
- sungrow_live_analysis_report.txt
- sungrow_documented_mapping.json
- sungrow_documentation_mapping.txt
- sungrow_quick_reference.txt
- register_map.csv
- test_register_map.json

**Note**: PCAPNG capture file (2.8 MB) is in .gitignore (too large for typical repos)

## Troubleshooting

### Error: "Permission denied (publickey)"
- Check SSH keys: `ssh -T git@github.com`
- Or use HTTPS with personal access token instead

### Error: "Repository not found"
- Verify repository exists on GitHub
- Check username and repository name spelling

### Large File Warning
If prompted about large files:
- Install Git LFS: https://git-lfs.github.com/
- Or remove .pcapng files before pushing

### Push Rejected
```powershell
# If remote already exists
git remote remove origin
git remote add origin https://YOUR_USERNAME:YOUR_TOKEN@github.com/YOUR_USERNAME/sungrow-modbus-analysis.git
git push -u origin main
```

## Next: Share Your Repository

Once uploaded:

1. Add topics: `modbus`, `solar`, `inverter`, `sungrow`, `iot`, `network-analysis`
2. Write a description in GitHub repo settings
3. Create GitHub Issues for tracking documentation requests
4. Share on Reddit: r/solar, r/homelab
5. Share on GitHub Discussions
6. Link from solar forum sites

## GitHub Repository Template

After uploading, consider:
- Adding GitHub Pages for documentation
- Setting up CI/CD for testing
- Creating GitHub Releases for versions
- Adding Contributing guidelines
- Creating Issue templates

---

**Repository Details:**
- Public: Yes (open source)
- License: MIT
- Stars Expected: For solar enthusiasts and integration engineers
- Use Cases: PCVue integration, Modbus learning, Sungrow reverse engineering
