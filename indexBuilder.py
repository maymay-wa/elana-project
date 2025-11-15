#!/usr/bin/env python3
import re
import os

def main():
    folder_path = "AP_Coll_Parsed_9"
    docMap = {}
    docMapReverse = {}
    counter = 1
    allContent = ""
    # Loops through all files in the AP folder
    for filename in os.listdir(folder_path):
        file_path = folder_path + "/" + filename
        with open(file_path, "r") as file:
            content = file.read()
        # create one long string of the file contents
        allContent += content

    # Give each document a unique integer ID
    docnos = re.findall(r"<DOCNO>(.*?)</DOCNO>", allContent)
    for docno in docnos:
        docMap[counter] = docno.strip()
        docMapReverse[docno.strip()] = counter
        counter += 1

    # Find all documents
    docs = re.findall(r"<DOC>(.*?)</DOC>", allContent, re.DOTALL)

    docTextMap = {}
    for doc in docs:
        # Extract DOCNO
        docno_match = re.search(r"<DOCNO>(.*?)</DOCNO>", doc)
        docno = docno_match.group(1).strip() if docno_match else None
        # Extract TEXT
        text_match = re.search(r"<TEXT>(.*?)</TEXT>", doc, re.DOTALL)
        text = text_match.group(1).strip() if text_match else None
        if docno and text:
            docTextMap[docno] = text

    print(docTextMap['AP880212-0001'])

if __name__ == "__main__":
    main()