import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd

st.set_page_config(page_title="Smart Invoice Extractor", layout="centered")
st.title("🧾 Smart Invoice Extractor")

uploaded_file = st.file_uploader("📤 Upload an invoice PDF", type="pdf")

# --- Extract text from PDF ---
def extract_text_from_pdf_bytes(file_bytes):
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
        for page in pdf:
            text += page.get_text()
    return text

# --- Parse fields using regex ---
def parse_invoice_text(text):
    name = re.search(r"Invoice to[:\-]?\s*(.*)", text, re.IGNORECASE)
    date = re.search(r"(?:Date|Invoice Date)[:\-]?\s*([\d/.-]+)", text, re.IGNORECASE)
    total = re.search(r"(?:Total Amount|Grand Total|Amount Due)[:\-]?\s*(?:₹|INR)?\s?([\d,]+)", text, re.IGNORECASE)
    invoice_num = re.search(r"(?:Invoice No|Invoice #)[:\-]?\s*([A-Za-z0-9\-]+)", text, re.IGNORECASE)

    return {
        "Invoice No": invoice_num.group(1) if invoice_num else "Not Found",
        "Name": name.group(1).strip() if name else "Not Found",
        "Date": date.group(1) if date else "Not Found",
        "Grand Total": total.group(1) if total else "Not Found"
    }

if uploaded_file:
    st.success("📄 File uploaded successfully!")
    file_bytes = uploaded_file.read()
    text = extract_text_from_pdf_bytes(file_bytes)
    data = parse_invoice_text(text)
    df = pd.DataFrame([data])
    st.dataframe(df)

    # 💾 Download CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download as CSV", csv, "invoice_data.csv", "text/csv")
else:
    st.info("Upload a PDF invoice to extract details.")
