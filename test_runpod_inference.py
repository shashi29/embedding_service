# from openai import OpenAI
# import time
# from typing import List, Dict, Any, Union

# def get_embedding(
#     text: Union[str, List[str]], 
#     api_key: str = 'rpa_I680DE4Z5FRUQHC1WAFFW9B8BE0J6Q9WFYKMYBW2ahqf76',
#     endpoint_id: str = '6avmw3c97zmx3q',
#     model: str = 'mixedbread-ai/mxbai-embed-large-v1',
#     return_metadata: bool = False
# ) -> Union[List[float], Dict[str, Any]]:
#     """
#     Generate embeddings for a text or list of texts using RunPod's API with OpenAI SDK.
    
#     Args:
#         text: Single string or list of strings to generate embeddings for
#         api_key: RunPod API key
#         endpoint_id: RunPod endpoint ID
#         model: Name of the embedding model to use
#         return_metadata: If True, returns dictionary with embedding and metadata
#                          If False, returns just the embedding vector
    
#     Returns:
#         If return_metadata is False:
#             - For single text: List of floating point numbers (embedding vector)
#             - For multiple texts: List of embedding vectors
#         If return_metadata is True:
#             - Dictionary containing embedding(s) and metadata
#     """
#     # Initialize OpenAI client with RunPod configuration
#     client = OpenAI(
#         api_key=api_key,
#         base_url=f'https://api.runpod.ai/v2/{endpoint_id}/openai/v1'
#     )
    
#     start_time = time.time()
    
#     # Generate embeddings
#     response = client.embeddings.create(
#         model=model,
#         input=text
#     )
    
#     elapsed_time = time.time() - start_time
    
#     # For single text input
#     if isinstance(text, str):
#         embedding = response.data[0].embedding
        
#         if return_metadata:
#             return {
#                 "embedding": embedding,
#                 "dimensions": len(embedding),
#                 "model": model,
#                 "text_length": len(text),
#                 "time_taken": elapsed_time
#             }
#         else:
#             print(f"Generated embedding with {len(embedding)} dimensions")
#             print(embedding)
#             return embedding
    
#     # For multiple text inputs
#     else:
#         embeddings = [item.embedding for item in response.data]
        
#         if return_metadata:
#             return {
#                 "embeddings": embeddings,
#                 "count": len(embeddings),
#                 "dimensions": len(embeddings[0]) if embeddings else 0,
#                 "model": model,
#                 "average_time_per_text": elapsed_time / len(text) if text else 0,
#                 "total_time": elapsed_time
#             }
#         else:
#             return embeddings

# # Example usage
# if __name__ == "__main__":
#     # Single text example
#     text = "This is a sample text for embedding generation."
    
#     # Get embedding only
#     embedding = get_embedding(text)
#     print(f"Generated embedding with {len(embedding)} dimensions")
    
#     # Get embedding with metadata
#     result = get_embedding(text, return_metadata=True)
#     print(f"Embedding dimensions: {result['dimensions']}")
#     print(f"Generation time: {result['time_taken']:.4f} seconds")
    
#     # Multiple texts example
#     texts = [
#         "First example text",
#         "Second example with different content",
#         "Third example text for batch processing"
#     ]
    
#     # Get batch embeddings with metadata
#     batch_result = get_embedding(texts[0], return_metadata=False)

from openai import OpenAI
import time
import os
import concurrent.futures
from typing import List, Dict, Any, Union


def get_embedding(
    text: Union[str, List[str]],
    api_key: str = 'rpa_I680DE4Z5FRUQHC1WAFFW9B8BE0J6Q9WFYKMYBW2ahqf76',
    endpoint_id: str = '6avmw3c97zmx3q',
    model: str = 'mixedbread-ai/mxbai-embed-large-v1',
    return_metadata: bool = False
) -> Union[List[float], Dict[str, Any]]:
    """
    Generate embeddings for a text or list of texts using RunPod's API with OpenAI SDK.
    
    Args:
        text: Single string or list of strings to generate embeddings for
        api_key: RunPod API key
        endpoint_id: RunPod endpoint ID
        model: Name of the embedding model to use
        return_metadata: If True, returns dictionary with embedding and metadata
                      If False, returns just the embedding vector
    
    Returns:
        If return_metadata is False:
            - For single text: List of floating point numbers (embedding vector)
            - For multiple texts: List of embedding vectors
        If return_metadata is True:
            - Dictionary containing embedding(s) and metadata
    """
    # Initialize OpenAI client with RunPod configuration
    client = OpenAI(
        api_key=api_key,
        base_url=f'https://api.runpod.ai/v2/{endpoint_id}/openai/v1'
    )
    
    start_time = time.time()
    
    # Generate embeddings
    response = client.embeddings.create(
        model=model,
        input=text
    )
    
    elapsed_time = time.time() - start_time
    
    # For single text input
    if isinstance(text, str):
        embedding = response.data[0].embedding
        
        if return_metadata:
            return {
                "embedding": embedding,
                "dimensions": len(embedding),
                "model": model,
                "text_length": len(text),
                "time_taken": elapsed_time
            }
        else:
            return embedding
    
    # For multiple text inputs
    else:
        embeddings = [item.embedding for item in response.data]
        
        if return_metadata:
            return {
                "embeddings": embeddings,
                "count": len(embeddings),
                "dimensions": len(embeddings[0]) if embeddings else 0,
                "model": model,
                "average_time_per_text": elapsed_time / len(text) if text else 0,
                "total_time": elapsed_time
            }
        else:
            return embeddings


