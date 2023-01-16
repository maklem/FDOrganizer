from typing import TypedDict


class PluginFolder(TypedDict, total = False):
    id: str
    displayname: str
    count: int