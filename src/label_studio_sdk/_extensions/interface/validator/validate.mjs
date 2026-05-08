// Offline validator for HumanSignal custom interface modules.
//
// Mirrors the layered checks the Create-Interface modal runs in the browser
// (see services/lse/web/apps/labelstudio/src/pages/Interfaces/interface-utils.ts),
// but offline so it works in CI: the CLI spawns this script with a file path,
// it prints a JSON report on stdout and exits with a non-zero status when
// any error is found.
//
// Layers:
//   1. compile          — sucrase JSX → CJS body
//   2. undefined refs   — regex scan for React.createElement(Foo) where Foo isn't defined
//   3. shape            — last expression is `({default, ...})`, default is a function
//   4. schema           — paramsSchema / inputSchema / outputSchema / regionSchema are
//                         plain objects (not full JSON Schema validation)
//   5. missing exports  — warn for missing getResults / parseResults / outputSchema / paramsSchema
//   6. round-trip       — getResults/parseResults run without throwing on stub input
//   7. consistency      — outputSchema → mock LLM → parseResults round-trip
//
// Layer 8 (actual render) is intentionally skipped — that requires React + DOM
// and is covered interactively by the playground.

import { readFileSync, existsSync } from "node:fs";
import { transform } from "sucrase";

const filePath = process.argv[2];
if (!filePath || !existsSync(filePath)) {
  process.stderr.write(`usage: node validate.mjs <file.jsx>\n`);
  process.exit(2);
}

const source = readFileSync(filePath, "utf8");
const report = validate(source);
// IMPORTANT: do not call process.exit() here. On non-TTY stdout (i.e. when
// invoked from another process via pipe), `process.stdout.write` is async and
// `process.exit` aborts before the OS pipe drains, truncating the JSON at
// roughly the pipe buffer size (~64 KiB on macOS). Setting `exitCode` lets
// Node finish flushing stdout before it exits naturally.
process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
process.exitCode = report.ok ? 0 : 1;

// ────────────────────────────────────────────────────────────────────────

