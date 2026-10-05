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

## Function-scoped Ghidra default

For a small static question, use [ghidra_function_slice.py](../scripts/ghidra_function_slice.py)
instead of importing the entire image with automatic analysis. This original helper
promotes the successful sparse registration procedure into a reviewed entry point.
It selects one to eight explicit function entries from AMD64 PE PDATA, follows
chained unwind ownership to retain split bodies, and caps selected code at one MiB.
It imports only that code plus `.rdata`/`.data` for static references; it never invokes
whole-image analysis. Leaf bodies without evidenced PDATA ownership are rejected
rather than inferred from an address. Concrete types and external callees can remain
unresolved in the sparse program.

Record the bounded question, pinned build/hash, exact entries, and instruction
cross-checks in the task brief. Use fresh, separate ignored output and database
directories. Save an invocation like the following in a task-specific `.ps1`, then
validate/execute that entire script through `Invoke-CodexPowerShell.ps1`. Substitute
a unique run identifier for `my-new-run`; existing destinations are rejected.

```powershell
$toolRunner = 'C:\Users\Austin\.codex\tools\reverse-engineering\Run-Tool.ps1'
$queryArguments = @(
    'C:\Code\NewWorldPreservation\scripts\ghidra_function_slice.py',
    '--image', 'C:\Program Files (x86)\Steam\steamapps\common\New World\Bin64\NewWorld.exe',
    '--expected-sha256', '8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e',
    '--functions', '0x141717fc0', '0x146af2340', '0x1461ad130',
    '--output', 'C:\Code\NewWorldPreservation\.scratch\my-new-run\output',
    '--project', 'C:\Code\NewWorldPreservation\private\ghidra\my-new-run',
    '--timeout', '30'
)
& $toolRunner -Tool python -ArgumentList $queryArguments
if ($LASTEXITCODE -ne 0) { throw 'Static query failed or was partial; inspect its private receipt.' }
```

The example entries belong to the pinned current player-construction investigation;
they are not universal addresses for other builds. Each decompile has a one-to-sixty
second timeout (default30); import/JVM/project-save time is additional. The helper
refuses a mismatched image hash, ambiguous/unbacked or overlapping code, excessive
selection, non-private destinations, dot-prefixed database segments, and output
reuse. It rechecks the image after analysis. `receipt.json` retains exact code-span,
script and output hashes, Git state, tool versions and completed/partial/failed
results. Failed or partial output does not qualify as successful decompilation.
Raw `.c`, errors and the analysis database remain ignored; publish only original
sanitized receipts. Whole-image analysis requires a concrete reason and bounded
resource/time plan in the task brief.

Verification on October5 completed all three example functions in the shared
Ghidra12.1.4/PyGhidra3.1.0 environment; the earlier whole-image attempt for those
entries had produced no decompilation. [Original validation receipt](../research/evidence/ghidra-function-slice-validation.json).
This establishes the helper's static operation, not a member wire schema, player
construction at runtime, or Milestone1.

## Evidence and project boundaries

Start static work at the [current player-construction/member boundary](ROADMAP.md#exact-next-blocker).
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
installed launcher/EAC. The user's October 4 authorization admits direct Frida
startup of a separate physical client copy and the pinned runtime trust hook under
[this bounded private procedure](FRIDA_PRIVATE_DTLS_TRIAL.md). It does not permit
protection evasion following an access denial, game endpoint traffic or capture hooks.

Wireshark was unpacked as a portable tool; no capture-driver installer was run.
Check capture prerequisites separately for any future authorized capture. The
locally named Cheat Engine build retains its upstream identity and has no claim of
anti-cheat invisibility or compatibility with other games.
