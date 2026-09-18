# Interface CLI Guide

The Label Studio SDK includes an `interface` CLI group for building, validating, previewing, and syncing interfaces from local JSX modules.

Interfaces are Enterprise-only in Label Studio. The CLI can still scaffold and validate files locally. Syncing and
project creation require an Enterprise instance with the interfaces API enabled. Preview needs an Enterprise instance
only to download its version-compatible browser artifact on first use and when revalidating the cache.

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
label-studio-sdk interface validate .
```

Open the live playground and sync local file changes as you edit:

```bash
label-studio-sdk interface preview .
```

Pull an existing interface and continue locally:

```bash
label-studio-sdk interface pull --id 73 ./existing-interface
cd existing-interface
```

Create or update a saved interface in Label Studio. By default, this creates a local draft version:

```bash
label-studio-sdk interface sync Screen.jsx \
  --title "Sentiment Review" \
  --workspace 3
```

Create a project that uses the synced interface:

```bash
label-studio-sdk interface start . \
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
label-studio-sdk interface validate ./my-interface
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

Start the local interface playground and live-sync source changes.

```bash
label-studio-sdk interface preview ./my-interface
label-studio-sdk interface preview Screen.jsx --task task.json
label-studio-sdk interface preview Screen.jsx --task task.json --no-open
label-studio-sdk interface preview Screen.jsx --lse-url http://localhost:8080
label-studio-sdk interface preview Screen.jsx --offline
```

`preview` downloads the version-compatible playground and sandbox artifacts from the configured Label Studio instance,
verifies them, and stores them in an origin- and protocol-scoped user cache. The first uncached run requires
`LABEL_STUDIO_API_KEY`; the CLI sends it with the same `Token` or `Bearer` authentication used by other SDK commands.
Before downloading public static assets, it probes `GET /api/current-user/whoami` and fails closed on `401`/`403` when
no verified cache exists. It never retries an authenticated asset request anonymously.

The CLI then starts two listeners bound only to `127.0.0.1`: one hosts the playground and localhost SSE file updates;
the other hosts the isolated sandbox shell. Both use unguessable capability paths. The API token is used only by the
CLI during artifact bootstrap and is never placed in browser JavaScript, HTML, query parameters, or local storage.
Treat the printed capability URL as workstation-local sensitive data and do not publish it. This preview layer does
not expose a Save gateway or proxy Label Studio API requests.

Pass a directory to use the scaffolded bundle defaults: `Screen.jsx` for the interface and `task.json` or `sample.json`
for example task data. Source and task saves travel over localhost SSE only—there is no Django playground stream,
Redis, Streamer, WebSocket, long poll, or long-lived Label Studio request.

On later starts, the CLI makes a short authenticated manifest revalidation request. If Label Studio is unreachable or
returns an authentication error and a verified cache exists, preview starts from that cache and prints a stale-artifact
warning. `--offline` skips all network access and requires an existing verified cache. A protocol mismatch fails before
the browser opens. The server's selected artifact path does not change during the process; cache cleanup retains the
active snapshot and one prior snapshot.

View-Only users cannot mint the PAT needed for first-run bootstrap. Cookie SSO, OAuth proxies, and IAP browser bootstrap
are out of scope; allow access to `/react-app/local-playground/` and `/react-app/editor-standalone/`, or populate the
cache from a reachable instance. Cached live preview still works without a token. `validate` remains fully local, while
`sync`, `pull`, and `start` remain authenticated server operations.

### `sync`

Create or update a saved interface. `sync` creates an unpublished local draft by default so you can review it in Label Studio before publishing.

```bash
label-studio-sdk interface sync Screen.jsx --title "Review UI"
label-studio-sdk interface sync Screen.jsx --id 12 --message "Tighten parser"
label-studio-sdk interface sync Screen.jsx --id 12 --publish
label-studio-sdk interface sync Screen.jsx --workspace-title "Data Science"
label-studio-sdk interface sync Screen.jsx --dry-run
```

By default, `sync`:

- validates and compiles the file
- creates a new interface when no id or sidecar entry exists
- updates the existing interface when `--id` or a sidecar entry is available
- appends a new draft version without replacing existing versions
- skips upload when the local source hash has not changed
- writes a sidecar file next to the JSX source

Useful options:

- `--id`: update a specific interface id.
- `--title`: set the interface title.
- `--workspace`: use a workspace id for newly created interfaces.
- `--workspace-title`: resolve a workspace by exact title.
- `--publish`: create a published version instead of a local draft.
- `--no-validate`: skip the validation gate, while still requiring successful compilation.
- `--force`: upload even when hashes match.
- `--dry-run`: print the planned action without writing to the server.
- `--message`: store a history message for the synced version.

### `pull`

Pull a saved interface into a local bundle.

```bash
label-studio-sdk interface pull --id 12 ./review-ui
label-studio-sdk interface pull --id 12 --version 4 ./review-ui
label-studio-sdk interface pull --id 12 ./review-ui --force
```

`pull` writes `Screen.jsx`, `task.json`, optional `params.json` defaults from `paramsSchema`, and a sidecar file. Without `--version`, it pulls the latest version, including local drafts.

### `start`

Sync the interface, create a project that uses it, and open the project data page.

```bash
label-studio-sdk interface start Screen.jsx \
  --project-title "Review Project" \
  --params params.json
```

`start` syncs a published version so the new project can safely reference it. `--params` must point to a JSON file. The JSON is saved as the project interface params and is passed into the component as `params`.
When you pass a directory, `start` uses `Screen.jsx` for the interface and `params.json` for project params when present.

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

The command checks Node.js, npm, the API token, validator dependencies, LSE reachability, and API authentication
separately. It also reports the preview cache path, origin key, protocol, artifact fingerprint, and last successful
fetch.

## Sidecar Files

After a successful `sync` or `pull`, the CLI writes a sidecar next to the source file:

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

This lets future `preview`, `sync`, `start`, and `open` commands find the saved interface without requiring `--id`.
Preview includes the matching-origin ID in local file-update events. A sidecar source version can point at a draft
version until you publish it.

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

## Preview diagnostics

`label-studio-sdk interface doctor` reports the local preview protocol and whether a verified artifact exists for the
configured canonical Label Studio origin. Reachability, API authentication, validator setup, and preview cache health
are separate checks so an unreachable server does not make a valid offline cache appear corrupt.

Preview's cache is stored in the platform user cache directory under `label-studio-sdk/interface-preview`. Cache slots
are keyed by canonical origin (scheme, host, and port) and local protocol version; artifacts from different Label Studio
instances or protocol majors are never mixed.

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

`offline preview requires a verified cache`

Run preview once without `--offline` against a reachable Label Studio Enterprise instance using a valid API key.

`preview protocol mismatch`

The installed SDK and the configured Label Studio instance do not share a local-preview protocol. Update the older side
before retrying; the CLI will not serve an incompatible cached artifact.

`failed to download preview assets and no verified cache exists`

Confirm the instance includes `/react-app/local-playground/manifest.json`, that the API key is valid, and that any
fronting proxy allows the local-playground and editor-standalone static paths.

`multiple workspaces titled ...`

Pass `--workspace` with the numeric workspace id instead of `--workspace-title`.
