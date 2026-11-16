#!/usr/bin/env bun
/**
 * Bundles the pure `window.InterfaceComponents` helper modules referenced by
 * `services/lse/web/apps/labelstudio/src/pages/Interfaces/host-interface-components.ts`
 * into a standalone, zero-dependency, Node-safe ESM file (`interface-components-shim.mjs`)
 * for offline SDK CLI validation (`validate.mjs`).
 *
 * Regenerate from anywhere inside the hs-platform monorepo with:
 *   bun libs/lso-client-generator/fern/.preview/fern-python-sdk/src/label_studio_sdk/_extensions/interface/validator/build-interface-components-shim.mjs
 */

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function findMonorepoRoot(startDir) {
  let current = path.resolve(startDir);
  while (true) {
    const icPkg = path.join(current, "services/lse/web/libs/interface-components/src");
    if (fs.existsSync(icPkg)) {
      return current;
    }
    const parent = path.dirname(current);
    if (parent === current) {
      throw new Error("Could not locate hs-platform monorepo root from " + startDir);
    }
    current = parent;
  }
}

const repoRoot = findMonorepoRoot(__dirname);
const icSrc = path.join(repoRoot, "services/lse/web/libs/interface-components/src");
const outFile = path.join(__dirname, "interface-components-shim.mjs");

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "ls-ic-shim-"));

const reactStubPath = path.join(tmpDir, "react-stub.mjs");
fs.writeFileSync(
  reactStubPath,
  [
    "export const useState = (init) => [typeof init === 'function' ? init() : init, () => {}];",
    "export const useReducer = (reducer, init) => [init, () => {}];",
    "export const useCallback = (fn) => fn;",
    "export const useMemo = (fn) => fn();",
    "export const useRef = (init) => ({ current: init });",
    "export const useEffect = () => {};",
    "export const useLayoutEffect = () => {};",
    "export const useId = () => 'id';",
    "export const createContext = (def) => ({ Provider: () => null, Consumer: () => null, _currentValue: def });",
    "export const useContext = (ctx) => ctx?._currentValue;",
    "export const forwardRef = (fn) => fn;",
    "export const memo = (fn) => fn;",
    "export const createElement = () => null;",
    "export const cloneElement = () => null;",
    "export const createRef = () => ({ current: null });",
    "export const Children = { map: () => [], forEach: () => {}, count: () => 0, toArray: () => [] };",
    "export const useDeferredValue = (v) => v;",
    "export const useTransition = () => [false, (fn) => fn()];",
    "export const useImperativeHandle = () => {};",
    "export const useSyncExternalStore = (_sub, getSnap) => getSnap();",
    "export class Component {}",
    "export class PureComponent {}",
    "export const Fragment = 'Fragment';",
    "export const jsx = () => null;",
    "export const jsxs = () => null;",
    "export const jsxDEV = () => null;",
    "export default { useState, useReducer, useCallback, useMemo, useRef, useEffect, useLayoutEffect, useId, createContext, useContext, forwardRef, memo, createElement, cloneElement, createRef, Children, Fragment, Component, PureComponent };",
  ].join("\n"),
  "utf8",
);

const workerUrlStubPath = path.join(tmpDir, "worker-url-stub.mjs");
fs.writeFileSync(workerUrlStubPath, 'export default "";\n', "utf8");

const uiInternalsStubPath = path.join(tmpDir, "ui-internals-stub.mjs");
fs.writeFileSync(
  uiInternalsStubPath,
  [
    "export const Badge = () => null;",
    "export const cn = (...args) => args.filter(Boolean).join(' ');",
  ].join("\n"),
  "utf8",
);

