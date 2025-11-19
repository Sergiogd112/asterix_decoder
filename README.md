# ASTERIX Decoder & Dashboard

A comprehensive ASTERIX message decoder with an interactive DearPyGui dashboard for real-time aircraft tracking visualization.

## 🚀 Quick Start

### Option 1: Download Pre-built Executables (Recommended)

Download the latest release from [GitHub Releases](https://github.com/Sergiogd112/asterix_decoder/releases):

- **Linux**: `asterix-dashboard-linux` - Self-contained executable for Linux x86-64
- **Windows**: `asterix-dashboard-windows.exe` - Self-contained executable for Windows x86-64

**Running:**
```bash
# Linux
chmod +x asterix-dashboard-linux
./asterix-dashboard-linux

# Windows
asterix-dashboard-windows.exe
```

### Option 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/Sergiogd112/asterix_decoder.git
cd asterix_decoder

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
uv pip install -e .

# Run the dashboard
uv run python dashboard.py
```

## ✨ Features

- **Interactive Dashboard**: Real-time aircraft tracking on an interactive map
- **Play/Pause Controls**: Control animation playback with adjustable speed
- **Advanced Filtering**: Filter by location, altitude, ground status, and category
- **Data Export**: Export filtered data to CSV format
- **Multi-format Support**: Handles various ASTERIX categories (CAT21, CAT48, etc.)
- **Self-contained**: No Python installation required for pre-built executables

## 📋 Requirements

### Pre-built Executables
- **Linux**: glibc 2.17+ (most modern distributions)
- **Windows**: Windows 10+ with Visual C++ Redistributable
- No Python installation required

### From Source
- Python 3.10+
- Dependencies listed in `pyproject.toml`

## 🔧 Building from Source

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for detailed build instructions, including:
- Local builds for Linux and Windows
- GitHub Actions automated builds
- Cross-platform compilation

## 📖 Usage

1. **Launch the dashboard** using one of the methods above
2. **Select ASTERIX data file** using the file dialog
3. **Configure loading options**:
   - Set maximum messages to load (optional)
   - Choose to load all messages
4. **Start visualization**:
   - Use Play/Pause buttons to control animation
   - Adjust playback speed with the slider
   - Navigate frames with the frame slider
5. **Apply filters**:
   - Set latitude/longitude bounds
   - Filter by altitude range
   - Filter by ground status (On Ground/Airborne)
   - Filter by ASTERIX category
6. **Export data**:
   - Click "Export to CSV" to save filtered data

## 🗂️ Project Structure

```
asterix_decoder/
├── decoder/           # Core ASTERIX decoding logic
├── dashboard.py       # Main DearPyGui dashboard
├── mapdata.py        # Map visualization data
├── Test_Data/        # Sample ASTERIX data files
├── BUILD_INSTRUCTIONS.md  # Detailed build guide
└── .github/workflows/    # Automated CI/CD
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [GitHub Repository](https://github.com/Sergiogd112/asterix_decoder)
- [GitHub Releases](https://github.com/Sergiogd112/asterix_decoder/releases)
- [Build Instructions](BUILD_INSTRUCTIONS.md)
- [Issues & Bug Reports](https://github.com/Sergiogd112/asterix_decoder/issues)