from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class VoIPAdapterResult:
    ok: bool
    provider: str
    message: str
    data: Dict[str, Any]


class VoIPProviderAdapter:
    provider_key = "generic"
    display_name = "Generic VOIP"

    def test(self, config: Dict[str, Any]) -> VoIPAdapterResult:
        raise NotImplementedError
