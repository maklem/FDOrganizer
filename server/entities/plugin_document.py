from typing import Optional, TypedDict


class PluginDocument(TypedDict, total = False):
    id: str
    displayname: str
    size: int
    type: str
    url: Optional[str]