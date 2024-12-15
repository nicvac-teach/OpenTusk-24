import os
import re
import requests
import logging
from lxml import html
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


def crawler_download():
    global file_path_in_G
    global file_path_out_G

    # Read the CSV with '|#|' as a separator using regex
    df = pd.read_csv(file_path_in_G, sep='¥', engine='python')

    # Iterate over the rows of the DataFrame
    for index, row in df.iterrows():
        tema = row.iloc[0]
        current_pagedataset_url = row.iloc[1]
        current_dataset_name = row.iloc[2]
        current_note = row.iloc[3]
        title = row.iloc[4]
        format = row.iloc[5]
        file_url = row.iloc[6]
        downloded = row.iloc[7]

        error = ( title=="" or format=="" or file_url=="" )

        fmt = format.upper()

        if not error and not downloded:
            if ('CSV' in fmt or 'XLS' in fmt or 'JSON' == fmt or 'XML' == fmt ):
                logging.info(f"url: {file_url}")
                logging.info(f"Downloading...")
                try:
                    response = requests.get(file_url)

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

                except Exception as e:
                    logging.error(f"Error {file_url}: {e}")
            
            logging.info("--------------------------------------------------")

        # Check if the CSV file exists
        if not os.path.exists(file_path_out_G):
            # Create an empty DataFrame with headers
            df_empty = pd.DataFrame(columns=csv_headers)            
            # Write the empty DataFrame to CSV with headers
            df_empty.to_csv(file_path_out_G, sep='¥', index=False)
            logging.info(f"Initialized CSV file with headers at {file_path_out_G}")

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

        # Convert the entry to a DataFrame
        df_entry = pd.DataFrame([csv_entry], columns=csv_headers)

        # Append the entry to the CSV file
        try:
            df_entry.to_csv(file_path_out_G, sep='¥', mode='a', header=False, index=False)
        except Exception as e:
            logging.error(f"Failed to append entry to CSV: {e}")

        csv_entries.clear()




################################################################################
file_path_in_G  = 'record_dataset.csv'
file_path_out_G = 'record_dataset_report.csv'

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
