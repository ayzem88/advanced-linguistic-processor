# 📚 Albhthya - Research Library

## Advanced Search System for Islamic Heritage

Albhthya (Research Library) is a modern and sophisticated desktop application designed for searching Islamic heritage books. Built specifically for researchers, students, and scholars, it provides a powerful and accurate search engine with an easy-to-use Arabic interface.

---

## ✨ Key Features

### 🔍 Advanced Search Engine
- **Smart search** with full Arabic diacritics support
- **Multiple search types**:
  - Exact match (complete words)
  - Partial match (word fragments)
  - Multi-word search (with flexible word spacing)
  - Morphological pattern search
  - Derivative search
- **Advanced filtering** by:
  - Main category
  - Subcategories
  - Specific books
  - Author

### 📖 Results Display
- **Automatic highlighting** of searched words in red
- **Context display** (5 words before and after)
- **Organized results table** showing:
  - Context surrounding the word
  - Book name
  - Author
  - Category
  - Page number
- **Full-text viewer** with highlighting

### ⚡ Performance & Speed
- **FTS5** (Full-Text Search) engine from SQLite
- Smart text indexing
- Instant results even in massive databases
- Caching for repeated searches
- Special optimizations for Arabic text

### 🎨 User Interface
- Elegant and eye-friendly Arabic design
- Full RTL (Right-to-Left) support
- Clear and readable Arabic fonts
- Logical organization of tools and menus
- Fast and smooth response

### 🗂️ Library Management
- Import books from text files
- Convert Access databases (.mdb) to SQLite
- Organize books by categories
- Detailed information for each book

---

## 🚀 Quick Start

### Requirements
- Python 3.8 or newer
- OS: Windows 10/11, macOS, Linux

### Installation

#### Windows
```cmd
# Double-click on
run_windows.bat

# Or manually:
pip install -r requirements.txt
python main.py
```

#### macOS / Linux
```bash
pip install -r requirements.txt
python main.py
```

---

## 📋 Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3.8+** | Core programming language |
| **PyQt6** | GUI framework |
| **SQLite** | Database |
| **FTS5** | Full-text search engine |
| **Regex** | Arabic text processing |
| **Pathlib** | Path management |

---

## 📖 User Guide

### Basic Search
1. Open the application
2. Choose search type (exact/partial/multi)
3. Enter the search term
4. Select search scope (optional)
5. Click "Search"

### Advanced Search
- **Respect Diacritics**: Enable for precise search with diacritics
- **Multi-word Search**: Search for multiple words (e.g., علم + عمل)
- **Pattern Search**: Search by morphological pattern
- **Select Specific Books**: Choose a specific book from subcategory

---

## 🏗️ Project Structure

```
Albhthya/
├── main.py                 # Main entry point
├── ui/                     # User interface
│   ├── main_window.py      # Main window
│   └── search_window.py    # Search window
├── db/                     # Database
│   ├── database.py         # Database management
│   └── performance_optimizer.py
├── utils/                  # Utilities
│   └── arabic_search.py    # Arabic text processing
├── converters/             # File converters
│   ├── mdb_converter.py    # Access converter
│   └── txt_converter.py    # Text importer
├── data/                   # Database and books
│   ├── shamela.db          # Main database
│   └── txt_books/          # Text books
└── requirements.txt        # Required packages
```

---

## 🎯 Future Development Plans

- [ ] Voice search
- [ ] Bookmarks support
- [ ] Export results to PDF/Word
- [ ] Notes and comments system
- [ ] Cloud synchronization
- [ ] Mobile app (iOS/Android)
- [ ] Web interface

---

## 📊 Statistics

- **Supported books**: Unlimited
- **Search speed**: Less than 1 second
- **Database size**: Depends on number of books
- **Diacritics support**: Full
- **Supported languages**: Arabic (expandable)

---

## 🤝 Contributing

We welcome contributions! You can:
- Report bugs
- Suggest new features
- Submit pull requests
- Translate the interface

---

## 📞 Contact & Support

**Developer**: Aymen Tayeb Ben Nji

**Email**: [aymen.nji@gmail.com](mailto:aymen.nji@gmail.com)

For technical support or inquiries, feel free to contact via email.

---

## 📄 License

This project is open source and available for personal and academic use.

---

## 🙏 Acknowledgments

- **Al-Maktaba Al-Shamela**: Source of inspiration
- **Arab Developer Community**: For support and open-source tools
- **Islamic Researchers**: Who benefit from this tool

---

## 📝 Release Notes

### Version 1.0.0
- ✅ Advanced search engine with full Arabic support
- ✅ Modern and elegant user interface
- ✅ High performance and speed
- ✅ Multiple search types
- ✅ Advanced result filtering
- ✅ Organized results display with context

---

<div align="center">

**Made with ❤️ for Islamic Heritage Researchers**

[Email](mailto:aymen.nji@gmail.com)

---

**Albhthya Research Library** - Your Tool for Precise Academic Research

© 2024 Aymen Tayeb Ben Nji. All rights reserved.

</div>




