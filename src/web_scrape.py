import os
import json
import logging
import re
from pythonjsonlogger import jsonlogger
from dotenv import load_dotenv
from elsapy.elsclient import ElsClient
from elsapy.elsprofile import ElsAuthor, ElsAffil
from elsapy.elsdoc import FullDoc, AbsDoc
from elsapy.elssearch import ElsSearch

# from bs4 import BeautifulSoup

load_dotenv()  # take environment variables from .env.
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

API_KEY = os.getenv("ELSEVIER_API_KEY")
TIME_OUT = 10
FILE_STORE_SCOPUS_IDS = "scopus_ids.json"
BATCH_SIZE = 100
## Initialize client
client = ElsClient(API_KEY)


def read_affiliations(affil_id):
    """Find affiliations by ID

    Args:
        affil_id (_type_): affiliation with ID as string
    """
    my_aff = ElsAffil(affil_id=affil_id)
    if my_aff.read(client):
        print("my_aff.name: ", my_aff.name)
        my_aff.write()
    else:
        print("Read affiliation failed.")


def read_scopus_abstract(scp_id):
    """read scopus through scp_id

    Args:
        scp_id (string): scopus id
    """
    ## Scopus (Abstract) document example
    # Initialize document with ID as integer
    scp_doc = AbsDoc(scp_id=scp_id)
    if scp_doc.read(client):
        print("scp_doc.title: ", scp_doc.title)
        scp_doc.write()
    else:
        print("Read document failed.")


def read_science_direct_pii(sd_pii):
    ## ScienceDirect (full-text) document example using PII
    pii_doc = FullDoc(sd_pii=sd_pii)
    if pii_doc.read(client):
        print("pii_doc.title: ", pii_doc.title)
        pii_doc.write()
    else:
        print("Read document failed.")


def read_science_direct_doi(doi):
    ## ScienceDirect (full-text) document example using DOI
    doi_doc = FullDoc(doi=doi)
    if doi_doc.read(client):
        print("doi_doc.title: ", doi_doc.title)
        doi_doc.write()
    else:
        print("Read document failed.")


def find_scopus_id_in_serch_result(search_result):
    pattern = r"\d+"

    # Find all numbers in the input string
    numbers = re.findall(pattern, search_result)

    if numbers:
        extracted_number = numbers[0]
        return extracted_number


def write_scopus_list_to_file(scopus_ids):
    print(len(scopus_ids), "Data has been saved to:", FILE_STORE_SCOPUS_IDS)
    scopus_ids = json.dumps(scopus_ids)
    with open(FILE_STORE_SCOPUS_IDS, "w") as f:
        f.write(scopus_ids)


def read_scopus_list_from_file():
    with open(FILE_STORE_SCOPUS_IDS, "r") as f:
        scopus_ids = json.load(f)
    return scopus_ids


def search_scopus(get_all=False, count=25):
    """search scopus for author

    Args:
        auth_name (_type_): _description_
    """
    doc_srch = ElsSearch(
        "AFFILCOUNTRY ( thailand ) AND PUBYEAR > 2023 AND SUBJAREA ( engi )",
        "scopus",
    )
    doc_srch.execute(client, get_all=get_all, count=count)
    print("doc_srch has", len(doc_srch.results), "results.")
    scopus_ids = []
    for doc in doc_srch.results:
        scopus_id = find_scopus_id_in_serch_result(doc["dc:identifier"])
        scopus_ids.append(scopus_id)
    return scopus_ids


def select_batch(scopus_list, batch_number, batch_size=25):
    if batch_number < 1:
        raise ValueError("batch_number should be greater than 0")
    if batch_size < 1:
        raise ValueError("batch_size should be greater than 0")
    print(
        "returning batch number",
        batch_number,
        "from",
        len(scopus_list),
        "scopus ids.",
        "batch size:",
        batch_size,
    )
    return scopus_list[(batch_number - 1) * batch_size : batch_number * batch_size]


def main():
    # ? Search scopus that published in 2024 and in Thailand
    # scopus_ids = search_scopus(False, 2000)
    # write_scopus_list_to_file(scopus_ids)
    # ? Find affiliations by ID
    scopus_list = read_scopus_list_from_file()
    selected_scopus_list = select_batch(scopus_list, 1, BATCH_SIZE)
    # selected_scopus_list = select_batch(scopus_list, 1, 1616)
    for scopus_id in selected_scopus_list:
        read_scopus_abstract(scopus_id)


if __name__ == "__main__":
    main()
