import os
import requests
from lxml import html

def download_dataset( dataset_url ):

    xpath_title =    '//*[@id="content"]//h2[@class="page-heading"]/text()'
    xpath_file_url = '//*[@id="content"]//div[@class="btn-group"]//a/@href'
    xpath_format =   '//td[contains(translate(../th/text(),"abcdefghijklmnopqrstuvwxyz", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),"FORMAT")]/text()'

    response = requests.get(dataset_url)
    tree = html.fromstring(response.content)

    title_list = tree.xpath( xpath_title )
    file_url_list = tree.xpath( xpath_file_url )
    format_list = tree.xpath( xpath_format ) 

    print("---", title_list)
    print("---", file_url_list)
    print("---", format_list)

    #Upper format
    format_list = [fmt.upper() for fmt in format_list]
    
    error = False
    try:
        title = title_list[0]
        file_url = file_url_list[0]
        format = format_list[0]
    except Exception as e:
        error = True
        print(f"Error: {e}")

    if not error:
        if any( ('CSV' in fmt or 'XLS' in fmt or 'JSON' == fmt or 'XML' == fmt )\
                for fmt in format_list ):
            
            print("Downloading...")
            try:
                response = requests.get(file_url)
            except Exception as e:
                print(f"Error: {e}")
                return

            filename = f"downl/{title}.{format.lower()}"

            #if filename exists, create a new name
            i = 1
            while os.path.exists(filename):
                filename = f"downl/{title}_{i:03}.{format.lower()}"
                i += 1

            with open( filename, 'wb') as f:
                f.write(response.content)
        else:
            print("Skipping...")
        print("--------------------------------------------------")



def inspect_page_dataset( pagedataset_url ):

    dataset_urls = []

    print(">>>", pagedataset_url)
    
    response = requests.get(pagedataset_url)
    tree = html.fromstring(response.content)

    xpath='//*[@id="dataset-resources"]//li[@class="resource-item"]/a/@href'
    elements = tree.xpath( xpath )

    dataset_urls.extend(elements)

    return dataset_urls


def inspect_tema_page( url ):
    response = requests.get(url)
    tree = html.fromstring(response.content)

    #xpath='//*[@id="content"]//div/ul/li[class="dataset-item"]'
    xpath='//*[@id="content"]//div/ul/li[@class="dataset-item"]//h2[@class="card-title"]/a/@href'

    elements = tree.xpath( xpath )
    return elements


def inspect_tema( tema_url ):
    pagedataset_urls = []
    for p in range(1, 101):
        url = f"{tema_url}?page={p}"
        print("##########",url)

        elements = inspect_tema_page( url )
        if len(elements) == 0:
            break
        else:
            pagedataset_urls.extend(elements)
    return pagedataset_urls

################################################################################
main_url = "https://dati.puglia.it"

tema_G = "ambiente"

def crawl():
    global tema_G
    print("crawling")

    temi=["ambiente"]
    for tema in temi:
        tema_G = tema
        url = f"{main_url}/ckan/group/{tema}"
        pagedataset_urls = inspect_tema( url )

    for pagedataset_url in pagedataset_urls:
        #print(element.text_content())
        pagedataset_url_abs = f"{main_url}{pagedataset_url}"
        dataset_urls = inspect_page_dataset( pagedataset_url_abs )

        for dataset_url in dataset_urls:
            udataset_url_abs = f"{main_url}{dataset_url}"
            download_dataset( udataset_url_abs )


if __name__ == "__main__":
    crawl()
