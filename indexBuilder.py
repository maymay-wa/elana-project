#!/usr/bin/env python3
import re

def main():
    #open the file for parsing
    #loop over the whole 
    with open("AP_Coll_Parsed_9/AP880212", "r") as file:
        content = file.read()
    
    # finds every use of <DOCNO> and </DOCNO> and extracts the text in between
    docnos = re.findall(r"<DOCNO>(.*?)</DOCNO>", content)
    
    counter = 1
    docMap = {}
    for docno in docnos:
        docMap[counter] = docno.strip()
        counter += 1
    print(docMap)

if __name__ == "__main__":
    main()
