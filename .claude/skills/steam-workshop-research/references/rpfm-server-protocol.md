# Driving the pack editor's headless server

Depth for step 8 of the skill: building, verifying and installing a `.pack` with no GUI,
by driving the editor's own backend over its local WebSocket API. The editor repo carries
this protocol under its `docs/server/` folder — read it there rather than from a blog,
because command names are stable but the docs folder is versioned with the tool.

## Lifecycle

- The desktop UI is only one client. The backend binary (`rpfm_server` on Windows) runs
  standalone and "can do pretty much everything" the UI can.
- Default bind: **`127.0.0.1:45127`**. Endpoints: `/ws` (JSON protocol over WebSocket),
  `/sessions` (REST, lists active sessions), `/mcp` (MCP; 150+ tools, for clients that
  already speak it).
- **The server exits when its last session disconnects.** Either do an entire
  build-verify-install in one session, or restart the binary between steps. A connection
  refused on the next call almost always means the previous client closed and took the
  server with it.
- First run logs a settings-file warning and falls back to defaults; harmless. Extract the
  portable build somewhere that does not require admin rights, or update-file writes fail
  confusingly.

## Message envelope

```json
{ "id": 1, "data": <command> }
```

Responses echo the `id`; match on it. An unsolicited `{"id": 0, …}` handshake message
arrives immediately after connecting (`SessionConnected`) — read and ignore it, or the
first correlated reply is read as garbage.

Serialization follows serde's enum conventions, which makes the command reference
directly readable: unit variant `"Name"`, newtype `{"Name": value}`, tuple
`{"Name": [a, b]}`, struct `{"Name": {field: value}}`.

## Commands for a build-verify-install cycle

| Purpose | Command | Shape |
|---|---|---|
| Select game | `SetGameSelected` | `["warhammer_3", false]` (key, rebuild-dependencies) |
| Empty pack in memory | `NewPack` | bare string `"NewPack"` → `{"String": "<pack_key>"}` |
| Add files from disk | `AddPackedFiles` | `[key, [src…], [ContainerPath…], null]` |
| Set type | `SetPackFileType` | `[key, "Movie"]` → `"Success"` |
| Inspect | `GetPackFileDataForTreeView` | `key` → `{"ContainerInfoVecRFileInfo": [ContainerInfo, [RFileInfo…]]}` |
| Read content back | `GetPackedFileRawData` | `[key, "in/pack/path"]` → `{"VecU8": [bytes…]}` |
| Metadata for paths | `GetPackedFilesInfo` | `[key, ["in/pack/path"]]` — a **paths array** |
| Save | `SavePackAs` | `[key, "C:/out/name.pack"]` → `{"ContainerInfo": {…}}` |
| Create an empty file in the pack | `NewPackedFile` | `[key, "in/pack/path", <NewFile>]` → `"Success"` |
| Write decoded content into a file | `SavePackedFileFromView` | `[key, "in/pack/path", <RFileDecoded>]` → `"Success"` |
| Close | `ClosePack` | `key` → `"Success"` |
| Disconnect | `ClientDisconnecting` | bare string → `"Success"` |

Traps found the hard way:

- **`GetPackedFilesInfo` takes an array of paths.** Passing `null` fails deserialization
  (`invalid type: null, expected a sequence`) and reads like a protocol mismatch rather
  than a parameter mistake. Use `GetPackFileDataForTreeView` for "what is in this pack".
- **`ContainerPath` is a tagged enum, not a string:** `{"File": "script/battle/mod/x.lua"}`
  or `{"Folder": "script/battle"}`. Intermediate folders are created as needed.
- **`NewPack`'s returned key is the in-memory name** (e.g. `new_pack.pack`); it is the
  handle you pass to every later command, and `SavePackAs` is what gives the file its real
  name. Pass the destination path with forward slashes.
- **`GetPackedFileRawData` is the verification primitive.** Hash those bytes against the
  source file before saving, and hash the installed copy after copying. Without it,
  "saved successfully" and "holds the right content" are the same claim.

## Writing a file the tool has no source copy of

`AddPackedFiles` only adds files that already exist on disk in the pack's own encoding. A
table or a localisation file has to be *built* instead, in two steps: `NewPackedFile`
creates the entry, `SavePackedFileFromView` fills it with decoded content in exactly the
shape `DecodePackedFile` returns.

- `NewPackedFile: [pack_key, path, <NewFile>]`. The spec picks the type:
  `{"Loc": "Loc"}` for a localisation file, `{"DB": ["<file name>", "<table name>", <version>]}`
  for a table, `{"Text": ["name.lua", "Lua"]}` for script/text.
- **The request enum and the response enum are named differently, and the request variant
takes less than the response hands back.** Decoding a localisation file answers
  `{"LocRFileInfo": [{"table": …}, RFileInfo]}`, but the save wants `{"Loc": {"table": …}}`.
  Passing the response's name is rejected (`unknown variant 'LocRFileInfo'` — the error lists
the valid set, which is the fastest way to learn it) and passing its two-element tuple is
  rejected as `trailing characters at line 1 column …`. Both failures are *shape*, not
content: when a save is refused, re-shape the payload before touching the data.
- **Decode an existing file of the same type and reuse its `definition`** to get the field
  list right — the vendor's own files are inside `data/local_<lang>.pack`. Hand-writing a
  schema the tool disagrees with is the slow path.
- **Read it back out of the pack and assert the rows round-trip** before installing. A
  content-shaped payload can be accepted and still encode to nothing useful.

### Localisation files (`text/db/<name>__.loc`)

Needed whenever the engine is asked to resolve text by key — an on-screen subtitle, a tooltip
that must be translatable, any UI string. The vendor names these `<name>__.loc` in
`text/db/`; a mod's own file works under that naming. Rows are `key`, `text`, `tooltip`
(`StringU16`, `StringU16`, `Boolean` — `false` for ordinary strings), the decoded object
being:

```json
{"table": {"table_name": "Loc",
  "definition": {"version": 1, "fields": [ …key, text, tooltip… ],
                 "localised_fields": [], "localised_key_order": []},
  "definition_patch": {}, "table_data": [[{"StringU16": "my_key"},
                                            {"StringU16": "My text"},
                                            {"Boolean": false}]], "altered": false}}
```

Keys resolve for the language the game is running in, which is written in plain text at
`<game install>/data/language.txt` (`EN`, `FR`, …). Check it before promising translated
text; otherwise ship the one language the user actually plays in.

## Pack types

`Boot`, `Release`, `Patch`, `Mod`, `Movie`.

- `Mod` — the player-mod type: listed in the launcher, loaded when enabled, order-controlled.
- `Movie` — always-on and hidden from the launcher. **This is the right type for a test
  mod:** drop it in `data/` and the engine loads it with no mod-manager step, which is the
  one part of the workflow no tool can do for the user.
- `Boot` / `Release` / `Patch` — the vendor's own; not for player mods.
- Editor-reserved settings files are written only for `Mod`/`Movie`, so switching type
  later strips them.

## Installing

Copy the `.pack` into `<game install>/data/`. That is the entire install; on a normal
Steam install it needs no elevation. Local packs sit alongside the vendor packs and the
per-mod folders under `steamapps/workshop/content/<appid>/`, and a third-party mod manager
may keep its own enabled-mod list elsewhere — none of which is required for a `Movie` test
pack.

## Reading a pack you did not build

The same session opens any `.pack` — third-party mods included — which is how you settle
"what does that mod actually change?" from its files instead of from its description. This
is usually the cheapest way to answer a mechanism question, because a working mod is a
worked example of the engine API it targets.

1. **Fetch the schema first, once per server lifetime.** `DecodePackedFile` answers
   `{"Error": "Missing or invalid extra data provided: \"schema\""}` until the editor has a
   schema in memory, and a fresh portable install ships an empty schema cache. Send
   `UpdateSchemas` (bare string, returns `"Success"`) and confirm with `IsSchemaLoaded`.
   Until then every table decode fails, indistinguishable from a broken pack.
