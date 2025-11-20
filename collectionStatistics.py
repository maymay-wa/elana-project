#!/usr/bin/env python3
# This program analyzes the collection statistics from the inverted index
# It finds top/bottom terms by document frequency and analyzes their characteristics

from indexBuilder import InvertedIndex


class CollectionStatistics:
    # This class analyzes statistics about the document collection
    
    def __init__(self, inverted_index):
        # Save the index so we can analyze it
        self.index = inverted_index
        # Pre-compute sorted term frequency list (used by multiple methods)
        self.term_freq_list = sorted(
            [(term, len(postings), postings) for term, postings in self.index.index.items()],
            key=lambda x: x[1]
        )
    
    def get_terms_by_doc_freq(self, n=10, highest=True):
        # Get top or bottom N terms by document frequency
        # highest=True returns top N, highest=False returns bottom N
        if highest:
            return [(term, freq) for term, freq, _ in self.term_freq_list[-n:][::-1]]
        else:
            return [(term, freq) for term, freq, _ in self.term_freq_list[:n]]
    
    def find_similar_freq_terms_same_docs(self):
        # Find two terms with similar document frequencies that appear in same documents
        # Focus on moderate frequency terms (50-200 docs) for meaningful results
        
        moderate_terms = [(t, f, p) for t, f, p in self.term_freq_list if 50 <= f <= 200]
        
        best_pair = None
        best_overlap = 0
        
        # Check pairs of nearby terms in frequency
        for i in range(len(moderate_terms)):
            term1, freq1, postings1 = moderate_terms[i]
            
            for j in range(i + 1, min(i + 50, len(moderate_terms))):
                term2, freq2, postings2 = moderate_terms[j]
                
                # Check if frequencies are similar (within 10%)
                if abs(freq1 - freq2) <= max(freq1, freq2) * 0.1:
                    shared_docs = set(postings1) & set(postings2)
                    overlap = len(shared_docs)
                    
                    # Want at least 30% overlap
                    if overlap >= min(freq1, freq2) * 0.3 and overlap > best_overlap:
                        best_overlap = overlap
                        best_pair = (term1, freq1, postings1, term2, freq2, postings2, shared_docs)
        
        return best_pair
    
    def generate_report(self, output_file):
        # Generate the full statistics report and write to file
        
        with open(output_file, 'w') as f:
            # Part 1: Top 10 terms by document frequency
            f.write("=" * 70 + "\n")
            f.write("PART 3: COLLECTION STATISTICS\n")
            f.write("=" * 70 + "\n\n")
            
            f.write("1. Top 10 Terms with Highest Document Frequency\n")
            f.write("-" * 70 + "\n")
            top_terms = self.get_terms_by_doc_freq(10, highest=True)
            for i, (term, doc_freq) in enumerate(top_terms, 1):
                percentage = (doc_freq / self.index.num_documents) * 100
                f.write(f"{i:2d}. '{term}' - appears in {doc_freq} documents ({percentage:.1f}%)\n")
            
            f.write("\n\n")
            
            # Part 2: Bottom 10 terms by document frequency
            f.write("2. Top 10 Terms with Lowest Document Frequency\n")
            f.write("-" * 70 + "\n")
            bottom_terms = self.get_terms_by_doc_freq(10, highest=False)
            for i, (term, doc_freq) in enumerate(bottom_terms, 1):
                f.write(f"{i:2d}. '{term}' - appears in {doc_freq} document(s)\n")
            
            f.write("\n\n")
            
            # Part 3: Explanation of characteristics
            f.write("3. Characteristics Comparison\n")
            f.write("-" * 70 + "\n")
            f.write("HIGH FREQUENCY TERMS (Top 10):\n")
            f.write("- These are mostly common English words (stop words) like 'the', 'a', 'of'\n")
            f.write("- They appear in almost every document (80-99% of documents)\n")
            f.write("- They don't carry much meaning for search because they're so common\n")
            f.write("- These words are usually removed in real search engines (stop word removal)\n")
            f.write("- Examples: articles (the, a), prepositions (of, in, to), pronouns (he, it)\n")
            f.write("\n")
            f.write("LOW FREQUENCY TERMS (Bottom 10):\n")
            f.write("- These are very specific or rare words\n")
            f.write("- They appear in only 1 document each\n")
            f.write("- Could be: proper names, technical terms, typos, or very specialized words\n")
            f.write("- These are very discriminative - if you search for them, you find specific docs\n")
            f.write("- Good for precise searches but not useful for general queries\n")
            f.write("\n\n")
            
            # Part 4: Similar frequency terms in same documents
            f.write("4. Terms with Similar Frequencies Appearing in Same Documents\n")
            f.write("-" * 70 + "\n")
            
            result = self.find_similar_freq_terms_same_docs()
            if result:
                term1, freq1, postings1, term2, freq2, postings2, shared_docs = result
                
                f.write(f"TERM 1: '{term1}'\n")
                f.write(f"  Document Frequency: {freq1} documents\n")
                f.write(f"\n")
                f.write(f"TERM 2: '{term2}'\n")
                f.write(f"  Document Frequency: {freq2} documents\n")
                f.write(f"\n")
                f.write(f"SHARED DOCUMENTS: {len(shared_docs)} documents (both terms appear together)\n")
                f.write(f"  Overlap percentage: {(len(shared_docs)/min(freq1, freq2)*100):.1f}%\n")
                f.write(f"\n")
                
                # Show first 10 shared documents
                f.write(f"First 10 shared document IDs:\n")
                shared_list = sorted(list(shared_docs))[:10]
                for doc_id in shared_list:
                    docno = self.index.doc_id_to_docno.get(doc_id)
                    f.write(f"  - {docno} (ID: {doc_id})\n")
                
                f.write(f"\n")
                f.write("HOW THESE TERMS WERE FOUND:\n")
                f.write("- Searched through terms with moderate frequency (50-200 documents)\n")
                f.write("- This range excludes very common words and very rare words\n")
                f.write("- Compared pairs of terms with similar document frequencies (within 10%)\n")
                f.write("- Selected the pair with highest document overlap (at least 30%)\n")
                f.write("- These terms likely appear in similar contexts or related topics\n")
                
            else:
                f.write("No suitable term pair found.\n")
            
            f.write("\n")
            f.write("=" * 70 + "\n")
        
        print(f"Statistics report written to {output_file}")


def main():
    # Main function to generate collection statistics
    print("Building Index...")
    index = InvertedIndex("AP_Coll_Parsed_9")
    print("Index built!")
    
    print("\nGenerating Collection Statistics...")
    stats = CollectionStatistics(index)
    stats.generate_report("Part_3.txt")
    
    print("\nDone! Check Part_3.txt for results.")


if __name__ == "__main__":
    main()
