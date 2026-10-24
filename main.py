from pathlib import Path
import pymupdf as pymu
import csv

def get_pdf_files(folder_path):
    folder_path = Path(folder_path)
    return list(folder_path.glob("*.[pP][dD][fF]"))

def export_inventory(pdf_files, output_file):
    fieldnames = ["filename", "extension", "size_bytes", "size_kb"]
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames = fieldnames)
        writer.writeheader()
        for pdf in pdf_files:
            writer.writerow({
                "filename": pdf.name,
                "extension": pdf.suffix,
                "size_bytes": pdf.stat().st_size,
                "size_kb": pdf.stat().st_size / 1024
            })

def extract_text_from_pdf(pdf_path):
    """Extracts text from every page of a PDF."""
    with pymu.open(pdf_path) as doc:
        pages = []

        for page in doc:
            pages.append(page.get_text())

    return "\n".join(pages)

def save_extracted_text_to_file(text, output_path):
    """Saves the extracted text to UTF-8 text file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(text, encoding="utf-8")

def process_pdfs(input_folder, output_folder):
    pdf_files = get_pdf_files(input_folder)

    for pdf_path in pdf_files:
        extracted_text = extract_text_from_pdf(pdf_path)

        output_path = Path(output_folder) / f"{pdf_path.stem}.txt"
        save_extracted_text_to_file(extracted_text, output_path)

def main():
    folder = Path("research_papers")
    pdf_files = get_pdf_files(folder)
    
    print(f"Found {len(pdf_files)} PDF files.")

    for pdf in pdf_files:
        print(f"{pdf} - {pdf.stat().st_size / (1024):.2f} KB")

    output_file = Path("inventory.csv")
    export_inventory(pdf_files, output_file)

    pdf_path = Path("research_papers/download.pdf")
    extracted_text = extract_text_from_pdf(pdf_path)

    # print("\n --Extracted Text from download.pdf--")
    # print(extracted_text[:1000])

    print(f"Inventory saved to: {output_file.resolve()}")

    output_path = Path("extracted_text/download.txt")
    save_extracted_text_to_file(extracted_text, output_path)

    print(f"Extracted text saved to: {output_path.resolve()}")

    process_pdfs("research_papers", "extracted_text")
    print("PDF processing completed.")

if __name__ == "__main__":
    main()