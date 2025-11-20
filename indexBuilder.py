#!/usr/bin/env python3
# This program builds an inverted index for searching documents
# An inverted index is like the index at the back of a textbook - it tells you which documents have which words

import re
import sys
from collections import defaultdict
from pathlib import Path


class InvertedIndex:
    # This class creates an index so we can search documents faster
    # It stores words and which documents they appear in
    
    def __init__(self, text_path):
        # Initialize all the variables we need
        self.index = {}  # stores words and their document lists
        self.doc_id_to_docno = {}  # converts numbers to document names
        self.docno_to_doc_id = {}  # converts document names to numbers
        self.num_documents = 0  # keeps track of how many documents we have
        
        # Build the index when we create the object
        self._build_index(text_path)
    
    def _load_documents(self, folder_path):
        # This function reads all the files from a folder (and its subfolders)
        # and combines them into one big string, efficiently.
        folder = Path(folder_path)

        texts = []      # collect each file's text here
        file_count = 0  # just for info

        # If you changed this earlier, keep using rglob to go through ALL subfolders:
        for file_path in sorted(folder.rglob("*")):
            if file_path.is_file():
                file_count += 1
                try:
                    text = file_path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    text = file_path.read_text(encoding="latin-1")
                texts.append(text)

        print(f"Loaded {file_count} files from {folder}")

        # Join once at the end – MUCH faster than += in a loop
        return "".join(texts)

    
    def _parse_documents(self, all_content):
        # This function pulls out the important parts from each document
        # We give each document a simple number ID (1, 2, 3, etc.) to make things easier
        doc_text_map = {}
        
        # Find all the documents (they're between <DOC> tags)
        docs = re.findall(r"<DOC>(.*?)</DOC>", all_content, re.DOTALL)
        
        # Loop through each document and give it a number starting at 1
        doc_num = 1
        for doc in docs:
            # Get the document name (DOCNO)
            docno_match = re.search(r"<DOCNO>(.*?)</DOCNO>", doc)
            if not docno_match:
                continue  # skip if we can't find a document name
            docno = docno_match.group(1).strip()
            
            # Save the mapping between the number and the name (both ways)
            self.doc_id_to_docno[doc_num] = docno
            self.docno_to_doc_id[docno] = doc_num
            
            # Get the actual text content
            text_match = re.search(r"<TEXT>(.*?)</TEXT>", doc, re.DOTALL)
            if text_match:
                doc_text_map[doc_num] = text_match.group(1).strip()
            
            doc_num += 1
        
        # Remember how many documents we found
        self.num_documents = len(self.doc_id_to_docno)
        return doc_text_map
    
    def _build_index(self, text_path):
        # This is the main function that builds the index
        # It reads all the files and creates a dictionary of words -> document lists
        
        # Read all the files
        all_content = self._load_documents(text_path)
        
        # Break them into documents and get the text
        doc_text_map = self._parse_documents(all_content)
        
        # Build the index (word -> list of documents)
        temp_index = defaultdict(list)
        
        # Go through each document
        for doc_id, text in doc_text_map.items():
            # Break the text into words (lowercase letters and numbers only)
            words = re.findall(r'\b[a-z0-9]+\b', text.lower())
            
            # Get unique words (we only need each word once per document)
            unique_words = set(words)
            
            # Add this document number to each word's list
            for word in unique_words:
                temp_index[word].append(doc_id)
        
        # Sort the document lists for each word and save it
        self.index = {}
        for word, doc_list in temp_index.items():
            self.index[word] = sorted(doc_list)
    
    def print_term_info(self, term):
        # This function prints out which documents contain a specific word
        postings = self.index.get(term.lower(), [])
        
        # Check if we found the word
        if not postings:
            print(f"'{term}' -> (not found)")
            return
        
        # Print the word and all the documents it appears in
        # Format: 'word' -> 1 (AP880212) -> 2 (AP880213) -> ...
        result = ""
        for doc_id in postings:
            docno = self.doc_id_to_docno.get(doc_id)
            result += f" -> {doc_id} ({docno})"
        print(f"'{term}'{result}")


def main():
    # This is the main function that runs when you start the program
    print("Building Inverted Index for AP Collection...")
    print("=" * 60)
    
    # If user gives a folder path when running the script, use that
    if len(sys.argv) > 1:
        data_path = Path(sys.argv[1])

    # Otherwise, assume data-20251119 is in the SAME folder as indexBuilder.py
    else:
        data_path = Path(__file__).resolve().parent / "data-20251119"

    if not data_path.exists():
        print(f"Error: data folder '{data_path}' not found.")
        return

    index = InvertedIndex(data_path)


    # Show some example words and their document lists
    print(f"\n{'=' * 60}")
    print("Sample Inverted Index Entries:")
    print("=" * 60)
    
    sample_terms = ['the', 'sanctions', 'african']
    for term in sample_terms:
        doc_list = index.index.get(term.lower(), [])
        if doc_list:
            # Only show first 3 documents to keep it short
            num_to_show = 3
            if len(doc_list) < num_to_show:
                num_to_show = len(doc_list)
            
            result = f"'{term}'"
            for i in range(num_to_show):
                doc_id = doc_list[i]
                docno = index.doc_id_to_docno.get(doc_id)
                result += f" -> {doc_id} ({docno})"
            
            # Add a note if there are more documents
            if len(doc_list) > num_to_show:
                result += f" -> ... ({len(doc_list)} total docs)"
            print(result)
        else:
            print(f"'{term}' -> (not found)")
    
    return index


if __name__ == "__main__":
    main()