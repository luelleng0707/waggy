import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const required = ["index.html", "src/workbench.js", "src/api/client.js", "src/api/config.js", "src/styles/workbench.css"];

if (process.argv.includes("--check")) {
  for (const rel of required) {
    if (!fs.existsSync(path.join(root, rel))) {
      console.error("missing " + rel);
      process.exit(1);
    }
  }
  process.exit(0);
}

const port = Number(process.env.PORT || 4173);
const types = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".svg": "image/svg+xml",
};

const server = http.createServer((req, res) => {
  const url = new URL(req.url || "/", "http://127.0.0.1");
  if (url.pathname === "/src/api/runtime-config.js") {
    const base = process.env.WAGGY_API_BASE_URL || "";
    res.writeHead(200, { "Content-Type": "text/javascript; charset=utf-8" });
    res.end('globalThis.__WAGGY_API_BASE_URL = "' + base + '";\n');
    return;
  }
  let rel = decodeURIComponent(url.pathname);
  if (rel === "/") rel = "/index.html";
  const target = path.resolve(root, "." + rel);
  if (!target.startsWith(root) || !fs.existsSync(target) || !fs.statSync(target).isFile()) {
    res.writeHead(404);
    res.end("not found");
    return;
  }
  res.writeHead(200, { "Content-Type": types[path.extname(target)] || "application/octet-stream" });
  fs.createReadStream(target).pipe(res);
});

server.listen(port);
