from typing import List, Tuple

import torch
from transformers import AutoTokenizer, AutoModelForMaskedLM
import logging
import psutil

doc_tokenizer = AutoTokenizer.from_pretrained(
    "naver/efficient-splade-VI-BT-large-doc"
)
doc_model = AutoModelForMaskedLM.from_pretrained(
    "naver/efficient-splade-VI-BT-large-doc"
)

query_tokenizer = AutoTokenizer.from_pretrained(
    "naver/efficient-splade-VI-BT-large-query"
)
query_model = AutoModelForMaskedLM.from_pretrained(
    "naver/efficient-splade-VI-BT-large-query"
)

device = "cuda" if torch.cuda.is_available() else "cpu"


def get_available_memory():
    """Get the available memory in the system."""
    ram = psutil.virtual_memory()
    logging.info(f"Available RAM: {ram.available / 1024**3:.2f} GB")
    logging.info(f"Total RAM: {ram.total / 1024**3:.2f} GB")
    logging.info(f"Used RAM: {ram.used / 1024**3:.2f} GB")
    logging.info(f"Percentage of RAM used: {ram.percent}%")


def sparse_doc_vectors(
        texts: List[str],
) -> Tuple[List[List[int]], List[List[float]]]:
    """
    Generates sparse vector representations of input documents.

    This function processes a list of text documents to create sparse vector
    representations, which capture the most important words and their relevance
    scores. The process involves:

    1. Tokenization: Converting text to numerical tokens.
    2. Model processing: Passing tokens through a pre-trained language model.
    3. Relevance scoring: Applying ReLU and log transformations to model outputs.
    4. Attention weighting: Focusing on relevant parts of the text.
    5. Max pooling: Selecting the highest relevance score for each word.
    6. Sparsification: Retaining only non-zero values and their indices.

    The resulting sparse vectors are efficient for storage and quick for
    similarity comparisons in information retrieval tasks.

    Args:
        texts (List[str]): A list of input documents to be processed.

    Returns:
        Tuple[List[List[int]], List[List[float]]]: A tuple containing:
            - A list of lists of integer indices representing important words.
            - A list of lists of float values representing importance scores.

    Note:
        This function uses the 'naver/efficient-splade-VI-BT-large-doc' model,
        which is specifically designed for creating document representations
        in sparse retrieval systems.
    """

    logging.info(f"processing text: \n {texts} \n length of the list is {len(texts)}\n")

    tokens = doc_tokenizer(
        texts, truncation=True, padding=True, return_tensors="pt"
    )
    logging.info(f"device selected for document embedding {device}")
    tokens = tokens.to(device)


    output = doc_model(**tokens)
    logits, attention_mask = output.logits, tokens.attention_mask
    relu_log = torch.log(1 + torch.relu(logits))
    weighted_log = relu_log * attention_mask.unsqueeze(-1)
    tvecs, _ = torch.max(weighted_log, dim=1)

    # extract the vectors that are non-zero and their indices
    indices = []
    vecs = []
    for batch in tvecs:
        indices.append(batch.nonzero(as_tuple=True)[0].tolist())
        vecs.append(batch[indices[-1]].tolist())

    get_available_memory()
    logging.info(f" End of the function sparse_doc_vectors \n")
    return indices, vecs


def sparse_query_vectors(
        texts: List[str],
) -> Tuple[List[List[int]], List[List[float]]]:
    """
    Generates sparse vector representations of input queries.

    This function processes a list of text queries to create sparse vector
    representations, optimized for matching with document vectors. The process involves:

    1. Tokenization: Converting query text to numerical tokens.
    2. Model processing: Passing tokens through a query-specific pre-trained model.
    3. Relevance scoring: Applying ReLU and log transformations to model outputs.
    4. Attention weighting: Focusing on relevant parts of the query.
    5. Max pooling: Selecting the highest relevance score for each term.
    6. Sparsification: Retaining only non-zero values and their indices.

    The resulting sparse vectors are designed to capture the essence of the query
    in a format that allows for efficient matching with document vectors.

    Args:
        texts (List[str]): A list of input queries to be processed.

    Returns:
        Tuple[List[List[int]], List[List[float]]]: A tuple containing:
            - A list of lists of integer indices representing important query terms.
            - A list of lists of float values representing importance scores.

    Note:
        This function uses the 'naver/efficient-splade-VI-BT-large-query' model,
        which is specifically designed for creating query representations
        in sparse retrieval systems. The query-specific model helps in
        emphasizing terms that are particularly relevant for search operations.

    Important:
        While similar to sparse_doc_vectors, this function is optimized for
        queries rather than documents, which can lead to better search performance.
    """
    # TODO: compute sparse vectors in batches if max length is exceeded
    tokens = query_tokenizer(
        texts, truncation=True, padding=True, return_tensors="pt"
    )

    print(f"device selected for question embedding {device}")
    tokens = tokens.to(device)

    output = query_model(**tokens)
    logits, attention_mask = output.logits, tokens.attention_mask
    relu_log = torch.log(1 + torch.relu(logits))
    weighted_log = relu_log * attention_mask.unsqueeze(-1)
    tvecs, _ = torch.max(weighted_log, dim=1)

    # extract the vectors that are non-zero and their indices
    indices = []
    vecs = []
    for batch in tvecs:
        indices.append(batch.nonzero(as_tuple=True)[0].tolist())
        vecs.append(batch[indices[-1]].tolist())

    return indices, vecs
