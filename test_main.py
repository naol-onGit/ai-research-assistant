from main import get_pdf_files

def test_get_pdf_files(tmp_path):

    (tmp_path/ "paper.pdf").touch()
    (tmp_path/ "download.pdf").touch()
    (tmp_path/ "AI in Clinical Diagnostics Research Paper.pdf").touch()
    (tmp_path/ "renewable_energy_research_paper_docx_draft.txt").touch()

    result = get_pdf_files(tmp_path)
    assert len(result) == 3
    assert {file.name for file in result} == {
        "paper.pdf",
        "download.pdf",
        "AI in Clinical Diagnostics Research Paper.pdf"
    }

def test_get_pdf_files_empty_folder(tmp_path):
    result = get_pdf_files(tmp_path)

    assert result == []

import csv
from main import export_inventory

def test_export_inventory_writes_correct_data(tmp_path):
    # create a sample PDF file
    pdf1 = tmp_path / "paper.pdf"
    pdf2 = tmp_path / "report.pdf"

    pdf1.write_bytes(b"12345")
    pdf2.write_bytes(b"1234567890")

    output_file = tmp_path / "inventory.csv" 

    export_inventory([pdf1, pdf2], output_file)

    with open(output_file, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    assert reader.fieldnames == ["filename", "extension", "size_bytes", "size_kb",]
    assert len(rows) == 2

    assert rows[0]["filename"] == "paper.pdf"
    assert rows[0]["extension"] == ".pdf"
    assert int(rows[0]["size_bytes"]) == 5
    assert float(rows[0]["size_kb"]) == 5 / 1024

    assert rows[1]["filename"] == "report.pdf"
    assert int(rows[1]["size_bytes"]) == 10

def test_export_inventory_empty_list(tmp_path):
    output_file = tmp_path / "empty_inventory.csv"

    export_inventory([], output_file)

    with open(output_file, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

        assert reader.fieldnames == [
            "filename",
            "extension",
            "size_bytes",
            "size_kb",
        ]
        assert rows == []

import csv
import pymupdf as pymu

from main import (get_pdf_files, export_inventory, extract_text_from_pdf)

def test_extract_text_from_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"

    with pymu.open() as doc:
        page = doc.new_page()
        page.insert_text((72, 72), "Artifical intelligence helps researchers.")
        doc.save(pdf_path)

    result = extract_text_from_pdf(pdf_path)
    assert "Artifical intelligence helps researchers." in result

def test_extract_text_from_pdf_empty_pdf(tmp_path):
    pdf_path = tmp_path / "blank.pdf"

    with pymu.open() as doc:
        doc.new_page()
        doc.save(pdf_path)

    result = extract_text_from_pdf(pdf_path)
    assert result == ""
    

    