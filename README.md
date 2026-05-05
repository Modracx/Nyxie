# Nyxie

Nyxie is a system assistant designed for Ubuntu Linux, providing automated tools and utilities to streamline system management, monitoring, and maintenance tasks.

## Features

- **System Monitoring**: Real-time monitoring of system resources including CPU, memory, disk usage, and network activity.
- **Automated Maintenance**: Scheduled tasks for system updates, package cleaning, and log rotation.
- **Troubleshooting Tools**: Built-in diagnostics for common Ubuntu issues, with guided fixes.
- **Customization**: Configurable settings to adapt to your specific Ubuntu environment.

## Installation

### Prerequisites
- Ubuntu 20.04 or later
- Python 3.8+
- Root or sudo access for system-level operations

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Modracx/Nyxie.git
   cd Nyxie
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the installer:
   ```bash
   sudo python setup.py install
   ```

## Usage

### Basic Commands
- Start the assistant: `nyxie start`
- Check system status: `nyxie status`
- Run diagnostics: `nyxie diagnose`
- Update system: `nyxie update`

### Configuration
Edit the configuration file at `/etc/nyxie/config.yaml` to customize settings.

### Examples
```bash
# Monitor system for 5 minutes
nyxie monitor --duration 300

# Clean up old packages
nyxie clean --packages
```

## Troubleshooting

### Common Issues
- **Permission Denied**: Ensure you're running commands with sudo if required.
- **Dependency Errors**: Verify Python version and reinstall dependencies.
- **Service Not Starting**: Check system logs with `journalctl -u nyxie`.

### Getting Help
- Open an issue on [GitHub](https://github.com/Modracx/Nyxie/issues)
- Check the [Wiki](https://github.com/Modracx/Nyxie/wiki) for detailed guides

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.