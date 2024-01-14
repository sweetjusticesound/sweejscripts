import os
import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfMerger

def merge_pdfs(paths, output):
    pdf_merger = PdfMerger()

    for path in paths:
        with open(path, 'rb') as f:
            pdf_merger.append(f)

    with open(output, 'wb') as output_pdf:
        pdf_merger.write(output_pdf)

def select_directory(title):
    root = tk.Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title=title)
    return directory

def select_output_file(title):
    root = tk.Tk()
    root.withdraw()
    file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=(("PDF file", "*.pdf"),("All Files", "*.*")), title=title)
    return file

def main():
    input_folder = select_directory("Select input folder")
    output_file = select_output_file("Select output file")

    if not input_folder or not output_file:
        print("No folder or output file selected.")
        return

    pdf_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".pdf")]
    merge_pdfs(pdf_files, output_file)
    print(f"PDFs merged into {output_file}")

if __name__ == '__main__':
    main()