const entryPath = path.join(tmpDir, "shim-entry.ts");
fs.writeFileSync(
  entryPath,
  `import * as labelPickerModel from "@humansignal/interface-components/components/LabelPicker/labelModel";
import * as answerFormLsResults from "@humansignal/interface-components/components/AnswerForm/lsResults";
import * as answerFormModel from "@humansignal/interface-components/components/AnswerForm/model";
import * as relationResults from "@humansignal/interface-components/shared/regions/relationResults";
import * as audioLsResults from "@humansignal/interface-components/components/AudioCanvas/lsResults";
import * as audioRegion from "@humansignal/interface-components/components/AudioCanvas/audioRegion";
import * as collectionSubmission from "@humansignal/interface-components/components/CollectionUploader/submission";
import * as choiceLsResults from "@humansignal/interface-components/components/ChoiceGroup/lsResults";
import * as choiceResultBase from "@humansignal/interface-components/components/ChoiceGroup/resultBase";
import * as dateTimeLsResults from "@humansignal/interface-components/components/DateTimeInput/lsResults";
import * as dateTimeFormat from "@humansignal/interface-components/components/DateTimeInput/dateFormat";
import * as documentLsResults from "@humansignal/interface-components/components/DocumentCanvas/lsResults";
import * as imageLsResults from "@humansignal/interface-components/components/ImageCanvas/lsResults";
import * as imageRegionUtils from "@humansignal/interface-components/components/ImageCanvas/regionUtils";
import * as imagePose from "@humansignal/interface-components/components/ImageCanvas/pose";
import * as imageCuboid from "@humansignal/interface-components/components/ImageCanvas/cuboid";
import * as imagePolygonTopology from "@humansignal/interface-components/components/ImageCanvas/polygonTopology";
import * as numberLsResults from "@humansignal/interface-components/components/NumberInput/lsResults";
import * as pairwiseLsResults from "@humansignal/interface-components/components/PairwiseRanker/lsResults";
import * as rankerLsResults from "@humansignal/interface-components/components/RankerBoard/lsResults";
import * as rankerModel from "@humansignal/interface-components/components/RankerBoard/rankerModel";
import * as ratingLsResults from "@humansignal/interface-components/components/RatingControl/lsResults";
import * as taxonomyLsResults from "@humansignal/interface-components/components/TaxonomyTree/lsResults";
import * as textCanvasLsResults from "@humansignal/interface-components/components/TextCanvas/lsResults";
import * as textInputLsResults from "@humansignal/interface-components/components/TextInput/lsResults";
import * as timeSeriesLsResults from "@humansignal/interface-components/components/TimeSeriesCanvas/lsResults";
import * as timeSeriesData from "@humansignal/interface-components/components/TimeSeriesCanvas/data";
import * as scene3DLsResults from "@humansignal/interface-components/components/Scene3DCanvas/lsResults";
import * as scene3DDocument from "@humansignal/interface-components/components/Scene3DCanvas/sceneDocument";
import * as scene3DHost from "@humansignal/interface-components/components/Scene3DCanvas/host";
import * as scene3DGeometry from "@humansignal/interface-components/components/Scene3DCanvas/geometry";
import * as videoLsResults from "@humansignal/interface-components/components/VideoCanvas/lsResults";
import * as videoNormalize from "@humansignal/interface-components/components/VideoCanvas/normalize";
import * as frameMetadata from "@humansignal/interface-components/shared/media/frameMetadata";
import * as temporalSpatial from "@humansignal/interface-components/shared/temporal/spatial";
import * as multiViewAssociation from "@humansignal/interface-components/shared/media/multiView/association";

type Namespace = Record<string, unknown>;

const HELPER_MODULES: Record<string, Namespace[]> = {
  LabelPicker: [labelPickerModel],
  AnswerForm: [answerFormLsResults, answerFormModel, relationResults],
  AudioCanvas: [audioLsResults, audioRegion, relationResults],
  CollectionUploader: [collectionSubmission],
  ChoiceGroup: [choiceLsResults, choiceResultBase],
  DateTimeInput: [dateTimeLsResults, dateTimeFormat],
  DocumentCanvas: [documentLsResults, relationResults],
  ImageCanvas: [
    imageLsResults,
    imageRegionUtils,
    imagePose,
    imageCuboid,
    imagePolygonTopology,
    relationResults,
  ],
  NumberInput: [numberLsResults],
  PairwiseRanker: [pairwiseLsResults],
  RankerBoard: [rankerLsResults, rankerModel],
  RatingControl: [ratingLsResults],
  TaxonomyTree: [taxonomyLsResults],
  TextCanvas: [textCanvasLsResults],
  TextInput: [textInputLsResults],
  TimeSeriesCanvas: [timeSeriesLsResults, timeSeriesData, relationResults],
  Scene3DCanvas: [scene3DLsResults, scene3DDocument, scene3DHost, { scene3DGeometry }],
  VideoCanvas: [
    videoLsResults,
    videoNormalize,
    frameMetadata,
    temporalSpatial,
    multiViewAssociation,
    relationResults,
  ],
};

export const HELPER_ENTRY_NAMES: readonly string[] = Object.freeze(Object.keys(HELPER_MODULES));

const PROXY_BUILTINS = new Set([
  "load",
  "isLoaded",
  "getLoaded",
  "createSandboxedWorker",
  "useComponentHotkeys",
  "matchesHotkey",
  "parseHotkeyCombo",
  "isInputElement",
  "resolveAssignedHotkey",
]);

function referencesInterfaceComponents(code: string | null | undefined): boolean {
  if (!code) return false;
  return (
    code.includes("InterfaceComponents") ||
    code.includes("requiredComponents") ||
    code.includes("@humansignal/interface-components")
  );
}

export function detectHostComponentEntries(code: string | null | undefined): string[] {
  if (!referencesInterfaceComponents(code) || !code) return [];
  const all = Object.keys(HELPER_MODULES);
  const topLevel = /\\bInterfaceComponents\\s*\\??\\.\\s*([a-z_$][A-Za-z0-9_$]*)/g;
  let match: RegExpExecArray | null;
  while ((match = topLevel.exec(code)) !== null) {
    if (!PROXY_BUILTINS.has(match[1])) return all;
  }
  const destructureRe = /\\{([^{}]*)\\}\\s*=\\s*(?:(?:window|globalThis)\\s*\\.\\s*)?InterfaceComponents\\b/g;
  while ((match = destructureRe.exec(code)) !== null) {
    const bindings = match[1].split(",").map((part) => part.split(":")[0].split("=")[0].trim());
    if (bindings.some((b) => /^[a-z_$]/.test(b) && !PROXY_BUILTINS.has(b))) {
      return all;
    }
  }
  const matched = all.filter((name) => new RegExp(\`\\\\b\${name}\\\\b\`).test(code));
  return matched.length > 0 ? matched : all;
}

function createComponentStub(displayPath: string, helpers: Namespace = {}): unknown {
  const fn = function ComponentStub() {
    return null;
  };
  Object.defineProperty(fn, "name", { value: displayPath, configurable: true });
  (fn as unknown as Record<string, unknown>).displayName = displayPath;
  for (const [key, val] of Object.entries(helpers)) {
    if (key !== "default" && key !== "__esModule") {
      (fn as unknown as Record<string, unknown>)[key] = val;
    }
  }
  const childCache = new Map<string, unknown>();
  return new Proxy(fn, {
    get(target, prop, receiver) {
      if (typeof prop !== "string") return Reflect.get(target, prop, receiver);
      if (prop in target) return Reflect.get(target, prop, receiver);
      if (/^[A-Z]/.test(prop)) {
        if (!childCache.has(prop)) {
          childCache.set(prop, createComponentStub(\`\${displayPath}.\${prop}\`));
        }
        return childCache.get(prop);
      }
      if (/^use[A-Z]/.test(prop)) {
        return function noopHook() {
          return {};
        };
      }
      return undefined;
    },
  });
}

export function loadHostInterfaceComponentsSync(code: string | null | undefined): Namespace | null {
  const entries = detectHostComponentEntries(code);
  if (!entries.length) return null;

  const byEntry: Record<string, Namespace> = {};
  const target: Namespace = {};

  for (const name of entries) {
    const mods = HELPER_MODULES[name];
    if (!mods) continue;
    const merged: Namespace = {};
    for (const mod of mods) {
      for (const [key, value] of Object.entries(mod)) {
        if (key === "default" || key === "__esModule") continue;
        merged[key] = value;
        if (!(key in target)) {
          target[key] = value;
        }
      }
    }
    byEntry[name] = merged;
  }

  for (const [name, helpers] of Object.entries(byEntry)) {
    target[name] = createComponentStub(name, helpers);
  }

  target.load = (name: string) => Promise.resolve(byEntry[name] ?? null);
  target.isLoaded = (name: string) => name in byEntry;
  target.getLoaded = (name: string) => byEntry[name] ?? null;
  target.useComponentHotkeys = () => {};
  target.matchesHotkey = () => false;
  target.parseHotkeyCombo = (combo: string) => ({ key: String(combo || ""), ctrl: false, meta: false, shift: false, alt: false });
  target.isInputElement = () => false;
  target.resolveAssignedHotkey = (_id: string, fallback?: string) => fallback ?? null;
  target.createSandboxedWorker = () => ({ postMessage() {}, terminate() {}, addEventListener() {}, removeEventListener() {} });

  const stubCache = new Map<string, unknown>();
  return new Proxy(target, {
    get(obj, prop, receiver) {
      if (typeof prop !== "string") return Reflect.get(obj, prop, receiver);
      if (prop in obj) return Reflect.get(obj, prop, receiver);
      if (/^[A-Z]/.test(prop)) {
        if (!stubCache.has(prop)) {
          stubCache.set(prop, createComponentStub(prop));
        }
        return stubCache.get(prop);
      }
      return undefined;
    },
  });
}

export async function loadHostInterfaceComponents(code: string | null | undefined): Promise<Namespace | null> {
  return loadHostInterfaceComponentsSync(code);
}

export function withHostInterfaceComponents<T>(helpers: Namespace | null, fn: () => T): T {
  const root = globalThis as { InterfaceComponents?: unknown; window?: { InterfaceComponents?: unknown } };
  const scopes = root.window && root.window !== (root as unknown) ? [root, root.window] : [root];
  const installed = helpers ? scopes.filter((scope) => scope.InterfaceComponents === undefined) : [];
  for (const scope of installed) scope.InterfaceComponents = helpers;
  try {
    return fn();
  } finally {
    for (const scope of installed) delete scope.InterfaceComponents;
  }
}
`,
  "utf8",
);

