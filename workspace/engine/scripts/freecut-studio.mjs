#!/usr/bin/env node

import { execFileSync, spawn } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const FREECUT_ORIGIN = "https://github.com/walterlow/freecut.git";
export const FREECUT_REVISION = "4d62e8082c5eb387a96275bcbd323d28f6e41a62";
export const FREECUT_PACKAGE_MANAGER = "npm@11.8.0";

export function resolveCheckout(platform = process.platform, environment = process.env, homeDirectory = os.homedir()) {
  if (platform === "win32") {
    if (!environment.LOCALAPPDATA) throw new Error("LOCALAPPDATA is required on Windows");
    return path.win32.join(environment.LOCALAPPDATA, "freecut");
  }
  if (platform === "darwin" || platform === "linux") {
    if (!homeDirectory) throw new Error("A home directory is required");
    return path.posix.join(homeDirectory, ".local", "share", "freecut");
  }
  throw new Error(`Unsupported platform: ${platform}`);
}

export function previewInvocation(platform = process.platform, port = 4173) {
  if (!Number.isInteger(port) || port < 1024 || port > 65535) throw new Error("Port must be an integer from 1024 through 65535");
  return {
    command: platform === "win32" ? "npm.cmd" : "npm",
    args: ["run", "preview", "--", "--host", "127.0.0.1", "--port", String(port), "--strictPort"],
    url: `http://127.0.0.1:${port}/`,
  };
}

function git(checkout, args) {
  return execFileSync("git", ["-C", checkout, ...args], { encoding: "utf8" }).trim();
}

export function checkCheckout(checkout = resolveCheckout()) {
  const failures = [];
  if (!existsSync(checkout)) return { ok: false, checkout, failures: ["checkout is missing"] };
  let origin;
  let revision;
  let status;
  try {
    origin = git(checkout, ["remote", "get-url", "origin"]);
    revision = git(checkout, ["rev-parse", "HEAD"]);
    status = git(checkout, ["status", "--porcelain"]);
  } catch (error) {
    return { ok: false, checkout, failures: [`git check failed: ${error.message}`] };
  }
  if (origin !== FREECUT_ORIGIN) failures.push(`origin is ${origin}`);
  if (revision !== FREECUT_REVISION) failures.push(`HEAD is ${revision}`);
  if (status !== "") failures.push("checkout has uncommitted state");

  const packagePath = path.join(checkout, "package.json");
  let packageManager;
  if (!existsSync(packagePath)) {
    failures.push("package.json is missing");
  } else {
    packageManager = JSON.parse(readFileSync(packagePath, "utf8")).packageManager;
    if (packageManager !== FREECUT_PACKAGE_MANAGER) failures.push(`packageManager is ${packageManager}`);
  }
  if (!existsSync(path.join(checkout, "dist", "index.html"))) failures.push("built dist/index.html is missing");
  if (!existsSync(path.join(checkout, "node_modules"))) failures.push("node_modules is missing");
  let runtimeNpm;
  try {
    runtimeNpm = execFileSync(process.platform === "win32" ? "npm.cmd" : "npm", ["--version"], { encoding: "utf8" }).trim();
  } catch (error) {
    failures.push(`npm runtime check failed: ${error.message}`);
  }
  return {
    ok: failures.length === 0,
    checkout,
    origin,
    revision,
    packageManager,
    runtimeNode: process.version,
    runtimeNpm,
    failures,
  };
}

function parseArguments(argumentsList) {
  const result = { command: argumentsList[0] || "check", port: 4173, platform: process.platform };
  for (let index = 1; index < argumentsList.length; index += 1) {
    const argument = argumentsList[index];
    if (argument === "--port") {
      result.port = Number(argumentsList[index + 1]);
      index += 1;
    } else if (argument === "--platform") {
      result.platform = argumentsList[index + 1];
      index += 1;
    } else {
      throw new Error(`Unknown argument: ${argument}`);
    }
  }
  return result;
}

function describe(platform, port) {
  const sampleEnvironment = platform === "win32" ? { LOCALAPPDATA: "C:\\Users\\owner\\AppData\\Local" } : {};
  const sampleHome = platform === "darwin" ? "/Users/owner" : platform === "linux" ? "/home/owner" : undefined;
  return {
    platform,
    checkout: resolveCheckout(platform, sampleEnvironment, sampleHome),
    preview: previewInvocation(platform, port),
    browser: "Open preview.url in the Codex in-app browser after the server reports ready.",
  };
}

function main() {
  try {
    const options = parseArguments(process.argv.slice(2));
    if (options.command === "describe") {
      console.log(JSON.stringify(describe(options.platform, options.port), null, 2));
      return;
    }
    const checkout = resolveCheckout();
    const result = checkCheckout(checkout);
    if (!result.ok) {
      console.error(JSON.stringify(result, null, 2));
      process.exitCode = 1;
      return;
    }
    if (options.command === "check") {
      console.log(JSON.stringify(result, null, 2));
      return;
    }
    if (options.command !== "serve") throw new Error(`Unknown command: ${options.command}`);
    const preview = previewInvocation(process.platform, options.port);
    console.log(`FreeCut checkout: ${checkout}`);
    console.log(`Loopback Studio: ${preview.url}`);
    const child = spawn(preview.command, preview.args, { cwd: checkout, stdio: "inherit", shell: false });
    for (const signal of ["SIGINT", "SIGTERM"]) {
      process.on(signal, () => child.kill(signal));
    }
    child.on("exit", (code, signal) => {
      if (signal) process.kill(process.pid, signal);
      else process.exitCode = code ?? 1;
    });
  } catch (error) {
    console.error(`ERROR: ${error.message}`);
    process.exitCode = 1;
  }
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) main();
