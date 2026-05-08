// Browser-driven scenario validator for HumanSignal custom interfaces.
//
// Runs an interface module in a minimal React/Playwright harness, lets each
// scenario execute browser actions with Playwright, then validates
// serialization, deserialization, and the Label Studio AnnotationResult shape.

import { existsSync, readFileSync } from "node:fs";
import { dirname, extname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { chromium } from "playwright";
import { transform } from "sucrase";

const filePath = process.argv[2];
const scenarioPath = process.argv[3];

if (!filePath || !scenarioPath || !existsSync(filePath) || !existsSync(scenarioPath)) {
  process.stderr.write("usage: node scenario-runner.mjs <file.jsx> <scenarios.js>\n");
  process.exit(2);
}

const report = await run().catch((error) => ({
  ok: false,
  file: filePath,
  scenarioFile: scenarioPath,
  errors: [{ stage: "runner", message: errorMessage(error) }],
  scenarios: [],
}));

process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
process.exitCode = report.ok ? 0 : 1;

async function run() {
  const errors = [];
  const warnings = [];

  let scenarios = [];
  try {
    scenarios = await loadScenarioModule(scenarioPath);
  } catch (error) {
    errors.push({ stage: "scenario-file", message: errorMessage(error) });
  }

  const scriptPaths = getScriptPaths();
  for (const [name, path] of Object.entries(scriptPaths)) {
    if (!existsSync(path)) {
      errors.push({ stage: "deps", message: `Missing ${name} browser bundle at ${path}. Run ls_interface.py validate again to install deps.` });
    }
  }

  let compiledBody = "";
  try {
    compiledBody = compile(readFileSync(filePath, "utf8"));
  } catch (error) {
    errors.push({ stage: "compile", message: errorMessage(error) });
  }

  if (errors.length > 0) {
    return {
      ok: false,
      file: filePath,
      scenarioFile: scenarioPath,
      errors,
      warnings,
      scenarios: [],
    };
  }

  const browser = await chromium.launch({ headless: true });
  const scenarioReports = [];
  try {
    for (const [index, scenario] of scenarios.entries()) {
      scenarioReports.push(await runScenario(browser, compiledBody, scenario, index, scriptPaths));
    }
  } finally {
    await browser.close();
  }

  return {
    ok: scenarioReports.every((scenario) => scenario.ok),
    file: filePath,
    scenarioFile: scenarioPath,
    errors,
    warnings,
    scenarios: scenarioReports,
  };
}

async function runScenario(browser, compiledBody, scenario, index, scriptPaths) {
  const name = scenario?.name || `scenario ${index + 1}`;
  const errors = [];
  const warnings = [];
  let results = [];
  let roundTripResults = [];
  let parsed = null;

  validateScenarioDefinition(scenario, errors);
  if (errors.length > 0) {
    return {
      name,
      ok: false,
      errors,
      warnings,
      results,
      parsed,
      roundTripResults,
    };
  }

  const page = await browser.newPage({ viewport: { width: 1024, height: 768 } });

  try {
    const scenarioData = serializeScenarioForHarness(scenario);

    await page.setContent(`
      <!doctype html>
      <html>
        <head>
          <meta charset="utf-8" />
          <style>
            html, body, #root {
              width: 100%;
              min-height: 100%;
              margin: 0;
            }
            body {
              font-family: Arial, sans-serif;
            }
            * {
              box-sizing: border-box;
            }
          </style>
        </head>
        <body><div id="root"></div></body>
      </html>
    `);
    await page.addScriptTag({ path: scriptPaths.react });
    await page.addScriptTag({ path: scriptPaths.reactDom });
    await page.evaluate(
      ({ body, scenarioDef, harnessSource }) => {
        const install = new Function(
          "compiledBody",
          "scenario",
          `return (${harnessSource})(compiledBody, scenario);`,
        );
        return install(body, scenarioDef);
      },
      {
        body: compiledBody,
        scenarioDef: scenarioData,
        harnessSource: getBrowserHarnessSource(),
      },
    );

    await page.waitForFunction(() => Boolean(window.__hsScenario), null, { timeout: 5000 });

    await scenario.run(makeScenarioContext(page));

    await validateVisibleText(page, scenario.expect?.visibleText, errors);

    results = await page.evaluate(() => window.__hsScenario.getResults());
    const outputSchema = await page.evaluate(() => window.__hsScenario.getOutputSchema());
    errors.push(...validateAnnotationResults(results, outputSchema, "serialize"));
    errors.push(...compareExpectedResults(results, scenario.expect?.results));

    const roundTrip = await validateRoundTrip(page, results, outputSchema);
    parsed = roundTrip.parsed;
    roundTripResults = roundTrip.results;
    errors.push(...roundTrip.errors);
  } catch (error) {
    errors.push({ stage: "scenario", message: errorMessage(error) });
  } finally {
    await page.close();
  }

  return {
    name,
    ok: errors.length === 0,
    errors,
    warnings,
    results,
    parsed,
    roundTripResults,
  };
}

async function loadScenarioModule(path) {
  if (extname(path) !== ".js") {
    throw new Error(`Scenario file must be a .js module, got ${JSON.stringify(path)}.`);
  }
  const url = pathToFileURL(resolve(path));
  url.searchParams.set("t", String(Date.now()));
  let mod;
  try {
    mod = await import(url.href);
  } catch (error) {
    throw new Error(`Could not import scenario module ${path}: ${errorMessage(error)}`);
  }
  if (!Array.isArray(mod.default)) {
    throw new Error("Scenario module must default-export an array of scenario objects.");
  }
  return mod.default;
}

function serializeScenarioForHarness(scenario) {
  const data = {};
  for (const key of [
    "task",
    "params",
    "settings",
    "initialRegions",
    "initialRelations",
    "selectedRegionIds",
    "initialResults",
    "interfaces",
    "readOnly",
  ]) {
    if (scenario[key] !== undefined) data[key] = cloneSerializable(scenario[key]);
  }
  return data;
}

function validateScenarioDefinition(scenario, errors) {
  if (!isPlainObject(scenario)) {
    errors.push({ stage: "scenario-file", message: "Each scenario must be an object." });
    return;
  }
  if (typeof scenario.name !== "string" || scenario.name.length === 0) {
    errors.push({ stage: "scenario-file", message: "Each scenario must define a non-empty `name` string." });
  }
  if (typeof scenario.run !== "function") {
    errors.push({
      stage: "scenario-file",
      message: `Scenario "${scenario.name || "<unnamed>"}" must define an async run(ctx) function.`,
    });
  }
  if (scenario.expect !== undefined && !isPlainObject(scenario.expect)) {
    errors.push({ stage: "scenario-file", message: `Scenario "${scenario.name || "<unnamed>"}" expect must be an object.` });
  }
  for (const key of ["task", "params", "settings", "initialRegions", "initialRelations", "selectedRegionIds", "initialResults", "interfaces", "readOnly"]) {
    const value = scenario[key];
    if (value !== undefined && !isJsonSerializable(value)) {
      errors.push({
        stage: "scenario-file",
        message: `Scenario "${scenario.name || "<unnamed>"}" field ${JSON.stringify(key)} must be JSON-serializable.`,
      });
    }
  }
}

function makeScenarioContext(page) {
  return {
    page,
    async getResults() {
      return page.evaluate(() => window.__hsScenario.getResults());
    },
    async parseResults(results) {
      return page.evaluate((serialized) => window.__hsScenario.parseResults(serialized), results);
    },
    async setParsed(parsed) {
      return page.evaluate((nextParsed) => window.__hsScenario.setParsed(nextParsed), parsed);
    },
    async getState() {
      return page.evaluate(() => window.__hsScenario.getState());
    },
    async getOutputSchema() {
      return page.evaluate(() => window.__hsScenario.getOutputSchema());
    },
  };
}

async function validateVisibleText(page, visibleText, errors) {
  if (visibleText === undefined) return;
  if (!Array.isArray(visibleText)) {
    errors.push({ stage: "expect", message: "`expect.visibleText` must be an array of strings." });
    return;
  }

  for (const text of visibleText) {
    if (typeof text !== "string") {
      errors.push({ stage: "expect", message: "`expect.visibleText` entries must be strings." });
      continue;
    }
    try {
      await page.getByText(text, { exact: false }).first().waitFor({ state: "visible", timeout: 1000 });
    } catch (error) {
      errors.push({ stage: "expect", message: `Expected visible text not found: ${JSON.stringify(text)}.` });
    }
  }
}

async function validateRoundTrip(page, results, outputSchema) {
  const errors = [];
  let parsed = null;
  let roundTripResults = [];

  try {
    parsed = await page.evaluate((serialized) => window.__hsScenario.parseResults(serialized), results);
  } catch (error) {
    errors.push({ stage: "deserialize", message: `parseResults threw: ${errorMessage(error)}` });
    return { errors, parsed, results: roundTripResults };
  }

  if (!isPlainObject(parsed) || !Array.isArray(parsed.regions)) {
    errors.push({
      stage: "deserialize",
      message: `parseResults must return { regions: [...] } (got ${describe(parsed)}).`,
    });
    return { errors, parsed, results: roundTripResults };
  }

  try {
    await page.evaluate((nextParsed) => window.__hsScenario.setParsed(nextParsed), parsed);
    await page.waitForTimeout(0);
    roundTripResults = await page.evaluate(() => window.__hsScenario.getResults());
  } catch (error) {
    errors.push({ stage: "round-trip", message: `Rerendering parsed regions failed: ${errorMessage(error)}` });
    return { errors, parsed, results: roundTripResults };
  }

  errors.push(...validateAnnotationResults(roundTripResults, outputSchema, "round-trip"));
  if (!deepEqual(stripGeneratedIds(results), stripGeneratedIds(roundTripResults))) {
    errors.push({
      stage: "round-trip",
      message: "getResults(parseResults(getResults(...))) changed the serialized annotation results.",
    });
  }

  return { errors, parsed, results: roundTripResults };
}

function compareExpectedResults(actual, expected) {
  const errors = [];
  if (expected === undefined) return errors;
  if (!Array.isArray(expected)) {
    return [{ stage: "expect", message: "`expect.results` must be an array." }];
  }
  if (!Array.isArray(actual)) {
    return [{ stage: "expect", message: "`getResults` did not return an array, so expected results cannot be compared." }];
  }
  if (actual.length !== expected.length) {
    errors.push({ stage: "expect", message: `Expected ${expected.length} result(s), got ${actual.length}.` });
  }

  for (let index = 0; index < Math.min(actual.length, expected.length); index += 1) {
    const actualResult = actual[index];
    const expectedResult = expected[index];
    if (!isPlainObject(expectedResult)) {
      errors.push({ stage: "expect", message: `expect.results[${index}] must be an object.` });
      continue;
    }
    for (const [key, expectedValue] of Object.entries(expectedResult)) {
      if (!deepEqual(actualResult?.[key], expectedValue)) {
        errors.push({
          stage: "expect",
          message: `Result ${index} field ${JSON.stringify(key)} mismatch. Expected ${stableStringify(expectedValue)}, got ${stableStringify(actualResult?.[key])}.`,
        });
      }
    }
  }

  return errors;
}

function validateAnnotationResults(results, outputSchema, stage) {
  const errors = [];
  if (!Array.isArray(results)) {
    return [{ stage, message: `getResults must return an array of AnnotationResult objects (got ${describe(results)}).` }];
  }

  const properties = isPlainObject(outputSchema?.properties) ? outputSchema.properties : null;
  for (const [index, result] of results.entries()) {
    const prefix = `results[${index}]`;
    if (!isPlainObject(result)) {
      errors.push({ stage, message: `${prefix} must be an object.` });
      continue;
    }
    if (result.id !== undefined && typeof result.id !== "string") {
      errors.push({ stage, message: `${prefix}.id must be a string when present.` });
    }
    for (const key of ["from_name", "to_name", "type"]) {
      if (typeof result[key] !== "string" || result[key].length === 0) {
        errors.push({ stage, message: `${prefix}.${key} must be a non-empty string.` });
      }
    }
    if (!isPlainObject(result.value)) {
      errors.push({ stage, message: `${prefix}.value must be an object.` });
    }
    if (result.origin !== undefined && typeof result.origin !== "string") {
      errors.push({ stage, message: `${prefix}.origin must be a string when present.` });
    }

    if (properties && result.from_name) {
      const fieldDef = properties[result.from_name];
      if (!fieldDef) {
        errors.push({
          stage,
          message: `${prefix}.from_name=${JSON.stringify(result.from_name)} is not declared in outputSchema.properties.`,
        });
      } else {
        errors.push(...validateResultAgainstOutputField(result, fieldDef, prefix, stage));
      }
    }
  }

  return errors;
}

function validateResultAgainstOutputField(result, fieldDef, prefix, stage) {
  const errors = [];
  const fieldType = nonNullJsonType(fieldDef);
  const enumValues = Array.isArray(fieldDef.enum) ? fieldDef.enum : null;
  const itemEnums = Array.isArray(fieldDef.items?.enum) ? fieldDef.items.enum : null;
  const usesParamOptions = typeof fieldDef.$param === "string";

  if (fieldType === "string" && (enumValues || usesParamOptions)) {
    if (result.type !== "choices") {
      errors.push({ stage, message: `${prefix}.type must be "choices" for string enum output fields.` });
    }
    if (!Array.isArray(result.value?.choices)) {
      errors.push({ stage, message: `${prefix}.value.choices must be an array.` });
    } else if (enumValues) {
      for (const choice of result.value.choices) {
        if (!enumValues.includes(choice)) {
          errors.push({
            stage,
            message: `${prefix}.value.choices contains ${JSON.stringify(choice)}, not present in outputSchema enum.`,
          });
        }
      }
    }
  } else if (fieldType === "string") {
    if (result.type !== "textarea") {
      errors.push({ stage, message: `${prefix}.type must be "textarea" for free-text string output fields.` });
    }
    if (!Array.isArray(result.value?.text)) {
      errors.push({ stage, message: `${prefix}.value.text must be an array.` });
    }
  } else if (fieldType === "number" || fieldType === "integer") {
    if (result.type !== "number") {
      errors.push({ stage, message: `${prefix}.type must be "number" for numeric output fields.` });
    }
    if (typeof result.value?.number !== "number") {
      errors.push({ stage, message: `${prefix}.value.number must be a number.` });
    }
    if (fieldType === "integer" && !Number.isInteger(result.value?.number)) {
      errors.push({ stage, message: `${prefix}.value.number must be an integer.` });
    }
  } else if (fieldType === "boolean") {
    if (result.type !== "choices") {
      errors.push({ stage, message: `${prefix}.type must be "choices" for boolean output fields.` });
    }
    if (!Array.isArray(result.value?.choices)) {
      errors.push({ stage, message: `${prefix}.value.choices must be an array.` });
    }
  } else if (fieldType === "array" && (itemEnums || usesParamOptions)) {
    if (result.type !== "choices") {
      errors.push({ stage, message: `${prefix}.type must be "choices" for enum array output fields.` });
    }
    if (!Array.isArray(result.value?.choices)) {
      errors.push({ stage, message: `${prefix}.value.choices must be an array.` });
    } else if (itemEnums) {
      for (const choice of result.value.choices) {
        if (!itemEnums.includes(choice)) {
          errors.push({
            stage,
            message: `${prefix}.value.choices contains ${JSON.stringify(choice)}, not present in outputSchema items enum.`,
          });
        }
      }
    }
  } else if (fieldType === "array") {
    const itemType = nonNullJsonType(fieldDef.items || {});
    if (itemType === "object" && isPlainObject(result.value)) {
      return errors;
    }
    if (result.type !== "labels" && !Array.isArray(result.value)) {
      errors.push({ stage, message: `${prefix} should serialize non-enum array output as labels or an array value.` });
    }
  }

  return errors;
}

function cloneSerializable(value) {
  if (value === undefined) return undefined;
  try {
    return JSON.parse(JSON.stringify(value));
  } catch (error) {
    throw new Error(`Value is not JSON-serializable: ${errorMessage(error)}`);
  }
}

function isJsonSerializable(value) {
  try {
    cloneSerializable(value);
    return true;
  } catch (_error) {
    return false;
  }
}

function compile(source) {
  const { code } = transform(source, {
    transforms: ["jsx"],
    jsxRuntime: "classic",
    production: true,
  });
  const lastParenIdx = code.lastIndexOf("\n(");
  if (lastParenIdx !== -1) {
    return `${code.slice(0, lastParenIdx)}\nreturn ${code.slice(lastParenIdx + 1)}`;
  }
  return `return (function() { ${code} })()`;
}

function getScriptPaths() {
  const validatorDir = dirname(fileURLToPath(import.meta.url));
  return {
    react: join(validatorDir, "node_modules", "react", "umd", "react.development.js"),
    reactDom: join(validatorDir, "node_modules", "react-dom", "umd", "react-dom.development.js"),
  };
}

function getBrowserHarnessSource() {
  return String(function installScenarioHarness(compiledBody, scenario) {
  function getField(obj, path) {
    if (!obj || typeof obj !== "object" || !path) return undefined;
    return String(path)
      .split(".")
      .reduce((value, key) => (value && typeof value === "object" ? value[key] : undefined), obj);
  }

  function clone(value) {
    if (value === undefined) return undefined;
    return JSON.parse(JSON.stringify(value));
  }

  if (!window.React || !window.ReactDOM) {
    throw new Error("React and ReactDOM must be loaded before installing the scenario harness.");
  }

  const factory = new Function(
    "React",
    "useState",
    "useRef",
    "useEffect",
    "useCallback",
    "useMemo",
    "getField",
    "EditorUI",
    compiledBody,
  );
  const mod = factory(
    window.React,
    window.React.useState,
    window.React.useRef,
    window.React.useEffect,
    window.React.useCallback,
    window.React.useMemo,
    getField,
    {},
  );

  if (!mod || typeof mod !== "object") {
    throw new Error("Interface module did not return an object.");
  }
  if (typeof mod.default !== "function") {
    throw new Error("Interface module is missing a default function component.");
  }
  if (typeof mod.getResults !== "function") {
    throw new Error("Interface module must export getResults for scenario validation.");
  }
  if (typeof mod.parseResults !== "function") {
    throw new Error("Interface module must export parseResults for scenario validation.");
  }

  let regions = clone(scenario.initialRegions) || [];
  let relations = clone(scenario.initialRelations) || [];
  let selectedRegionIds = new Set(scenario.selectedRegionIds || []);
  const rootElement = document.getElementById("root");
  const root = window.ReactDOM.createRoot(rootElement);

  function replaceRegion(id, patch) {
    regions = regions.map((region) => (region.id === id ? { ...region, ...patch } : region));
  }

  function render() {
    const props = {
      task: clone(scenario.task) || { id: "scenario-task", data: {} },
      regions,
      relations,
      selectedRegionIds,
      readOnly: Boolean(scenario.readOnly),
      params: clone(scenario.params) || {},
      settings: clone(scenario.settings) || {},
      interfaces: new Set(scenario.interfaces || []),
      initialResults: clone(scenario.initialResults) || [],
      addRegion(region) {
        const nextRegion = { ...clone(region), id: region?.id || `region-${Date.now()}` };
        regions = [...regions, nextRegion];
        if (nextRegion.selected) selectedRegionIds = new Set([nextRegion.id]);
        render();
        return nextRegion;
      },
      updateRegion(id, patch) {
        replaceRegion(id, clone(patch) || {});
        render();
      },
      deleteRegion(id) {
        regions = regions.filter((region) => region.id !== id);
        selectedRegionIds.delete(id);
        selectedRegionIds = new Set(selectedRegionIds);
        render();
      },
      selectRegion(id) {
        selectedRegionIds = id ? new Set([id]) : new Set();
        regions = regions.map((region) => ({ ...region, selected: region.id === id }));
        render();
      },
      addRelation(relation) {
        const nextRelation = { ...clone(relation), id: relation?.id || `relation-${Date.now()}` };
        relations = [...relations, nextRelation];
        render();
        return nextRelation;
      },
      deleteRelation(id) {
        relations = relations.filter((relation) => relation.id !== id);
        render();
      },
      rotateRelationDirection(id) {
        relations = relations.map((relation) => {
          if (relation.id !== id) return relation;
          return { ...relation, direction: relation.direction === "right" ? "left" : "right" };
        });
        render();
      },
      toggleRegionVisibility(id) {
        replaceRegion(id, { hidden: !regions.find((region) => region.id === id)?.hidden });
        render();
      },
      toggleRegionLock(id) {
        replaceRegion(id, { locked: !regions.find((region) => region.id === id)?.locked });
        render();
      },
    };

    if (window.ReactDOM.flushSync) {
      window.ReactDOM.flushSync(() => root.render(window.React.createElement(mod.default, props)));
    } else {
      root.render(window.React.createElement(mod.default, props));
    }
  }

  window.__hsScenario = {
    getState() {
      return clone({
        regions,
        relations,
        selectedRegionIds: Array.from(selectedRegionIds),
      });
    },
    getResults() {
      return clone(mod.getResults(regions, relations));
    },
    parseResults(results) {
      return clone(mod.parseResults(clone(results)));
    },
    setParsed(parsed) {
      const nextParsed = clone(parsed) || {};
      regions = Array.isArray(nextParsed.regions) ? nextParsed.regions : [];
      relations = Array.isArray(nextParsed.relations) ? nextParsed.relations : [];
      selectedRegionIds = new Set();
      render();
      return this.getState();
    },
    getOutputSchema() {
      return clone(mod.outputSchema || null);
    },
    getExports() {
      return Object.keys(mod);
    },
  };

  render();
  return window.__hsScenario.getExports();
  });
}

function nonNullJsonType(fieldDef) {
  const type = fieldDef?.type ?? "string";
  if (Array.isArray(type)) return type.find((entry) => entry !== "null") || "string";
  return type;
}

function stripGeneratedIds(value) {
  if (Array.isArray(value)) return value.map(stripGeneratedIds);
  if (isPlainObject(value)) {
    return Object.fromEntries(
      Object.entries(value)
        .filter(([key]) => key !== "id")
        .map(([key, entry]) => [key, stripGeneratedIds(entry)])
        .sort(([left], [right]) => left.localeCompare(right)),
    );
  }
  return value;
}

function deepEqual(left, right) {
  return stableStringify(left) === stableStringify(right);
}

function stableStringify(value) {
  return JSON.stringify(stable(value));
}

function stable(value) {
  if (Array.isArray(value)) return value.map(stable);
  if (isPlainObject(value)) {
    return Object.fromEntries(Object.entries(value).sort(([left], [right]) => left.localeCompare(right)).map(([key, entry]) => [key, stable(entry)]));
  }
  return value;
}

function isPlainObject(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function describe(value) {
  if (value === null) return "null";
  if (Array.isArray(value)) return "array";
  return typeof value;
}

function errorMessage(error) {
  return error instanceof Error ? error.message : String(error);
}