try {
  const result = await Bun.build({
    entrypoints: [entryPath],
    target: "node",
    format: "esm",
    minify: true,
    plugins: [
      {
        name: "resolve-monorepo-pure-helpers",
        setup(build) {
          build.onResolve({ filter: /^@humansignal\/interface-components\// }, (args) => {
            const sub = args.path.replace(/^@humansignal\/interface-components\//, "");
            const base = path.join(icSrc, sub);
            for (const ext of [".ts", ".tsx", "/index.ts", ".js"]) {
              if (fs.existsSync(base + ext)) {
                return { path: base + ext };
              }
            }
            return { path: base };
          });
          build.onResolve({ filter: /\?worker/ }, () => ({
            path: workerUrlStubPath,
          }));
          build.onResolve({ filter: /(\/badge\/badge|\/utils\/utils)$/ }, () => ({
            path: uiInternalsStubPath,
          }));
          build.onResolve({ filter: /^@humansignal\/ui$/ }, () => ({
            path: uiInternalsStubPath,
          }));
          build.onResolve({ filter: /^react(\/.*)?$/ }, () => ({
            path: reactStubPath,
          }));
        },
      },
    ],
  });

  if (!result.success) {
    for (const log of result.logs) {
      console.error(log);
    }
    process.exit(1);
  }

  const bundled = await result.outputs[0].text();
  // Bun.build strips `// trufflehog:ignore` comments from Scene3DCanvas's 20-char action id;
  // split the string literal so secret scanners do not misclassify it as an API token.
  const eraserActionId = `${"classification"}${"Eraser"}`;
  const sanitized = bundled.replaceAll(
    JSON.stringify(eraserActionId),
    '("classification"+"Eraser")',
  );
  const header = [
    "// AUTO-GENERATED by build-interface-components-shim.mjs — DO NOT EDIT MANUALLY.",
    "// Pure Node-safe window.InterfaceComponents helper shim for offline SDK CLI validation.",
    "",
  ].join("\n");
  fs.writeFileSync(outFile, header + sanitized, "utf8");
  console.log(`Generated ${outFile} (${Buffer.byteLength(header + sanitized)} bytes)`);
} finally {
  fs.rmSync(tmpDir, { recursive: true, force: true });
}
