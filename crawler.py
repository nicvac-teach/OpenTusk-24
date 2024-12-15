import os
import re
import requests
import logging
from lxml import html
import pandas as pd


def record_dataset( dataset_url ):
    global tema_G
    global current_dataset_name_G
    global current_note_G
    global current_pagedataset_url_G
    global file_path_G
    global csv_entries_G

    xpath_title =    '//*[@id="content"]//h2[@class="page-heading"]/text()'
    xpath_file_url = '//*[@id="content"]//div[@class="btn-group"]//a/@href'
    xpath_format =   '//td[contains(translate(../th/text(),"abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),"FORMAT")]/text()'

    try:
        response = requests.get(dataset_url)
    except Exception as e:
        logging.error(f"Error {dataset_url}: {e}")
        return
    
    tree = html.fromstring(response.content)

    title_list = tree.xpath( xpath_title )
    file_url_list = tree.xpath( xpath_file_url )
    format_list = tree.xpath( xpath_format ) 

    logging.info(f"---{title_list}")
    logging.info(f"---{file_url_list}")
    logging.info(f"---{format_list}")

    #Upper format
    format_list = [fmt.upper() for fmt in format_list]
    
    error = False
    title = ""
    file_url = ""
    format = ""
    try:
        title = title_list[0]
        file_url = file_url_list[0]
        format = format_list[0]
    except Exception as e:
        error = True
        logging.error(f"Error: {e}")

    if not error:
        csv_entry = [
            tema_G,
            current_pagedataset_url_G,
            current_dataset_name_G,
            current_note_G,
            title,
            format.lower(),
            file_url,
            False
        ]
        
        # Append the entry to the csv_entries list
        csv_entries_G.append(csv_entry)




current_dataset_name_G = ""
current_note_G = ""
current_pagedataset_url_G = ""

def inspect_page_dataset( pagedataset_url ):
    global current_note_G
    global current_dataset_name_G
    global current_pagedataset_url_G

    current_pagedataset_url_G = pagedataset_url

    dataset_urls = []

    logging.info(f">>> {pagedataset_url}")
    
    try:
        response = requests.get(pagedataset_url)
    except Exception as e:
        logging.error(f"Error {pagedataset_url}: {e}")
        return dataset_urls

    tree = html.fromstring(response.content)

    xpath_dataset_name = '//*[@id="content"]//article/div[@class="module-content"]/h1/text()'
    xpath_notes = '//*[@id="content"]//article/div[@class="module-content"]/div[1]'
    xpath_datasets_urls='//*[@id="dataset-resources"]//li[@class="resource-item"]/a/@href'
    
    dataset_name = tree.xpath( xpath_dataset_name )
    notes = tree.xpath( xpath_notes )
    elements = tree.xpath( xpath_datasets_urls )

    current_note_G = ""
    try:
        current_note_G = notes[0].text_content()
        current_note_G = re.sub(r'^[^A-Za-z0-9]+|[^A-Za-z0-9]+$', '', current_note_G)
    except Exception as e:
        logging.error(f"Error: {e}")

    current_dataset_name_G = ""
    try:
        current_dataset_name_G = dataset_name[0]
        current_dataset_name_G = re.sub(r'^[^A-Za-z0-9]+|[^A-Za-z0-9]+$', '', current_dataset_name_G)
    except Exception as e:
        logging.error(f"Error: {e}")

    dataset_urls.extend(elements)

    return dataset_urls


def inspect_tema_page( url ):
    
    try:
        response = requests.get(url)
    except Exception as e:
        logging.error(f"Error {url}: {e}")
        return []

    tree = html.fromstring(response.content)

    #xpath='//*[@id="content"]//div/ul/li[class="dataset-item"]'
    xpath='//*[@id="content"]//div/ul/li[@class="dataset-item"]//h2[@class="card-title"]/a/@href'

    elements = tree.xpath( xpath )
    return elements


def inspect_tema( tema_url ):
    pagedataset_urls = []
    for p in range(1, 101):
        url = f"{tema_url}?page={p}"
        logging.info(f"########## {url}")

        elements = inspect_tema_page( url )
        if len(elements) == 0:
            break
        else:
            pagedataset_urls.extend(elements)
    return pagedataset_urls

################################################################################
main_url_G = "https://dati.puglia.it"
file_path_G = 'record_dataset.csv'
tema_G = ""

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log'),
        logging.StreamHandler()
    ]
)


# Initialize list to store CSV entries
csv_entries_G = []

# Define the CSV headers
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

def crawl():
    global main_url_G
    global file_path_G
    global tema_G

    logging.info("crawling")

    temi=["economia-e-finanze", "governo-e-settore-pubblico", "popolazione-e-societa", 
    "istruzione-cultura-e-sport", "ambiente", "trasporti", "regioni-e-citta", "salute",
    "scienza-e-tecnologia", "giustizia"]

    if os.path.exists(file_path_G):
        os.remove(file_path_G)

    for tema in temi:
        tema_G = tema
        url = f"{main_url_G}/ckan/group/{tema}"
        pagedataset_urls = inspect_tema( url )

        for pagedataset_url in pagedataset_urls:
            #print(element.text_content())
            pagedataset_url_abs = f"{main_url_G}{pagedataset_url}"
            dataset_urls = inspect_page_dataset( pagedataset_url_abs )

            for dataset_url in dataset_urls:
                udataset_url_abs = f"{main_url_G}{dataset_url}"
                record_dataset( udataset_url_abs )

                # Check if the CSV file exists
                if not os.path.exists(file_path_G):
                    # Create an empty DataFrame with headers
                    df_empty = pd.DataFrame(columns=csv_headers)
                    
                    # Write the empty DataFrame to CSV with headers
                    df_empty.to_csv(file_path_G, index=False)
                    
                    logging.info(f"Initialized CSV file with headers at {file_path_G}")

                # Convert the entry to a DataFrame
                df_entry = pd.DataFrame(csv_entries_G, columns=csv_headers)

                # Append the entry to the CSV file
                try:
                    df_entry.to_csv(file_path_G, sep='¥', mode='a', header=False, index=False)
                except Exception as e:
                    logging.error(f"Failed to append entry to CSV: {e}")

                csv_entries_G.clear()


if __name__ == "__main__":
    crawl()
