# Software Install Script (CLI/TUI Version)

This is a command-line interface (CLI) and text-based user interface (TUI) version of the Software Install Script, designed to provide a more interactive and user-friendly experience for installing software across different platforms.

## Features

- **Cross-platform support**: Works on both Windows and macOS
- **Interactive TUI**: Text-based user interface for easy navigation
- **Command-line interface**: Powerful CLI for scripting and automation
- **Rich output**: Colorful and informative terminal output
- **Configurable software list**: Easy to customize the software you want to install
- **Progress tracking**: Real-time installation progress and status
- **Error handling**: Graceful handling of installation errors

## Requirements

- Python 3.7 or higher
- Windows: winget (Windows Package Manager)
- macOS: homebrew

## Installation

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/cgartlab/Software_Install_Script.git
   cd Software_Install_Script
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

## Usage

### Command-line Interface (CLI)

#### Show version
```bash
sis version
```

#### Install software
```bash
sis install
```

#### Configure software list
```bash
sis config
```

### Text-based User Interface (TUI)

Launch the interactive TUI:
```bash
sis tui
```

## Configuration

The configuration is stored in `~/.sis/config.yaml`.

You can edit this file directly or use the `sis config` command to manage the software list interactively.

### Configuration Format

```yaml
software:
  - name: Git
    id: Git.Git  # Windows (winget ID)
    category: Development
  - name: Git
    package: git  # macOS (brew package name)
    category: Development
```

## Platform-specific Notes

### Windows
- Uses winget package manager
- Requires Windows 10 1709 or later
- Winget must be installed and accessible in PATH

### macOS
- Uses homebrew package manager
- Will automatically offer to install homebrew if not found
- Requires macOS 10.15 or later

## Examples

### Install software using TUI
1. Run `sis tui`
2. Select "Install software" from the menu
3. Review the software list
4. Confirm installation
5. Wait for the installation to complete

### Customize software list
1. Run `sis config`
2. Use the interactive menu to add, remove, or view software
3. Save your changes
4. Run `sis install` to install the updated list

## Troubleshooting

### Common Issues

1. **Winget not found** (Windows):
   - Install Windows Package Manager from the Microsoft Store
   - Ensure winget is in your PATH

2. **Homebrew not found** (macOS):
   - Run the script and it will offer to install homebrew
   - Or install manually from https://brew.sh/

3. **Permission denied** (macOS):
   - Run the script with sudo if necessary
   - Ensure homebrew has proper permissions

4. **Installation failed**:
   - Check your internet connection
   - Verify the software ID/package name is correct
   - Check the error message for specific details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE-2.0 file for details.
