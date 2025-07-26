import re
from PyPDF2 import PdfReader, PdfWriter

sku_pattern = re.compile(r"\b([a-zA-Z0-9\-]+)\*(\d+)\b", re.IGNORECASE)

def first_segment_key(sku):
    return sku.split('-')[0].lower()

def sort_pdf_by_sku(input_pdf_path, output_pdf_path):
    reader = PdfReader(input_pdf_path)
    page_sku_qty = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.replace(';*', '*')
        match = sku_pattern.findall(text)

        if match:
            sku, qty = match[0]
            sku = sku.upper().strip()
            qty = int(qty)
        else:
            sku = f"ZZZ{i:04}"
            qty = 1

        page_sku_qty.append((i, sku, qty))

    # Sort by SKU prefix, then quantity DESC, then page index
    sorted_page_info = sorted(page_sku_qty, key=lambda x: (first_segment_key(x[1]), -x[2], x[0]))

    expanded_sorted_pages = []
    for page_index, sku, qty in sorted_page_info:
        for _ in range(qty):
            expanded_sorted_pages.append((page_index, sku))

    writer = PdfWriter()
    for page_index, _ in expanded_sorted_pages:
        writer.add_page(reader.pages[page_index])

    with open(output_pdf_path, "wb") as f:
        writer.write(f)
