from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from chartquery_api import share_call


class ChartQueryQrCodeTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        yield from share_call(
            self,
            tool_parameters,
            "/v1/qrcode",
            {"data": "data", "size": "size", "color": "color", "format": "format"},
            required=("data",),
            fixed={"format": "png"},
        )
