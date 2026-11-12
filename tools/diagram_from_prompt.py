from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from chartquery_api import share_call


class ChartQueryDiagramFromPromptTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        yield from share_call(
            self,
            tool_parameters,
            "/v1/diagram/ai",
            {"prompt": "prompt", "language": "diagram_type"},
            required=("prompt",),
            fixed={"output_format": "png"},
            timeout=120,
        )
