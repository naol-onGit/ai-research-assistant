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

from main import process_pdf_into_chunks

def test_process_pdf_into_chunks_return_chunk_records(tmp_path):
    pdf_path = tmp_path / "research.pdf"

    doc = pymu.open()
    page = doc.new_page()
    page.insert_text((50, 50),  "Artificial intelligence supports scientific research. "
        "Machine learning helps researchers discover patterns.")
    doc.save(pdf_path)
    doc.close()

    records = process_pdf_into_chunks(pdf_path, chunk_size=50, overlap=10)
    assert len(records) > 0
    assert records[0]["source"] == "research.pdf"
    assert records[0]["chunk_index"] == 1
    assert records[0]["text"] != " "

def test_process_pdf_into_chunks_preserves_chunk_indices(tmp_path):
    pdf_path = tmp_path / "research.pdf"

    doc = pymu.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "A" * 200
    )
    doc.save(pdf_path)
    doc.close()

    records = process_pdf_into_chunks(
        pdf_path,
        chunk_size=50,
        overlap=10,
    )

    expected_indices = list(range(1, len(records) + 1))

    assert [record["chunk_index"] for record in records] == expected_indices


def test_process_pdf_into_chunks_handles_empty_pdf(tmp_path):
    pdf_path = tmp_path / "empty.pdf"

    doc = pymu.open()
    doc.new_page()
    doc.save(pdf_path)
    doc.close()

    records = process_pdf_into_chunks(pdf_path)

    assert records == []

import json
from main import save_chunk_records

def test_save_chunk_records_writes_correct_data(tmp_path):
    records = [
        {"source": "research.pdf",
         "chunk_index": 1,
         "text": "AI supports scientific research.",}
    ]

    output_file = tmp_path / "chunks.json"

    save_chunk_records(records, output_file)
    assert output_file.exists()

    with open(output_file, "r", encoding="utf-8") as file:
        saved_records = json.load(file)

    assert saved_records == records

def test_save_chunk_records_preserves_all_fields(tmp_path):
    records = [
        {
            "source": "AI_Paper.pdf",
            "chunk_index": 3,
            "text": "Machine learning helps researchers.",
        }
    ]

    output_file = tmp_path / "chunks.json"
    save_chunk_records(records, output_file)

    with open(output_file, "r", encoding="utf-8") as file:
        saved_records = json.load(file)

    assert saved_records[0]["source"] == "AI_Paper.pdf"
    assert saved_records[0]["chunk_index"] == 3
    assert saved_records[0]["text"] == ("Machine learning helps researchers.")

def test_save_chunk_records_creates_missing_directory(tmp_path):
    records = [
        {
            "source": "research.pdf",
            "chunk_index": 1,
            "text": "Sample research text.",
        }
    ]

    output_file = tmp_path / "data" / "chunk.json"

    save_chunk_records(records, output_file)

    assert output_file.exists()
    assert output_file.parent.is_dir()

def test_save_chunk_records_handles_empty_list(tmp_path):
    records = []
    output_file = tmp_path / "chunks.json"

    save_chunk_records(records, output_file)

    with open(output_file, "r", encoding="utf-8") as file:
        saved_records = json.load(file)

    assert saved_records == []

def test_save_chunk_records_preserves_unicode_text(tmp_path):
    records = [
        {
            "source": "amharic_research.pdf",
            "chunk_index": 1,
            "text": "ሰላም — AI supports scientific research.",
        }
    ]

    output_file = tmp_path / "chunks.json"

    save_chunk_records(records, output_file)

    with open(output_file, "r", encoding="utf-8") as file:
        saved_records = json.load(file)

    assert saved_records == records

    saved_text = output_file.read_text(encoding="utf-8")
    assert "ሰላም" in saved_text

from main import load_chunk_records

def test_load_chunk_records_reads_correct_data(tmp_path):
    records = [
        {
            "source": "research_paper.pdf",
            "chunk_index": 1,
            "text": "Machine learning is useful."
    }
    ]

    input_file = tmp_path / "chunks.json"
    with open(input_file, "w", encoding="utf-8") as file:
        json.dump(records, file)

    loaded_records = load_chunk_records(input_file)
    assert loaded_records == records

def test_load_chunk_records_handles_empty_list(tmp_path):
    input_file = tmp_path / "chunks.json"
    input_file.write_text("[]", encoding="utf-8")

    loaded_records = load_chunk_records(input_file)

    assert loaded_records == []

