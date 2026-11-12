from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from chartquery_api import chart_config, share_call


class ChartQueryCreateChartTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        yield from share_call(
            self, tool_parameters, "/v1/chart", {"config": "query"}, required=("config",), prepare=chart_config
        )
