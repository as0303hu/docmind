from app.core.logging import get_logger
from app.core.openai import create_openai_client, embedding_model_name
from app.core.config import settings

logger = get_logger(__name__)

client = create_openai_client()

class EmbeddingService:
    def __init__(self):
        self.model = embedding_model_name()
        self.dimension = settings.embedding_dimension
        
    async def genrate_embedding(self,text:str)-> list[float]:
        response = await client.embeddings.create(
            model=self.model,
            input=text,
            dimensions=self.dimension
        )
        return response.data[0].embedding
    async def generate_embeddings_batch(
        self,texts:list[str]
    )->list[list[float]]:
        all_embeddings = []
        batch_size=100
        
        for i in range(0,len(texts),batch_size):
            batch = texts[i:i+batch_size]
            response = await client.embeddings.create(
                model=self.model,
                input=batch,
                dimensions=self.dimension
            )
            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
            logger.info(
                "embeddings_generated",
                batch_number=i //batch_size+1,
                batch_size = len(batch),
                total_processed =len(all_embeddings)
            )
        return all_embeddings
            