def test_load_chunk_records_missing_file(tmp_path):
    input_file = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_chunk_records(input_file)

def test_load_chunk_records_preserve_unicode(tmp_path):
    records = [
         {"source": "research.pdf",
            "chunk_index": 1,
            "text": "የማሽን ትምህርት"}
    ]  

    input_file = tmp_path / "chunks.json"

    with open(input_file, "w", encoding="utf") as file:
        json.dump(records, file, ensure_ascii=False)

    loaded_records = load_chunk_records(input_file)

    assert loaded_records == records

from main import search_chunks

def test_search_chunks_finds_matching_records():
    records =  [
        {
            "source": "paper1.pdf",
            "chunk_index": 1,
            "text": "Machine learning is useful in healthcare."
        },
        {
            "source": "paper2.pdf",
            "chunk_index": 2,
            "text": "Neural networks analyze medical images."
        },
        {
            "source": "paper3.pdf",
            "chunk_index": 1,
            "text": "Machine learning can detect diseases."
        }
    ]

    results = search_chunks(records, "machine learning")

    assert len(results) == 2
    assert results[0]["source"] == "paper1.pdf"
    assert results[1]["source"] == "paper3.pdf"

def test_search_chunks_is_case_insensitive():
    records = [
        {
            "source": "paper1.pdf",
            "chunk_index": 1,
            "text": "Machine Learning improves medical diagnosis."
        }
    ]

    results = search_chunks(records, "MACHINE LEARNING")

    assert len(results) == 1
    assert results[0]["source"] == "paper1.pdf"

def test_search_chunks_returns_empty_list_when_no_match():
    records = [
        {
            "source": "paper1.pdf",
            "chunk_index": 1,
            "text": "Machine learning improves medical diagnosis."
        }
    ]

    results = search_chunks(records, "robotics")

    assert results == []

def test_search_chunks_rejects_empty_query():
    records = [{
            "source": "paper1.pdf",
            "chunk_index": 1,
            "text": "Machine learning improves medical diagnosis."
        }]

    with pytest.raises(ValueError):
        search_chunks(records, "")

def test_search_chunks_rejects_whitespace_query():
    records = [
        {
            "source": "paper1.pdf",
            "chunk_index": 1,
            "text": "Machine learning improves medical diagnosis."
        }
    ]

    with pytest.raises(ValueError):
        search_chunks(records, "   ")

def test_search_chunks_preserves_chunk_metadata():
    records = [
        {
            "source": "paper1.pdf",
            "chunk_index": 4,
            "text": "Machine learning improves medical diagnosis."
        }
    ]

    results = search_chunks(records, "machine learning")

    assert results[0]["source"] == "paper1.pdf"
    assert results[0]["chunk_index"] == 4
    assert results[0]["text"] == records[0]["text"]

from main import rank_chunks

def test_rank_chunks_sorts_by_score():
    records = [
        {
            "source": "paper1.pdf",
            "chunk_index": 1,
            "text": "Machine learning is useful."
        },
        {
            "source": "paper2.pdf",
            "chunk_index": 2,
            "text": (
                "Machine learning is important. "
                "Machine learning is powerful."
            )
        }
    ]

    results = rank_chunks(records, "machine learning")

    assert results[0]["record"]["source"] == "paper2.pdf"
    assert results[1]["record"]["source"] == "paper1.pdf"

def test_rank_chunks_calculates_correct_scores():
    records = [
        {
            "source": "paper1.pdf",
            "chunk_index": 1,
            "text": "Machine learning is useful."
        },
        {
            "source": "paper2.pdf",
            "chunk_index": 2,
            "text": (
                "Machine learning is important. "
                "Machine learning is powerful."
            )
        }   
    ]

    results = rank_chunks(records, "machine learning")

    assert results[0]["score"] == 2
    assert results[1]["score"] == 1

def test_rank_chunks_is_case_insensitive():
    records = [
         {
            "source": "paper1.pdf",
            "chunk_index": 1,
            "text": "Machine Learning is useful."
        }
    ]

    results = rank_chunks(records, "MACHINE LEARNING")

    assert len(results) == 1
    assert results[0]["score"] == 1

def test_rank_chunks_returns_empty_list_when_no_match():
    records = [
        {
            "source": "paper1.pdf",
            "chunk_index": 1,
            "text": "Machine learning is useful."
        }
    ]

    results = rank_chunks(records, "robotics")

    assert results == []

def test_rank_chunks_rejects_empty_query():
    records = []

    with pytest.raises(ValueError):
        rank_chunks(records, "")

