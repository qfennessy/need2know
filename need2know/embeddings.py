from __future__ import annotations

import hashlib
import re
from functools import lru_cache
from pathlib import Path

import numpy as np

DIMENSIONS = 256


class LocalEmbedder:
    """Use a local Model2Vec snapshot when present, otherwise offline feature hashing."""

    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self._model = None
        if self.model_path.exists():
            from model2vec import StaticModel

            self._model = StaticModel.from_pretrained(str(self.model_path))

    @property
    def name(self) -> str:
        return str(self.model_path) if self._model else "offline-hash-v1"

    @lru_cache(maxsize=512)
    def embed(self, text: str) -> np.ndarray:
        if self._model is not None:
            raw = np.asarray(self._model.encode([text])[0], dtype=np.float32)
            return _resize_normalize(raw)

        vector = np.zeros(DIMENSIONS, dtype=np.float32)
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        features = tokens + [f"{a}_{b}" for a, b in zip(tokens, tokens[1:])]
        for feature in features:
            digest = hashlib.blake2b(feature.encode(), digest_size=8).digest()
            slot = int.from_bytes(digest[:4], "little") % DIMENSIONS
            vector[slot] += 1 if digest[4] & 1 else -1
        return _resize_normalize(vector)


def _resize_normalize(vector: np.ndarray) -> np.ndarray:
    if len(vector) != DIMENSIONS:
        resized = np.zeros(DIMENSIONS, dtype=np.float32)
        for index, value in enumerate(vector):
            resized[index % DIMENSIONS] += value
        vector = resized
    norm = float(np.linalg.norm(vector))
    return vector / norm if norm else vector