function validate(source) {
  const errors = [];
  const warnings = [];
  const metadata = {};

  // ── layer 1: compile ────────────────────────────────────────────────
  let body;
  try {
    const { code } = transform(source, {
      transforms: ["jsx"],
      jsxRuntime: "classic",
      production: true,
    });
    // Match `compileScreen` in interface-utils.ts: the last parenthesized
    // expression becomes the return value so eval() can pull it out.
    const lastParenIdx = code.lastIndexOf("\n(");
    if (lastParenIdx !== -1) {
      body = `${code.slice(0, lastParenIdx)}\nreturn ${code.slice(lastParenIdx + 1)}`;
    } else {
      body = `return (function() { ${code} })()`;
    }
  } catch (e) {
    errors.push({ stage: "compile", message: String(e?.message ?? e) });
    return { ok: false, errors, warnings, exports: [], metadata };
  }

  // ── layer 2: undefined component refs ──────────────────────────────
  // Regex scan for `React.createElement(Foo, …)` where `Foo` isn't defined
  // anywhere in the compiled body. Catches typos like `<MyButtn />` that
  // would crash the iframe at render time but pass eval-shape checks.
  const missingRefs = checkUndefinedComponents(body);
  if (missingRefs) {
    errors.push({ stage: "undefined-refs", message: missingRefs });
    return { ok: false, errors, warnings, exports: [], metadata, compiled: body };
  }

  // ── layer 3: eval & module shape ────────────────────────────────────
  let mod;
  try {
    const React = makeStubReact();
    const factory = new Function(
      "React",
      "useState",
      "useRef",
      "useEffect",
      "useCallback",
      "useMemo",
      "getField",
      "EditorUI",
      body,
    );
    mod = factory(
      React,
      React.useState,
      React.useRef,
      React.useEffect,
      React.useCallback,
      React.useMemo,
      getField,
      {},
    );
  } catch (e) {
    errors.push({ stage: "eval", message: String(e?.message ?? e) });
    return { ok: false, errors, warnings, exports: [], metadata };
  }

  if (!mod || typeof mod !== "object") {
    errors.push({
      stage: "shape",
      message: "Module did not return an object — last expression must be `({ default: Component, ... })`",
    });
    return { ok: false, errors, warnings, exports: [], metadata };
  }
  if (typeof mod.default !== "function") {
    errors.push({ stage: "shape", message: "Module is missing `default` export (must be a function component)" });
  }

  const exports_ = Object.keys(mod);
  metadata.hasDefault = typeof mod.default === "function";
  metadata.hasGetResults = typeof mod.getResults === "function";
  metadata.hasParseResults = typeof mod.parseResults === "function";
  metadata.hasParamsSchema = isPlainObject(mod.paramsSchema);
  metadata.hasInputSchema = isPlainObject(mod.inputSchema);
  metadata.hasOutputSchema = isPlainObject(mod.outputSchema);
  metadata.hasRegionSchema = isPlainObject(mod.regionSchema);
  metadata.specVersion = typeof mod.specVersion === "number" ? mod.specVersion : null;
  if (metadata.hasParamsSchema) metadata.paramsSchema = mod.paramsSchema;
  if (metadata.hasInputSchema) metadata.inputSchema = mod.inputSchema;
  if (metadata.hasOutputSchema) metadata.outputSchema = mod.outputSchema;
  if (metadata.hasRegionSchema) metadata.regionSchema = mod.regionSchema;

  // ── layer 4: schema sanity ──────────────────────────────────────────
  for (const key of ["paramsSchema", "inputSchema", "outputSchema", "regionSchema"]) {
    if (mod[key] !== undefined && !isPlainObject(mod[key])) {
      errors.push({ stage: "schema", message: `\`${key}\` must be a plain object if present` });
    }
  }

  // ── layer 5: missing optional exports (warnings) ────────────────────
  // Mirrors the in-app modal — these are ergonomic warnings, not blocking
  // errors. They flag interfaces that will work but lose some capability.
  if (!metadata.hasGetResults) {
    warnings.push({
      stage: "missing-export",
      message:
        "Missing `getResults` — the shell's default serialization will be used, which may not match your annotation structure",
    });
  }
  if (!metadata.hasParseResults) {
    warnings.push({
      stage: "missing-export",
      message: "Missing `parseResults` — saved annotations may not load back correctly",
    });
  }
  if (!metadata.hasOutputSchema) {
    warnings.push({
      stage: "missing-export",
      message: "Missing `outputSchema` — auto-labeling (Prompter) will not work with this interface",
    });
  }
  if (!metadata.hasParamsSchema) {
    warnings.push({
      stage: "missing-export",
      message: "Missing `paramsSchema` — the interface won't be configurable per-project",
    });
  }

  // ── layer 6: serialization round-trip ───────────────────────────────

  if (metadata.hasGetResults) {
    runSafe(() => mod.getResults([], []), (err) =>
      errors.push({ stage: "round-trip", message: `getResults([]) threw: ${err.message}` }),
    );
    runSafe(
      () => {
        const out = mod.getResults(seedRegions(), []);
        if (!Array.isArray(out)) {
          errors.push({
            stage: "round-trip",
            message: `getResults must return an array of AnnotationResult objects (got ${describe(out)})`,
          });
        }
        return out;
      },
      (err) => errors.push({ stage: "round-trip", message: `getResults(seed) threw: ${err.message}` }),
    );
  }

  if (metadata.hasParseResults) {
    runSafe(() => mod.parseResults([]), (err) =>
      errors.push({ stage: "round-trip", message: `parseResults([]) threw: ${err.message}` }),
    );
  }

  if (metadata.hasGetResults && metadata.hasParseResults) {
    runSafe(
      () => {
        const seeded = seedRegions();
        const serialized = mod.getResults(seeded, []);
        if (!Array.isArray(serialized)) return;
        const parsed = mod.parseResults(serialized);
        if (!parsed || !Array.isArray(parsed.regions)) {
          errors.push({
            stage: "round-trip",
            message: `parseResults must return \`{ regions: [...] }\` (got ${describe(parsed)})`,
          });
        }
      },
      (err) => errors.push({ stage: "round-trip", message: `Round-trip threw: ${err.message}` }),
    );
  }

  // ── layer 7: outputSchema ↔ parseResults consistency ────────────────
  // Generates a mock LLM JSON response from outputSchema, converts it to LS
  // annotation results (same mapping the Prompter pipeline uses), and feeds
  // that into parseResults. Catches deserializers that work for hand-built
  // results but not for ones produced by the Prompter.
  const consistency = validateOutputSchemaConsistency(mod);
  if (!consistency.ok && consistency.error) {
    errors.push({ stage: "consistency", message: consistency.error });
  }

  return {
    ok: errors.length === 0,
    errors,
    warnings,
    exports: exports_,
    metadata,
    // Pass the compiled body through so callers (push) don't need a second
    // sucrase invocation. Always present on a successful compile, even when
    // shape/schema/round-trip layers report errors.
    compiled: body,
  };
}

