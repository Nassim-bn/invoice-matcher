import pandas as pd
import os
from rapidfuzz import fuzz



def load_data(invoices_path, bank_statement_path):
    """
    load_data() : prend en entrée le chemin vers le CSV des factures extraites et 
    le chemin vers le dossier des relevés bancaires. Combine les 6 CSV bancaires 
    en un seul dataframe et retourne les deux dataframes (invoices, bank_statement).
    """
    df_invoices = pd.read_csv(invoices_path)

    #  Lire tous les CSV du dossier et les combiner (6 fichier csv)
    bank_statements = []
    for filename in os.listdir(bank_statement_path):
        if filename.endswith(".csv"):
            df = pd.read_csv(os.path.join(bank_statement_path, filename))
            bank_statements.append(df)
    
    df_bank_statement = pd.concat(bank_statements, ignore_index=True)

    return df_invoices, df_bank_statement


def normalize_date(date):
    """
    normalize_date() : prend en entrée une date en string et retourne la date normalisée 
    au format YYYY-MM-DD
    """
    try:
        return pd.to_datetime(date).strftime("%Y-%m-%d")
    except:
        return None


def preprocess_data(df_invoices, df_bank):
    """
    preprocess_data() : prend en entrée les deux dataframes (invoices et bank statement),
    normalise les dates au format YYYY-MM-DD, met les vendors en minuscules 
    et retourne les deux dataframes normalisés.
    """
    df_invoices["date"] = df_invoices["date"].apply(normalize_date)
    df_bank["date"] = df_bank["date"].apply(normalize_date)
    df_invoices["vendor"] = df_invoices["vendor"].str.lower().str.strip()
    df_bank["vendor"] = df_bank["vendor"].str.lower().str.strip()
    
    return df_invoices, df_bank



def match_invoice(bank_row, df_invoices):
    """
    match_invoice() : prend en entrée une ligne du relevé bancaire et le dataframe des factures extraites,
    calcule un score de similarité pour chaque facture (montant + date + vendor) 
    et retourne la meilleure facture correspondante ainsi que son score.
    """
    best_score = 0
    best_match = None

    for _, invoice_row in df_invoices.iterrows():
        score = 0

        # 1 Montant exact
        if bank_row["amount"] == invoice_row["amount"]:
            score += 1

        # 2 Date
        if bank_row["date"] and invoice_row["date"]:
            if bank_row["date"] == invoice_row["date"]:
                score += 1

        # 3 fuzzy matching avec  vendor
        if bank_row["vendor"] and invoice_row["vendor"]:
            vendor_score = fuzz.ratio(bank_row["vendor"], invoice_row["vendor"])
            score += vendor_score / 100  # normalise entre 0 et 1


        if score > best_score:
            best_score = score
            best_match = invoice_row

    return best_match, best_score



def run_matching(df_invoices, df_bank):
    """
    run_matching() : prend en entrée les deux dataframes (invoices et bank statement),
    boucle sur chaque ligne du relevé bancaire, appelle match_invoice() pour trouver 
    la meilleure facture correspondante et retourne un dataframe avec les résultats du matching.
    """
    results = []

    for _, bank_row in df_bank.iterrows():
        best_match, best_score = match_invoice(bank_row, df_invoices)
        results.append({
            "date": bank_row["date"],
            "amount": bank_row["amount"],
            "vendor_bank": bank_row["vendor"],
            "vendor_invoice": best_match["vendor"] if best_match is not None else None,
            "invoice_name": best_match["invoice_name"] if best_match is not None else None,
            "source": bank_row["source"],
            "match_score": best_score
        })

    return pd.DataFrame(results)



if __name__ == "__main__":
    df_invoices, df_bank = load_data(
        "./invoices_extraction.csv",
        "./dataset/bank_statements"
    )
    
    df_invoices, df_bank = preprocess_data(df_invoices, df_bank)
    
    df_results = run_matching(df_invoices, df_bank)
    
    df_results.to_csv("./matching_results.csv", index=False)
    print(df_results)