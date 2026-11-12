from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from chartquery_api import share_call


class ChartQueryBarcodeTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        yield from share_call(
            self,
            tool_parameters,
            "/v1/barcode",
            {"data": "data", "type": "type", "format": "format"},
            required=("data",),
            fixed={"format": "png"},
        )
