r"""memprobe: READ-ONLY memory reader for Warhammer3.exe (feasibility experiment, 2026-11-14).

Opens the game with PROCESS_VM_READ | PROCESS_QUERY_INFORMATION only. It never writes
to the game, never injects anything, never touches game files.

Commands (run with: uv run --with numpy python tools/memprobe/memprobe.py <cmd> ...):
  info                         pid, module base, writable memory size
  scan <int>                   first scan: every 4-byte aligned int32 equal to <int>
  next <int>                   keep candidates whose value is now <int>
  show                         print current candidates and their values
  chain <base_hex> <off_hex>.. follow a Cheat Engine style pointer path, print the value
  chains <file>                same for every line "base o0 o1 ..." in a file
"""
import ctypes
import ctypes.wintypes as wt
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")
CAND = os.path.join(RUNS, "candidates.npy")
EXE = "Warhammer3.exe"

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
TH32CS_SNAPPROCESS = 0x2
TH32CS_SNAPMODULE = 0x8
TH32CS_SNAPMODULE32 = 0x10
MEM_COMMIT = 0x1000
WRITABLE = {0x04, 0x08, 0x40, 0x80}


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ProcessID", wt.DWORD),
                ("th32DefaultHeapID", ctypes.c_size_t), ("th32ModuleID", wt.DWORD),
                ("cntThreads", wt.DWORD), ("th32ParentProcessID", wt.DWORD),
                ("pcPriClassBase", ctypes.c_long), ("dwFlags", wt.DWORD),
                ("szExeFile", ctypes.c_wchar * 260)]


class MODULEENTRY32W(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("th32ModuleID", wt.DWORD), ("th32ProcessID", wt.DWORD),
                ("GlblcntUsage", wt.DWORD), ("ProccntUsage", wt.DWORD),
                ("modBaseAddr", ctypes.c_void_p), ("modBaseSize", wt.DWORD),
                ("hModule", wt.HMODULE), ("szModule", ctypes.c_wchar * 256),
                ("szExePath", ctypes.c_wchar * 260)]


class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", wt.DWORD), ("PartitionId", wt.WORD),
                ("RegionSize", ctypes.c_size_t), ("State", wt.DWORD),
                ("Protect", wt.DWORD), ("Type", wt.DWORD)]


k32.CreateToolhelp32Snapshot.restype = wt.HANDLE
k32.OpenProcess.restype = wt.HANDLE
k32.VirtualQueryEx.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.POINTER(MBI), ctypes.c_size_t]
k32.VirtualQueryEx.restype = ctypes.c_size_t
k32.ReadProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p,
                                  ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]


def find_pid():
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    e = PROCESSENTRY32W(); e.dwSize = ctypes.sizeof(e)
    ok = k32.Process32FirstW(snap, ctypes.byref(e))
    while ok:
        if e.szExeFile.lower() == EXE.lower():
            k32.CloseHandle(snap); return e.th32ProcessID
        ok = k32.Process32NextW(snap, ctypes.byref(e))
    k32.CloseHandle(snap)
    sys.exit("Warhammer3.exe is not running")


def module_base(pid):
    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid)
    e = MODULEENTRY32W(); e.dwSize = ctypes.sizeof(e)
    ok = k32.Module32FirstW(snap, ctypes.byref(e))
    while ok:
        if e.szModule.lower() == EXE.lower():
            k32.CloseHandle(snap); return e.modBaseAddr, e.modBaseSize
        ok = k32.Module32NextW(snap, ctypes.byref(e))
    k32.CloseHandle(snap)
    sys.exit("module not found (error %d)" % ctypes.get_last_error())


class Proc:
    def __init__(self):
        self.pid = find_pid()
        self.h = k32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, self.pid)
        if not self.h:
            sys.exit("OpenProcess failed, error %d" % ctypes.get_last_error())
        self.base, self.size = module_base(self.pid)

    def read(self, addr, n):
        buf = ctypes.create_string_buffer(n); got = ctypes.c_size_t()
        if not k32.ReadProcessMemory(self.h, ctypes.c_void_p(addr), buf, n, ctypes.byref(got)):
            return None
        return buf.raw[:got.value]

    def u64(self, addr):
        b = self.read(addr, 8)
        return None if b is None or len(b) < 8 else int.from_bytes(b, "little")

    def i32(self, addr):
        b = self.read(addr, 4)
        return None if b is None or len(b) < 4 else int.from_bytes(b, "little", signed=True)

    def regions(self):
        addr, m = 0, MBI()
        while k32.VirtualQueryEx(self.h, ctypes.c_void_p(addr), ctypes.byref(m), ctypes.sizeof(m)):
            base = m.BaseAddress or 0
            if m.State == MEM_COMMIT and (m.Protect & 0xFF) in WRITABLE and not (m.Protect & 0x100):
                yield base, m.RegionSize
            addr = base + m.RegionSize
            if addr >= 0x7FFFFFFFFFFF:
                break


def cmd_info(p):
    total = sum(s for _, s in p.regions())
    print("pid %d  module base 0x%X  size 0x%X  writable memory %.2f GB"
          % (p.pid, p.base, p.size, total / 2**30))


def cmd_scan(p, value):
    hits, chunk = [], 64 * 2**20
    for base, size in p.regions():
        off = 0
        while off < size:
            n = min(chunk, size - off)
            b = p.read(base + off, n)
            if b:
                arr = np.frombuffer(b[: len(b) // 4 * 4], dtype="<i4")
                idx = np.nonzero(arr == value)[0]
                if idx.size:
                    hits.append(base + off + idx.astype(np.uint64) * 4)
            off += n
    c = np.concatenate(hits) if hits else np.array([], dtype=np.uint64)
    os.makedirs(RUNS, exist_ok=True); np.save(CAND, c)
    print("first scan for %d: %d candidates" % (value, c.size))


def cmd_next(p, value):
    c = np.load(CAND)
    keep = np.array([a for a in c.tolist() if p.i32(a) == value], dtype=np.uint64)
    np.save(CAND, keep)
    print("next scan for %d: %d -> %d candidates" % (value, c.size, keep.size))
    if keep.size <= 20:
        cmd_show(p)


def cmd_show(p):
    for a in np.load(CAND).tolist()[:50]:
        print("  0x%X = %s" % (a, p.i32(a)))


def follow(p, base_off, offs):
    ptr = p.u64(p.base + base_off)
    for o in offs[:-1]:
        if ptr is None:
            return None, None
        ptr = p.u64(ptr + o)
    if ptr is None:
        return None, None
    addr = ptr + offs[-1]
    return addr, p.i32(addr)


def cmd_chains(p, lines):
    for line in lines:
        parts = line.split()
        if not parts or parts[0].startswith("#"):
            continue
        nums = [int(x, 16) for x in parts]
        addr, val = follow(p, nums[0], nums[1:])
        where = "unreadable" if addr is None else "0x%X = %s" % (addr, val)
        print("%-40s -> %s" % (" ".join(parts), where))


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    p = Proc()
    if a[0] == "info": cmd_info(p)
    elif a[0] == "scan": cmd_scan(p, int(a[1]))
    elif a[0] == "next": cmd_next(p, int(a[1]))
    elif a[0] == "show": cmd_show(p)
    elif a[0] == "chain": cmd_chains(p, [" ".join(a[1:])])
    elif a[0] == "chains":
        with open(a[1]) as f: cmd_chains(p, f.read().splitlines())
    else: sys.exit(__doc__)


if __name__ == "__main__":
    main()