// ── undefined component refs (port of interface-utils.ts:checkUndefinedComponents)
function checkUndefinedComponents(compiledBody) {
  const referenced = new Set();
  const createRe = /React\.createElement\(([A-Z][A-Za-z0-9_]*)\s*[,)]/g;
  let m;
  while ((m = createRe.exec(compiledBody)) !== null) {
    referenced.add(m[1]);
  }
  if (referenced.size === 0) return null;
  const defined = new Set(["React"]);
  const defRe = /(?:function|const|let|var|class)\s+([A-Z][A-Za-z0-9_]*)/g;
  while ((m = defRe.exec(compiledBody)) !== null) {
    defined.add(m[1]);
  }
  const missing = [];
  for (const name of referenced) {
    if (!defined.has(name)) missing.push(name);
  }
  if (missing.length === 0) return null;
  const subject = missing.length > 1 ? "These are" : "This is";
  const plural = missing.length > 1 ? "s" : "";
  return `Undefined component${plural}: ${missing.join(", ")}. ${subject} referenced in JSX but not defined anywhere in the code.`;
}

// ── outputSchema → mock LLM → annotation results → parseResults round-trip
// (port of interface-utils.ts:generateMockLlmOutput / outputToLsRegions /
// validateOutputSchemaConsistency)

function generateMockLlmOutput(outputSchema) {
  const properties = outputSchema?.properties;
  if (!properties) return {};
  const mock = {};
  for (const [key, def] of Object.entries(properties)) {
    let fieldType = def.type ?? "string";
    if (Array.isArray(fieldType)) fieldType = fieldType.find((t) => t !== "null") ?? "string";
    if (def.$param && !def.enum) continue;
    if (fieldType === "string" && def.enum) {
      mock[key] = def.enum[0];
    } else if (fieldType === "string") {
      mock[key] = "sample text";
    } else if (fieldType === "number" || fieldType === "integer") {
      mock[key] = 0;
    } else if (fieldType === "boolean") {
      mock[key] = true;
    } else if (fieldType === "array") {
      const items = def.items;
      mock[key] = items?.enum ? [items.enum[0]] : [];
    } else {
      mock[key] = "sample text";
    }
  }
  return mock;
}

function outputToLsRegions(llmOutput, outputSchema) {
  const properties = outputSchema?.properties;
  if (!properties || !llmOutput) return [];
  const regions = [];
  for (const [fieldKey, fieldDef] of Object.entries(properties)) {
    const value = llmOutput[fieldKey];
    if (value === undefined || value === null) continue;
    let fieldType = fieldDef.type ?? "string";
    if (Array.isArray(fieldType)) fieldType = fieldType.find((t) => t !== "null") ?? "string";
    const hasEnum = "enum" in fieldDef;
    const region = { id: `mock-${fieldKey}`, from_name: fieldKey, to_name: "data" };
    if (fieldType === "string" && hasEnum) {
      region.type = "choices";
      region.value = { choices: typeof value === "string" ? [value] : value };
    } else if (fieldType === "string") {
      region.type = "textarea";
      region.value = { text: typeof value === "string" ? [value] : value };
    } else if (fieldType === "number" || fieldType === "integer") {
      region.type = "number";
      region.value = { number: value };
    } else if (fieldType === "boolean") {
      region.type = "choices";
      region.value = { choices: [String(value)] };
    } else if (fieldType === "array") {
      const items = fieldDef.items;
      if (items && "enum" in items) {
        region.type = "choices";
        region.value = { choices: Array.isArray(value) ? value : [value] };
      } else {
        region.type = "labels";
        region.value = value;
      }
    } else {
      region.type = "textarea";
      region.value = { text: [String(value)] };
    }
    regions.push(region);
  }
  return regions;
}

