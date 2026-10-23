from pathlib import Path

def get_pdf_files(folder_path):
    folder_path = Path(folder_path)
    return list(folder_path.glob("*.[pP][dD][fF]"))

def main():
    folder = Path("research_papers")
    pdf_files = get_pdf_files(folder)

    print(f"Found {len(pdf_files)} PDF files.")

    for pdf in pdf_files:
        print(f"{pdf} - {pdf.stat().st_size / (1024):.2f} KB")

if __name__ == "__main__":
    main()