# LedgerLite

A polished macOS desktop expense tracker built with PySide6 (Qt for Python), SQLite, SQLAlchemy, pandas, and matplotlib.

## Features

### Implemented (MVP)
- **Dashboard**: Key metrics (income/expense/net) with category bar chart and daily net trend chart
- **Transactions**: Full CRUD operations with advanced filtering (date range, category, account, type, search)
- **Database**: SQLite with SQLAlchemy ORM, repository pattern, and sample data seeding
- **UI**: Modern sidebar navigation with month selector and responsive design
- **Styling**: Professional light theme with dark theme support

###  TODO (Stretch Items)
- **Categories**: CRUD operations with color picker and hierarchical categories
- **Budgets**: Monthly spending limits with progress bars and warnings
- **Import/Export**: CSV import wizard with column mapping and export functionality
- **Advanced Features**: Recurring transactions, receipt attachments, security features

## Architecture

```
ledgerlite/
├── app/                    # Qt UI Application
│   ├── main.py            # Application entry point
│   └── ui/
│       ├── main_window.py # Main window with sidebar navigation
│       ├── pages/         # Application pages
│       │   ├── dashboard_page.py      
│       │   ├── transactions_page.py   
│       │   ├── categories_page.py     
│       │   ├── budgets_page.py        
│       │   └── import_export_page.py 
│       └── widgets/
│           └── transaction_form.py    
├── charts/                
│   ├── category_bar.py   
│   └── monthly_trend.py  
├── data/                  
│   ├── models.py          
│   ├── db.py              
│   ├── repo.py            
│   └── seed.py            
├── services/             
├── utils/                 
├── assets/
│   └── styles.qss         
├── tests/                 
├── scripts/
│   ├── dev_run.sh         
│   └── package_mac.sh     
└── pyproject.toml         
```

## Data Model

- **accounts**: Financial accounts (cash, bank, card)
- **categories**: Transaction categories (expense/income) with colors
- **transactions**: Financial transactions with full details
- **budgets**: Monthly spending limits per category
- **attachments**: Receipt and document attachments

## Quick Start

### Prerequisites
- Python 3.9+
- macOS (for packaging)

### Development Setup

1. **Clone and navigate to the project:**
   ```bash
   cd ledgerlite
   ```

2. **Run the development script:**
   ```bash
   ./scripts/dev_run.sh
   ```

   This script will:
   - Create a virtual environment
   - Install all dependencies
   - Initialize the database with sample data
   - Launch the application

### Manual Setup

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Initialize database:**
   ```bash
   python -c "
   from ledgerlite.data.db import init_database
   from ledgerlite.data.seed import seed_database
   init_database()
   seed_database()
   "
   ```

4. **Run the application:**
   ```bash
   python -m ledgerlite.app.main
   ```

## Building for Distribution

### macOS App Bundle

```bash
./scripts/package_mac.sh
```

This creates:
- `dist/LedgerLite.app` - macOS application bundle
- `dist/LedgerLite-1.0.0-macOS.dmg` - DMG installer (optional)

## Usage

### Dashboard
- View key financial metrics for the selected month
- Analyze expenses by category with interactive bar chart
- Track daily net amounts with trend line chart

### Transactions
- Add, edit, and delete transactions
- Filter by date range, category, account, type, and search terms
- Sort by any column
- Real-time data updates

### Navigation
- Use the sidebar to switch between pages
- Select different months using the month selector
- Toggle between light and dark themes (coming soon)

## Development

### Code Quality
- **Type Hints**: Full type annotations throughout
- **Documentation**: Comprehensive docstrings
- **Linting**: Ruff for code quality
- **Formatting**: Black for consistent code style
- **Testing**: pytest for unit tests

### Database
- **Repository Pattern**: Clean separation of data access
- **SQLAlchemy ORM**: Type-safe database operations
- **SQLite**: Lightweight, file-based database
- **Migrations**: Automatic schema management

### UI/UX
- **PySide6**: Native Qt widgets and styling
- **Responsive Design**: Adapts to different window sizes
- **Modern Styling**: Professional appearance with QSS
- **Accessibility**: Keyboard navigation and screen reader support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run linting and formatting
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Roadmap

### Version 1.1
- [ ] Complete categories management
- [ ] Implement budgets with progress tracking
- [ ] Add CSV import/export functionality

### Version 1.2
- [ ] Recurring transactions
- [ ] Receipt attachments
- [ ] Advanced reporting
- [ ] Data backup/restore

### Version 2.0
- [ ] Multi-currency support
- [ ] Cloud synchronization
- [ ] Mobile companion app
- [ ] Advanced analytics

---

**Built with ❤️ by HexSoftware**
