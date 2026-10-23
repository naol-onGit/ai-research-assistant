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

    