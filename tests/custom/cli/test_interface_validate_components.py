from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import threading
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from typer.testing import CliRunner

from label_studio_sdk._extensions.interface import cli as interface_cli
from label_studio_sdk._extensions.interface.preview import (
    PROTOCOL_VERSION,
    PreviewAssetCache,
    resolve_scenario_editor_bundle,
    serve_scenario_editor_bundle,
)

runner = CliRunner()


def _find_monorepo_path(relative: str) -> Path | None:
    """Locate a monorepo path when running inside hs-platform; return None in sparse/SDK-only CI."""
    start = Path(__file__).resolve()
    for parent in [start, *start.parents]:
        candidate = parent / relative
        if candidate.exists():
            return candidate
    return None


def _require_node_and_npm() -> None:
    if shutil.which("node") is None or shutil.which("npm") is None:
        pytest.skip("node and npm are required for interface validator tests")


def _loads_cli_json(result: Any) -> dict[str, Any]:
    """Parse JSON from CLI stdout, tolerating one-time validator bootstrap banners on mixed stderr."""
    raw = getattr(result, "stdout", None) or result.output
    stripped = raw.lstrip()
    if not stripped.startswith("{"):
        brace = raw.find("{")
        if brace != -1:
            raw = raw[brace:]
    return json.loads(raw)


MULTI_COMPONENT_SCREEN_JSX = """const DEFAULT_LABELS = [
  { id: "car", name: "Car", color: "#ef4444", hotkey: "1" },
  { id: "person", name: "Person", color: "#3b82f6", hotkey: "2" },
];

const ANSWER_FIELDS = [
  {
    name: "scene_type",
    type: "choices",
    label: "Scene Type",
    required: true,
    options: ["Indoor", "Outdoor"],
  },
  {
    name: "notes",
    type: "textarea",
    label: "Notes",
  },
];

const ANSWER_FIELD_TYPES = { scene_type: "choices", notes: "textarea" };
const ANSWER_ID_PREFIX = "__answer__:";

const {
  ImageCanvas,
  LabelPicker,
  AnswerForm,
  toImageResults,
  fromImageResults,
  answersToResults,
  resultsToAnswers,
  collectAnswerErrors,
  normalizeLabels,
} = window.InterfaceComponents;

function answerValuesFromRegions(regions) {
  const values = {};
  for (const r of regions || []) {
    if (r && r.type === "answer" && r.field) {
      values[r.field] = r.value;
    }
  }
  return values;
}

function Screen({
  task,
  regions = [],
  selectedRegionIds = [],
  params = {},
  readOnly = false,
  addRegion,
  updateRegion,
  deleteRegion,
  selectRegion,
  onValidationChange,
}) {
  const imageSrc = getField(task?.data || {}, params?.imageField || "image") || "";
  const labels = React.useMemo(
    () => normalizeLabels(params?.labels?.length ? params.labels : DEFAULT_LABELS),
    [params?.labels],
  );
  const [activeLabel, setActiveLabel] = React.useState(labels[0]?.id ?? null);

  const canvasRegions = React.useMemo(
    () => (regions || []).filter((r) => r && r.type !== "answer"),
    [regions],
  );
  const answerValues = React.useMemo(() => answerValuesFromRegions(regions), [regions]);

  React.useEffect(() => {
    if (typeof onValidationChange !== "function") return;
    const errs = collectAnswerErrors(ANSWER_FIELDS, answerValues);
    const messages = Object.values(errs || {}).filter(Boolean);
    onValidationChange({ valid: messages.length === 0, errors: messages });
  }, [answerValues, onValidationChange]);

  const handleAnswersChange = (nextValues) => {
    if (readOnly) return;
    for (const field of ANSWER_FIELDS) {
      const id = ANSWER_ID_PREFIX + field.name;
      const existing = (regions || []).find((r) => r.id === id);
      const val = nextValues ? nextValues[field.name] : undefined;
      const isEmpty = val === undefined || val === null || val === "" || (Array.isArray(val) && val.length === 0);
      if (isEmpty) {
        if (existing) deleteRegion(id);
      } else if (existing) {
        updateRegion(id, { value: val });
      } else {
        addRegion({ id, type: "answer", field: field.name, value: val });
      }
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12, padding: 12 }}>
      <LabelPicker
        labels={labels}
        value={activeLabel}
        onChange={setActiveLabel}
        disabled={readOnly}
      />
      <ImageCanvas
        src={imageSrc}
        labels={labels}
        activeLabel={activeLabel}
        regions={canvasRegions}
        selectedRegionIds={selectedRegionIds}
        readOnly={readOnly}
        onAddRegion={(region) => addRegion(region)}
        onUpdateRegion={(id, patch) => updateRegion(id, patch)}
        onDeleteRegion={(id) => deleteRegion(id)}
        onSelectRegion={(id, opts) => selectRegion(id, opts)}
      />
      <AnswerForm
        fields={ANSWER_FIELDS}
        values={answerValues}
        onChange={handleAnswersChange}
        readOnly={readOnly}
      />
    </div>
  );
}

function getResults(regions = []) {
  const canvasRegions = (regions || []).filter((r) => r && r.type !== "answer");
  const answerValues = answerValuesFromRegions(regions);
  return [
    ...toImageResults(canvasRegions, { fromName: "objects", toName: "image" }),
    ...answersToResults(answerValues, ANSWER_FIELDS, { toName: "image" }),
  ];
}

function parseResults(results = []) {
  const imageRegions = fromImageResults(results, { fromName: "objects" });
  const answers = resultsToAnswers(results, ANSWER_FIELD_TYPES);
  const answerRegions = Object.entries(answers || {}).map(([field, value]) => ({
    id: ANSWER_ID_PREFIX + field,
    type: "answer",
    field,
    value,
  }));
  return { regions: [...imageRegions, ...answerRegions], relations: [] };
}

({
  default: Screen,
  specVersion: 1,
  getResults,
  parseResults,
  inputSchema: {
    type: "object",
    properties: {
      image: { type: "dataField", dataType: "image", default: "image" },
    },
  },
  paramsSchema: {
    type: "object",
    properties: {
      imageField: { type: "string", default: "image" },
    },
  },
  outputSchema: {
    type: "object",
    properties: {
      objects: {
        type: "array",
        items: { type: "string", enum: ["car", "person"] },
      },
      scene_type: {
        type: "string",
        enum: ["Indoor", "Outdoor"],
      },
      notes: {
        type: "string",
      },
    },
  },
});
"""


