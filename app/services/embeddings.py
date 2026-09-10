from app.core.config import settings
from app.core.logging import get_logger
from app.core.openai_client import get_openai_client, with_retry

logger = get_logger(__name__)


class EmbeddingService:
    """Genertes vector embeddings for text via OpenAI, with batch support."""
    def __init__(self):
        self.model = settings.embedding_model

    @with_retry()
    async def genrate_embedding(self, text: str) -> list[float]:
        """Generate a single embedding vector for the given text."""
        client = get_openai_client()
        response = await client.embeddings.create(
            model=self.model, input=text,
        )
        return response.data[0].embedding
    
    @with_retry()
    async def _embed_batch(self,texts:list[str])-> list[list[float]]:
        """Embed a single batch with retry protection."""
        client = get_openai_client()
        response = await client.embeddings.create(
            model = self.model,
            input=texts
        )
        return [item.embedding for item in response.data]

    async def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        all_embeddings: list[list[float]] = []
        batch_size = 100

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            embeddings = await self._embed_batch(batch)
            all_embeddings.extend(embeddings)
            logger.info(
                "embeddings_generated",
                batch_number=i // batch_size + 1,
                batch_size=len(batch),
                total_processed=len(all_embeddings),
            )
        return all_embeddings
    
  
