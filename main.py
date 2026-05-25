import pandas as pd
import os
from tqdm import tqdm
from invoice_extractor import extract_info_from_receipt
import shutil
from datetime import datetime


def extract_all_invoices(dataset_path):
    """
    extract_all_invoices() : prend en entrée un chemin vers un dossier d'images,
    boucle sur toutes les factures et retourne un dataframe pandas avec les infos extraites.
    Si le CSV existe et est complet, on le recharge directement sans rappeler l'API.
    Si le CSV existe mais est incomplet, on l'archive et on recommence.
    """

    if os.path.exists("./invoices_extraction.csv"):
        df_existing = pd.read_csv("./invoices_extraction.csv")

        if len(df_existing) == len(os.listdir(dataset_path)):
            print("CSV complet, chargement...")
            return df_existing
        else:
            print("CSV incomplet, on archive et on recommence...")
            if not os.path.exists("./archive"):
                os.makedirs("./archive")
            shutil.move(
                "./invoices_extraction.csv",
                os.path.join("./archive", f"invoices_extraction_{datetime.now().strftime('%Y-%m-%d')}.csv")
            )

    dates, vendors, amounts, currencies, invoice_names = [], [], [], [], []

    for invoice_name in tqdm(os.listdir(dataset_path), total=len(os.listdir(dataset_path))):
        try:
            invoice_path = os.path.join(dataset_path, invoice_name)
            result = extract_info_from_receipt(invoice_path)

            dates.append(result["date"])
            vendors.append(result["vendor"])
            amounts.append(result["amount"])
            currencies.append(result["currency"])
            invoice_names.append(invoice_name)

            # Sauvegarde après chaque image
            pd.DataFrame({
                "date": dates,
                "vendor": vendors,
                "amount": amounts,
                "currency": currencies,
                "invoice_name": invoice_names
            }).to_csv("./invoices_extraction.csv", index=False)

        except Exception as e:
            print(f"Erreur sur {invoice_name}: {e}")
            continue

    return pd.read_csv("./invoices_extraction.csv")


if __name__ == "__main__":
    dataset_path = "./dataset/receipts"
    df = extract_all_invoices(dataset_path)
    print(df)