MULTI_COMPONENT_SCENARIOS_JS = """const TINY_PNG =
  "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==";

export default [
  {
    name: "annotates bounding box and fills answer form with InterfaceComponents",
    task: {
      data: {
        image: TINY_PNG,
      },
    },
    steps: {
      pickPerson: () => "select the Person label in LabelPicker",
      drawBox: () => "create a bounding box region in ImageCanvas",
      chooseScene: () => "pick Outdoor in AnswerForm",
      typeNotes: () => "enter scene notes in AnswerForm",
    },
    async run({ page, step }) {
      step.pickPerson();
      await page.getByRole("button", { name: /Person/ }).click();

      step.drawBox();
      await page.getByTestId("mock-image-canvas-draw").click();

      step.chooseScene();
      await page.getByRole("button", { name: "Outdoor" }).click();

      step.typeNotes();
      await page.getByLabel("Notes").fill("Clear sunny frame");
    },
    expect: {
      regionCount: 3,
      results: [
        {
          from_name: "objects",
          to_name: "image",
          type: "rectanglelabels",
          value: {
            x: 12,
            y: 18,
            width: 40,
            height: 30,
            rotation: 0,
            rectanglelabels: ["person"],
          },
        },
        {
          from_name: "scene_type",
          to_name: "image",
          type: "choices",
          value: { choices: ["Outdoor"] },
        },
        {
          from_name: "notes",
          to_name: "image",
          type: "textarea",
          value: { text: ["Clear sunny frame"] },
        },
      ],
    },
  },
];
"""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _build_mock_editor_standalone(editor_dir: Path, validator_runtime_dir: Path) -> None:
    """Create a self-contained editor-standalone bundle matching LSE's runtime contract."""
    editor_dir.mkdir(parents=True, exist_ok=True)
    components_dir = editor_dir / "components"
    assets_dir = components_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    react_umd = (validator_runtime_dir / "node_modules/react/umd/react.development.js").read_text(encoding="utf-8")
    react_dom_umd = (validator_runtime_dir / "node_modules/react-dom/umd/react-dom.development.js").read_text(
        encoding="utf-8"
    )
    main_js = (
        f"{react_umd}\n;\n{react_dom_umd}\n;\n"
        "window.__editorUIExports = window.__editorUIExports || { Button: function(p){ return window.React.createElement('button', p, p.children); } };\n"
        "window.EditorUI = window.__editorUIExports;\n"
        "window.EditorDeps = window.EditorDeps || {};\n"
    )
    main_css = ":root { --color-neutral-background: #ffffff; }\n"

    (editor_dir / "manifest.json").write_text(
        json.dumps({"main.js": "main-test.js", "main.css": "main-test.css"}),
        encoding="utf-8",
    )
    (editor_dir / "main-test.js").write_text(main_js, encoding="utf-8")
    (editor_dir / "main-test.css").write_text(main_css, encoding="utf-8")
    (assets_dir / "ImageCanvas.test.css").write_text(
        "[data-testid='mock-image-canvas'] { border: 1px solid #cbd5e1; }\n",
        encoding="utf-8",
    )

    label_picker_chunk = """import React from "react";

export function normalizeLabels(raw = []) {
  return (raw || []).map((item, idx) => {
    if (typeof item === "string") {
      return { id: item, name: item, color: "#4c5fa9", hotkey: String(idx + 1) };
    }
    const id = String(item.id ?? item.value ?? item.name ?? idx);
    return {
      id,
      name: String(item.name ?? item.label ?? id),
      color: item.color || "#4c5fa9",
      hotkey: item.hotkey,
    };
  });
}

export function labelKey(label) {
  return typeof label === "string" ? label : String(label?.id ?? label?.name ?? "");
}

export function LabelPicker({ labels = [], value, onChange, disabled = false }) {
  const normalized = normalizeLabels(labels);
  return React.createElement(
    "div",
    { "data-testid": "mock-label-picker", role: "toolbar" },
    normalized.map((lbl) =>
      React.createElement(
        "button",
        {
          key: lbl.id,
          type: "button",
          disabled,
          "aria-pressed": value === lbl.id,
          onClick: () => !disabled && onChange && onChange(lbl.id),
        },
        lbl.name,
      ),
    ),
  );
}
LabelPicker.normalizeLabels = normalizeLabels;
LabelPicker.labelKey = labelKey;
export default LabelPicker;
"""

    image_canvas_chunk = """import React from "react";

export function toImageResults(regions = [], opts = {}) {
  const fromName = opts.fromName || "label";
  const toName = opts.toName || "image";
  return (regions || [])
    .filter((r) => r && (r.type === "bbox" || r.type === "rectangle"))
    .map((r) => ({
      id: r.id,
      from_name: fromName,
      to_name: toName,
      type: "rectanglelabels",
      origin: r.origin || "manual",
      value: {
        x: r.x ?? 10,
        y: r.y ?? 20,
        width: r.width ?? 30,
        height: r.height ?? 40,
        rotation: r.rotation ?? 0,
        rectanglelabels: Array.isArray(r.labels) ? r.labels : r.label ? [r.label] : [],
      },
    }));
}

export function fromImageResults(results = [], opts = {}) {
  const fromName = opts.fromName;
  return (results || [])
    .filter((res) => res && res.type === "rectanglelabels" && (!fromName || res.from_name === fromName))
    .map((res, idx) => ({
      id: res.id || `img_${idx + 1}`,
      type: "bbox",
      x: res.value?.x ?? 10,
      y: res.value?.y ?? 20,
      width: res.value?.width ?? 30,
      height: res.value?.height ?? 40,
      rotation: res.value?.rotation ?? 0,
      labels: Array.isArray(res.value?.rectanglelabels) ? res.value.rectanglelabels : [],
    }));
}

export function ImageCanvas({ src, activeLabel, regions = [], readOnly = false, onAddRegion }) {
  return React.createElement(
    "div",
    { "data-testid": "mock-image-canvas", "data-src": src || "" },
    React.createElement(
      "button",
      {
        type: "button",
        "data-testid": "mock-image-canvas-draw",
        disabled: readOnly,
        onClick: () => {
          if (readOnly || !onAddRegion || !activeLabel) return;
          onAddRegion({
            id: `bbox_${(regions || []).length + 1}`,
            type: "bbox",
            x: 12,
            y: 18,
            width: 40,
            height: 30,
            rotation: 0,
            labels: [activeLabel],
          });
        },
      },
      "Draw box",
    ),
    React.createElement(
      "ul",
      { "data-testid": "mock-image-regions" },
      (regions || []).map((r) =>
        React.createElement("li", { key: r.id, "data-region-id": r.id }, (r.labels || []).join(",")),
      ),
    ),
  );
}
ImageCanvas.toImageResults = toImageResults;
ImageCanvas.fromImageResults = fromImageResults;
export default ImageCanvas;
"""

    answer_form_chunk = """import React from "react";

export function answersToResults(values = {}, fields = [], opts = {}) {
  const toName = opts.toName || "task";
  const out = [];
  for (const field of fields || []) {
    const val = values ? values[field.name] : undefined;
    if (val === undefined || val === null || val === "") continue;
    if (field.type === "choices") {
      const choices = Array.isArray(val) ? val : [String(val)];
      if (!choices.length) continue;
      out.push({
        id: `ans_${field.name}`,
        from_name: field.name,
        to_name: toName,
        type: "choices",
        origin: "manual",
        value: { choices },
      });
    } else if (field.type === "textarea" || field.type === "text") {
      out.push({
        id: `ans_${field.name}`,
        from_name: field.name,
        to_name: toName,
        type: "textarea",
        origin: "manual",
        value: { text: [String(val)] },
      });
    }
  }
  return out;
}

export function resultsToAnswers(results = [], fieldTypes = {}) {
  const out = {};
  for (const res of results || []) {
    if (!res || !res.from_name || !(res.from_name in fieldTypes)) continue;
    const kind = fieldTypes[res.from_name];
    if (kind === "choices" && Array.isArray(res.value?.choices)) {
      out[res.from_name] = res.value.choices.length === 1 ? res.value.choices[0] : res.value.choices;
    } else if ((kind === "textarea" || kind === "text") && Array.isArray(res.value?.text)) {
      out[res.from_name] = res.value.text[0] ?? "";
    }
  }
  return out;
}

export function collectAnswerErrors(fields = [], values = {}) {
  const errors = {};
  for (const field of fields || []) {
    if (!field.required) continue;
    const val = values ? values[field.name] : undefined;
    if (val === undefined || val === null || val === "" || (Array.isArray(val) && !val.length)) {
      errors[field.name] = `${field.label || field.name} is required`;
    }
  }
  return errors;
}

export function AnswerForm({ fields = [], values = {}, onChange, readOnly = false }) {
  return React.createElement(
    "div",
    { "data-testid": "mock-answer-form" },
    (fields || []).map((field) => {
      if (field.type === "choices") {
        return React.createElement(
          "div",
          { key: field.name },
          React.createElement("span", null, field.label || field.name),
          (field.options || []).map((opt) =>
            React.createElement(
              "button",
              {
                key: opt,
                type: "button",
                disabled: readOnly,
                "aria-pressed": values?.[field.name] === opt,
                onClick: () => !readOnly && onChange && onChange({ ...values, [field.name]: opt }),
              },
              opt,
            ),
          ),
        );
      }
      const inputId = `answer-input-${field.name}`;
      return React.createElement(
        "div",
        { key: field.name },
        React.createElement("label", { htmlFor: inputId }, field.label || field.name),
        React.createElement("textarea", {
          id: inputId,
          disabled: readOnly,
          value: values?.[field.name] ?? "",
          onChange: (e) => !readOnly && onChange && onChange({ ...values, [field.name]: e.target.value }),
        }),
      );
    }),
  );
}
AnswerForm.answersToResults = answersToResults;
AnswerForm.resultsToAnswers = resultsToAnswers;
AnswerForm.collectAnswerErrors = collectAnswerErrors;
export default AnswerForm;
"""

    (components_dir / "LabelPicker.test.js").write_text(label_picker_chunk, encoding="utf-8")
    (components_dir / "ImageCanvas.test.js").write_text(image_canvas_chunk, encoding="utf-8")
    (components_dir / "AnswerForm.test.js").write_text(answer_form_chunk, encoding="utf-8")

    components_manifest = {
        "version": "1.0.0",
        "components": {
            "LabelPicker": {
                "name": "LabelPicker",
                "chunk": "components/LabelPicker.test.js",
                "hash": "test1",
                "exports": ["LabelPicker", "normalizeLabels", "labelKey"],
            },
            "ImageCanvas": {
                "name": "ImageCanvas",
                "chunk": "components/ImageCanvas.test.js",
                "hash": "test2",
                "css": "components/assets/ImageCanvas.test.css",
                "exports": ["ImageCanvas", "toImageResults", "fromImageResults"],
            },
            "AnswerForm": {
                "name": "AnswerForm",
                "chunk": "components/AnswerForm.test.js",
                "hash": "test3",
                "exports": [
                    "AnswerForm",
                    "answersToResults",
                    "resultsToAnswers",
                    "collectAnswerErrors",
                ],
            },
        },
    }
    (components_dir / "manifest.json").write_text(json.dumps(components_manifest), encoding="utf-8")

    interface_shell_html = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body>
