from typing import Generic, Optional, Type, TypeVar

import aiofiles
import yaml

from cachetools import Cache, TTLCache
from pydantic import BaseModel

_YamlRepoSchema = TypeVar("_YamlRepoSchema", bound=BaseModel)


class YamlRepo(Generic[_YamlRepoSchema]):
    _path: str
    _schema: Type[_YamlRepoSchema]

    def __init__(
        self, path: str, schema: Type[_YamlRepoSchema], cache: Optional[Cache] = None
    ):
        self._path = path
        self._schema = schema
        self._cache = cache or TTLCache(ttl=500, maxsize=1)

    async def get(self, update_cache: bool = False) -> _YamlRepoSchema:
        if not update_cache and "data" in self._cache:
            return self._cache["data"]
        try:
            async with aiofiles.open(self._path, "r", encoding="utf-8") as f:
                data = self._schema.model_validate(yaml.safe_load(await f.read()))
                self._cache["data"] = data
                return data
        except FileNotFoundError:
            await self.save(self._schema())
            return await self.get(update_cache=True)

    async def save(self, data: _YamlRepoSchema) -> None:
        async with aiofiles.open(self._path, "w", encoding="utf-8") as f:
            data = yaml.dump(data.model_dump(mode="json"), indent=2, allow_unicode=True)
            await f.write(data)
