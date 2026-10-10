# Faker CSV Generator

A modular desktop application built with **wxPython** (wxWidgets wrapper) and the **Faker** library that allows users to effortlessly generate customized mock CSV data files.

---

## Features

- **Custom Column Builder**: Define arbitrary column titles and map them directly to any standard `Faker` provider (e.g., `name`, `email`, `address`, `company`, `phone_number`, `uuid4`, etc.).
- **Flexible Row Count**: Generate anywhere from 1 row up to millions of mock data records.
- **Locale Support**: Select from multiple regional locales (e.g., `en_US`, `fr_FR`, `de_DE`, `ja_JP`, `ar_AA`) for localized mock data.
- **Background Processing**: Employs threading to keep the GUI responsive during large dataset generation with progress visualization.
- **Modular OOP Architecture**: Clean separation between Data Models, Core Generation Engine, and UI Components.

---

## Installation

1. Ensure you have Python 3.8+ installed.
2. Clone or download this repository.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt