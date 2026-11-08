#!/usr/bin/env python3
"""Build a Total War .pack with the pack editor's headless server, verify, install.

Start the editor's backend first (it exits when its last session disconnects):

    <rpfm-dir>/rpfm_server.exe

Then, e.g. for a battle-script test mod:

    uv run --quiet --with websockets python build_and_install_pack.py \\
        --add mod.lua=script/battle/mod/zz_my_mod.lua \\
        --out build/zz_my_mod.pack \\
        --game warhammer_3 --type Movie \\
        --install-dir "C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III/data"

Every file is read back *out of the pack* and hashed against its source before anything is
saved, and the installed copy is hashed against the built pack. A pack that "saves" is not
evidence that it holds the right bytes, and the failure mode is a silent in-game no-op.

Type `Movie` is loaded from data/ unconditionally and hidden from the launcher, so a test
mod needs no mod-manager step. Use `Mod` when the user should be able to toggle it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys

DEFAULT_URL = "ws://127.0.0.1:45127/ws"


try:
    from websockets.sync.client import connect
except ImportError:  # pragma: no cover - dependency hint beats a traceback
    sys.exit(
        "needs the websockets package, e.g.:\n"
        f"    uv run --with websockets python {os.path.basename(__file__)} ..."
    )


class RpfmClient:
    """Minimal client for the editor server's WebSocket JSON protocol."""

    def __init__(self, url: str) -> None:
        self.ws = connect(url, max_size=None, open_timeout=15)
        self.next_id = 1
        hello = json.loads(self.ws.recv(timeout=15))
        # unsolicited handshake, id 0: SessionConnected
        if hello.get("id") != 0:
            raise RuntimeError(f"unexpected first message from server: {hello}")

    def send(self, command):
        req_id = self.next_id
        self.next_id += 1
        self.ws.send(json.dumps({"id": req_id, "data": command}))
        while True:  # correlated by id; ignore any chatter
            message = json.loads(self.ws.recv(timeout=180))
            if message.get("id") == req_id:
                return message.get("data")

    def close(self) -> None:
        try:
            self.send("ClientDisconnecting")
        except Exception:
            pass  # the server exits on its own once no sessions remain
        try:
            self.ws.close()
        except Exception:
            pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def md5_file(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.md5(handle.read()).hexdigest()


def parse_add(spec: str):
    source, sep, in_pack = spec.partition("=")
    if not sep or not source or not in_pack:
        raise argparse.ArgumentTypeError(f"--add expects SOURCE=IN_PACK_PATH, got {spec!r}")
    return os.path.abspath(source), in_pack


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--add",
        action="append",
        type=parse_add,
        required=True,
        metavar="SRC=IN_PACK",
        help="file to pack and its path inside the pack; repeatable",
    )
    parser.add_argument("--out", required=True, help="path of the .pack to write")
    parser.add_argument("--game", default="warhammer_3", help="editor game key (default: warhammer_3)")
    parser.add_argument(
        "--type", default="Movie", choices=["Movie", "Mod"], help="pack type (default: Movie)"
    )
    parser.add_argument(
        "--install-dir", help="the game's data/ folder; copies the pack there and verifies"
    )
    parser.add_argument("--url", default=DEFAULT_URL, help=f"server WebSocket (default: {DEFAULT_URL})")
    args = parser.parse_args()

    missing = [src for src, _ in args.add if not os.path.isfile(src)]
    if missing:
        sys.exit(f"missing source file(s): {missing}")

    out_path = os.path.abspath(args.out)

    client = RpfmClient(args.url)
    try:
        print("game       ->", client.send({"SetGameSelected": [args.game, False]}))
        pack_key = client.send("NewPack")["String"]
        print("pack key   ->", pack_key)

        print(
            "add files  ->",
            client.send(
                {
                    "AddPackedFiles": [
                        pack_key,
                        [src for src, _ in args.add],
                        [{"File": in_pack} for _, in_pack in args.add],
                        None,
                    ]
                }
            ),
        )
        print("pack type  ->", client.send({"SetPackFileType": [pack_key, args.type]}))

        # Verify content by reading it back out of the pack, not by trusting the save.
        mismatches = []
        for src, in_pack in args.add:
            packed = bytes(client.send({"GetPackedFileRawData": [pack_key, in_pack]})["VecU8"])
            with open(src, "rb") as handle:
                source_bytes = handle.read()
            same = len(packed) == len(source_bytes) and sha256(packed) == sha256(source_bytes)
            print(f"  verify   {in_pack}: {len(packed)} bytes, identical={same}")
            if not same:
                mismatches.append(in_pack)
        if mismatches:
            sys.exit(f"content mismatch in {mismatches} - nothing saved, nothing installed")

        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        if os.path.exists(out_path):
            os.remove(out_path)
        print("save       ->", client.send({"SavePackAs": [pack_key, out_path.replace(os.sep, "/")]}))
        client.send({"ClosePack": pack_key})
    finally:
        client.close()

    print(f"built      {out_path} ({os.path.getsize(out_path)} bytes)")

    if args.install_dir:
        target = os.path.join(args.install_dir, os.path.basename(out_path))
        shutil.copy2(out_path, target)
        identical = md5_file(out_path) == md5_file(target)
        print(f"installed  {target} (md5 identical={identical})")
        if not identical:
            sys.exit("installed copy differs from the built pack")
        if args.type == "Mod":
            print("note: a Mod pack still has to be enabled in the user's launcher.")
        else:
            print("note: a Movie pack is loaded as-is - no mod-manager step needed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