def process_file(file_path, return_metadata=True):
    """Process a single file and return its embedding."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
        
        file_name = os.path.basename(file_path)
        start_time = time.time()
        result = get_embedding(content, return_metadata=return_metadata)
        elapsed_time = time.time() - start_time
        
        return {
            "file_name": file_name,
            "result": result,
            "success": True,
            "processing_time": elapsed_time
        }
    except Exception as e:
        return {
            "file_name": os.path.basename(file_path),
            "success": False,
            "error": str(e)
        }


def batch_process_files(folder_path, max_workers=10, return_metadata=True):
    """
    Process all text files in the specified folder in parallel.
    
    Args:
        folder_path: Path to the folder containing text files
        max_workers: Maximum number of parallel workers
        return_metadata: Whether to return metadata with embeddings
        
    Returns:
        List of results for each file
    """
    # Get all text files in the folder
    files = [
        os.path.join(folder_path, f) 
        for f in os.listdir(folder_path) 
        if f.endswith('.txt') and os.path.isfile(os.path.join(folder_path, f))
    ]
    
    print(f"Found {len(files)} text files in {folder_path}")
    
    # Process files in parallel
    results = []
    successful = 0
    failed = 0
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(process_file, file_path, return_metadata): file_path 
            for file_path in files
        }
        
        # Process results as they complete
        for i, future in enumerate(concurrent.futures.as_completed(future_to_file)):
            file_path = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
                
                if result["success"]:
                    successful += 1
                    print(f"[{i+1}/{len(files)}] Successfully processed: {os.path.basename(file_path)}")
                else:
                    failed += 1
                    print(f"[{i+1}/{len(files)}] Failed to process: {os.path.basename(file_path)} - {result['error']}")
            
            except Exception as e:
                failed += 1
                print(f"[{i+1}/{len(files)}] Exception processing {os.path.basename(file_path)}: {str(e)}")
                results.append({
                    "file_name": os.path.basename(file_path),
                    "success": False,
                    "error": str(e)
                })
    
    total_time = time.time() - start_time
    
    # Print summary
    print(f"\nProcessing complete!")
    print(f"Total files: {len(files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per file: {total_time/len(files):.2f} seconds")
    
    return results


def save_results(results, output_file="embedding_results.txt"):
    """Save the results to a file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(f"File: {result['file_name']}\n")
            f.write(f"Success: {result['success']}\n")
            
            if result['success']:
                f.write(f"Processing time: {result['processing_time']:.4f} seconds\n")
                
                if isinstance(result['result'], dict) and 'embedding' in result['result']:
                    # Single text with metadata
                    embedding = result['result']['embedding']
                    f.write(f"Dimensions: {len(embedding)}\n")
                    f.write(f"Model: {result['result']['model']}\n")
                    f.write(f"Text length: {result['result']['text_length']}\n")
                    # Write first 5 dimensions as sample
                    f.write(f"Embedding (first 5 dimensions): {embedding[:5]}\n")
                else:
                    # Just the embedding vector
                    embedding = result['result']
                    f.write(f"Dimensions: {len(embedding)}\n")
                    f.write(f"Embedding (first 5 dimensions): {embedding[:5]}\n")
            else:
                f.write(f"Error: {result['error']}\n")
            
            f.write("\n" + "-"*50 + "\n\n")
    
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    # Configuration
    FOLDER_PATH = "/root/bulk-resume-process/ocr_results/batch_1/"  # Change this to your folder path
    MAX_PARALLEL_REQUESTS = 100  # Adjust based on API rate limits
    RETURN_METADATA = True
    OUTPUT_FILE = "embedding_results.txt"
    
    # Process all files
    results = batch_process_files(
        folder_path=FOLDER_PATH,
        max_workers=MAX_PARALLEL_REQUESTS,
        return_metadata=RETURN_METADATA
    )
    
    # Save results
    save_results(results, OUTPUT_FILE)