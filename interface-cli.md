# Interface CLI Guide

The Label Studio SDK includes an `interface` CLI group for building, validating, previewing, and syncing interfaces from local JSX modules.

Interfaces are Enterprise-only in Label Studio. The CLI can still scaffold and validate files locally, but syncing, previewing, and project creation require an Enterprise instance with the interfaces API enabled.

## Prerequisites

- Python package: `label-studio-sdk`
- Node.js and npm on `PATH`
- A Label Studio Enterprise URL and API token for server operations

Set the server configuration once per shell:

```bash
export LABEL_STUDIO_URL="https://app.humansignal.com"
export LABEL_STUDIO_API_KEY="YOUR_API_KEY"
```

You can pass `--lse-url` and `--token` to individual commands instead of using environment variables.

Check local setup:

```bash
label-studio-sdk interface doctor
```

The first validation or doctor run installs the Node validator dependencies into a user cache directory.

## Quick Start

Create a starter interface:

```bash
label-studio-sdk interface init ./sentiment-interface
cd sentiment-interface
```

Validate the interface statically and run its browser scenario:

```bash
label-studio-sdk interface validate Screen.jsx --scenario scenarios.js
```

Open the live playground and sync local file changes as you edit:

```bash
label-studio-sdk interface preview Screen.jsx --task task.json
```

Create or update a saved interface in Label Studio:

```bash
label-studio-sdk interface sync Screen.jsx \
  --title "Sentiment Review" \
  --workspace 3
```

Create a project that uses the synced interface:

```bash
label-studio-sdk interface start Screen.jsx \
  --project-title "Sentiment Review Project" \
  --workspace 3
```

## Interface Module Shape

An interface file is a JSX module whose final expression returns an object. The object must include a default function component.

```jsx
function Screen({ task, regions, setRegions, params }) {
  return <div>{task.data.text}</div>;
}

function getResults(regions) {
  return regions;
}

function parseResults(results) {
  return { regions: results };
}

({
  default: Screen,
  getResults,
  parseResults,
  inputSchema: {
    type: "object",
    properties: {
      text: { type: "dataField", default: "text" },
    },
  },
  outputSchema: {
    type: "object",
    properties: {
      sentiment: { type: "string", enum: ["Positive", "Negative"] },
    },
  },
  paramsSchema: {
    type: "object",
    properties: {
      mode: { type: "string", default: "review" },
    },
  },
});
```

Important exports:

- `default`: required React function component.
- `getResults(regions, relations)`: serializes interface state into Label Studio annotation results.
- `parseResults(results)`: deserializes Label Studio annotation results into `{ regions: [...] }`.
- `inputSchema`: declares task data fields used by the interface.
- `outputSchema`: declares fields produced by the interface and used by Prompter-style auto-labeling.
- `paramsSchema`: declares per-project configuration passed into the component as `params`.
- `regionSchema`: optional schema metadata for custom region shapes.
- `specVersion`: optional numeric compatibility marker.

The CLI compiles JSX with the classic React runtime. Do not use `import` statements in the interface file; use globals provided by the Label Studio interface runtime, such as `React`, hooks, `getField`, and `EditorUI`.

## Command Reference

### `init`

Scaffold a starter `Screen.jsx`, `task.json`, and `scenarios.js`.

```bash
label-studio-sdk interface init ./my-interface
label-studio-sdk interface init ./my-interface --force
```

Without `--force`, the command refuses to overwrite existing scaffold files.

### `validate`

Run offline validation.

```bash
label-studio-sdk interface validate Screen.jsx
label-studio-sdk interface validate Screen.jsx --scenario scenarios.js
label-studio-sdk interface validate Screen.jsx --json
```

Static validation checks:

- JSX compilation
- undefined JSX component references
- final module object shape
- schema export shape
- missing optional exports
- `getResults` and `parseResults` smoke tests
- `outputSchema` and `parseResults` consistency

Scenario validation uses Playwright in a minimal React harness. Scenario files must default-export an array of scenario objects:

```js
export default [
  {
    name: "selects a label",
    task: { data: { text: "Example text" } },
    async run({ page }) {
      await page.getByRole("button", { name: "Positive" }).click();
    },
    expect: {
      visibleText: ["Example text"],
      results: [
        {
          from_name: "sentiment",
          type: "choices",
          value: { choices: ["Positive"] },
        },
      ],
    },
  },
];
```

The scenario context includes:

