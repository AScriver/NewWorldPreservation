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
        const actual = Array.from(new Uint8Array(target.readByteArray(expected.bytes.length)))
            .map(value => value.toString(16).padStart(2, "0")).join("");
        if (actual !== expected.hex) throw new Error("initializer entry bytes mismatch");
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
        send({type: "observer-status", ok: true, event: "admitted_and_attached"});
    } catch (error) {
        send({type: "observer-status", ok: false, error: String(error)});
    }
})();
