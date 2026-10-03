# Agent analysis tools

The shared Windows tool root is `C:\Users\Austin\.codex\tools\reverse-engineering`.
The root is outside this repository and is discoverable from both the global and
project `AGENTS.md`. Read its `README.md`, `manifest.json` and `verification.json`
for exact installed versions, source identity, hashes and executed checks.

## Entry points

| Tool | Shared-root path | Project use |
|---|---|---|
| Ghidra headless | `ghidra\ghidra_12.1.4_PUBLIC\support\analyzeHeadless.bat` | Function-scoped static analysis, references and decompilation of the pinned owned client |
| PyGhidra / tool Python | `python-env\Scripts\pyghidra.exe`, `python-env\Scripts\python.exe` | Repeatable Python queries through Ghidra's API |
| Private JDK 21 | `jdk\jdk-21.0.12.1+1` | Runtime for Ghidra; supplied by the wrapper |
| TShark / Wireshark | `wireshark\App\Wireshark\tshark.exe`, `wireshark\App\Wireshark\Wireshark.exe` | Offline inspection of existing authorized captures |
| Frida | `python-env\Scripts\frida.exe`, `python-env\Scripts\frida-trace.exe`, `python-env\Scripts\frida-ps.exe` | Scriptable inspection of explicitly authorized owned processes |
| Local Cheat Engine | `cheat-engine\runtime\NWPreservation-CE-x64.exe` | Lua-based inspection under an authorized owned-process procedure; consult the manifest for build/verification status |

Use `Run-Tool.ps1` so the private JDK and Python environment are supplied only for
that command. The installation does not change the persistent system/user PATH.

Put invocations in a task-specific `.ps1`, validate the whole script with
`Invoke-CodexPowerShell.ps1 -Path <script> -Execute`, and pass the tool's arguments
as a string array. The validator's `-File` child boundary cannot preserve a nested
argument array containing switches; do not forward tool switches through the
validator's own `-ArgumentList`. For example, save these lines in a task script:

```powershell
$toolRunner = 'C:\Users\Austin\.codex\tools\reverse-engineering\Run-Tool.ps1'
& $toolRunner -Tool frida -ArgumentList @('--version')
& $toolRunner -Tool tshark -ArgumentList @('--version')
$toolArguments = @('-r', 'C:\Code\NewWorldPreservation\private\my-run\capture.pcapng', '-T', 'json')
& $toolRunner -Tool tshark -ArgumentList $toolArguments
```

The path above is an example, not an existing capture. PyGhidra code runs through
`Run-Tool.ps1 -Tool python -ArgumentList @('C:\...\analysis.py')`; call
`pyghidra.start()` in the script to start the headless API. The wrapper sets
`GHIDRA_INSTALL_DIR` and `JAVA_HOME` and restores the invoking environment.

## Evidence and project boundaries

Start static work at the [current configuration/provider-to-REP boundary](ROADMAP.md#exact-next-blocker).
Pin the client build/hash, analyzed functions and script/database identity. A
decompiler result is source inference and can contain incorrect recovered types;
check material joins against instructions and data flow. Static findings do not
establish runtime configuration consumption or game transport acceptance.

Ghidra rejects project paths containing a segment starting with a dot; store its
databases under ignored `private/ghidra/`, not `.scratch/` or `.codex`. Other
proprietary disassembly/decompilation and raw captures stay in ignored `.scratch/`
or `private/`. Commit only original scripts and sanitized
evidence permitted by [AGENTS](../AGENTS.md). Tool installation adds no client
assets or upstream decompilations to the repository.

The tools do not change the existing live-observation gates. Do not launch clients,
attach Frida/Cheat Engine/debuggers, enable capture, change hosts/certificate stores
or contact game endpoints during offline validation. Any live trial needs the
existing separately authorized ownership and cleanup procedure. Preserve intact
launcher/EAC; an access denial is a result, not permission to bypass protections.

Wireshark was unpacked as a portable tool; no capture-driver installer was run.
Check capture prerequisites separately for any future authorized capture. The
locally named Cheat Engine build retains its upstream identity and has no claim of
anti-cheat invisibility or compatibility with other games.
