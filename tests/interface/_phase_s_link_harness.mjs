import fs from "node:fs";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const workbenchPath = fileURLToPath(new URL("../../waggy-frontend/src/workbench.js", import.meta.url));
const src = fs.readFileSync(workbenchPath, "utf8");

function sliceBetween(startMarker, endMarker) {
  const start = src.indexOf(startMarker);
  const end = src.indexOf(endMarker);
  if (start < 0 || end <= start) {
    throw new Error(`cannot slice ${startMarker} before ${endMarker}`);
  }
  return src.slice(start, end);
}

const code =
  sliceBetween("function evidenceReportHref", "function renderCareHistory") +
  sliceBetween("function renderCareHistory", "async function loadPersistedDog");

function createDocument() {
  const nodes = new Map();
  function make(tag) {
    const node = {
      tag,
      _id: "",
      attributes: {},
      children: [],
      parent: null,
      textContent: "",
      href: "",
      innerHTML: "",
      setAttribute(key, value) {
        this.attributes[key] = value;
      },
      getAttribute(key) {
        return this.attributes[key];
      },
      appendChild(child) {
        child.parent = this;
        this.children.push(child);
        return child;
      },
      insertBefore(child, reference) {
        child.parent = this;
        const index = this.children.indexOf(reference);
        if (index < 0) this.children.push(child);
        else this.children.splice(index, 0, child);
        return child;
      },
      remove() {
        if (this._id) nodes.delete(this._id);
        if (this.parent) {
          this.parent.children = this.parent.children.filter((child) => child !== this);
        }
        this.parent = null;
      },
    };
    Object.defineProperty(node, "id", {
      get() {
        return this._id;
      },
      set(value) {
        if (this._id) nodes.delete(this._id);
        this._id = value || "";
        if (this._id) nodes.set(this._id, this);
      },
    });
    return node;
  }

  const panel = make("section");
  const list = make("ul");
  panel.id = "care-history-panel";
  list.id = "care-history-list";
  panel.appendChild(list);

  return {
    panel,
    document: {
      getElementById(id) {
        return nodes.get(id) || null;
      },
      createElement(tag) {
        return make(tag);
      },
    },
    links() {
      return panel.children
        .filter((child) => child.tag === "a")
        .map((child) => ({ id: child.id, href: child.href, text: child.textContent }));
    },
  };
}

const dom = createDocument();
const context = {
  URLSearchParams,
  document: dom.document,
  $(id) {
    return dom.document.getElementById(id);
  },
};
vm.runInNewContext(code, context);

function snapshot() {
  return {
    dataDogId: dom.panel.getAttribute("data-dog-id"),
    links: dom.links(),
    events: dom.panel.children.find((child) => child.id === "care-history-list").children.length,
  };
}

const result = {
  plain: context.evidenceReportHref("dog-123"),
  encoded: context.evidenceReportHref("dog 123&id"),
};
context.renderCareHistory("dog-123", [{ event_id: "evt-1", event_type: "SYSTEM_EVENT" }]);
result.persisted = snapshot();
context.renderCareHistory("dog-123", [{ event_id: "evt-1" }]);
result.renderedAgain = snapshot();
context.renderCareHistory("", []);
result.cleared = snapshot();

process.stdout.write(JSON.stringify(result));
