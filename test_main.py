import pytest
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
    

from main import save_extracted_text_to_file

def test_save_extracted_text(tmp_path):
    output_path = tmp_path / "output.txt"
    sample_text = "Artificial intelligence helps researchers."

    save_extracted_text_to_file(sample_text, output_path)
    assert output_path.exists() 
    assert output_path.read_text(encoding="utf-8") == sample_text

def test_save_extracted_text_unicode(tmp_path):
    output_path = tmp_path / "paper.txt"
    sample_text = "Research paper: AI and coding"

    save_extracted_text_to_file(sample_text, output_path)
    assert output_path.read_text(encoding="utf-8") == sample_text

from main import process_pdfs

def test_process_pdfs_creates_text_files(tmp_path):
    input_folder = tmp_path / "research_papers"
    output_folder = tmp_path / "extracted_text"

    input_folder.mkdir()
    pdf_path = input_folder / "sample.pdf"

    with pymu.open() as doc:
        page = doc.new_page()
        page.insert_text((72, 72), "Batch processing works.")
        doc.save(pdf_path)

    process_pdfs(input_folder, output_folder)

    output_file = output_folder / "sample.txt"
    assert output_file.exists()
    assert "Batch processing works." in output_file.read_text(encoding="utf-8")

from main import chunk_text

def test_chunk_text():
    text = "ABCDEFGHIJKL"
    result = chunk_text(text, chunk_size=5, overlap=2)

    assert result == ["ABCDE", "DEFGH", "GHIJK", "JKL"]

def test_chunk_text_without_overlap():
    text = "ABCDEFGHIJ"

    result = chunk_text(text, chunk_size=4, overlap=0)

    assert result == ["ABCD", "EFGH", "IJ"]

def test_chunk_text_empty_string():
    text = ""
    result = chunk_text(text, chunk_size=3, overlap=1)

    assert result == []

def test_chunk_text_invalid_chunk_size():
    with pytest.raises(ValueError):
        chunk_text("Hello world", chunk_size=0, overlap=0)

def test_chunk_text_invald_overlap():
    with pytest.raises(ValueError):
        chunk_text("Hello world", chunk_size=5, overlap=5)
        chunk_text("Hello world", chunk_size=5, overlap=-2) # Added this statement inorder to test for negative values

from main import create_chunk_records

def test_create_chunk_records_returns_correct_metadata():
    text = "ABCDEFGHIJ"

    records = create_chunk_records(
        text,
        source_filename="research.pdf",
        chunk_size=5,
        overlap=0,
    )

    assert len(records) == 2

    assert records[0] == {
        "source": "research.pdf",
        "chunk_index": 1,
        "text": "ABCDE",
    }

    assert records[1] == {
        "source": "research.pdf",
        "chunk_index": 2,
        "text": "FGHIJ",
    }


def test_create_chunk_records_uses_overlapping_chunks():
    text = "ABCDEFGHIJ"

    records = create_chunk_records(
        text,
        source_filename="research.pdf",
        chunk_size=6,
        overlap=2,
    )

    assert records[0]["text"] == "ABCDEF"
    assert records[1]["text"] == "EFGHIJ"


def test_create_chunk_records_uses_sequential_indices():
    text = "ABCDEFGHIJKLMNO"

    records = create_chunk_records(
        text,
        source_filename="research.pdf",
        chunk_size=5,
        overlap=0,
    )

    assert [record["chunk_index"] for record in records] == [1, 2, 3]


def test_create_chunk_records_handles_empty_text():
    records = create_chunk_records(
        "",
        source_filename="empty.pdf",
        chunk_size=5,
        overlap=0,
    )

    assert records == []


def test_create_chunk_records_preserves_source_filename():
    records = create_chunk_records(
        "Hello world",
        source_filename="AI Research Paper.pdf",
        chunk_size=20,
        overlap=0,
    )

    assert records[0]["source"] == "AI Research Paper.pdf"
