# AI Research Assistant

A Python project that organizes research papers by discovering PDF files, displaying their file sizes, and exporting document metadata to a CSV inventory.

## Current Features

- Discover PDF files in a research papers directory.
- Display each PDF's filename and size in kilobytes.
- Export document metadata to a CSV file.
- Handle empty folders and empty file lists.
- Test core functionality with pytest.

## Project Structure

```text
ai-research-assistant/
├── research_papers/   # Research PDFs (not tracked by Git)
├── main.py            # Application logic
├── test_main.py       # Automated tests
├── inventory.csv      # Generated CSV inventory (not tracked by Git)
├── .gitignore         # Files and folders excluded from Git
└── README.md          # Project documentation
```

## Requirements

- Python 3
- pytest for running tests

## Setup

Clone the repository and enter the project directory:

```bash
git clone <your-repository-url>
cd ai-research-assistant
```

Create and activate a virtual environment on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install pytest:

```powershell
python -m pip install pytest
```

## Usage

1. Place research PDF files in the `research_papers/` directory.
2. Run the application from the project root:

```powershell
python main.py
```

3. Check the generated `inventory.csv` file for the document inventory.

## Running Tests

Run the automated test suite:

```powershell
python -m pytest -v
```

The current test suite checks PDF discovery and CSV export behavior, including empty inputs.

## Roadmap

- [x] Discover PDF files.
- [x] Display PDF file sizes.
- [x] Export an inventory to CSV.
- [x] Test PDF discovery and CSV export.
- [ ] Extract text from research papers.
- [ ] Clean and structure extracted text.
- [ ] Search papers by keywords.
- [ ] Build a research question-answering system.
- [ ] Add a web interface.

## Project Goal

The long-term goal is to build an AI-powered research assistant that can help users explore research papers, search for relevant information, and answer questions grounded in the contents of their documents.
