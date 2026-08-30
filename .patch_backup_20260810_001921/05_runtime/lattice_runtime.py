"""
lattice_runtime.py — REPL Entry Point & Command Dispatcher
PATCH v1.1:
  CRITICAL FIX: CommandParser.parse() used HTML-encoded angle brackets
  ('&lt;Signal:Send&gt;' etc.) — ALL CLI commands NEVER matched user input.
  Fixed to use literal '<' and '>' characters throughout.
  REMOVE: Inline class duplicates — all components imported from modules.
  ADD: <Echo:Trace>, <Vault:Retrieve> now wired. 'hud' command added.
"""
from __future__ import annotations
import sys
from lattice_core import Lattice

COMMANDS = {
    "<Signal:Send>":    "Send signal through full pipeline",
    "<Vault:Retrieve>": "Retrieve stored value by key",
    "<Vault:Export>":   "Export full vault snapshot",
    "<Echo:Trace>":     "Trace recorded signal by label/index",
    "<Stumpy:Audit>":   "Run integrity audit on last cycle",
    "∮ <value>":        "Measurement operator",
    "‰ <name>":         "Identity operator",
    "hud":              "Component status summary",
    "exit":             "Exit REPL",
}

class CommandParser:
    def parse(self, raw: str) -> tuple:
        t = raw.strip()
        # FIX: All comparisons below use literal '<' '>' — v1.0 used &lt; &gt;
        if t.startswith("<Signal:Send>"):    return ("<Signal:Send>",    t[len("<Signal:Send>"):].strip())
        if t.startswith("<Vault:Retrieve>"): return ("<Vault:Retrieve>", t[len("<Vault:Retrieve>"):].strip())
        if t.startswith("<Vault:Export>"):   return ("<Vault:Export>",   "")
        if t.startswith("<Echo:Trace>"):     return ("<Echo:Trace>",     t[len("<Echo:Trace>"):].strip())
        if t.startswith("<Stumpy:Audit>"):   return ("<Stumpy:Audit>",   "")
        if t.startswith("∮"):               return ("∮",  t[1:].strip())
        if t.startswith("‰"):               return ("‰",  t[1:].strip())
        if t.lower() == "hud":              return ("hud", "")
        if t.lower() in ("exit","quit",":q"): return ("exit","")
        return ("<Signal:Send>", t)

class LatticeREPL:
    BANNER = (
        "\n╔══════════════════════════════════════════╗\n"
        "║   Canonical Lattice Runtime  v1.1-patch  ║\n"
        "╚══════════════════════════════════════════╝\n"
        "  Commands: <Signal:Send> · <Vault:Retrieve> · <Vault:Export>\n"
        "            <Echo:Trace> · <Stumpy:Audit> · ∮ · ‰ · hud · exit\n"
    )
    def __init__(self) -> None:
        self.lattice = Lattice()
        self.parser  = CommandParser()
        self._last_cycle: dict = {}

    def _fmt(self, obj) -> str:
        import json
        try: return json.dumps(obj, indent=2, default=str)
        except Exception: return str(obj)

    def dispatch(self, cmd: str, arg: str) -> str:
        L = self.lattice
        if cmd == "<Signal:Send>":
            if not arg: return "[!] <Signal:Send> requires an argument."
            c = L.run(arg); self._last_cycle = c
            blocked = c.get("blocked_at")
            if blocked: return f"[BLOCKED at {blocked}] {c.get('veil_reason','gate denied')}"
            out = c.get("result")
            return "[IV·SIL] Silence — signal acknowledged." if out is None else self._fmt(out)
        if cmd == "<Vault:Retrieve>":
            if not arg: return "[!] <Vault:Retrieve> requires a key."
            return self._fmt(L.vault.retrieve(arg))     # FIX: retrieve() now exists
        if cmd == "<Vault:Export>":
            return self._fmt(L.vault.export())
        if cmd == "<Echo:Trace>":
            if not arg: return "[!] <Echo:Trace> requires a label/index."
            return self._fmt(L.echo.trace(arg))         # FIX: trace() now exists
        if cmd == "<Stumpy:Audit>":
            return self._fmt(L.stumpy.audit(self._last_cycle))
        if cmd == "∮":
            c = L.run(f"[∮] {arg}"); self._last_cycle = c; return self._fmt(c.get("result"))
        if cmd == "‰":
            return self._fmt({"operator": "LiminalJermo", "token": arg, "resolved": True})
        if cmd == "hud":
            return self._fmt(L.hud())
        if cmd == "exit":
            return "__EXIT__"
        return f"[?] Unknown command: {cmd!r}"

    def run(self) -> None:
        print(self.BANNER)
        while True:
            try:
                raw = input("lattice> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n[Lattice] Session closed.")
                break
            if not raw: continue
            cmd, arg = self.parser.parse(raw)
            resp = self.dispatch(cmd, arg)
            if resp == "__EXIT__":
                print("[Lattice] Exiting. Invariants maintained.")
                break
            print(resp); print()

def main() -> None:
    LatticeREPL().run()

if __name__ == "__main__":
    main()
