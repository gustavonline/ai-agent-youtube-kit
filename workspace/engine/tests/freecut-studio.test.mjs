import assert from "node:assert/strict";
import test from "node:test";

import { FREECUT_PACKAGE_MANAGER, FREECUT_REVISION, previewInvocation, resolveCheckout } from "../scripts/freecut-studio.mjs";

test("FreeCut pin and declared package manager stay explicit", () => {
  assert.equal(FREECUT_REVISION, "4d62e8082c5eb387a96275bcbd323d28f6e41a62");
  assert.equal(FREECUT_PACKAGE_MANAGER, "npm@11.8.0");
});

test("macOS and Linux use the single external checkout", () => {
  assert.equal(resolveCheckout("darwin", {}, "/Users/owner"), "/Users/owner/.local/share/freecut");
  assert.equal(resolveCheckout("linux", {}, "/home/owner"), "/home/owner/.local/share/freecut");
});

test("Windows uses one external LocalAppData checkout", () => {
  assert.equal(
    resolveCheckout("win32", { LOCALAPPDATA: "C:\\Users\\owner\\AppData\\Local" }),
    "C:\\Users\\owner\\AppData\\Local\\freecut",
  );
});

test("all platforms launch the same Vite preview on strict loopback", () => {
  for (const platform of ["darwin", "linux", "win32"]) {
    const invocation = previewInvocation(platform, 4173);
    assert.deepEqual(invocation.args, ["run", "preview", "--", "--host", "127.0.0.1", "--port", "4173", "--strictPort"]);
    assert.equal(invocation.url, "http://127.0.0.1:4173/");
    assert.equal(invocation.command, platform === "win32" ? "npm.cmd" : "npm");
  }
});