def test_rank_chunks_rejects_whitespace_query():
    records = []

    with pytest.raises(ValueError):
        rank_chunks(records, "    ")

def test_rank_chunks_preserves_meta_data():
    records = [
        {
            "source": "research.pdf",
            "chunk_index": 5,
            "text": "Machine learning is useful."
        }
    ]

    results = rank_chunks(records, "machine learning")

    assert results[0]["record"]["source"] == "research.pdf"
    assert results[0]["record"]["chunk_index"] == 5
    assert results[0]["record"]["text"] == records[0]["text"]

def test_rank_chunks_handles_equal_scores():
    records = [
        {
            "source": "paper1.pdf",
            "chunk_index": 1,
            "text": "Machine learning is useful."
        },
        {
            "source": "paper2.pdf",
            "chunk_index": 2,
            "text": "Machine learning is powerful."
        }
    ]

    results = rank_chunks(records, "machine learning")

    assert len(results) == 2
    assert results[0]["score"] == 1
    assert results[1]["score"] == 1

from main import rank_chunks_tfidf

def test_rank_chunks_tfidf_rejects_whitespace_query():
    records = [{"source": "a.pdf", "chunk_index": 0, "text": "neural networks"}]

    with pytest.raises(ValueError):
        rank_chunks_tfidf(records, "    ")

def test_rank_chunks_tfidf_returns_empty_list_for_empty_records():
    records = []

    results = rank_chunks_tfidf(records, "machine learning")
    assert results == []

def test_rank_chunks_tfidf_ranks_more_relevant_chunk_first():
    records = [
        {"source": "b.pdf", "chunk_index": 1, "text": "neural networks are everywhere"},
        {"source": "a.pdf", "chunk_index": 0, "text": "neural neural neural networks"},
    ]

    results = rank_chunks_tfidf(records, "neural")
    assert results[0]["record"] == records[1] 
    assert results[0]["score"] > results[1]["score"]

def test_rank_chunks_tfidf_returns_empty_list_for_absent_term():
    records = [
        {"source": "a.pdf", "chunk_index": 0, "text": "neural networks"},
        {"source": "a.pdf", "chunk_index": 1, "text": "deep learning models"},
    ]

    assert rank_chunks_tfidf(records, "quantum") == []

def test_rank_chunks_tfidf_preserves_record_metadata():
    records = [{"source": "a.pdf", "chunk_index": 0, "text": "neural networks"}]

    results = rank_chunks_tfidf(records, "neural")

    assert results[0]["record"]["source"] == "a.pdf"
    assert results[0]["record"]["chunk_index"] == 0
    assert isinstance(results[0]["score"], float)

import numpy as np

class FakeModel:
    """Tiny stand-in: 'car'/'automobile' -> vehicle axis, 'banana' -> food axis."""
    def encode(self, texts):
        vectors = []
        for text in texts:
            text = text.lower()
            vehicle = 1.0 if ("car" in text or "automobile" in text) else 0.0
            food = 1.0 if "banana" in text else 0.0
            vectors.append([vehicle, food])
        return np.array(vectors)

from main import rank_chunks_semantic

def test_rank_chunks_semantic_ranks_by_meaning(monkeypatch):
    monkeypatch.setattr("main.get_embedding_model", lambda: FakeModel())
    records = [
        {"source": "a.pdf", "chunk_index": 1, "text": "I ate a banana"},
        {"source": "a.pdf", "chunk_index": 2, "text": "The automobile was fast"},
    ]

    results = rank_chunks_semantic(records, "car")
    assert results[0]["record"] == records[1]
    assert results[0]["score"] > results[1]["score"]

def test_rank_chunks_semantic_respects_top_k(monkeypatch):
    monkeypatch.setattr("main.get_embedding_model", lambda: FakeModel())
    records = [
        {"source": "a.pdf", "chunk_index": 1, "text": "a car"},
        {"source": "a.pdf", "chunk_index": 2, "text": "an automobile"},
        {"source": "a.pdf", "chunk_index": 3, "text": "a banana"},
    ]

    results = rank_chunks_semantic(records, "car", top_k=2)

    assert len(results) == 2

def test_rank_chunks_semantics_rejects_empty_query():
    with pytest.raises(ValueError):
        rank_chunks_semantic([{"source": "a.pdf", "chunk_index": 1, "text": "x"}], "    ")

