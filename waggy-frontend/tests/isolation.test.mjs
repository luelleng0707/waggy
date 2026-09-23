import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import assert from "node:assert/strict";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

test("workbench stays a client of the HTTP API", () => {
  const js = fs.readFileSync(path.join(root, "src/workbench.js"), "utf8");
  assert.equal(js.includes("fetch("), false);
  assert.equal(js.includes("select_canonical"), false);
  assert.equal(js.includes("scientific_care"), false);
  assert.match(js, /from "\.\/api\/client\.js"/);
});

test("demo profile is marked synthetic", () => {
  const demo = fs.readFileSync(path.join(root, "src/demo/dogs.js"), "utf8");
  assert.match(demo, /SYNTHETIC \/ DEMO ONLY/);
});
