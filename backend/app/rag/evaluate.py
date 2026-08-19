from retriever import search_knowledge_base

def run_evaluation():
    # The assessment requires 5 test queries covering different scenarios
    test_queries = [
        {"type": "Qualification", "question": "What is the minimum monthly revenue required?"},
        {"type": "Policy", "question": "How many years must my business be operating?"},
        {"type": "Process", "question": "What documents do I need to apply?"},
        {"type": "Objection", "question": "Can I get a loan if I have an existing default?"},
        {"type": "Unsupported", "question": "What is the exact interest rate for the loan?"}
    ]

    print("=========================================")
    print(" Q2 RETRIEVAL EVALUATION REPORT")
    print("=========================================\n")

    for i, test in enumerate(test_queries):
        print(f"Test {i+1}: {test['type']}")
        print(f"Question: {test['question']}")
        
        # Retrieve the top 1 most relevant chunk
        results = search_knowledge_base(test['question'], top_k=1)
        
        if results.get('documents') and len(results['documents'][0]) > 0:
            text = results['documents'][0][0]
            metadata = results['metadatas'][0][0]
            
            print(f"Retrieved Source: {metadata['source']} (Chunk {metadata['chunk_id']})")
            print(f"Retrieved Text: {text.strip()}")
            
            # For the unsupported question, we expect a low relevance or irrelevant text
            # In Q1, our AI will use this text to realize the answer isn't there
        else:
            print("Retrieved: No documents found.")
            
        print("-" * 40 + "\n")

if __name__ == "__main__":
    run_evaluation()