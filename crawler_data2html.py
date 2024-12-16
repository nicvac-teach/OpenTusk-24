#Prende i record_dataser_report.cvs e crea dei documenti html con gli schemi csv
# utile da dare in pasto a ChatGpt/Claude/NotebookLM per trovare relazioni 
# e suggerire applicazioni


import glob
import os
from pathlib import Path
import logging
import re
import pandas as pd

csv_entries = []

csv_headers = [
    'Tema',
    'Pagedataset URL',
    'Dataset Name',
    'Note',
    'Title',
    'Format',
    'File URL',
    'Downloaded'
]


def crawler_data2html():
    # Read the CSV with '¥' as a separator
    df = pd.read_csv(file_path_in_G, sep='¥', engine='python')

    #if exists, ignore
    os.makedirs(f"html", exist_ok=True)

     # Iterate over the rows of the DataFrame
    tema_prev = "___"
    dataset_name_prev = "___"

    page=""
    for index, row in df.iterrows():
        tema = row.iloc[0]
        pagedataset_url = row.iloc[1]
        dataset_name = row.iloc[2]
        note = row.iloc[3]
        title = row.iloc[4]
        format = row.iloc[5]
        file_url = row.iloc[6]
        downloded = row.iloc[7]

        error = ( title=="" or format=="" or file_url=="" )

        if not error and downloded:
            #New theme ==> new html file
            if tema_prev != tema:
                if page != "":
                    with open(f'html/{tema_prev}.html', 'w') as file:
                        file.write(page)
                        file.close()
                page = f"<h1>{tema}</h1>"
                logging.info(f"Processing: {tema}")
                iTema = 0

                #Load theme downloaded files
                files_downl = []
                root_dir = f"downl/{tema}"
                for dirpath, dirnames, filenames in os.walk(root_dir):
                    files_downl = [ os.path.join(dirpath, filename) for filename in filenames]
                numFiles = len(files_downl)

            tema_prev = tema
            iTema += 1
            if iTema % 100 == 0:
                logging.info(f"{iTema}/{numFiles}")

            #New dataset ==> New title
            if dataset_name_prev != dataset_name:
                page += f"<h2>Nome Dataset</h2>"
                page += f"<p>{dataset_name}</p>"
                page += f"<h2>Descrizione Dataset</h2>"
                page += f"<p>{note}</p>"
                #Get all downloaded files (different format) for each file in dataset
                files = {}

            #Find downloaded file for this item (title)
            #filename = f"downl/{tema}/{title}_{i:03}.{format.lower()}"

            #Find downloaded files related to title.
            # Select only one, preferring csv format
            files[title] = ""
            pattern = f".*{title}(_[[:digit:]]{3})?\.(csv|xls.?)$"
            regex = re.compile(pattern, re.IGNORECASE)
            
            for filename in files_downl:
                if regex.match(filename):
                    if filename.lower().endswith(".csv"):
                        files[title] = filename  #csv fisrt
                    elif files[title] == "":
                        files[title] = filename  #then xls

            #Here I have a file (csv or xls) related to title
            page += f"<h3>Nome Tabella</h3>"
            page += f"<p>{title}</p>"
            page += f"<h4>Tabella</h4>"
            if files[title] == "":
                page += f"<p>dati mancanti</p>"
                continue

            try:
                #Insert a couple of rows of the csv file
                if files[title].lower().endswith(".csv"):
                    df = pd.read_csv(files[title], sep='¥', engine='python')
                else:
                    df = pd.read_excel(files[title])
            except Exception as e:
                df = None
                logging.error(f"Failed to read CSV {files[title]}: {e}")

            # Get header and first two rows as HTML table
            if df is not None:
                num_rows, num_columns = df.shape
                if num_rows > 0 and num_columns > 0:
                    html_table = df.head( min(2,num_rows) ).to_html(index=False)
                    page += html_table
                else:
                    page += f"<p>dati mancanti</p>"

################################################################################
file_path_in_G = 'record_dataset_report.csv'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler_data2html.log'),
        logging.StreamHandler()
    ]
)


if __name__ == "__main__":
    crawler_data2html()
