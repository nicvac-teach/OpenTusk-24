import os
import re
import requests
import logging
from lxml import html
import pandas as pd

csv_entries = []

def crawler_download( dataset_url ):
    global file_path_G

    # Read the CSV with '|#|' as a separator using regex
    df = pd.read_csv(file_path_G, sep=r'\|#\|', engine='python')

    # Iterate over the rows of the DataFrame
    for index, row in df.iterrows():
        tema = row[0]
        current_pagedataset_url = row[1]
        current_dataset_name = row[2]
        current_note = row[3]
        title = row[4]
        format = row[5]
        file_url = row[6]
        downloded = row[7]

        error = ( title=="" or format=="" or file_url=="" )

        fmt = format.upper()

        if not error and not downloded:
            if ('CSV' in fmt or 'XLS' in fmt or 'JSON' == fmt or 'XML' == fmt ):
                logging.info(f"url: {file_url}")
                logging.info(f"Downloading...")
                try:
                    response = requests.get(file_url)
                except Exception as e:
                    logging.error(f"Error {file_url}: {e}")
                    return
                
                #if exists, ignore
                os.makedirs(f"downl/{tema}", exist_ok=True)

                filename = f"downl/{tema}/{title}.{format.lower()}"

                #if filename exists, create a new name
                i = 1
                while os.path.exists(filename):
                    filename = f"downl/{tema}/{title}_{i:03}.{format.lower()}"
                    i += 1

                with open( filename, 'wb') as f:
                    f.write(response.content)
                
                downloded = True
            
            logging.info("--------------------------------------------------")

        csv_entry = [
            tema,
            current_pagedataset_url,
            current_dataset_name,
            current_note,
            title,
            format,
            file_url,
            downloded
        ]

        # Append the entry to the csv_entries list
        csv_entries.append(csv_entry)

    # After crawling, create a DataFrame and write to CSV
    df = pd.DataFrame(csv_entries, columns=[
        'Tema',
        'Pagedataset URL',
        'Dataset Name',
        'Note',
        'Title',
        'Format',
        'File URL',
        'Downloaded'
    ])

    # Write to CSV with '|#|' as separator
    df.to_csv(file_path_G+"_report.csv", sep='|#|', index=False)



################################################################################
file_path_G = 'record_dataset.csv'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler_download.log'),
        logging.StreamHandler()
    ]
)



if __name__ == "__main__":
    crawler_download()
