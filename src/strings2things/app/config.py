from typing import List
from pydantic import PrivateAttr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GRAPHDB_USERNAME: str
    GRAPHDB_PASSWORD: str
    ONTOLOGY_SPARQL_ENDPOINT: str
    ONTOLOGY_GRAPH_IRIS: str  # raw string from .env

    _graph_iris: List[str] = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._graph_iris = [i.strip() for i in self.ONTOLOGY_GRAPH_IRIS.split(",")]

    def get_graph_iris(self) -> List[str]:
        return self._graph_iris

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
