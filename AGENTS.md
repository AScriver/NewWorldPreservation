# New World preservation scope

- Start with `docs/AGENT_START.md` for the reading order, safe offline/preflight commands, task briefs, evidence index and handoff format. Current task status stays in `docs/ROADMAP.md`.
- Preserve the existing legitimately owned PC client; do not remake its presentation or assets.
- Milestone 1 is two private clients entering one world and seeing each other's movement. Do not claim it from offline tests.
- Distinguish current executed evidence, source inference, historical upstream reports, proposals, and unknowns. Pin upstream commits and relevant dirty-file state.
- No copyrighted client assets, credentials, captures containing secrets, leaked source, proprietary Amazon material, or upstream decompilations in this repository. External reference checkouts and private observations stay ignored.
- Do not run upstream capture/instrumentation hooks, alter hosts/certificate stores, launch game clients, or contact game endpoints as part of offline validation.
- Use existing Python protocol components where evidence supports them. No invented wire formats.
- Keep upstream edits small and export reviewable patches only after provenance/license review; otherwise use original integration scripts that load a local reference checkout.
- Validate PowerShell scripts using C:\Users\Austin\.codex\tools\Invoke-CodexPowerShell.ps1 before execution; use task-specific variables and native argument arrays.
- Run tests with explicit scope, isolated temp resources, and loopback-only listeners. Do not stop unrelated processes.
- Do not publish, push, or message contributors without explicit authorization.
- Record tasks and verification in docs/ROADMAP.md. No Actionables work item was supplied; do not browse or claim unrelated items.

## Agent analysis toolchain

- Shared tools are at `C:\Users\Austin\.codex\tools\reverse-engineering`: Ghidra/PyGhidra, private JDK 21, Wireshark/TShark, Frida and a local Cheat Engine x64 build. Read [docs/TOOLS.md](docs/TOOLS.md) and the shared `manifest.json`/`verification.json` before use; those receipts distinguish installed tools from executed checks.
- Use the validated `Run-Tool.ps1` entry point with explicit native argument arrays. Prefer Ghidra headless/PyGhidra for pinned-image static analysis and TShark for existing authorized private captures. Ghidra rejects project paths containing a segment starting with a dot: put its databases under ignored `private/ghidra/`, not `.scratch/` or the shared `.codex` tool folder. Other client-derived output stays under ignored `.scratch/` or `private/`.
- Tool availability preserves the existing offline/client boundaries above. Frida attachment, Cheat Engine process reads, packet capture and debugger use require a separately authorized owned-client procedure; installation and smoke checks do not authorize them. Preserve intact launcher/EAC and report denied access. The local build's name is not proof that other games will accept it.
