from typing import Any, Dict, Optional, TypedDict


class NinjaAPIConfig(TypedDict, total=False):  # total=False allows for optional keys
    title: Optional[str]
    version: Optional[str]
    description: Optional[str]
    openapi_url: Optional[str]
    docs_url: Optional[str]
    docs: Optional[Any]  # DocsBase type, but Any for simplicity if not deeply typed
    csrf: Optional[bool]
    auth: Optional[Any]  # AuthBase or list of AuthBase, Any for simplicity
    renderer: Optional[Any]  # BaseRenderer
    parser: Optional[Any]  # Parser
    urls_namespace: Optional[str]
    openapi_extra: Optional[Dict[str, Any]]
    throttle: Optional[Any]  # BaseThrottle or list of BaseThrottle
