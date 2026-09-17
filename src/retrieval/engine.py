
import json
from collections import defaultdict
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


class RetrievalEngine:
    """
    Semantic retrieval engine for the RAG-powered talent search system.

    The engine loads persisted FAISS vectors, chunk metadata,
    candidate profiles, and embedding configuration.
    """

    def __init__(self, artifact_dir):
        self.artifact_dir = Path(artifact_dir)

        self._load_config()
        self._load_index()
        self._load_chunks()
        self._load_candidate_profiles()
        self._load_embedding_model()

    def _load_config(self):
        config_path = self.artifact_dir / "config.json"

        with open(
            config_path,
            "r",
            encoding="utf-8"
        ) as file:
            self.config = json.load(file)

    def _load_index(self):
        index_path = self.artifact_dir / "resume_faiss.index"

        self.index = faiss.read_index(
            str(index_path)
        )

    def _load_chunks(self):
        chunks_path = self.artifact_dir / "chunks.json"

        with open(
            chunks_path,
            "r",
            encoding="utf-8"
        ) as file:
            self.chunks = json.load(file)

        if len(self.chunks) != self.index.ntotal:
            raise ValueError(
                "Chunk count does not match FAISS index size."
            )

    def _load_candidate_profiles(self):
        profiles_path = (
            self.artifact_dir /
            "candidate_profiles.json"
        )

        with open(
            profiles_path,
            "r",
            encoding="utf-8"
        ) as file:
            self.candidate_profiles = json.load(file)

    def _load_embedding_model(self):
        model_name = self.config["embedding"]["model_name"]

        self.embedding_model = SentenceTransformer(
            model_name
        )

    def semantic_search(
        self,
        query,
        top_k=30
    ):
        """
        Retrieve the most semantically similar resume chunks.
        """

        query_embedding = self.embedding_model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype("float32")

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):
            if index == -1:
                continue

            result = self.chunks[index].copy()
            result["similarity_score"] = float(score)

            results.append(result)

        return results

    def retrieve_candidates(
        self,
        query,
        top_k_chunks=30,
        top_k_candidates=5
    ):
        """
        Retrieve and group relevant chunks by candidate.
        """

        chunk_results = self.semantic_search(
            query=query,
            top_k=top_k_chunks
        )

        candidate_groups = defaultdict(list)

        for result in chunk_results:
            candidate_id = result["candidate_id"]

            candidate_groups[
                candidate_id
            ].append(result)

        candidate_results = []

        for candidate_id, candidate_chunks in (
            candidate_groups.items()
        ):
            best_score = max(
                chunk["similarity_score"]
                for chunk in candidate_chunks
            )

            sorted_chunks = sorted(
                candidate_chunks,
                key=lambda item: item["similarity_score"],
                reverse=True
            )

            candidate_results.append({
                "candidate_id": candidate_id,
                "similarity_score": best_score,
                "matched_chunks": sorted_chunks
            })

        candidate_results.sort(
            key=lambda item: item["similarity_score"],
            reverse=True
        )

        return candidate_results[
            :top_k_candidates
        ]

    def get_candidate_profile(
        self,
        candidate_id
    ):
        """
        Return the persisted profile for a candidate.
        """

        profile = self.candidate_profiles.get(
            str(candidate_id)
        )

        if profile is None:
            raise ValueError(
                f"Candidate ID {candidate_id} was not found."
            )

        return profile
