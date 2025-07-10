import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd

st.set_page_config(page_title="Smart Invoice Extractor", layout="centered")
st.title("🧾 Smart Invoice Extractor")

uploaded_file = st.file_uploader("📤 Upload an invoice PDF", type="pdf")

# 🔍 Extract text from PDF
def extract_text_from_pdf_bytes(file_bytes):
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
        for page in pdf:
            text += page.get_text()
    return text

# 🧠 Parse multiple invoices using re.findall()
def parse_multiple_invoices(text):
    invoice_nos = re.findall(r"Invoice No[:\-]?\s*([A-Za-z0-9\-]+)", text, re.IGNORECASE)
    names = re.findall(r"Invoice to[:\-]?\s*(.*)", text, re.IGNORECASE)
    dates = re.findall(r"(?:Date|Invoice Date)[:\-]?\s*([\d/.-]+)", text, re.IGNORECASE)
    totals = re.findall(r"(?:Total Amount|Grand Total|Amount Due)[:\-]?\s*(?:₹|INR)?\s*([\d,]+)", text, re.IGNORECASE)

    invoices = []
    count = min(len(invoice_nos), len(names), len(dates), len(totals))
    for i in range(count):
        invoices.append({
            "Invoice No": invoice_nos[i],
            "Name": names[i],
            "Date": dates[i],
            "Grand Total": totals[i]
        })
    return invoices

# 🧾 Process uploaded file
if uploaded_file:
    st.success("📄 File uploaded successfully!")
    file_bytes = uploaded_file.read()
    text = extract_text_from_pdf_bytes(file_bytes)
    invoice_data = parse_multiple_invoices(text)

    if invoice_data:
        df = pd.DataFrame(invoice_data)
        st.dataframe(df)

        # 💾 Download CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download as CSV", csv, "invoice_data.csv", "text/csv")
    else:
        st.warning("❌ No invoices found in this file.")
else:
    st.info("Upload a PDF invoice to extract details.")
