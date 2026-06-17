"""
Shared pytest fixtures for the Minerva test suite.

Provides:
  - db       : fresh in-memory Database per test (function scope)
  - embedder : EmbeddingModel shared across the entire session (avoids ONNX reload overhead)
  - engine   : RetrievalEngine wired to the per-test db and session embedder
"""
import pytest
from minerva.db import Database
from minerva.embeddings import EmbeddingModel
from minerva.retrieval import RetrievalEngine


@pytest.fixture(scope="function")
def db():
    """Fresh in-memory SQLite Database for each test. Automatically closed after the test."""
    database = Database(":memory:")
    yield database
    database.close()


@pytest.fixture(scope="session")
def embedder():
    """
    EmbeddingModel loaded once per test session.
    Session scope prevents reloading the ONNX model for every test,
    which would add ~200ms of overhead per test.
    """
    return EmbeddingModel()


@pytest.fixture(scope="function")
def engine(db, embedder):
    """RetrievalEngine wired to the per-test database and session-scoped embedder."""
    return RetrievalEngine(db, embedder)
