"use strict";

// Original observation only. The upstream trust script is loaded separately,
// unmodified, after this listener. Entry and return are distinct time points.
(function () {
    const expected = __ADMISSION__;
    try {
        const module = Process.enumerateModules()[0];
        const normalized = value => value.replace(/\//g, "\\").toLowerCase();
        if (!module || normalized(module.path) !== normalized(expected.path) ||
            module.name.toLowerCase() !== "newworld.exe") {
            throw new Error("main module path/name mismatch");
        }
        const target = module.base.add(0x5dce750);
        function guard(address, entry) {
            const actual = Array.from(new Uint8Array(address.readByteArray(entry.bytes.length)))
                .map(value => value.toString(16).padStart(2, "0")).join("");
            if (actual !== entry.hex) throw new Error("entry bytes mismatch");
        }
        guard(target, expected);
        const allowedSites = [
            ["self_identification", 0x6454c00, 0x990],
            ["level_info", 0x6446800, 0x990],
            ["context_load", 0x6448cd0, 0]
        ];
        const gates = expected.context_gate_targets;
        if (gates !== undefined) {
            if (!Array.isArray(gates) || gates.length !== allowedSites.length)
                throw new Error("context-gate targets mismatch");
            gates.forEach((entry, index) => {
                const allowed = allowedSites[index];
                if (entry.site !== allowed[0] || entry.rva !== allowed[1] ||
                    entry.adjustment !== allowed[2] || entry.bytes.length !== 16)
                    throw new Error("context-gate target mismatch");
                guard(module.base.add(entry.rva), entry);
            });
        }
        Interceptor.attach(target, {
            onEnter(args) {
                this.slot = args[0].add(0x288);
                try {
                    this.beforeNonzero = !this.slot.readPointer().isNull();
                    this.beforeRead = true;
                } catch (_) { this.beforeRead = false; }
            },
            onLeave(retval) {
                let afterZero = null;
                try { afterZero = this.slot.readPointer().isNull(); } catch (_) {}
                send({type: "hook-invocation", before_read: this.beforeRead === true,
                    before_nonzero: this.beforeRead ? this.beforeNonzero : null,
                    after_zero_at_return: afterZero,
                    retval_hex: retval.toString(), retval_zero: retval.isNull()});
            }
        });
        if (gates !== undefined) {
            const portTags = new Map();
            let emitted = 0;
            function readFlag(port, offset) {
                try { return port.add(offset).readU8() !== 0; } catch (_) { return null; }
            }
            function snapshot(site, phase, port, tag) {
                if (emitted >= 96 || tag === null) return;
                let javPresent = null, sdkPresent = null, gamePresent = null;
                try {
                    const jav = port.add(0x48).readPointer();
                    javPresent = !jav.isNull();
                    if (javPresent) sdkPresent = !jav.add(8).readPointer().isNull();
                    else sdkPresent = false;
                } catch (_) {}
                try {
                    const environment = module.base.add(0xa7ba0e0).readPointer();
                    gamePresent = !environment.isNull() && !environment.add(0x60).readPointer().isNull();
                } catch (_) {}
                emitted++;
                send({type: "context-gate", site: site, phase: phase, port_tag: tag,
                    self_identified: readFlag(port, 0x1a0),
                    activation_latched: readFlag(port, 0x1a1),
                    context_ready: readFlag(port, 0x1a2),
                    level_pending: readFlag(port, 0x190),
                    jav_context_present: javPresent, client_sdk_present: sdkPresent,
                    game_present: gamePresent});
            }
            gates.forEach(entry => Interceptor.attach(module.base.add(entry.rva), {
                onEnter(args) {
                    this.port = null;
                    if (emitted >= 96) return;
                    try {
                        const port = args[0].sub(entry.adjustment);
                        if (port.isNull()) return;
                        const key = port.toString(); // Internal correlation only; never emitted.
                        if (!portTags.has(key)) {
                            if (portTags.size >= 16) return;
                            portTags.set(key, portTags.size + 1);
                        }
                        this.port = port;
                        this.tag = portTags.get(key);
                        snapshot(entry.site, "entry", this.port, this.tag);
                    } catch (_) {}
                },
                onLeave() {
                    if (this.port !== null) snapshot(entry.site, "return", this.port, this.tag);
                }
            }));
        }
        send({type: "observer-status", ok: true, event: "admitted_and_attached"});
    } catch (error) {
        send({type: "observer-status", ok: false, error: "observer admission or attachment failed"});
    }
})();
