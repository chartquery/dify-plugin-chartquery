import ast
import importlib
from pathlib import Path

import pytest
import requests
import yaml
from conftest import ROOT
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from provider.chartquery import ChartQueryProvider

KEY = "test-key-not-real"
BASE = "https://api.chartquery.com"
TOOLS = {
    "create_chart": "ChartQueryCreateChartTool",
    "chart_from_prompt": "ChartQueryChartFromPromptTool",
    "create_diagram": "ChartQueryCreateDiagramTool",
    "diagram_from_prompt": "ChartQueryDiagramFromPromptTool",
    "qr_code": "ChartQueryQrCodeTool",
    "barcode": "ChartQueryBarcodeTool",
}


def run(tool_cls, params):
    return list(tool_cls.from_credentials({"api_key": KEY}).invoke(params))


def texts(messages):
    return [m.message.text for m in messages if m.type.value == "text"]


def jsons(messages):
    return [m.message.json_object for m in messages if m.type.value == "json"]


def test_credentials_check_calls_the_free_endpoint(http):
    http.reply(200, {"credits": 100})
    ChartQueryProvider()._validate_credentials({"api_key": f" {KEY} "})
    call = http.calls[0]
    assert (call["method"], call["url"]) == ("GET", BASE + "/v1/usage")
    assert call["headers"]["x-api-key"] == KEY
    assert call["timeout"] == 30


def test_credentials_check_rejects_a_bad_key_without_showing_it(http):
    http.reply(401, {"error": f"Invalid API key {KEY}"})
    with pytest.raises(ToolProviderCredentialValidationError) as error:
        ChartQueryProvider()._validate_credentials({"api_key": KEY})
    assert "401" in str(error.value) and "not valid" in str(error.value)
    assert KEY not in str(error.value)


def test_credentials_check_needs_a_key(http):
    with pytest.raises(ToolProviderCredentialValidationError):
        ChartQueryProvider()._validate_credentials({"api_key": "  "})
    assert http.calls == []


def test_network_error_has_a_clear_message(http):
    http.raise_error(requests.ConnectionError(f"failed with {KEY}"))
    with pytest.raises(ToolProviderCredentialValidationError) as error:
        ChartQueryProvider()._validate_credentials({"api_key": KEY})
    assert "api.chartquery.com" in str(error.value) and KEY not in str(error.value)


def test_plugin_registers_provider_and_tools():
    from dify_plugin import DifyPluginEnv
    from dify_plugin.core.plugin_registration import PluginRegistration

    registration = PluginRegistration(DifyPluginEnv())
    assert registration.get_tool_provider_cls("chartquery").__name__ == "ChartQueryProvider"
    for tool, class_name in TOOLS.items():
        assert registration.get_tool_cls("chartquery", tool).__name__ == class_name


def test_each_tool_file_has_one_tool_class():
    for path in Path(ROOT, "tools").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        assert len([n for n in tree.body if isinstance(n, ast.ClassDef)]) == 1, path.name


def test_manifest_and_tool_files_agree():
    manifest = yaml.safe_load(Path(ROOT, "manifest.yaml").read_text(encoding="utf-8"))
    provider = yaml.safe_load(Path(ROOT, "provider/chartquery.yaml").read_text(encoding="utf-8"))
    assert manifest["version"] == manifest["meta"]["version"]
    assert manifest["author"] == provider["identity"]["author"] == "chartquery"
    assert manifest["network"]["domains"] == ["api.chartquery.com"]
    assert Path(ROOT, "_assets", manifest["icon"]).is_file()
    assert Path(ROOT, manifest["privacy"]).is_file()
    assert sorted(Path(f).stem for f in provider["tools"]) == sorted(TOOLS)
    for tool_file in provider["tools"]:
        tool = yaml.safe_load(Path(ROOT, tool_file).read_text(encoding="utf-8"))
        assert tool["identity"]["author"] == "chartquery"
        assert Path(ROOT, tool["extra"]["python"]["source"]).is_file()
        for param in tool["parameters"]:
            assert param["form"] in ("llm", "form")
            assert param["form"] == "form" or param.get("llm_description")


CASES = []


@pytest.mark.parametrize("tool, cls_name, sample, method, url, values", CASES)
def test_tool_request(http, tool, cls_name, sample, method, url, values):
    http.reply(200, {"ok": True, "items": [1, 2]})
    cls = getattr(importlib.import_module(f"tools.{tool}"), cls_name)
    messages = run(cls, sample)
    call = http.calls[0]
    assert (call["method"], call["url"]) == (method, BASE + url)
    sent = call["params"] if method in ("GET", "DELETE") else call["json"]
    assert sent == values
    assert call["headers"]["x-api-key"] == KEY
    assert '"ok": true' in texts(messages)[0]
    assert jsons(messages) == [{"ok": True, "items": [1, 2]}]


