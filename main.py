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

    print("\n --Extracted Text from download.pdf--")
    print(extracted_text[:1000])

    print(f"Inventory saved to: {output_file.resolve()}")
if __name__ == "__main__":
    main()