function validateOutputSchemaConsistency(mod) {
  const outputSchema = mod.outputSchema;
  const parseResults = mod.parseResults;
  if (!outputSchema || typeof outputSchema !== "object" || typeof parseResults !== "function") {
    return { ok: true, skipped: true };
  }
  const properties = outputSchema.properties;
  if (!properties || Object.keys(properties).length === 0) return { ok: true, skipped: true };
  const mockLlmOutput = generateMockLlmOutput(outputSchema);
  const testedFields = Object.keys(mockLlmOutput);
  if (testedFields.length === 0) return { ok: true, skipped: true };

  const mockResults = outputToLsRegions(mockLlmOutput, outputSchema);
  if (mockResults.length === 0) {
    return {
      ok: false,
      error: `outputSchema declares ${testedFields.length} fields (${testedFields.join(", ")}) but none produced valid LS annotation results. Check that property types are valid (string, number, boolean, array).`,
    };
  }
  let parsed;
  try {
    parsed = parseResults(mockResults);
  } catch (err) {
    return {
      ok: false,
      error: `parseResults crashed when given Prompter-style annotation results: ${err instanceof Error ? err.message : String(err)}. Each outputSchema property key becomes a from_name in the annotation results — fix parseResults to handle: ${testedFields.join(", ")}.`,
    };
  }
  const regions = Array.isArray(parsed) ? parsed : (parsed?.regions ?? []);
  if (regions.length === 0 && mockResults.length > 0) {
    return {
      ok: false,
      error: `parseResults returned 0 regions for ${mockResults.length} annotation results. parseResults must return \`{ regions: [...] }\` with one region per annotation result. Each result has from_name matching an outputSchema key — handle: ${testedFields.join(", ")}.`,
    };
  }
  return { ok: true };
}

// ── helpers ─────────────────────────────────────────────────────────────

function makeStubReact() {
  // Components aren't invoked during validate — only the module's last-expression
  // object literal is evaluated. So the stub only needs to satisfy code that
  // *might* run at module top level (rare).
  const noop = () => null;
  const factory = (..._args) => null;
  factory.createElement = factory;
  factory.Fragment = "Fragment";
  factory.useState = (init) => [typeof init === "function" ? init() : init, noop];
  factory.useRef = (val) => ({ current: val });
  factory.useEffect = noop;
  factory.useCallback = (fn) => fn;
  factory.useMemo = (fn) => (typeof fn === "function" ? fn() : fn);
  return factory;
}

function getField(obj, path) {
  if (!obj || typeof obj !== "object" || !path) return undefined;
  return path.split(".").reduce((o, k) => (o && typeof o === "object" ? o[k] : undefined), obj);
}

function isPlainObject(v) {
  return typeof v === "object" && v !== null && !Array.isArray(v);
}

function describe(v) {
  if (v === null) return "null";
  if (Array.isArray(v)) return "array";
  return typeof v;
}

function seedRegions() {
  // Generic ScreenRegion-shaped seed. Modules may filter on region ids/types
  // they don't recognise (returning []), which is fine — round-trip is a
  // smoke test, not a deep-equality check.
  return [
    {
      id: "seed-region-1",
      type: "choice",
      labels: ["Seed"],
      colors: ["#10b981"],
      score: null,
      hidden: false,
      locked: false,
      selected: false,
      parentId: null,
      text: "",
    },
  ];
}

function runSafe(fn, onError) {
  try {
    return fn();
  } catch (e) {
    onError(e instanceof Error ? e : new Error(String(e)));
    return undefined;
  }
}
