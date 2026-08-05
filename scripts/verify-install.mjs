#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

// Skills are installed as single directories, so this copies each skill out of
// the repo on its own and checks frontmatter plus same-skill relative links
// that point at real files in the source tree.

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const skillsDir = path.join(root, "skills");
const workDir = fs.mkdtempSync(path.join(os.tmpdir(), "playbook-install-"));
const installDir = path.join(workDir, "installed");
const failures = [];

const skills = fs
  .readdirSync(skillsDir)
  .filter((entry) => !entry.startsWith("_") && !entry.startsWith("."))
  .filter((entry) => fs.statSync(path.join(skillsDir, entry)).isDirectory())
  .filter((entry) => fs.existsSync(path.join(skillsDir, entry, "SKILL.md")));

for (const skill of skills) {
  fs.cpSync(path.join(skillsDir, skill), path.join(installDir, skill), { recursive: true });
}

for (const skill of skills) {
  checkFrontmatter(skill);
  checkReferences(skill);
}

fs.rmSync(workDir, { recursive: true, force: true });

if (failures.length > 0) {
  console.error("Standalone install verification failed:");
  for (const failure of failures) console.error(`  ${failure}`);
  process.exit(1);
}

console.log(`Verified ${skills.length} skill(s) as standalone installs.`);

function checkFrontmatter(skill) {
  const skillFile = path.join(installDir, skill, "SKILL.md");
  const content = fs.readFileSync(skillFile, "utf8");
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) {
    failures.push(`${skill}/SKILL.md: missing YAML frontmatter`);
    return;
  }

  const frontmatter = match[1];
  if (!/^\s*name:\s*\S+/m.test(frontmatter)) {
    failures.push(`${skill}/SKILL.md: frontmatter missing name`);
  }
  if (!/^\s*description:\s*\S+/m.test(frontmatter)) {
    failures.push(`${skill}/SKILL.md: frontmatter missing description`);
  }
}

function checkReferences(skill) {
  const sourceRoot = path.join(skillsDir, skill);
  const skillRoot = path.join(installDir, skill);
  for (const file of markdownFiles(skillRoot)) {
    const content = fs.readFileSync(file, "utf8");
    const from = path.relative(installDir, file);
    const sourceFile = path.join(sourceRoot, path.relative(skillRoot, file));

    for (const reference of content.matchAll(/\[[^\]]*\]\(([^)]+)\)/g)) {
      const target = reference[1].split("#")[0].split("?")[0].trim();
      if (!target || /^(https?:|mailto:)/i.test(target)) continue;
      if (target.startsWith("../")) {
        failures.push(
          `${from}: cross-skill relative link ${target} breaks standalone install`
        );
        continue;
      }
      if (target.startsWith("/") || target.includes("://")) continue;

      const resolvedSource = path.resolve(path.dirname(sourceFile), target);
      // Skip illustrative links that never existed in the source skill.
      if (!fs.existsSync(resolvedSource)) continue;

      const resolved = path.resolve(path.dirname(file), target);
      if (!resolved.startsWith(skillRoot + path.sep) && resolved !== skillRoot) {
        failures.push(`${from}: link ${target} escapes skill directory`);
        continue;
      }
      if (!fs.existsSync(resolved)) {
        failures.push(`${from}: reference ${target} does not resolve after install`);
      }
    }
  }
}

function markdownFiles(dir) {
  const found = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === "node_modules" || entry.name.startsWith(".")) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) found.push(...markdownFiles(full));
    else if (entry.name.endsWith(".md")) found.push(full);
  }
  return found;
}