2. `OpenPackFiles` → `GetPackFileDataForTreeView` → `DecodePackedFile: [key, path, "PackFile"]`.
   Valid data sources are `PackFile`, `GameFiles`, `ParentFiles`, `AssKitFiles`,
   `ExternalFile` — `"Dependency"` is not one and fails deserialization (the error lists the
   valid set, which is the fastest way to learn it).
3. **Decoded DB shape:** the reply key names the type (`DBRFileInfo` for a table) and holds
   `[db, RFileInfo]`; the table object carries `table_name`, `definition.fields` (column names
   and types) and `table_data` — rows as lists of typed cells such as
   `[{"StringU8": "out_of_melee"}, {"StringU8": "<ability key>"}]`. Take columns from
   `definition.fields`, never from a row, and unwrap each cell's single key for its value.
   The rows key is **`table_data`**; a wrong guess (e.g. `rows`) returns an empty list rather
   than an error, so a table that "decoded to 0 rows" is usually your typo, not an empty table.
4. **Extract only after the schema is loaded.** With an empty schema cache,
   `ExtractPackedFiles` wrote tables in the editor's raw binary form (readable only as
   UTF-16 string fragments), not TSV. Decode into memory and write your own TSV when you
   want to diff; treat extraction as the path for scripts, UI files and images.
5. **Judging additive versus replacement — this changes the verdict completely.** A table
   file named anything other than `data__` is a **table fragment**: its rows are merged into
   the vendor's table, with conflicts settled by filename order (`!` sorts ahead of letters,
   which is what the leading `!`/`!!` in these filenames is for). A file named exactly
   `data__` **replaces** the table wholesale. So a mod shipping 400 flag rows under its own
   name is *adding* them, while the same 400 rows named `data__` would be deleting hundreds
   of vendor rules — and a naive row-set diff reads the second case as "removed 569 rows".
   Check the filenames before reporting that a mod deletes vendor behaviour.
   **Normalise before diffing:** the editor's TSV export writes `34.0000` and `true` where a
   decoded table gives `34.0` and `True`, so a raw string comparison reports every row as
   changed and buries the handful that actually differ. Compare numbers as floats and
   booleans lower-cased.
6. **Take the vendor baseline from the installed game, not from a dump repo**, whenever the
   question is whether a given pack is unusual: `data/db.pack` →
   `db/<table>_tables/data__` is the authoritative current copy, and a community dump may lag
   a patch. The vendor's UI layouts are the exception worth knowing: they live in
   `data/ui3.pack` as `ui/<area>/<name>.twui.xml`, while `ui.pack`/`ui2.pack` hold images only.

### Surveying many packs for a symbol, without opening any of them

For "has any of the mods I own ever used <engine call/event>?" a raw byte scan is enough and
costs no session: pack **paths are stored uncompressed** in the index, and third-party script
text usually is too, so `grep -a` sees both.

```bash
for p in "<game>/steamapps/workshop/content/<appid>"/*/*.pack; do
  printf "%-50s %8s KB | add_listener: %-4s | LClickUp: %-4s | RClickUp: %s\\n" \\
    "$(basename "$p")" "$(( $(stat -c%s "$p") / 1024 ))" \\
    "$(grep -a -c add_listener "$p")" \\
    "$(grep -a -c ComponentLClickUp "$p")" \\
    "$(grep -a -c ComponentRClickUp "$p")"
done
```

Always include a **control symbol** you know at least one pack contains (`add_listener`,
`ComponentLClickUp`): a row of zeros means nothing if every row is zero, and that is the
difference between "no mod uses it" and "my scan cannot see into these packs". State the limit
plainly — a pack whose scripts are compressed matches neither, so its silence is inconclusive —
and report the result as "in the mods on this machine", not "nobody uses it". The same scan is
the cheap way to ask what a 200 MB overhaul actually does before spending a session decoding it.

## Re-runnable implementation

`scripts/build_and_install_pack.py` takes `--add SRC=IN_PACK` (repeatable), `--out`,
`--game`, `--type` and `--install-dir`; it builds, verifies every file byte-for-byte out of
 the pack, saves, installs, and refuses to write anything if a content check fails. Run it
with the `websockets` package available (e.g. `uv run --with websockets python …`) and the
server already running.
