#!/usr/bin/env python3
# This program does Boolean search on documents using an inverted index
# Boolean search means using AND, OR, and NOT to combine search terms

import re
from IndexBuilder import InvertedIndex


class BooleanRetrieval:
    # This class handles Boolean queries (like "word1 AND word2")
    # It uses the inverted index to find matching documents
    
    def __init__(self, inverted_index):
        # Save the index so we can use it for searching
        self.index = inverted_index
    
    def _merge_two_lists(self, list1, list2, keep_both, keep_left_only, keep_right_only):
        # This is a generic merge function that handles all three operations
        # We pass in three boolean flags to control what gets kept
        # keep_both: add to result when item is in both lists
        # keep_left_only: add to result when item is only in list1
        # keep_right_only: add to result when item is only in list2
        result = []
        i = 0  # pointer for list1
        j = 0  # pointer for list2
        
        # Go through both lists at the same time
        while i < len(list1) and j < len(list2):
            if list1[i] == list2[j]:
                # Item is in both lists
                if keep_both:
                    result.append(list1[i])
                i += 1
                j += 1
            elif list1[i] < list2[j]:
                # Item is only in list1
                if keep_left_only:
                    result.append(list1[i])
                i += 1
            else:
                # Item is only in list2
                if keep_right_only:
                    result.append(list2[j])
                j += 1
        
        # Add any remaining documents from list1
        if keep_left_only:
            while i < len(list1):
                result.append(list1[i])
                i += 1
        
        # Add any remaining documents from list2
        if keep_right_only:
            while j < len(list2):
                result.append(list2[j])
                j += 1
        
        return result
    
    def merge_and(self, list1, list2):
        # This function finds documents that appear in BOTH lists
        # Only keep items that are in both (intersection)
        return self._merge_two_lists(list1, list2, keep_both=True, keep_left_only=False, keep_right_only=False)
    
    def merge_or(self, list1, list2):
        # This function finds documents that appear in EITHER list (or both)
        # Keep everything (union)
        return self._merge_two_lists(list1, list2, keep_both=True, keep_left_only=True, keep_right_only=True)
    
    def merge_not(self, list1, list2):
        # This function finds documents in list1 but NOT in list2
        # Only keep items from list1 that aren't in list2 (difference)
        return self._merge_two_lists(list1, list2, keep_both=False, keep_left_only=True, keep_right_only=False)
    
    def get_all_docs(self):
        # Returns a list of all document IDs (sorted)
        all_docs = []
        for doc_id in range(1, self.index.num_documents + 1):
            all_docs.append(doc_id)
        return all_docs
    
    def parse_and_execute_query(self, query):
        # This function parses a Boolean query in POLISH NOTATION and returns matching documents
        # Polish notation means operators come AFTER their operands (also called postfix/RPN)
        # Example: "iran israel AND" means AND(iran, israel)
        
        # Clean up the query - make it lowercase and split into parts
        query = query.strip().lower()
        
        # Split the query into tokens (words and operators)
        tokens = re.findall(r'\b\w+\b', query)
        
        # Use a stack to process Polish notation
        # We push terms onto the stack, and when we see an operator, we pop the needed terms
        stack = []
        
        for token in tokens:
            if token == 'and':
                # AND needs 2 operands - pop them from stack
                if len(stack) >= 2:
                    right = stack.pop()
                    left = stack.pop()
                    result = self.merge_and(left, right)
                    stack.append(result)
                elif len(stack) == 1:
                    # Only one thing on stack, just keep it
                    pass
                    
            elif token == 'or':
                # OR needs 2 operands - pop them from stack
                if len(stack) >= 2:
                    right = stack.pop()
                    left = stack.pop()
                    result = self.merge_or(left, right)
                    stack.append(result)
                elif len(stack) == 1:
                    # Only one thing on stack, just keep it
                    pass
                    
            elif token == 'not':
                # NOT needs 2 operands in our case: NOT(A, B) means "A but not B"
                if len(stack) >= 2:
                    right = stack.pop()  # what to exclude
                    left = stack.pop()   # what to include
                    result = self.merge_not(left, right)
                    stack.append(result)
                elif len(stack) == 1:
                    # Only one thing on stack, just keep it
                    pass
                    
            else:
                # This is a search term - get its document list and push to stack
                term_docs = self.index.index.get(token, [])
                stack.append(term_docs)
        
        # The final result should be at the top of the stack
        if len(stack) > 0:
            return stack[0]
        else:
            return []
    
    def convert_to_docnos(self, doc_ids):
        # Convert internal document IDs to original DOCNOs
        docnos = []
        for doc_id in doc_ids:
            docno = self.index.doc_id_to_docno.get(doc_id)
            if docno:
                docnos.append(docno)
        return docnos
    
    def process_queries_from_file(self, query_file, output_file):
        # Read queries from a file and write results to output file
        # Each line in the query file is one query
        
        try:
            # Read all the queries
            with open(query_file, 'r') as f:
                queries = f.readlines()
            
            # Open output file for writing
            with open(output_file, 'w') as f:
                # Process each query
                for query in queries:
                    query = query.strip()
                    if not query:
                        continue  # skip empty lines
                    
                    # Execute the query to get matching document IDs
                    doc_ids = self.parse_and_execute_query(query)
                    
                    # Convert to original DOCNOs
                    docnos = self.convert_to_docnos(doc_ids)
                    
                    # Write results to file (space-separated)
                    f.write(' '.join(docnos) + '\n')
            
            print(f"Results written to {output_file}")
            
        except FileNotFoundError:
            print(f"Error: Could not find file {query_file}")
        except Exception as e:
            print(f"Error processing queries: {e}")


def main():
    # Main function to test the Boolean retrieval system
    print("Building Index...")
    index = InvertedIndex("AP_Coll_Parsed_9")
    print("Index built!")
    
    print("\nInitializing Boolean Retrieval System...")
    retrieval = BooleanRetrieval(index)
    
    # Process queries from file
    print("\nProcessing queries from BooleanQueries.txt (Polish notation)...")
    retrieval.process_queries_from_file("BooleanQueries.txt", "Part_2.txt")
    
    # Show a sample query in Polish notation
    print("\nSample query: 'iran israel AND' (Polish notation)")
    doc_ids = retrieval.parse_and_execute_query("iran israel AND")
    print(f"Found {len(doc_ids)} matching documents")
    
    # Show first few results
    docnos = retrieval.convert_to_docnos(doc_ids[:5])
    print(f"First 5 results: {' '.join(docnos)}")


if __name__ == "__main__":
    main()
