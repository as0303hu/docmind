from openai import AsyncOpenAI, AsyncAzureOpenAI

from app.core.config import settings


def create_openai_client() -> AsyncAzureOpenAI | AsyncOpenAI:
    # use the configured provider flag
    if settings.llm_provider == "azure":
        if not settings.azure_openai_api_key or not settings.azure_openapi_endpoint:
            raise ValueError(
                "AZURE openapi key and endpoint required when LLM_PROVIDER=azure"
            )
        return AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            azure_endpoint=settings.azure_openapi_endpoint,
            api_version=settings.azure_openai_api_version,
        )

    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
    return AsyncOpenAI(api_key=settings.openai_api_key)

def embedding_model_name()->str:
    if settings.llm_provider=="azure":
        if not settings.azure_embedding_deployment:
            raise ValueError("AZURE_EMBEDDING_DEPLOYMENT is required when LLM_PROVEDR=azure")
        return settings.azure_embedding_deployment
    return settings.embedding_model