- `page`: the Playwright page.
- `getResults()`: reads serialized annotation results from the harness.
- `parseResults(results)`: calls the interface parser.
- `setParsed(parsed)`: replaces harness state from parsed results.
- `getState()`: reads current harness regions, relations, and selection.
- `getOutputSchema()`: reads the interface `outputSchema`.

### `preview`

Open the Label Studio interface playground and live-sync source changes.

```bash
label-studio-sdk interface preview Screen.jsx --task task.json
label-studio-sdk interface preview Screen.jsx --task task.json --no-open
label-studio-sdk interface preview Screen.jsx --lse-url http://localhost:8080
```

`preview` starts a local file watcher. On each save, it pushes the current source to the playground session. The initial push can include task data from `--task`; later pushes update only the code.

### `sync`

Create or update a saved interface.

```bash
label-studio-sdk interface sync Screen.jsx --title "Review UI"
label-studio-sdk interface sync Screen.jsx --id 12 --message "Tighten parser"
label-studio-sdk interface sync Screen.jsx --workspace-title "Data Science"
label-studio-sdk interface sync Screen.jsx --dry-run
```

By default, `sync`:

- validates and compiles the file
- creates a new interface when no id or sidecar entry exists
- updates the existing interface when `--id` or a sidecar entry is available
- skips upload when the local source hash has not changed
- writes a sidecar file next to the JSX source

Useful options:

- `--id`: update a specific interface id.
- `--title`: set the interface title.
- `--workspace`: use a workspace id for newly created interfaces.
- `--workspace-title`: resolve a workspace by exact title.
- `--no-validate`: skip the validation gate, while still requiring successful compilation.
- `--force`: upload even when hashes match.
- `--dry-run`: print the planned action without writing to the server.
- `--message`: store a history message for the synced version.

### `start`

Sync the interface, create a project that uses it, and open the project data page.

```bash
label-studio-sdk interface start Screen.jsx \
  --project-title "Review Project" \
  --params params.json
```

`--params` must point to a JSON file. The JSON is saved as the project interface params and is passed into the component as `params`.

Useful options:

- `--id`: sync against an existing interface id.
- `--title`: title to use if a new interface is created.
- `--project-title`: project title. Defaults to `<interface title> Project`.
- `--description`: project description.
- `--workspace`: workspace id for the interface and project.
- `--workspace-title`: workspace title for interface creation.
- `--force`: sync even when the source hash is unchanged.
- `--no-open`: create the project without opening a browser.

### `open`

Open a saved interface using the local sidecar file.

```bash
label-studio-sdk interface open Screen.jsx
label-studio-sdk interface open Screen.jsx --no-open
```

Run `sync` first so the sidecar contains the interface id for the selected Label Studio URL.

### `doctor`

Check prerequisites and connectivity.

```bash
label-studio-sdk interface doctor
label-studio-sdk interface doctor --lse-url http://localhost:8080
```

The command checks Node.js, npm, the API token, validator dependency installation, and the configured Label Studio URL.

## Sidecar Files

After a successful `sync`, the CLI writes a sidecar next to the source file:

```text
Screen.jsx.ls-interface.json
```

The sidecar is keyed by Label Studio base URL and stores:

- interface id
- interface title
- workspace id
- source version
- last pushed source hash
- last pushed timestamp

This lets future `sync`, `start`, and `open` commands find the saved interface without requiring `--id`.

## Auth and URL Resolution

For API calls, the CLI resolves configuration in this order:

- explicit command option
- parent CLI context
- environment variables
- default base URL `https://app.humansignal.com`

Token environment variable:

```bash
LABEL_STUDIO_API_KEY
```

Base URL environment variables:

```bash
LABEL_STUDIO_URL
LS_URL
```

Tokens that look like JWTs use `Bearer` authentication. Other tokens use Label Studio `Token` authentication.

## Troubleshooting

`node is required for interface validation`

Install Node.js and make sure `node` is available on `PATH`.

`npm is required to install validator dependencies`

Install npm and rerun `label-studio-sdk interface doctor`.

`source did not compile`

Fix JSX syntax or unsupported module syntax. Interface files are compiled as self-contained JSX snippets, not bundled application modules.

`Module did not return an object`

Make the final expression in the file an object literal wrapped in parentheses, for example `({ default: Screen })`.

`Missing getResults` or `Missing parseResults`

These are warnings during static validation but required for scenario validation. Add both functions when you need reliable save/load behavior.

`no sidecar entry`

Run `label-studio-sdk interface sync Screen.jsx` for the target Label Studio URL, or pass `--id` to commands that support it.

`multiple workspaces titled ...`

Pass `--workspace` with the numeric workspace id instead of `--workspace-title`.
