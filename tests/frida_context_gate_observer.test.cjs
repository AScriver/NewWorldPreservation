// Synthetic Frida facade only: no client, process attachment or network.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { test } = require("node:test");
const source = fs.readFileSync(path.join(__dirname, "../scripts/frida_trial_observer.js"), "utf8");
const base = 0x140000000;
const sites = [["self_identification", 0x6454c00, 0x990],
    ["level_info", 0x6446800, 0x990], ["context_load", 0x6448cd0, 0]];
const flags = ["self_identified", "activation_latched", "context_ready", "level_pending",
    "jav_context_present", "client_sdk_present", "game_present"];

function facade(enabled = true, change = () => {}) {
    const entries = new Map(), pointers = new Map(), bytes = new Map();
    const attached = new Map(), messages = [];
    let reads = 0;
    class Pointer {
        constructor(value) { this.value = value; }
        add(value) { return new Pointer(this.value + value); }
        sub(value) { return new Pointer(this.value - value); }
        isNull() { return this.value === 0; }
        toString() { return "0x" + this.value.toString(16); }
        readByteArray(length) {
            return Uint8Array.from(entries.get(this.value) || Array(length).fill(0)).buffer;
        }
        readPointer() {
            reads++;
            if (!pointers.has(this.value)) throw new Error("unreadable secret-sentinel");
            return new Pointer(pointers.get(this.value));
        }
        readU8() {
            reads++;
            if (!bytes.has(this.value)) throw new Error("unreadable secret-sentinel");
            return bytes.get(this.value);
        }
    }
    const expected = {path: "C:\\private\\client\\Bin64\\NewWorld.exe", hex: "00".repeat(16), bytes: Array(16).fill(0)};
    if (enabled) expected.context_gate_targets = sites.map(([site, rva, adjustment]) =>
        ({site, rva, adjustment, hex: "00".repeat(16), bytes: Array(16).fill(0)}));
    change(expected, entries);
    vm.runInNewContext(source.replace("__ADMISSION__", JSON.stringify(expected)), {
        Process: {enumerateModules: () => [{name: "NewWorld.exe", path: expected.path, base: new Pointer(base)}]},
        Interceptor: {attach: (target, callbacks) => attached.set(target.value, callbacks)},
        send: payload => messages.push(JSON.parse(JSON.stringify(payload)))
    });
    function state(port, values = [0, 0, 0, 0], jav = 0x9000, sdk = 0xa000, game = 0xb000) {
        [0x1a0, 0x1a1, 0x1a2, 0x190].forEach((offset, index) => bytes.set(port + offset, values[index]));
        pointers.set(port + 0x48, jav);
        if (jav) pointers.set(jav + 8, sdk);
        pointers.set(base + 0xa7ba0e0, 0xc000);
        pointers.set(0xc000 + 0x60, game);
    }
    function invoke(index, port, during = () => {}) {
        const [, rva, adjustment] = sites[index];
        const callback = attached.get(base + rva), invocation = {};
        callback.onEnter.call(invocation, [new Pointer(port + adjustment)]);
        during();
        callback.onLeave.call(invocation, new Pointer(0));
    }
    return {attached, messages, state, invoke, reads: () => reads};
}

test("default admission attaches only the existing trust observer", () => {
    const run = facade(false);
    assert.equal(run.attached.size, 1);
    assert.equal(run.messages[0].ok, true);
});

test("all guards pass before attachment; altered site or prefix refuses admission", () => {
    for (const change of [
        expected => { expected.context_gate_targets[1].rva++; },
        (expected, entries) => { entries.set(base + expected.context_gate_targets[2].rva, Array(16).fill(1)); }
    ]) {
        const run = facade(true, change);
        assert.equal(run.attached.size, 0);
        assert.equal(run.messages[0].ok, false);
        assert.ok(!JSON.stringify(run.messages).includes("secret-sentinel"));
    }
});

test("adjusted callbacks correlate with the direct port and expose only booleans", () => {
    const run = facade();
    assert.equal(run.attached.size, 4);
    run.state(0x5000);
    run.invoke(0, 0x5000, () => run.state(0x5000, [1, 0, 0, 0]));
    run.invoke(1, 0x5000, () => run.state(0x5000, [1, 0, 0, 1]));
    run.invoke(2, 0x5000, () => run.state(0x5000, [1, 1, 0, 0]));
    const events = run.messages.filter(item => item.type === "context-gate");
    assert.equal(events.length, 6);
    assert.deepEqual(events.map(item => item.port_tag), Array(6).fill(1));
    assert.equal(events[0].self_identified, false);
    assert.equal(events[1].self_identified, true);
    assert.equal(events[3].level_pending, true);
    assert.equal(events[5].activation_latched, true);
    for (const event of events) {
        assert.deepEqual(Object.keys(event).sort(), ["type", "site", "phase", "port_tag", ...flags].sort());
        for (const flag of flags) assert.equal(typeof event[flag], "boolean");
    }
    assert.ok(!JSON.stringify(events).includes("0x5000"));
});

test("unreadable state is unknown and null JavContext implies absent SDK", () => {
    const run = facade();
    run.invoke(0, 0x5000);
    const first = run.messages.find(item => item.type === "context-gate");
    assert.ok(flags.every(flag => first[flag] === null));
    run.state(0x6000, [0, 0, 0, 0], 0);
    run.invoke(2, 0x6000);
    const last = run.messages.at(-1);
    assert.equal(last.jav_context_present, false);
    assert.equal(last.client_sdk_present, false);
    assert.equal(last.game_present, true);
    assert.ok(!JSON.stringify(run.messages).includes("secret-sentinel"));
});

test("missing game pointer is observed without emitting its address", () => {
    const run = facade();
    run.state(0x5000, [1, 0, 0, 1], 0x9000, 0xa000, 0);
    run.invoke(2, 0x5000);
    assert.equal(run.messages.at(-1).game_present, false);
    assert.ok(!JSON.stringify(run.messages).includes("0xc000"));
});

test("global event cap also stops additional state reads", () => {
    const run = facade();
    run.state(0x5000);
    for (let index = 0; index < 48; index++) run.invoke(2, 0x5000);
    const reads = run.reads();
    for (let index = 0; index < 30; index++) run.invoke(0, 0x5000);
    assert.equal(run.messages.filter(item => item.type === "context-gate").length, 96);
    assert.equal(run.reads(), reads);
});

test("ephemeral object tags admit at most16 distinct receivers", () => {
    const run = facade();
    for (let index = 0; index < 17; index++) {
        const port = 0x5000 + index * 0x2000;
        run.state(port);
        run.invoke(0, port);
    }
    const events = run.messages.filter(item => item.type === "context-gate");
    assert.equal(events.length, 32);
    assert.deepEqual([...new Set(events.map(item => item.port_tag))], Array.from({length: 16}, (_, index) => index + 1));
});