<div id="shell-root"></div>
<script>
(function() {
  var base = location.pathname.replace(/\\/[^/]*$/, "");
  var loadedModules = {};
  var manifestPromise = null;

  function fetchManifest() {
    if (!manifestPromise) {
      manifestPromise = fetch(base + "/components/manifest.json").then(function(r) {
        if (!r.ok) throw new Error("manifest HTTP " + r.status);
        return r.json();
      });
    }
    return manifestPromise;
  }

  function resolveEntry(manifest, name) {
    var comps = (manifest && manifest.components) || {};
    if (comps[name]) return { entryName: name, entry: comps[name] };
    var keys = Object.keys(comps);
    for (var i = 0; i < keys.length; i++) {
      var ex = comps[keys[i]].exports || [];
      if (ex.indexOf(name) !== -1) return { entryName: keys[i], entry: comps[keys[i]] };
    }
    return null;
  }

  function evalChunk(code) {
    var reactKeys = Object.keys(window.React || {}).filter(function(k) { return /^[A-Za-z_$][\\w$]*$/.test(k); });
    var reactShim = "const R = window.React || {}; export default R; export const { " + reactKeys.join(", ") + " } = R;";
    var reactBlob = URL.createObjectURL(new Blob([reactShim], { type: "text/javascript" }));
    var rewritten = code.replace(/from\\s+["']react["']/g, 'from "' + reactBlob + '"');
    var chunkBlob = URL.createObjectURL(new Blob([rewritten], { type: "text/javascript" }));
    return import(chunkBlob).finally(function() {
      URL.revokeObjectURL(chunkBlob);
      URL.revokeObjectURL(reactBlob);
    });
  }

  function loadModule(name) {
    return fetchManifest().then(function(manifest) {
      var resolved = resolveEntry(manifest, name);
      if (!resolved) throw new Error("Unknown component: " + name);
      if (loadedModules[resolved.entryName]) return loadedModules[resolved.entryName];
      if (resolved.entry.css) {
        var link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = base + "/" + resolved.entry.css;
        document.head.appendChild(link);
      }
      return fetch(base + "/" + resolved.entry.chunk)
        .then(function(r) {
          if (!r.ok) throw new Error("chunk HTTP " + r.status);
          return r.text();
        })
        .then(evalChunk)
        .then(function(mod) {
          loadedModules[resolved.entryName] = mod;
          return mod;
        });
    });
  }

  var target = {
    load: loadModule,
    isLoaded: function(name) { return Boolean(loadedModules[name]); },
    getLoaded: function(name) { return loadedModules[name] || null; },
    useComponentHotkeys: function() {},
  };

  window.InterfaceComponents = new Proxy(target, {
    get: function(t, prop) {
      if (typeof prop !== "string") return t[prop];
      if (prop in t) return t[prop];
      var keys = Object.keys(loadedModules);
      for (var i = 0; i < keys.length; i++) {
        if (prop in loadedModules[keys[i]]) return loadedModules[keys[i]][prop];
      }
      return undefined;
    },
  });

  fetch(base + "/manifest.json")
    .then(function(r) { return r.json(); })
    .then(function(m) {
      if (m["main.css"]) {
        var link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = base + "/" + m["main.css"];
        document.head.appendChild(link);
      }
      var s = document.createElement("script");
      s.src = base + "/" + m["main.js"];
      document.head.appendChild(s);
    });
})();
</script>
</body>
</html>
"""
    (editor_dir / "interface-shell.html").write_text(interface_shell_html, encoding="utf-8")


def _populate_preview_cache_snapshot(cache_root: Path, origin: str, validator_runtime_dir: Path) -> PreviewAssetCache:
    """Create a verified protocol-2 PreviewAssetCache snapshot containing editor-standalone + components."""
    staging_bundle = cache_root / "_source_editor_bundle"
    _build_mock_editor_standalone(staging_bundle, validator_runtime_dir)

    playground_html = b"<!DOCTYPE html><html><body>playground</body></html>"
    playground_js = b"console.log('playground');"
    editor_manifest = (staging_bundle / "manifest.json").read_bytes()
    editor_js = (staging_bundle / "main-test.js").read_bytes()
    editor_css = (staging_bundle / "main-test.css").read_bytes()
    editor_shell = (staging_bundle / "interface-shell.html").read_bytes()
    components_manifest = (staging_bundle / "components/manifest.json").read_bytes()

    responses: dict[str, tuple[int, bytes]] = {
        f"{origin}/api/current-user/whoami": (200, b'{"id": 1}'),
        f"{origin}/react-app/local-playground/manifest.json": (
            200,
            json.dumps(
                {
                    "protocolVersion": PROTOCOL_VERSION,
                    "files": {
                        "index.html": {"url": "index.html", "sha256": _sha256(playground_html)},
                        "app.js": {"url": "app.js", "sha256": _sha256(playground_js)},
                    },
                }
            ).encode("utf-8"),
        ),
        f"{origin}/react-app/local-playground/index.html": (200, playground_html),
        f"{origin}/react-app/local-playground/app.js": (200, playground_js),
        f"{origin}/react-app/editor-standalone/manifest.json": (200, editor_manifest),
        f"{origin}/react-app/editor-standalone/main-test.js": (200, editor_js),
        f"{origin}/react-app/editor-standalone/main-test.css": (200, editor_css),
        f"{origin}/react-app/editor-standalone/interface-shell.html": (200, editor_shell),
        f"{origin}/react-app/editor-standalone/components/manifest.json": (200, components_manifest),
    }

    def handler(request: httpx.Request) -> httpx.Response:
        status, content = responses.get(str(request.url).split("?")[0], (404, b"missing"))
        return httpx.Response(status, content=content, request=request)

    cache = PreviewAssetCache(origin, cache_root=cache_root)
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        snapshot = cache.resolve(client=client, headers={"Authorization": "Token test"})

    # Copy pre-cached component chunks + CSS into the snapshot's editor-standalone/components/
    shutil.copytree(
        staging_bundle / "components",
        snapshot.root / "editor-standalone" / "components",
        dirs_exist_ok=True,
    )
    shutil.rmtree(staging_bundle)
    return cache


class TestValidateInterfaceComponents:
    """Tests for `label-studio-sdk interface validate` on window.InterfaceComponents screens."""

    def test_validate_multi_component_screen_succeeds(self, tmp_path: Path) -> None:
        """Validate a multi-component Screen.jsx (ImageCanvas + LabelPicker + AnswerForm) without --no-validate."""
        _require_node_and_npm()
        screen_file = tmp_path / "Screen.jsx"
        screen_file.write_text(MULTI_COMPONENT_SCREEN_JSX, encoding="utf-8")

        result = runner.invoke(interface_cli.app, ["validate", "--json", str(screen_file)])

        assert result.exit_code == 0, result.output
        report = _loads_cli_json(result)
        assert report["ok"] is True
        assert report["errors"] == []
        undefined_warnings = [w for w in report.get("warnings", []) if w.get("stage") == "undefined-refs"]
        assert undefined_warnings == []

    def test_validate_catches_broken_interface_components_round_trip(self, tmp_path: Path) -> None:
        """Confirm the pure-helper shim executes real serialization rather than skipping round-trip checks."""
        _require_node_and_npm()
        broken_source = MULTI_COMPONENT_SCREEN_JSX.replace(
            "return { regions: [...imageRegions, ...answerRegions], relations: [] };",
            "return { regions: [], relations: [] };",
        )
        screen_file = tmp_path / "Screen.jsx"
        screen_file.write_text(broken_source, encoding="utf-8")

        result = runner.invoke(interface_cli.app, ["validate", "--json", str(screen_file)])

        assert result.exit_code == 1
        report = _loads_cli_json(result)
        assert report["ok"] is False
        error_stages = {err["stage"] for err in report["errors"]}
        assert error_stages & {"round-trip", "consistency"}

    def test_validate_succeeds_on_system_catalog_images_screen(self) -> None:
        """AC #1: `interface validate` succeeds (exit 0) on system_template_catalog/images/Screen.jsx."""
        _require_node_and_npm()
        images_screen = _find_monorepo_path(
            "services/lse/label_studio_enterprise/lse_interfaces/system_template_catalog/images/Screen.jsx"
        )
        if images_screen is None:
            pytest.skip("system_template_catalog/images/Screen.jsx not present in sparse/SDK-only checkout")

        result = runner.invoke(interface_cli.app, ["validate", "--json", str(images_screen)])

        assert result.exit_code == 0, result.output
        report = _loads_cli_json(result)
        assert report["ok"] is True
        assert report["errors"] == []

    def test_validate_succeeds_on_all_modernized_catalog_screens(self) -> None:
        """Every modernized system_template_catalog Screen.jsx referencing InterfaceComponents passes validate."""
        _require_node_and_npm()
        catalog_dir = _find_monorepo_path("services/lse/label_studio_enterprise/lse_interfaces/system_template_catalog")
        if catalog_dir is None:
            pytest.skip("system_template_catalog not present in sparse/SDK-only checkout")

        screens = sorted(catalog_dir.glob("*/Screen.jsx"))
        component_screens = [s for s in screens if "InterfaceComponents" in s.read_text(encoding="utf-8")]
        assert len(component_screens) >= 10

        failures: list[tuple[str, list[dict[str, Any]]]] = []
        for screen in component_screens:
            result = runner.invoke(interface_cli.app, ["validate", "--json", str(screen)])
            if result.exit_code != 0:
                payload = json.loads(result.output) if result.output.strip().startswith("{") else {"raw": result.output}
                failures.append((screen.parent.name, payload.get("errors", [payload])))

        assert failures == []

    def test_pure_helper_shim_parity_with_host_interface_components(self) -> None:
        """AC #2: Validator pure-helper shim covers every component entry in host-interface-components.ts."""
        _require_node_and_npm()
        host_ts = _find_monorepo_path(
            "services/lse/web/apps/labelstudio/src/pages/Interfaces/host-interface-components.ts"
        )
        if host_ts is None:
            pytest.skip("host-interface-components.ts not present in sparse/SDK-only checkout")

        host_source = host_ts.read_text(encoding="utf-8")
        loader_block_match = re.search(
            r"const\s+HELPER_LOADERS\b.*?=\s*\{(.*?)\n\};",
            host_source,
            re.DOTALL,
        )
        assert loader_block_match is not None
        expected_entries = sorted(re.findall(r"^  ([A-Z][A-Za-z0-9]*)\s*:", loader_block_match.group(1), re.M))
        assert len(expected_entries) >= 18

        runtime_dir = interface_cli._ensure_validator_ready()
        shim_path = runtime_dir / "interface-components-shim.mjs"
        assert shim_path.is_file(), "interface-components-shim.mjs must be installed in validator runtime dir"

        probe_js = f"""
import {{ HELPER_ENTRY_NAMES, loadHostInterfaceComponentsSync }} from {json.dumps(shim_path.as_uri())};
const allRefs = HELPER_ENTRY_NAMES.map((n) => `window.InterfaceComponents.${{n}}`).join("\\n");
const ic = loadHostInterfaceComponentsSync(allRefs);
const fnKeys = Object.keys(ic).filter((k) => typeof ic[k] === "function");
console.log(JSON.stringify({{ entries: [...HELPER_ENTRY_NAMES].sort(), fnKeys }}));
"""
        proc = subprocess.run(
            ["node", "--input-type=module", "-e", probe_js],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(proc.stdout.strip())
        assert data["entries"] == expected_entries
        expected_helpers = {
            "normalizeLabels",
            "answersToResults",
            "resultsToAnswers",
            "toImageResults",
            "fromImageResults",
            "toAudioResults",
            "fromAudioResults",
            "toVideoResults",
            "fromVideoResults",
            "toTextCanvasResults",
            "fromTextCanvasResults",
            "toDocumentResults",
            "fromDocumentResults",
            "toTimeSeriesResults",
            "fromTimeSeriesResults",
            "toScene3DResults",
            "fromScene3DResults",
            "toChoicesResult",
            "fromChoicesResult",
            "toRatingResult",
            "fromRatingResult",
            "toRankerResult",
            "fromRankerResult",
            "toPairwiseResult",
            "fromPairwiseResult",
            "toTaxonomyResult",
            "fromTaxonomyResult",
            "toDateTimeResult",
            "fromDateTimeResult",
            "toNumberResult",
            "fromNumberResult",
            "toTextAreaResult",
            "fromTextAreaResult",
            "serializeSubmissionRegions",
        }
        missing_helpers = expected_helpers - set(data["fnKeys"])
        assert not missing_helpers, f"Missing expected InterfaceComponents helpers: {sorted(missing_helpers)}"


class TestScenarioRunnerInterfaceComponents:
    """Tests for `label-studio-sdk interface validate --scenario` on window.InterfaceComponents screens."""

    @staticmethod
    def _skip_if_browser_os_deps_missing(output: str) -> None:
        if (
            "Host system is missing dependencies to run browsers" in output
            or "error while loading shared libraries" in output
        ):
            pytest.skip("Headless Chromium OS shared libraries unavailable in this container")

    def test_validate_scenario_reuses_cached_preview_editor_bundle(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """AC #3 & #5: `validate --scenario` mounts multi-component Screen reusing cached preview editor-bundle."""
        _require_node_and_npm()
        runtime_dir = interface_cli._ensure_validator_ready(require_scenario=True)

        cache_root = tmp_path / "preview-cache"
        _populate_preview_cache_snapshot(cache_root, "https://cached-lse.example", runtime_dir)

        monkeypatch.delenv("LABEL_STUDIO_URL", raising=False)
        monkeypatch.delenv("LS_URL", raising=False)
        monkeypatch.delenv("LABEL_STUDIO_API_KEY", raising=False)
        monkeypatch.setenv("LS_INTERFACE_PREVIEW_CACHE_DIR", str(cache_root))

        screen_file = tmp_path / "Screen.jsx"
        screen_file.write_text(MULTI_COMPONENT_SCREEN_JSX, encoding="utf-8")
        scenario_file = tmp_path / "scenarios.js"
        scenario_file.write_text(MULTI_COMPONENT_SCENARIOS_JS, encoding="utf-8")

        result = runner.invoke(
            interface_cli.app,
            ["validate", "--json", "--scenario", str(scenario_file), str(screen_file)],
        )
        self._skip_if_browser_os_deps_missing(result.output)

        assert result.exit_code == 0, result.output
        payload = _loads_cli_json(result)
        assert payload["ok"] is True
        assert payload["scenario"]["ok"] is True
        assert len(payload["scenario"]["scenarios"]) == 1
        assert payload["scenario"]["scenarios"][0]["ok"] is True

    def test_validate_scenario_fetches_editor_bundle_when_label_studio_url_configured(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """AC #3 & #5: `validate --scenario` fetches editor-bundle + component chunks when LABEL_STUDIO_URL is set."""
        _require_node_and_npm()
        runtime_dir = interface_cli._ensure_validator_ready(require_scenario=True)

        upstream_bundle = tmp_path / "upstream_editor_standalone"
        _build_mock_editor_standalone(upstream_bundle, runtime_dir)
        served_paths: list[str] = []

        class UpstreamHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                clean_path = self.path.split("?", 1)[0]
                served_paths.append(clean_path)
                prefix = "/react-app/editor-standalone/"
                if clean_path.startswith(prefix):
                    rel = clean_path[len(prefix) :]
                    target = (upstream_bundle / rel).resolve()
                    if target.is_file() and upstream_bundle.resolve() in target.parents:
                        body = target.read_bytes()
                        content_type = "application/octet-stream"
                        if target.suffix == ".json":
                            content_type = "application/json"
                        elif target.suffix == ".js":
                            content_type = "application/javascript"
                        elif target.suffix == ".css":
                            content_type = "text/css"
                        elif target.suffix == ".html":
                            content_type = "text/html; charset=utf-8"
                        self.send_response(200)
                        self.send_header("Content-Type", content_type)
                        self.send_header("Content-Length", str(len(body)))
                        self.end_headers()
                        self.wfile.write(body)
                        return
                self.send_response(404)
                self.end_headers()

            def log_message(self, format: str, *args: Any) -> None:
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), UpstreamHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            empty_cache_root = tmp_path / "empty-preview-cache"
            empty_cache_root.mkdir()
            origin = f"http://127.0.0.1:{server.server_port}"

            monkeypatch.setenv("LABEL_STUDIO_URL", origin)
            monkeypatch.delenv("LS_URL", raising=False)
            monkeypatch.delenv("LABEL_STUDIO_API_KEY", raising=False)
            monkeypatch.setenv("LS_INTERFACE_PREVIEW_CACHE_DIR", str(empty_cache_root))

            screen_file = tmp_path / "Screen.jsx"
            screen_file.write_text(MULTI_COMPONENT_SCREEN_JSX, encoding="utf-8")
            scenario_file = tmp_path / "scenarios.js"
            scenario_file.write_text(MULTI_COMPONENT_SCENARIOS_JS, encoding="utf-8")

            result = runner.invoke(
                interface_cli.app,
                ["validate", "--json", "--scenario", str(scenario_file), str(screen_file)],
            )
            self._skip_if_browser_os_deps_missing(result.output)

            assert result.exit_code == 0, result.output
            payload = _loads_cli_json(result)
            assert payload["ok"] is True
            assert payload["scenario"]["ok"] is True
            assert len(payload["scenario"]["scenarios"]) == 1
            assert payload["scenario"]["scenarios"][0]["ok"] is True
            assert "/react-app/editor-standalone/manifest.json" in served_paths
            assert "/react-app/editor-standalone/components/manifest.json" in served_paths
            assert "/react-app/editor-standalone/components/ImageCanvas.test.js" in served_paths
            assert "/react-app/editor-standalone/components/LabelPicker.test.js" in served_paths
            assert "/react-app/editor-standalone/components/AnswerForm.test.js" in served_paths
        finally:
            server.shutdown()
            server.server_close()

    def test_validate_scenario_reports_clear_error_when_bundle_unavailable(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """When neither a cached preview bundle nor a reachable LABEL_STUDIO_URL exists, fail with guidance."""
        _require_node_and_npm()
        empty_cache_root = tmp_path / "empty-cache"
        empty_cache_root.mkdir()

        monkeypatch.delenv("LABEL_STUDIO_URL", raising=False)
        monkeypatch.delenv("LS_URL", raising=False)
        monkeypatch.delenv("LABEL_STUDIO_API_KEY", raising=False)
        monkeypatch.setenv("LS_INTERFACE_PREVIEW_CACHE_DIR", str(empty_cache_root))

        screen_file = tmp_path / "Screen.jsx"
        screen_file.write_text(MULTI_COMPONENT_SCREEN_JSX, encoding="utf-8")
        scenario_file = tmp_path / "scenarios.js"
        scenario_file.write_text(MULTI_COMPONENT_SCENARIOS_JS, encoding="utf-8")

        result = runner.invoke(
            interface_cli.app,
            ["validate", "--scenario", str(scenario_file), str(screen_file)],
        )

        assert result.exit_code != 0
        assert "LABEL_STUDIO_URL" in result.output or "preview" in result.output

    def test_validate_scenario_falls_back_to_cached_bundle_when_env_url_unreachable(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Offline scenario validation falls back to a cached preview snapshot if env LABEL_STUDIO_URL is down."""
        _require_node_and_npm()
        runtime_dir = interface_cli._ensure_validator_ready(require_scenario=True)

        cache_root = tmp_path / "preview-cache"
        _populate_preview_cache_snapshot(cache_root, "http://localhost:24508", runtime_dir)

        monkeypatch.setenv("LABEL_STUDIO_URL", "http://127.0.0.1:1")
        monkeypatch.delenv("LS_URL", raising=False)
        monkeypatch.setenv("LABEL_STUDIO_API_KEY", "offline-token")
        monkeypatch.setenv("LS_INTERFACE_PREVIEW_CACHE_DIR", str(cache_root))

        screen_file = tmp_path / "Screen.jsx"
        screen_file.write_text(MULTI_COMPONENT_SCREEN_JSX, encoding="utf-8")
        scenario_file = tmp_path / "scenarios.js"
        scenario_file.write_text(MULTI_COMPONENT_SCENARIOS_JS, encoding="utf-8")

        from label_studio_sdk._extensions.cli.main import app as root_app

        result = runner.invoke(
            root_app,
            ["interface", "validate", "--json", "--scenario", str(scenario_file), str(screen_file)],
        )
        self._skip_if_browser_os_deps_missing(result.output)

        assert result.exit_code == 0, result.output
        payload = _loads_cli_json(result)
        assert payload["ok"] is True
        assert payload["scenario"]["ok"] is True

        pinned_result = runner.invoke(
            root_app,
            [
                "--base-url",
                "http://127.0.0.1:1",
                "interface",
                "validate",
                "--json",
                "--scenario",
                str(scenario_file),
                str(screen_file),
            ],
        )
        assert pinned_result.exit_code != 0
        pinned_payload = _loads_cli_json(pinned_result)
        assert pinned_payload["scenario"]["ok"] is False

    def test_scenario_bundle_revalidates_after_lse_upgrade_and_falls_back_when_offline(self, tmp_path: Path) -> None:
        """Revalidate scenario-editor-standalone against upstream manifest so upgrades don't 404 chunks."""
        state = {"hash": "aaaaaaaa"}
        requested_paths: list[str] = []

        class UpgradeHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                clean = self.path.split("?", 1)[0]
                requested_paths.append(clean)
                h = state["hash"]
                routes: dict[str, tuple[str, bytes]] = {
                    "/react-app/editor-standalone/manifest.json": (
                        "application/json",
                        json.dumps({"main.js": f"main-{h}.js"}).encode("utf-8"),
                    ),
                    "/react-app/editor-standalone/interface-shell.html": (
                        "text/html; charset=utf-8",
                        b"<!DOCTYPE html><html><body>shell</body></html>",
                    ),
                    f"/react-app/editor-standalone/main-{h}.js": (
                        "application/javascript",
                        f"window.__deployHash = {h!r};\n".encode("utf-8"),
                    ),
                    "/react-app/editor-standalone/components/manifest.json": (
                        "application/json",
                        json.dumps(
                            {
                                "version": "1.0.0",
                                "components": {
                                    "ImageCanvas": {
                                        "name": "ImageCanvas",
                                        "chunk": f"components/ImageCanvas.{h}.js",
                                        "exports": ["ImageCanvas"],
                                    }
                                },
                            }
                        ).encode("utf-8"),
                    ),
                    f"/react-app/editor-standalone/components/ImageCanvas.{h}.js": (
                        "application/javascript",
                        f"export const chunkHash = {h!r};\n".encode("utf-8"),
                    ),
                }
                hit = routes.get(clean)
                if hit is None:
                    self.send_response(404)
                    self.end_headers()
                    return
                content_type, body = hit
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: Any) -> None:
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), UpgradeHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        origin = f"http://127.0.0.1:{server.server_port}"
        cache_root = tmp_path / "cache"
        cache_root.mkdir()
        try:
            # 1. Cold fetch at deploy hash aaaaaaaa
            with serve_scenario_editor_bundle(explicit_base_url=origin, cache_root=cache_root) as bundle_url:
                assert len(requested_paths) == 4
                resp = httpx.get(f"{bundle_url}/components/ImageCanvas.aaaaaaaa.js")
                assert resp.status_code == 200
                assert "aaaaaaaa" in resp.text

            # 2. Warm revalidation at same deploy hash aaaaaaaa skips re-downloading main/shell
            requested_paths.clear()
            editor_dir_same, _, release_same = resolve_scenario_editor_bundle(
                explicit_base_url=origin, cache_root=cache_root
            )
            release_same()
            assert (editor_dir_same / "main-aaaaaaaa.js").is_file()
            assert "/react-app/editor-standalone/main-aaaaaaaa.js" not in requested_paths

            # 3. Upstream upgrades to deploy hash bbbbbbbb — revalidation refreshes bundle & chunks
            state["hash"] = "bbbbbbbb"
            requested_paths.clear()
            with serve_scenario_editor_bundle(explicit_base_url=origin, cache_root=cache_root) as bundle_url:
                manifest = httpx.get(f"{bundle_url}/manifest.json").json()
                assert manifest["main.js"] == "main-bbbbbbbb.js"
                comp_resp = httpx.get(f"{bundle_url}/components/ImageCanvas.bbbbbbbb.js")
                assert comp_resp.status_code == 200
                assert "bbbbbbbb" in comp_resp.text
                stale_resp = httpx.get(f"{bundle_url}/components/ImageCanvas.aaaaaaaa.js")
                assert stale_resp.status_code == 404
        finally:
            server.shutdown()
            server.server_close()

        # 4. Upstream unreachable — falls back to same-origin cached bbbbbbbb bundle
        offline_dir, offline_origin, release_offline = resolve_scenario_editor_bundle(
            explicit_base_url=origin,
            cache_root=cache_root,
            allow_cross_origin_cache_fallback=False,
        )
        try:
            assert offline_origin == origin
            assert (offline_dir / "main-bbbbbbbb.js").is_file()
            assert not (offline_dir / "main-aaaaaaaa.js").exists()
        finally:
            release_offline()

    def test_scenario_bundle_revalidates_preview_snapshot_after_lse_upgrade(self, tmp_path: Path) -> None:
        """When a PreviewAssetCache snapshot exists, resolve_scenario_editor_bundle still revalidates on upgrade."""
        state = {"hash": "aaaaaaaa"}

        class PreviewUpgradeHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                clean = self.path.split("?", 1)[0]
                h = state["hash"]
                playground_html = b"<!DOCTYPE html><html><body>playground</body></html>"
                playground_js = f"console.log({h!r});".encode("utf-8")
                routes: dict[str, tuple[str, bytes]] = {
                    "/api/current-user/whoami": ("application/json", b'{"id": 1}'),
                    "/react-app/local-playground/manifest.json": (
                        "application/json",
                        json.dumps(
                            {
                                "protocolVersion": PROTOCOL_VERSION,
                                "files": {
                                    "index.html": {"url": "index.html", "sha256": _sha256(playground_html)},
                                    "app.js": {"url": "app.js", "sha256": _sha256(playground_js)},
                                },
                            }
                        ).encode("utf-8"),
                    ),
                    "/react-app/local-playground/index.html": ("text/html", playground_html),
                    "/react-app/local-playground/app.js": ("application/javascript", playground_js),
                    "/api/interfaces/editor-bundle/": (
                        "application/json",
                        json.dumps({"main.js": f"main-{h}.js", "main.css": f"main-{h}.css"}).encode("utf-8"),
                    ),
                    "/react-app/editor-standalone/interface-shell.html": (
                        "text/html",
                        b"<!DOCTYPE html><html><body>shell</body></html>",
                    ),
                    f"/react-app/editor-standalone/main-{h}.js": (
                        "application/javascript",
                        f"window.__hash = {h!r};".encode("utf-8"),
                    ),
                    f"/react-app/editor-standalone/main-{h}.css": ("text/css", b":root {}"),
                    "/react-app/editor-standalone/components/manifest.json": (
                        "application/json",
                        json.dumps(
                            {
                                "version": "1.0.0",
                                "components": {
                                    "ImageCanvas": {
                                        "name": "ImageCanvas",
                                        "chunk": f"components/ImageCanvas.{h}.js",
                                        "exports": ["ImageCanvas"],
                                    }
                                },
                            }
                        ).encode("utf-8"),
                    ),
                    f"/react-app/editor-standalone/components/ImageCanvas.{h}.js": (
                        "application/javascript",
                        f"export const h = {h!r};".encode("utf-8"),
                    ),
                }
                hit = routes.get(clean)
                if hit is None:
                    self.send_response(404)
                    self.end_headers()
                    return
                content_type, body = hit
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: Any) -> None:
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), PreviewUpgradeHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        origin = f"http://127.0.0.1:{server.server_port}"
        cache_root = tmp_path / "preview-cache"
        cache_root.mkdir()
        auth = {"Authorization": "Token test"}
        try:
            editor_a, _, release_a = resolve_scenario_editor_bundle(
                explicit_base_url=origin, auth_headers=auth, cache_root=cache_root
            )
            try:
                assert (editor_a / "main-aaaaaaaa.js").is_file()
            finally:
                release_a()

            state["hash"] = "bbbbbbbb"
            with serve_scenario_editor_bundle(
                explicit_base_url=origin, auth_headers=auth, cache_root=cache_root
            ) as bundle_url:
                manifest = httpx.get(f"{bundle_url}/manifest.json").json()
                assert manifest["main.js"] == "main-bbbbbbbb.js"
                comp_resp = httpx.get(f"{bundle_url}/components/ImageCanvas.bbbbbbbb.js")
                assert comp_resp.status_code == 200
                assert "bbbbbbbb" in comp_resp.text
        finally:
            server.shutdown()
            server.server_close()


class _FakeSyncResponse:
    def __init__(self, payload: dict[str, Any], status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code
        self.text = json.dumps(payload)
        self.request = SimpleNamespace(url="http://ls/api/interfaces/")

    def json(self) -> dict[str, Any]:
        return self.payload

    def raise_for_status(self) -> None:
        return None


class _FakeSyncHttpClient:
    calls: list[tuple[str, str, dict[str, Any] | None]] = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.headers = kwargs.get("headers")

    def __enter__(self) -> "_FakeSyncHttpClient":
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def post(self, url: str, json: dict[str, Any] | None = None, **kwargs: Any) -> _FakeSyncResponse:
        _FakeSyncHttpClient.calls.append(("POST", url, deepcopy(json)))
        body = json or {}
        versions = [
            {**v, "id": idx, "createdAt": "2026-01-01T00:00:00Z"}
            for idx, v in enumerate(body.get("versions") or [{"code": body.get("code", "")}])
        ]
        return _FakeSyncResponse(
            {
                "id": 42,
                "title": body.get("title", "Synced IC Screen"),
                "code": body.get("code", ""),
                "compiled": body.get("compiled", ""),
                "versions": versions,
                "workspace": body.get("workspace", 5),
                "metadata": body.get("metadata", {}),
            }
        )


class TestSyncAndStartWithInterfaceComponents:
    """AC #4: Default `interface sync` and `interface start` succeed without --no-validate."""

    def test_sync_succeeds_without_no_validate_on_interface_components_screen(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Default `interface sync` runs real validator and succeeds on a multi-component Screen.jsx."""
        _require_node_and_npm()
        _FakeSyncHttpClient.calls = []
        monkeypatch.setattr(interface_cli.httpx, "Client", _FakeSyncHttpClient)

        screen_file = tmp_path / "Screen.jsx"
        screen_file.write_text(MULTI_COMPONENT_SCREEN_JSX, encoding="utf-8")

        result = runner.invoke(
            interface_cli.app,
            [
                "sync",
                str(screen_file),
                "--title",
                "Image IC Interface",
                "--workspace",
                "5",
                "--token",
                "test-token",
                "--lse-url",
                "http://ls",
            ],
        )

        assert result.exit_code == 0, result.output
        assert len(_FakeSyncHttpClient.calls) == 1
        method, url, payload = _FakeSyncHttpClient.calls[0]
        assert method == "POST"
        assert url == "http://ls/api/interfaces/"
        assert payload is not None
        assert payload["compiled"]
        assert "objects" in payload["output_schema"]["properties"]

    def test_start_succeeds_without_no_validate_on_interface_components_screen(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Default `interface start` runs real validator and creates project without --no-validate."""
        _require_node_and_npm()
        _FakeSyncHttpClient.calls = []
        monkeypatch.setattr(interface_cli.httpx, "Client", _FakeSyncHttpClient)
        created_projects: list[dict[str, Any]] = []

        def fake_create_project(**kwargs: Any) -> SimpleNamespace:
            created_projects.append(kwargs)
            return SimpleNamespace(id=99)

        monkeypatch.setattr(interface_cli, "_create_project", fake_create_project)

        screen_file = tmp_path / "Screen.jsx"
        screen_file.write_text(MULTI_COMPONENT_SCREEN_JSX, encoding="utf-8")

        result = runner.invoke(
            interface_cli.app,
            [
                "start",
                str(screen_file),
                "--title",
                "Image IC Interface",
                "--project-title",
                "Image IC Project",
                "--workspace",
                "5",
                "--no-open",
                "--token",
                "test-token",
                "--lse-url",
                "http://ls",
            ],
        )

        assert result.exit_code == 0, result.output
        assert len(created_projects) == 1
        assert created_projects[0]["interface_id"] == 42
        assert created_projects[0]["title"] == "Image IC Project"
