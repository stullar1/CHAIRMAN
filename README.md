# CHAIRMAN

**Run the shop. Own the chair.**

A professional, modern barber shop management system built with Python and PySide6.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

---

## Features

### Current Features

- **Appointment Scheduling**
  - Book appointments with time conflict detection
  - Day-view calendar for easy scheduling
  - Automatic buffer time between appointments
  - Payment tracking and payment method selection

- **Client Management**
  - Add and manage client profiles
  - Track client phone numbers and notes
  - Monitor no-show counts
  - Search functionality

- **Service Management**
  - Create and manage barber services
  - Set pricing and duration for each service
  - Configure buffer times between appointments
  - Track service details

- **Professional Code Quality**
  - Comprehensive input validation
  - Centralized logging system
  - Error handling throughout
  - Type hints and docstrings
  - Clean, maintainable architecture

### Upcoming Features

- **Multi-Tier Business Modes**
  - Solo Mode: Perfect for individual barbers/hairdressers
  - Enterprise Mode: Multi-employee support with privacy controls

- **Enhanced UI**
  - Cleaner, more modern interface
  - Layered client section
  - Improved navigation and workflows

- **Advanced Features**
  - SMS/Email reminders
  - Analytics and reporting
  - Online sync capabilities
  - Multi-location support

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd barber_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

---

## Usage

### First Launch

On first launch, CHAIRMAN will automatically create a local SQLite database (`barber.db`) with the necessary schema. No additional configuration is required.

### Booking an Appointment

1. Navigate to the "Schedule" page
2. Select a date
3. Fill in the quick booking form:
   - Select a client (or add a new one)
   - Choose a service
   - Pick a time slot
   - Add optional payment information and notes
4. Click "Book"

### Managing Clients

1. Navigate to the "Clients" page
2. View all existing clients in the list
3. To add a new client:
   - Enter name (required)
   - Add phone number (optional but recommended)
   - Click "Add Client"

### Managing Services

1. Navigate to the "Services" page
2. View all available services
3. Services can be added/modified through the database or future UI enhancements

---

## Project Structure

```
barber_app/
│
├── core/                      # Business logic layer
│   ├── clients.py            # Client management
│   ├── scheduler.py          # Appointment scheduling
│   ├── services.py           # Service management
│   ├── validators.py         # Input validation
│   ├── logging_config.py     # Logging configuration
│   └── app_state.py          # Global application state
│
├── data/                      # Data layer
│   ├── db.py                 # Database connection and schema
│   └── models.py             # Data models (Client, Service, Appointment)
│
├── ui/                        # Presentation layer
│   ├── main_window.py        # Main application window
│   ├── sidebar.py            # Navigation sidebar
│   ├── statusbar.py          # Status bar
│   └── pages/                # Page components
│       ├── schedule_page.py  # Scheduling interface
│       ├── client_page.py    # Client management
│       └── services_page.py  # Service display
│
├── assets/                    # Static resources
│   ├── icons/                # Application icons
│   ├── images/               # Images
│   └── sounds/               # Sound effects
│
├── logs/                      # Application logs (auto-created)
│
├── config.py                  # Configuration and constants
├── app.py                     # Application entry point
├── main.py                    # Launcher
├── style.qss                  # Qt stylesheet
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## Configuration

All configuration is centralized in [`config.py`](config.py). Key settings include:

- **Business Hours**: Default 9 AM - 6 PM
- **Buffer Time**: 15 minutes between appointments
- **Payment Methods**: Cash, Card, Cash App, Zelle, Venmo, PayPal
- **Validation Rules**: Name lengths, price limits, duration limits
- **UI Settings**: Window sizes, colors, component dimensions

---

## Database Schema

CHAIRMAN uses SQLite for offline-first operation. The database includes three main tables:

### Clients
- `id`: Primary key
- `name`: Client name (required)
- `phone`: Phone number (optional)
- `notes`: Additional notes
- `no_show_count`: Track missed appointments

### Services
- `id`: Primary key
- `name`: Service name
- `price`: Service price
- `duration_minutes`: Service duration
- `buffer_minutes`: Buffer time after service

### Appointments
- `id`: Primary key
- `client_id`: Foreign key to clients
- `service_id`: Foreign key to services
- `start_time`: Appointment start (ISO format)
- `end_time`: Appointment end (ISO format)
- `paid`: Payment status (boolean)
- `payment_method`: Payment method used
- `notes`: Appointment notes

---

## Development

### Code Style

- **Type Hints**: All functions use type hints
- **Docstrings**: Google-style docstrings throughout
- **Error Handling**: Comprehensive exception handling
- **Logging**: Centralized logging system
- **Validation**: All user inputs are validated

### Adding New Features

1. **Core Logic**: Add business logic to `core/` modules
2. **Database**: Update schema in `data/db.py` if needed
3. **UI**: Add/update components in `ui/` directory
4. **Configuration**: Add constants to `config.py`
5. **Validation**: Add validation rules to `core/validators.py`

### Testing

Unit tests are planned for all core business logic. To run tests:

```bash
pytest tests/
```

---

## Logging

CHAIRMAN maintains comprehensive logs for debugging and auditing:

- **Location**: `logs/chairman.log`
- **Format**: Timestamped entries with log levels
- **Rotation**: 10 MB max file size, 5 backup files
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

View logs to troubleshoot issues or track application usage.

---

## Troubleshooting

### Application won't start
- Check that Python 3.10+ is installed: `python --version`
- Verify dependencies are installed: `pip install -r requirements.txt`
- Check logs in `logs/chairman.log` for error details

### Database errors
- Ensure `barber.db` has write permissions
- Delete `barber.db` to reset (WARNING: loses all data)
- Check logs for specific SQL errors

### UI issues
- Verify `style.qss` exists in the project root
- Check PySide6 installation: `pip show PySide6`
- Try running with default styling (remove/rename `style.qss`)

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper documentation
4. Test thoroughly
5. Submit a pull request

### Code Standards

- Follow PEP 8 style guide
- Add type hints to all functions
- Write docstrings for all public methods
- Include error handling
- Add logging where appropriate

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Roadmap

### Version 1.1 (Q1 2026)
- Enterprise/Solo mode implementation
- Enhanced UI redesign
- Layered client management
- Advanced search and filtering

### Version 1.2 (Q2 2026)
- SMS/Email reminder system
- Analytics dashboard
- Reporting features
- Data export capabilities

### Version 2.0 (Q3 2026)
- Cloud sync functionality
- Multi-location support
- Mobile companion app
- Advanced scheduling algorithms

---

## Support

For issues, questions, or feature requests:

- **Issues**: Open an issue on GitHub
- **Documentation**: See this README and inline code documentation
- **Logs**: Check `logs/chairman.log` for debugging information

---

## Acknowledgments

- Built with [PySide6](https://doc.qt.io/qtforpython/) (Qt for Python)
- Uses [SQLite](https://www.sqlite.org/) for data storage
- Inspired by the needs of professional barbers and hairdressers

---

**CHAIRMAN** - Empowering barbers to run their business professionally and efficiently.