@pytest.mark.parametrize("tool, cls_name, sample, method, url, values", CASES)
def test_required_inputs_are_checked_before_any_request(http, tool, cls_name, sample, method, url, values):
    cls = getattr(importlib.import_module(f"tools.{tool}"), cls_name)
    tool_yaml = yaml.safe_load(Path(ROOT, f"tools/{tool}.yaml").read_text(encoding="utf-8"))
    if not any(p["required"] for p in tool_yaml["parameters"]):
        pytest.skip("no required input")
    messages = run(cls, {})
    assert "is required" in texts(messages)[0] and jsons(messages) == []
    assert http.calls == []


def test_errors_are_returned_as_text(http):
    if not CASES:
        pytest.skip("covered by the brand tests")
    tool, cls_name, sample = CASES[0][:3]
    cls = getattr(importlib.import_module(f"tools.{tool}"), cls_name)
    http.reply(402, {"error": "No credits"})
    assert texts(run(cls, sample)) == ["ChartQuery error 402: Not enough credits. (No credits)"]


def test_timeout(http):
    if not CASES:
        pytest.skip("covered by the brand tests")
    tool, cls_name, sample = CASES[0][:3]
    cls = getattr(importlib.import_module(f"tools.{tool}"), cls_name)
    http.raise_error(requests.Timeout("slow"))
    assert texts(run(cls, sample)) == ["ChartQuery did not answer in time. Try again."]


from tools.barcode import ChartQueryBarcodeTool  # noqa: E402
from tools.create_chart import ChartQueryCreateChartTool  # noqa: E402
from tools.create_diagram import ChartQueryCreateDiagramTool  # noqa: E402
from tools.diagram_from_prompt import ChartQueryDiagramFromPromptTool  # noqa: E402

LINKS = {
    "id": "cq-1",
    "render_url": "https://api.chartquery.com/v1/chart/render/cq-1",
    "view_url": "https://api.chartquery.com/v1/chart/view/cq-1",
    "expires_in": "3 days",
}


def test_chart_sends_compact_config_and_shows_the_image(http):
    http.reply(200, LINKS)
    messages = run(ChartQueryCreateChartTool, {"config": '{"type": "bar", "data": {"labels": ["a"]}}'})
    call = http.calls[0]
    assert (call["method"], call["url"]) == ("GET", BASE + "/v1/chart")
    assert call["params"] == {"share": "true", "query": '{"type":"bar","data":{"labels":["a"]}}'}
    assert (
        texts(messages)[0]
        == "Image: https://api.chartquery.com/v1/chart/render/cq-1\nPage: https://api.chartquery.com/v1/chart/view/cq-1\nThe links expire in 3 days."
    )
    assert [m.type.value for m in messages] == ["text", "image", "json"]
    assert messages[1].message.text == LINKS["render_url"]
    assert jsons(messages) == [LINKS]


@pytest.mark.parametrize("config", ["not json", "[1, 2]"])
def test_chart_rejects_a_bad_config_before_any_request(http, config):
    assert "chart config" in texts(run(ChartQueryCreateChartTool, {"config": config}))[0]
    assert http.calls == []


def test_diagram_defaults_and_choices(http):
    http.reply(200, LINKS)
    http.reply(200, LINKS)
    run(ChartQueryCreateDiagramTool, {"source": "graph TD; A-->B"})
    run(ChartQueryCreateDiagramTool, {"source": "a -> b", "language": "d2", "format": "svg"})
    assert http.calls[0]["params"] == {"share": "true", "type": "mermaid", "format": "png", "query": "graph TD; A-->B"}
    assert http.calls[1]["params"] == {"share": "true", "type": "d2", "format": "svg", "query": "a -> b"}


def test_diagram_from_prompt(http):
    http.reply(200, LINKS)
    run(ChartQueryDiagramFromPromptTool, {"prompt": "OAuth login", "language": "plantuml"})
    call = http.calls[0]
    assert call["url"] == BASE + "/v1/diagram/ai" and call["timeout"] == 120
    assert call["params"] == {
        "share": "true",
        "output_format": "png",
        "prompt": "OAuth login",
        "diagram_type": "plantuml",
    }


def test_barcode_and_missing_link(http):
    http.reply(200, {"id": "x"})
    messages = run(ChartQueryBarcodeTool, {"data": "4006381333931", "type": "ean13"})
    assert http.calls[0]["params"] == {"share": "true", "format": "png", "data": "4006381333931", "type": "ean13"}
    assert texts(messages) == ["ChartQuery sent no image link."]


def test_required_input_and_errors(http):
    assert "is required" in texts(run(ChartQueryBarcodeTool, {}))[0]
    http.reply(402, {"error": "No credits"})
    assert texts(run(ChartQueryBarcodeTool, {"data": "x"})) == [
        "ChartQuery error 402: Not enough credits. (No credits)"
    ]
