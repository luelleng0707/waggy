import test from "node:test";
import assert from "node:assert/strict";
import { runWorkbenchAnalysis, getRecalculationExplanation } from "../src/api/client.js";

test("client exports the workbench and recalculation helpers", () => {
  assert.equal(typeof runWorkbenchAnalysis, "function");
  assert.equal(getRecalculationExplanation({ explanation: { summary_facts: ["shown"] } }).summary_facts[0], "shown");
});
