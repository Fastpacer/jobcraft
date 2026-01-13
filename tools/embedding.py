from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """
    Thin wrapper around sentence-transformers embedding models.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed(
        self,
        texts: Union[str, List[str]],
        normalize: bool = True,
    ) -> np.ndarray:
        """
        Generate embeddings for a string or list of strings.

        Args:
            texts: Text or list of texts to embed
            normalize: Whether to L2-normalize embeddings

        Returns:
            numpy.ndarray of shape (n, dim)
        """
        if isinstance(texts, str):
            texts = [texts]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=normalize,
        )

        return embeddings
