# Just De Pic

A lightweight, offline image metadata tool that does one thing well - removes/edits metadata from your images without uploading them anywhere.

> [!NOTE]
> Coded to life with some help from Claude 4 Opus

## Features

### Privacy First
- 100% offline - no internet connection required
- Your images stay on your computer
- No analytics, no tracking, no BS

### Folder Mode
- Batch process entire folders
- Grid and list view options
- Adjustable thumbnail sizes
- Multi-select with Ctrl/Shift+Click
- Visual selection feedback

### Single Image Mode
- Detailed metadata inspection (EXIF, IPTC, XMP)
- Edit individual metadata fields
- Full-size preview
- Real-time updates

### Core Operations
- **Remove Metadata**: Strip all metadata with one click
- **Resize**: Downscale images while maintaining aspect ratio
- **Crop**: Center-crop to specific dimensions
- **Batch Processing**: Apply operations to multiple images at once

### Technical Features
- Automatically sets up virtual environment
- Clean, modular codebase
- Native GUI using Tkinter (no Electron bloat!)
- Supports common formats: JPEG, PNG, GIF, BMP, TIFF

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/LazySeaHorse/just-de-pic.git
   cd just-de-pic
   ```

2. **Run the application**
   ```bash
   python main.py
   ```

That's it! The app will automatically:
- Create a virtual environment
- Install required dependencies (Pillow, piexif)
- Launch the GUI

## Usage

### Quick Start

1. **Folder Mode** (for batch operations):
   - Click "Open Folder"
   - Select images (Ctrl+Click for multiple)
   - Click "Remove Metadata from Selected"

2. **Single Image Mode** (for detailed work):
   - Switch to "Single Image Mode" tab
   - Click "Open Image"
   - View/edit metadata in the side panel
   - Click "Remove All Metadata"

### Keyboard Shortcuts
- `Ctrl+A`: Select all (in folder mode)
- `Ctrl+Click`: Multi-select images
- `Shift+Click`: Range select

## Screenshots

### Folder Mode - Grid View
![Folder Mode Grid](https://i.postimg.cc/Gpq8p8fH/grid.png)
*Responsive grid that adjusts to window size*

### Folder Mode - List View
![Folder Mode List](https://i.postimg.cc/KYZ3FrJ6/list.png)
*Detailed list with file information*

### Single Image Mode
![Single Image Mode](https://i.postimg.cc/LX5qg4dv/single.png)
*Inspect individual metadata fields*

### Single Image Mode
![Single Image Mode](https://i.postimg.cc/ht8QH3b8/edit.png)
*Edit individual metadata fields*

## Requirements

- Python 3.7+
- Works on Windows, macOS, and Linux
- ~10MB disk space

## Project Structure

```
just_de_pic/
├── main.py              # Entry point with auto-venv setup
├── requirements.txt     # Minimal dependencies
├── gui/                 # UI components
│   ├── main_window.py   # Main application window
│   ├── folder_view.py   # Batch operations view
│   └── single_image_view.py # Single image operations
├── core/                # Business logic
│   ├── image_processor.py   # Resize/crop operations
│   └── metadata_handler.py  # Metadata read/write/remove
└── utils/               # Helper functions
    └── helpers.py       # Utility functions
```

## Privacy & Security

- **No Network Access**: The app doesn't require or use internet
- **No Telemetry**: We don't collect any usage data
- **Local Processing**: All operations happen on your machine
- **Open Source**: Verify the code yourself

## Contributing

Found a bug? Want a feature? PRs are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Why I Built This

I got tired of:
- Uploading personal photos to random websites just to check/remove metadata
- Installing bloated software with "premium features" for basic tasks
- Not having a simple, trustworthy tool for a simple job
- If you want something more feature-rich, use [Phil Harvey's EXIF Tool](https://github.com/FrankBijnen/ExifToolGui)

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

- Built with [Pillow](https://python-pillow.org/) for image processing
- [piexif](https://github.com/hMatoba/Piexif) for EXIF handling
- Tkinter for keeping it simple and cross-platform

---

**Remember**: Your metadata can reveal location, camera details, and editing history. Stay private! 🔐
