"""Standalone PFH5 pack reader - no RPFM required.

Lists a .pack file's index and can slice out any file's bytes by index order.
Format established empirically from this project's RPFM-built Movie packs:

  [0:4]    magic 'PFH5'
  [4:28]   6 u32 header fields (variant?, 0, 0, file_count, index_size, timestamp)
  [28:28+index_size]  index entries, each:
                        u32 size
                        u8  flag (0 = stored uncompressed)
                        path bytes, 0x00-terminated (backslash separators)
  [28+index_size:]    data blocks of every entry, contiguous, in index order

Usage:  python parse_pack_pfh5.py <pack path>
"""
import struct
import sys


def parse_bytes(pack):
    assert pack[:4] == b"PFH5", f"not a PFH5 pack: magic {pack[:4]!r}"
    v, z1, z2, file_count, index_size, ts = struct.unpack_from("<6I", pack, 4)
    off, end = 28, 28 + index_size
    entries = []
    while off < end:
        size = struct.unpack_from("<I", pack, off)[0]
        off += 4
        flag = pack[off]
        off += 1
        nul = pack.index(b"\x00", off)
        path = pack[off:nul].decode("utf-8", "replace")
        off = nul + 1
        entries.append({"path": path.replace("\\", "/"), "size": size, "flag": flag})
    assert off == end, f"index walk ended at {off}, expected {end}"
    assert len(entries) == file_count, f"{len(entries)} entries vs header count {file_count}"
    data = end
    for e in entries:
        e["offset"] = data
        data += e["size"]
    assert data == len(pack), f"data walk ends at {data}, file is {len(pack)}"
    return entries


def parse(path):
    with open(path, "rb") as fh:
        pack = fh.read()
    return pack, parse_bytes(pack)


if __name__ == "__main__":
    p, entries = parse(sys.argv[1])
    print(f"{sys.argv[1]}  ({len(p)} bytes, {len(entries)} entries)")
    for e in entries:
        print(f"  {e['size']:>9d}  flag={e['flag']}  @{e['offset']:>9d}  {e['path']}")
