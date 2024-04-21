import os
import math
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PyPDF2 import PdfReader, PdfWriter

def split_pdf_by_parts(file_path, parts, output_path):
    pdf = PdfReader(file_path)
    total_pages = len(pdf.pages)
    pages_per_part = math.ceil(total_pages / parts)

    for i in range(parts):
        pdf_writer = PdfWriter()
        start_page = i * pages_per_part
        end_page = min((i+1) * pages_per_part, total_pages)

        for page in range(start_page, end_page):
            pdf_writer.add_page(pdf.pages[page])

        output = f'{output_path}_{i+1}.pdf'
        with open(output, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)

def split_pdf_by_page(file_path, split_page, output_path):
    pdf = PdfReader(file_path)
    total_pages = len(pdf.pages)

    for i in range(2):
        pdf_writer = PdfWriter()
        start_page = i * split_page
        end_page = min((i+1) * split_page, total_pages) if i < 1 else total_pages

        for page in range(start_page, end_page):
            pdf_writer.add_page(pdf.pages[page])

        output = f'{output_path}_{i+1}.pdf'
        with open(output, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)

def main():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select the PDF file to split", filetypes=(("PDF Files", "*.pdf"),)
    )
    if not file_path:
        messagebox.showinfo("Information", "No file selected.")
        return

    mode = simpledialog.askstring(
        "Input", "Split by parts (p) or page number (n)?", parent=root
    )
    if mode not in ['p', 'n']:
        messagebox.showinfo("Information", "Invalid mode selected.")
        return

    if mode == 'p':
        parts = simpledialog.askinteger(
            "Input", "Enter number of parts to split the PDF into", parent=root
        )
        if not parts or parts <= 0:
            messagebox.showinfo("Information", "Invalid number of parts.")
            return
    else:
        split_page = simpledialog.askinteger(
            "Input", "Enter the page number to split at", parent=root
        )
        if not split_page or split_page <= 0:
            messagebox.showinfo("Information", "Invalid page number.")
            return

    output_path = filedialog.asksaveasfilename(
        title="Save as", defaultextension=".pdf", filetypes=(("PDF Files", "*.pdf"),)
    )
    if not output_path:
        messagebox.showinfo("Information", "No output path selected.")
        return

    if mode == 'p':
        split_pdf_by_parts(file_path, parts, output_path)
    else:
        split_pdf_by_page(file_path, split_page, output_path)

    messagebox.showinfo("Information", "PDF split successfully!")

if __name__ == '__main__':
    main()
