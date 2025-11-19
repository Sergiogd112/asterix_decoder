# Building Executables for ASTERIX Dashboard

## Automated Builds (Recommended)

### GitHub Actions
This project uses GitHub Actions to automatically build and release executables:

1. **Automatic Releases**: Push a tag like `v1.0.0` to trigger automatic builds
2. **Manual Builds**: Use "Actions" tab in GitHub to trigger builds manually
3. **Cross-Platform**: Builds both Linux and Windows executables simultaneously
4. **Release Assets**: Binaries are automatically attached to GitHub releases

### To Create a Release:
```bash
git tag v1.0.0
git push origin v1.0.0
```

This will automatically:
- Build Linux and Windows executables
- Create a GitHub release with both binaries
- Include detailed release notes and instructions

## Local Build

### Linux (Already Built)

A Linux executable has been successfully created:
- **File**: `dist/asterix_dashboard`
- **Size**: 109MB
- **Architecture**: x86-64 ELF executable
- **Status**: Ready to run

## Windows Build Instructions

To build the Windows executable, follow these steps:

### Prerequisites
1. Install Python 3.10+ on Windows
2. Install Git
3. Install Visual Studio Build Tools or Visual Studio Community

### Build Steps

1. **Clone the repository:**
   ```cmd
   git clone <repository-url>
   cd asterix_decoder
   ```

2. **Install uv (Python package manager):**
   ```cmd
   pip install uv
   ```

3. **Create virtual environment and install dependencies:**
   ```cmd
   uv venv
   uv pip install -e .
   ```

4. **Build the executable:**
   ```cmd
   uv run python -m PyInstaller asterix_dashboard.spec
   ```

5. **Find the executable:**
   - The Windows executable will be created as `dist/asterix_dashboard.exe`
   - Expected size: ~100-150MB

### Alternative: One-Command Build

If you have uv installed, you can build with a single command:
```cmd
uv run python -m PyInstaller --onefile --name asterix_dashboard --add-data "mapdata.py;." --add-data "Test_Data;Test_Data" --hidden-import dearpygui --hidden-import numpy --hidden-import pandas --hidden-import tqdm --hidden-import decoder.decoder --hidden-import decoder.geoutils --exclude-module matplotlib --exclude-module scipy --exclude-module contextily --exclude-module imageio --exclude-module ffmpeg-python --exclude-module ipykernel --exclude-module ipython --exclude-module ipywidgets --exclude-module nbformat --exclude-module black --exclude-module rich dashboard.py
```

## Running the Executables

### Linux
```bash
./dist/asterix_dashboard
```

### Windows
```cmd
dist\asterix_dashboard.exe
```

## Notes

- Both executables are self-contained and don't require Python installation
- The executables include all necessary dependencies and the Test_Data folder
- File size is large (~100MB) due to inclusion of all dependencies
- The application will show a file selection dialog on startup to load ASTERIX data files

## Troubleshooting

### Windows Issues
- If the executable fails to run, ensure you have the latest Visual C++ Redistributable
- Windows Defender may flag the executable - this is a false positive from PyInstaller

### Linux Issues
- Ensure the executable has execute permissions: `chmod +x dist/asterix_dashboard`
- If you get library errors, you may need to install missing system dependencies

## Cross-Platform Building

For building Windows executables on Linux, you can use:
- Docker with a Windows container
- GitHub Actions (automated builds)
- Cross-compilation tools like mingw-w64

The current setup builds the executable for the platform it's run on.