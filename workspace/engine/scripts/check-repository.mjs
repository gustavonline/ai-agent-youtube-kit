#!/usr/bin/env node

import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { loadAndValidate } from "./check-content-graph.mjs";

const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../..");
const required = [
  "AGENTS.md",
  "README.md",
  "package.json",
  "docs/ARCHITECTURE.md",
  "docs/CONTENT_GRAPH.md",
  "docs/DIFFUSION_STUDIO.md",
  "docs/SPECIALIST_MOTION.md",
  ".agents/skills/agentic-content-system/SKILL.md",
  ".agents/skills/diffusion-studio/SKILL.md",
  "workspace/engine/scripts/check-content-graph.mjs",
  "workspace/engine/scripts/diffusion-studio.mjs",
  "workspace/engine/templates/content-graph.json",
  "workspace/engine/templates/publisher-handoff.json",
  "workspace/engine/tests/fixtures/content-graph/content-graph.json",
  "workspace/engine/tests/fixtures/content-graph/publisher-handoff.json",
];
const retiredEditor = ["free", "cut"].join("");
const retired = [
  "pyproject.toml",
  "docs/ADAPTERS.md",
  "docs/CLI.md",
  "docs/EDITOR_ENGINE_DECISION.md",
  "docs/RECOVERY.md",
  "docs/SEMANTIC_EVALUATION.md",
  "docs/SYSTEM_TEMPLATE_MAPPING.md",
  `docs/${retiredEditor.toUpperCase()}_STUDIO.md`,
  `.agents/skills/${retiredEditor}-studio`,
  `workspace/engine/scripts/${retiredEditor}-studio.mjs`,
  `workspace/engine/tests/${retiredEditor}-studio.test.mjs`,
  "workspace/engine/agentic_content_system",
  "workspace/engine/contracts/schemas",
  "workspace/engine/media",
  "workspace/engine/motion-adapters",
  "workspace/engine/checks.py",
  "workspace/engine/tracer.py",
  "workspace/history",
  "workspace/runs",
];
const stalePatterns = [
  [new RegExp(`\\b${retiredEditor}\\b`, "gi"), "retired ordinary-editor route"],
  [/agentic_content_system/g, "retired Python package"],
  [/\bpython\s+-m\s+agentic-content-system\b/gi, "retired module invocation"],
  [/\bacs\s+(?:init|inspect|validate|render|derive|package|verify|review-report|export-result|semantic-eval|import-adapter)\b/gi, "retired application command"],
  [/workspace\/engine\/tracer\.py/g, "retired tracer"],
  [/workspace\/history\//g, "retired history ledger"],
  [/workspace\/runs\//g, "retired run ledger"],
  [/workspace\/engine\/motion-adapters/g, "retired bundled motion projects"],
  [/docs\/(?:CLI|ADAPTERS|EDITOR_ENGINE_DECISION|RECOVERY|SEMANTIC_EVALUATION|SYSTEM_TEMPLATE_MAPPING)\.md/g, "retired documentation"],
  [/publish\/manifest\.json/g, "retired generated manifest"],
  [/results\/run-result\.json/g, "retired generated result"],
  [/\bimport-adapter\b/g, "retired adapter seam"],
];

function relative(filePath) {
  return path.relative(repositoryRoot, filePath).split(path.sep).join("/");
}

function walk(directory, predicate, output = []) {
  if (!existsSync(directory)) return output;
  for (const entry of readdirSync(directory, { withFileTypes: true })) {
    if ([".git", ".venv", "node_modules", ".cache"].includes(entry.name)) continue;
    const candidate = path.join(directory, entry.name);
    if (entry.isDirectory()) walk(candidate, predicate, output);
    else if (predicate(candidate)) output.push(candidate);
  }
  return output;
}

function containsFiles(directory) {
  if (!existsSync(directory)) return false;
  if (!statSync(directory).isDirectory()) return true;
  return walk(directory, () => true, []).length > 0;
}

function checkMarkdownLink(sourceFile, rawTarget, errors) {
  let target = rawTarget.trim();
  if (target.startsWith("<") && target.endsWith(">")) target = target.slice(1, -1);
  if (/^(?:https?:|mailto:|app:)/i.test(target) || target.startsWith("#")) return;
  target = target.split("#", 1)[0];
  if (target === "") return;
  try {
    target = decodeURIComponent(target);
  } catch {
    errors.push(`${relative(sourceFile)} has an invalid encoded link: ${rawTarget}`);
    return;
  }
  const resolved = path.resolve(path.dirname(sourceFile), target);
  if (!existsSync(resolved)) errors.push(`${relative(sourceFile)} links to missing ${rawTarget}`);
}

export function checkRepository() {
  const errors = [];
  for (const item of required) {
    if (!existsSync(path.join(repositoryRoot, item))) errors.push(`missing required ${item}`);
  }
  for (const item of retired) {
    if (containsFiles(path.join(repositoryRoot, item))) errors.push(`retired surface still exists: ${item}`);
  }

  const markdownRoots = ["AGENTS.md", "README.md", ".agents", "docs", "examples", "workspace"];
  const markdownFiles = [];
  for (const root of markdownRoots) {
    const absolute = path.join(repositoryRoot, root);
    if (!existsSync(absolute)) continue;
    if (statSync(absolute).isFile()) markdownFiles.push(absolute);
    else walk(absolute, (candidate) => candidate.endsWith(".md"), markdownFiles);
  }
  for (const filePath of markdownFiles) {
    const text = readFileSync(filePath, "utf8");
    const linkPattern = /!?\[[^\]]*\]\(([^)]+)\)/g;
    for (const match of text.matchAll(linkPattern)) checkMarkdownLink(filePath, match[1], errors);
    for (const [pattern, label] of stalePatterns) {
      pattern.lastIndex = 0;
      if (pattern.test(text)) errors.push(`${relative(filePath)} references ${label}`);
    }
  }

  const pythonFiles = walk(path.join(repositoryRoot, "workspace"), (candidate) => candidate.endsWith(".py"));
  for (const filePath of pythonFiles) {
    const text = readFileSync(filePath, "utf8");
    if (/agentic_content_system|from\s+contracts\b/.test(text)) {
      errors.push(`${relative(filePath)} imports retired application code`);
    }
  }

  const packageJson = JSON.parse(readFileSync(path.join(repositoryRoot, "package.json"), "utf8"));
  if (packageJson.private !== true) errors.push("package.json must remain private");
  if (packageJson.dependencies || packageJson.devDependencies) errors.push("contract proof must remain zero-dependency");
  if (packageJson.engines?.node !== ">=22") errors.push("package.json must require Node >=22");

  const fixtureDirectory = path.join(repositoryRoot, "workspace/engine/tests/fixtures/content-graph");
  const graphErrors = loadAndValidate(
    path.join(fixtureDirectory, "content-graph.json"),
    path.join(fixtureDirectory, "publisher-handoff.json"),
  );
  errors.push(...graphErrors.map((error) => `neutral fixture: ${error}`));
  return { errors, markdownCount: markdownFiles.length, pythonHelperCount: pythonFiles.length };
}

function main() {
  const result = checkRepository();
  if (result.errors.length > 0) {
    result.errors.forEach((error) => console.error(`ERROR: ${error}`));
    process.exitCode = 1;
    return;
  }
  console.log(`PASS repository structure, ${result.markdownCount} Markdown link/stale checks, ${result.pythonHelperCount} optional Python helpers`);
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) main();
