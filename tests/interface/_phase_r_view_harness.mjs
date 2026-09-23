import fs from "node:fs";

import { evidenceErrorView, evidenceReportPath } from "../../waggy-frontend/src/evidence/load.js";
import { renderEvidenceError, renderEvidenceReport } from "../../waggy-frontend/src/evidence/render.js";

const op = process.argv[2];
const payload = JSON.parse(fs.readFileSync(0, "utf8") || "{}");
let result;
if (op === "render") result = { html: renderEvidenceReport(payload) };
else if (op === "error") result = { html: renderEvidenceError(payload) };
else if (op === "path") result = { path: evidenceReportPath(payload.dog_id, payload) };
else if (op === "http-error") result = evidenceErrorView(payload.status, payload.body);
else throw new Error(`unknown op ${op}`);
process.stdout.write(JSON.stringify(result));
