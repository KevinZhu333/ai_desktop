import os
from typing import Optional

from objectbox import *
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

EMBEDDING_DIM = 1536
# EMBEDDING_DIM = 3072

@Entity()
class Documents:
    id = Id()
    content = String()
    vectorSpace = Float32Vector(index=HnswIndex(
        dimensions=EMBEDDING_DIM,
        distance_type=VectorDistanceType.COSINE,
        neighbors_per_node=64,
        indexing_search_count=128))

class Database:
    def __init__(
            self,
            directory: str = "../../db",
            openai_api_key: Optional[str] = None,
            openai_client: Optional[OpenAI] = None,
    ):
        if openai_client is not None:
            self.openai_client = openai_client
        else:
            if not openai_api_key:
                openai_api_key = os.getenv("OPENAI_API_KEY")
            self.openai_client = OpenAI(api_key=openai_api_key)

        self._store = Store(directory=directory)
        self._box = self._store.box(Documents)


    def add_objectbox(self, memory: str):
        vector = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=memory
        ).data[0].embedding

        self._box.put(Documents(
            content=memory,
            vectorSpace=vector,
        ))

        return

    def update_objectbox(self, ide: int, memory: str):
        vector = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=memory
        ).data[0].embedding

        self._box.put(Documents(
            id=ide,
            content=memory,
            vectorSpace=vector,
        ))

    # text-embedding-3-small: Best threshold range: 0.65 - 0.76
    # text-embedding-3-large: Best threshold range: 0.71 to 0.75
    def retrieve_objectbox(self, prompt: str, top_k: int = 3, threshold : float = 0.65):
        prompt_vec = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=prompt
        ).data[0].embedding

        retrieved_doc = self._box.query(
            Documents.vectorSpace.nearest_neighbor(prompt_vec, top_k)
        )

        neighbors = retrieved_doc.build().find_with_scores()

        return [
            {"id": d.id, "score": s, "content": d.content}
            for d, s in neighbors
            if s <= threshold
        ]

    def list_all(self):
        return self._box.get_all()

    def remove_objectbox(self, ide):
        self._box.remove(ide)

    def close(self):
        self._store.close()

if __name__ == "__main__":
    docDatabase = Database(directory='../../db')

    item = "Brainstorm ideas for team-building event"

    docDatabase.add_objectbox(item)

    print(docDatabase.retrieve_objectbox("Brainstorm"))

    docDatabase.close()