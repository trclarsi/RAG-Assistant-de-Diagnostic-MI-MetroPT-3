from rag_app.config import Settings


def test_settings_load_with_defaults():
    settings = Settings(_env_file=None)

    assert settings.vector_store_backend == "pgvector"
    assert settings.chunk_size == 800
    assert settings.top_k == 5
