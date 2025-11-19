# GitHub Actions Setup

This repository uses GitHub Actions for automated building and releasing of the ASTERIX Dashboard executables.

## Workflow Overview

### Triggers
- **Tag Push**: When you push a tag starting with `v` (e.g., `v1.0.0`), it automatically builds both Linux and Windows executables and creates a GitHub release
- **Manual Dispatch**: You can manually trigger builds from the Actions tab in GitHub

### Build Matrix
The workflow builds on both platforms:
- **Ubuntu Latest**: Creates `asterix-dashboard-linux`
- **Windows Latest**: Creates `asterix-dashboard-windows.exe`

### Release Process
1. Both executables are built in parallel
2. Artifacts are uploaded and downloaded
3. A GitHub release is created with:
   - Both binaries as release assets
   - Detailed release notes with features and instructions
   - Proper versioning based on tag or manual input

## Usage

### Automatic Release (Recommended)
```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

### Manual Build
1. Go to the "Actions" tab in your GitHub repository
2. Select "Build and Release Executables" workflow
3. Click "Run workflow"
4. Enter the version number (e.g., `v1.0.0`)
5. Click "Run workflow"

## Workflow Features

- ✅ Cross-platform builds (Linux + Windows)
- ✅ Self-contained executables (~100MB each)
- ✅ Automatic dependency management with uv
- ✅ Proper executable permissions for Linux
- ✅ Professional release notes with instructions
- ✅ No manual intervention required
- ✅ Cached dependencies for faster builds

## Security

The workflow uses:
- Official GitHub Actions (setup-python, checkout, upload/download-artifact, gh-release)
- No external dependencies or custom scripts
- Standard GitHub token for release creation
- No sensitive information exposed

## Troubleshooting

If a build fails:
1. Check the Actions tab for detailed logs
2. Ensure all dependencies are properly specified in `pyproject.toml`
3. Verify the PyInstaller spec file is correct
4. Check for any platform-specific issues

The workflow is designed to be robust and should handle most build scenarios automatically.