def test_rank_chunks_semantics_rejects_invalid_top_k():
    with pytest.raises(ValueError):
        rank_chunks_semantic([{"source": "a.pdf", "chunk_index": 1, "text": "x"}], "car", top_k=0)

def test_rank_chunks_semantics_returns_empty_list_for_empty_records():
    assert rank_chunks_semantic([], "car") == []

from main import embed_chunks

def test_embed_chunks_adds_embedding_to_each_record(monkeypatch):
    monkeypatch.setattr("main.get_embedding_model", lambda: FakeModel())
    records = [
        {"source": "a.pdf", "chunk_index": 1, "text": "a car"},
        {"source": "a.pdf", "chunk_index": 2, "text": "a banana"},
    ]

    results = embed_chunks(records)

    assert len(results) == 2
    for result in results:
        assert len(result["embedding"]) == 2
        assert isinstance(result["embedding"], list)


def test_embed_chunks_preserves_metadata_and_leaves_originals_unchanged(monkeypatch):
    monkeypatch.setattr("main.get_embedding_model", lambda: FakeModel())
    records = [{"source": "a.pdf", "chunk_index": 1, "text": "a car"}]

    results = embed_chunks(records)

    assert results[0]["source"] == "a.pdf"
    assert results[0]["chunk_index"] == 1
    assert results[0]["text"] == "a car"
    assert "embedding" not in records[0]


def test_embed_chunks_returns_empty_list_for_empty_records():
    assert embed_chunks([]) == []

def test_rank_chunks_semantic_respects_min_score_drops_weak_matches(monkeypatch):
    monkeypatch.setattr("main.get_embedding_model", lambda: FakeModel())
    records = [
        {"source": "a.pdf", "chunk_index": 1, "text": "I ate a banana"},
        {"source": "a.pdf", "chunk_index": 2, "text": "The automobile was fast"},
    ]

    results = rank_chunks_semantic(records, "car", min_score=0.5)

    assert len(results) == 1
    assert results[0]["record"] == records[1]

def test_rank_chunks_semantic_without_min_score_keeps_all_up_to_top_k(monkeypatch):
    monkeypatch.setattr("main.get_embedding_model", lambda: FakeModel())
    records = [
        {"source": "a.pdf", "chunk_index": 1, "text": "I ate a banana"},
        {"source": "a.pdf", "chunk_index": 2, "text": "The automobile was fast"},
    ]

    results = rank_chunks_semantic(records, "car")

    assert len(results) == 2

def test_rank_chunks_semantic_returns_empty_list_when_nothing_meets_min_score(monkeypatch):
    monkeypatch.setattr("main.get_embedding_model", lambda: FakeModel())
    records = [
        {"source": "a.pdf", "chunk_index": 1, "text": "I ate a banana"},
        {"source": "a.pdf", "chunk_index": 2, "text": "Plain text"},
    ]

    assert rank_chunks_semantic(records, "car", min_score=0.5) == []

from main import add_chunks, get_chroma_collection

def make_records():
    return [
        {"source": "a.pdf", "chunk_index": 1, "text": "a car", "embedding": [1.0, 0.0]},
        {"source": "a.pdf", "chunk_index": 2, "text": "a banana", "embedding": [0.0, 1.0]},
    ]

def test_add_chunks_stores_records(tmp_path):
    stored = add_chunks("u1", make_records(), db_path=str(tmp_path))
    assert stored == 2
    assert get_chroma_collection(str(tmp_path)).count() == 2

def test_add_chunks_saves_text_and_metadata(tmp_path):
    add_chunks("u1", make_records(), db_path=str(tmp_path))
    result = get_chroma_collection(str(tmp_path)).get(ids=["u1:a.pdf:2"])

    assert result["documents"][0] == "a banana"
    assert result["metadatas"][0]["user_id"] == "u1"
    assert result["metadatas"][0]["source"] == "a.pdf"
    assert result["metadatas"][0]["chunk_index"] == 2


def test_add_chunks_twice_does_not_create_duplicates(tmp_path):
    add_chunks("u1", make_records(), db_path=str(tmp_path))
    add_chunks("u1", make_records(), db_path=str(tmp_path))

    assert get_chroma_collection(str(tmp_path)).count() == 2


def test_add_chunks_requires_user_id(tmp_path):
    with pytest.raises(ValueError):
        add_chunks("", make_records(), db_path=str(tmp_path))


def test_add_chunks_returns_zero_for_empty_records(tmp_path):
    assert add_chunks("u1", [], db_path=str(tmp_path)) == 0
