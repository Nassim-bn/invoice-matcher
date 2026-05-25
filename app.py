import streamlit as st
import pandas as pd
from invoice_extractor import extract_info_from_receipt
from matching import preprocess_data, run_matching
import tempfile
import os

st.title(":material/receipt_long: Invoice Matcher")
st.write("Faites correspondre automatiquement vos factures à votre relevé bancaire")

# 1. Upload des factures JPG
st.header(":material/upload_file: Factures")
uploaded_invoices = st.file_uploader(
    "Glissez-déposez vos factures JPG",
    type=["jpg", "jpeg"],
    accept_multiple_files=True
)

# 2. Upload du relevé bancaire
st.header(":material/account_balance: Relevé bancaire")
uploaded_bank = st.file_uploader(
    "Glissez-déposez votre relevé bancaire CSV",
    type=["csv"]
)

# 3. Bouton pour lancer le matching
if uploaded_invoices and uploaded_bank:
    if st.button(":material/play_arrow: Lancer le matching"):

        progress = st.progress(0)
        st.write("Extraction des factures en cours...")

        dates, vendors, amounts, currencies, invoice_names = [], [], [], [], []

        for i, invoice_file in enumerate(uploaded_invoices):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(invoice_file.read())
                tmp_path = tmp.name

            result = extract_info_from_receipt(tmp_path)
            dates.append(result["date"])
            vendors.append(result["vendor"])
            amounts.append(result["amount"])
            currencies.append(result["currency"])
            invoice_names.append(invoice_file.name)

            os.remove(tmp_path)
            progress.progress((i + 1) / len(uploaded_invoices))

        df_invoices = pd.DataFrame({
            "date": dates,
            "vendor": vendors,
            "amount": amounts,
            "currency": currencies,
            "invoice_name": invoice_names
        })

        df_bank = pd.read_csv(uploaded_bank)

        df_invoices, df_bank = preprocess_data(df_invoices, df_bank)
        df_results = run_matching(df_invoices, df_bank)

        df_results = df_results.sort_values("match_score", ascending=False)

        st.header(":material/table_chart: Résultats du matching")
        st.dataframe(df_results)