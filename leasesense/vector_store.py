from __future__ import annotations

from pathlib import Path
from typing import Callable

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams

from leasesense.models import RetrievedEvidence, TextChunk


class LeaseVectorStore:
    def __init__(self, path: Path, collection_name: str) -> None:
        path.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.collection_name = collection_name

    def _with_client(self, operation: Callable[[QdrantClient], object]) -> object:
        client = QdrantClient(path=str(self.path))
        try:
            return operation(client)
        finally:
            client.close()

    def ensure_collection(self, client: QdrantClient, vector_size: int) -> None:
        collections = client.get_collections().collections
        exists = any(collection.name == self.collection_name for collection in collections)
        if exists:
            return
        client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    def upsert_chunks(self, lease_id: str, chunks: list[TextChunk], embeddings: list[list[float]]) -> None:
        if not chunks:
            raise ValueError("No text chunks were produced from the lease.")

        def operation(client: QdrantClient) -> None:
            self.ensure_collection(client, len(embeddings[0]))
            points = [
                PointStruct(
                    id=chunk.id,
                    vector=embedding,
                    payload={
                        "lease_id": lease_id,
                        "chunk_id": chunk.id,
                        "chunk_index": chunk.index,
                        "text": chunk.text,
                        "section": chunk.section,
                        "clause_type": chunk.clause_type,
                        "risk_tags": list(chunk.risk_tags),
                    },
                )
                for chunk, embedding in zip(chunks, embeddings)
            ]
            client.upsert(collection_name=self.collection_name, points=points)

        self._with_client(operation)

    def search(
        self,
        lease_id: str,
        query_vector: list[float],
        top_k: int,
        section: str | None = None,
    ) -> list[RetrievedEvidence]:

        def operation(client: QdrantClient) -> list[RetrievedEvidence]:
            conditions = [FieldCondition(key="lease_id", match=MatchValue(value=lease_id))]
            if section:
                conditions.append(FieldCondition(key="section", match=MatchValue(value=section)))
            lease_filter = Filter(
                must=conditions
            )
            if hasattr(client, "search"):
                results = client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    query_filter=lease_filter,
                    limit=top_k,
                    with_payload=True,
                )
            else:
                response = client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    query_filter=lease_filter,
                    limit=top_k,
                    with_payload=True,
                )
                results = response.points
            evidence: list[RetrievedEvidence] = []
            for result in results:
                payload = result.payload or {}
                evidence.append(
                    RetrievedEvidence(
                        text=str(payload.get("text", "")),
                        score=float(result.score),
                        chunk_id=str(payload.get("chunk_id", result.id)),
                        section=str(payload.get("section", "General")),
                        clause_type=str(payload.get("clause_type", "general")),
                        risk_tags=tuple(payload.get("risk_tags", []) or ()),
                    )
                )
            return evidence

        return self._with_client(operation)
