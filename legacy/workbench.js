/* Wagtopia unified demo — presentation only. Packages come from the backend. */
(function () {
  "use strict";

  var API_BASE = window.location.origin;
  var WORKBENCH_PATH = "/api/v1/presentation/workbench";
  var NA = "NOT AVAILABLE FROM RUNTIME";
  var DEMO_PROFILE = Object.freeze({
    name: "Dolly",
    pet_name: "Dolly",
    breeds: ["Labrador Retriever", "Golden Retriever"],
    primary_breed: "Labrador Retriever",
    secondary_breed: "Golden Retriever",
    birthday: "2021-04-15",
    weight: 30,
    sex: "Female",
    activity_level: "Moderate",
    current_environment: "Temperate Outdoor",
    observed_conditions: ["joint_stiffness", "itching"]
  });

  var currentAnalysis = null;
  var currentRole = "customer";
  var analysisRunCount = 0;
  var demoOrdinal = 0;
  var showAllOptions = true;
  var selectedBundleId = "";
  var compareIds = {};

  function nextCorrelationId() {
    demoOrdinal += 1;
    return "omega97-demo-" + String(demoOrdinal).padStart(3, "0");
  }

  function esc(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function isMissing(value) {
    return value == null || value === "" || value === NA;
  }

  function display(value, fallback) {
    if (isMissing(value)) return fallback || "—";
    if (Array.isArray(value)) return value.length ? value.join(", ") : fallback || "—";
    return String(value);
  }

  function formValue(value) {
    if (isMissing(value)) return "";
    return String(value);
  }

  function yen(value) {
    if (typeof value === "number" && isFinite(value)) {
      return "¥" + Math.round(value).toLocaleString();
    }
    return display(value);
  }

  function $(id) {
    return document.getElementById(id);
  }

  function packageIds(rolePayload) {
    var packages = rolePackages(rolePayload);
    var ids = [];
    packages.forEach(function (pkg) {
      (pkg.products || []).forEach(function (item) {
        if (item && item.product_id && item.product_id !== NA) ids.push(String(item.product_id));
      });
    });
    return ids;
  }

  function rolePackages(rolePayload) {
    if (!rolePayload) return [];
    if (Array.isArray(rolePayload.package_composition)) return rolePayload.package_composition;
    if (rolePayload.wellness && Array.isArray(rolePayload.wellness.package_composition)) {
      return rolePayload.wellness.package_composition;
    }
    if (rolePayload.portfolio && Array.isArray(rolePayload.portfolio.package_composition)) {
      return rolePayload.portfolio.package_composition;
    }
    if (rolePayload.package_optimization && Array.isArray(rolePayload.package_optimization.composition)) {
      return rolePayload.package_optimization.composition;
    }
    return [];
  }

  function fillForm(profile) {
    var form = $("intake-form");
    if (!form) return;
    form.elements.name.value = profile.name || profile.pet_name || "";
    form.elements.primary_breed.value = profile.primary_breed || (profile.breeds && profile.breeds[0]) || "";
    form.elements.secondary_breed.value = profile.secondary_breed || (profile.breeds && profile.breeds[1]) || "";
    form.elements.birthday.value = profile.birthday || "";
    form.elements.weight.value = profile.weight != null ? profile.weight : "";
    form.elements.sex.value = profile.sex || "";
    form.elements.activity_level.value = profile.activity_level || "";
    form.elements.current_environment.value = profile.current_environment || "";
    form.elements.observed_conditions.value = (profile.observed_conditions || []).join(", ");
  }

  function readForm() {
    var form = $("intake-form");
    var observed = String(form.elements.observed_conditions.value || "")
      .split(",")
      .map(function (item) { return item.trim(); })
      .filter(Boolean);
    var primary = String(form.elements.primary_breed.value || "").trim();
    var secondary = String(form.elements.secondary_breed.value || "").trim();
    var breeds = [primary, secondary].filter(Boolean);
    return {
      name: String(form.elements.name.value || "").trim() || "Dolly",
      pet_name: String(form.elements.name.value || "").trim() || "Dolly",
      breeds: breeds,
      primary_breed: primary,
      secondary_breed: secondary || undefined,
      birthday: form.elements.birthday.value || undefined,
      weight: form.elements.weight.value ? Number(form.elements.weight.value) : undefined,
      sex: form.elements.sex.value || undefined,
      activity_level: form.elements.activity_level.value || undefined,
      current_environment: form.elements.current_environment.value || undefined,
      observed_conditions: observed,
      monthly_budget: form.elements.monthly_budget && form.elements.monthly_budget.value
        ? Number(form.elements.monthly_budget.value)
        : undefined,
      notes: String(form.elements.notes.value || "").trim() || undefined
    };
  }

  function roleContext() {
    var groomerObs = document.getElementById("groomer-observations");
    var groomerFlags = document.getElementById("groomer-flags");
    var businessSegment = document.getElementById("business-segment");
    var flags = groomerFlags
      ? String(groomerFlags.value || "").split(",").map(function (item) { return item.trim(); }).filter(Boolean)
      : [];
    return {
      groomer: {
        observations: groomerObs ? String(groomerObs.value || "").trim() : "",
        observed_conditions: flags
      },
      business: {
        segment: businessSegment ? String(businessSegment.value || "").trim() : ""
      }
    };
  }

  function setError(message) {
    var box = $("workbench-error");
    if (!message) {
      box.hidden = true;
      box.textContent = "";
      return;
    }
    box.hidden = false;
    box.textContent = message;
  }

  function setStatus(message) {
    var box = $("workbench-status");
    box.hidden = !message;
    box.textContent = message || "";
  }

  function switchRole(role) {
    currentRole = role;
    document.querySelectorAll(".wb-role").forEach(function (btn) {
      btn.classList.toggle("is-active", btn.getAttribute("data-role") === role);
    });
    document.querySelectorAll(".wb-view").forEach(function (panel) {
      var active = panel.getAttribute("data-view") === role;
      panel.hidden = !active;
      panel.setAttribute("aria-hidden", active ? "false" : "true");
      panel.classList.toggle("is-active", active);
    });
    renderRoleView();
  }

  function emptyState(role) {
    return '<div class="wb-empty">Run analysis to project this ' + esc(role) + " view from the canonical result.</div>";
  }

  function num(value, digits) {
    if (typeof value !== "number" || !isFinite(value)) return display(value);
    var n = digits == null ? 2 : digits;
    return String(Math.round(value * Math.pow(10, n)) / Math.pow(10, n));
  }

  function searchStats(payload, canonical) {
    return (payload && payload.package_search)
      || ((payload && payload.wellness) && payload.wellness.package_search)
      || ((payload && payload.portfolio) && payload.portfolio.package_search)
      || (((canonical || {}).package_optimization || {}).search)
      || {};
  }

  function statusClass(status) {
    if (status === "FAIL_MINIMUM" || status === "FAIL_MAXIMUM" || status === "DEFICIENT" || status === "EXCESS") return "wb-fail";
    if (status === "NEAR_MAXIMUM") return "wb-near";
    if (status === "LOW") return "wb-low";
    return "wb-pass";
  }
  function productName(item, opts) {
    opts = opts || {};
    if (!item) return "Unnamed product";
    var name = item.product_name || item.name;
    if (isMissing(name)) name = "";
    if (opts.showInternalId && item.product_id) {
      return name ? (name + " — " + item.product_id) : String(item.product_id);
    }
    return name || "Unnamed product";
  }

  function productNames(opt, opts) {
    var products = (opt && opt.products) || [];
    if (products.length) {
      return products.map(function (item) { return productName(item, opts); });
    }
    return ((opt && opt.display_product_names) || []).filter(Boolean);
  }

  function productNamesLine(opt, opts) {
    return productNames(opt, opts).join(" + ");
  }

  function productListHtml(opt, opts) {
    var names = productNames(opt, opts);
    if (!names.length) return '<p class="wb-muted">No product names in this bundle.</p>';
    return '<div class="wb-product-list">' + names.map(function (name) {
      return "<div>" + esc(name) + "</div>";
    }).join("") + "</div>";
  }

  function pathwayChips(opt) {
    var paths = opt.preventative_pathways || [];
    if (paths.length) {
      return '<div class="wb-chips">' + paths.map(function (item) {
        return '<span class="wb-chip">♥ ' + esc(display(item.label || item.pathway)) + "</span>";
      }).join("") + "</div>";
    }
    return "";
  }

  function coverageChecks(opt) {
    var minP = opt.minimums_passed;
    var minT = opt.minimums_total;
    var maxP = opt.maximums_passed;
    var maxT = opt.maximums_total;
    var minText = (minP != null && minT != null) ? (minP + "/" + minT + " minimums met") : "modeled minimums met";
    var maxText = (maxP != null && maxT != null) ? (maxP + "/" + maxT + " maximums respected") : "modeled maximums respected";
    return '<p class="wb-checks">✓ ' + esc(minText) + "<br>✓ " + esc(maxText) + "</p>";
  }

  function nutrientStatusText(row) {
    var label = row.status_label || row.status;
    if (row.status === "FAIL_MINIMUM" || row.status === "FAIL_MAXIMUM") return "✗ " + display(label);
    if (row.status === "NOT_MODELED") return display(label);
    return "✓ " + display(label);
  }

  var nutritionStore = {};
  var selectedBundleForNutrition = null;

  function renderNutritionFacts(opt, id, opts) {
    var rows = (opt.nutrition_ledger && opt.nutrition_ledger.nutrients) || opt.nutrition_facts || opt.nutrient_rows || [];
    if (!rows.length) return "";
    var nameOpts = { showInternalId: currentRole === "developer" };
    var densityId = id + "-density";
    var contribId = id + "-contrib";
    var body = rows.map(function (row) {
      var star = row.breed_recommended || row.star ? "*" : "";
      var daily = row.actual_per_day != null ? row.actual_per_day : row.daily_amount;
      var reqDaily = row.required_daily_min != null ? row.required_daily_min : row.daily_minimum_equivalent;
      var maxDaily = row.maximum_daily_amount != null ? row.maximum_daily_amount : row.daily_maximum_equivalent;
      var maxText = row.maximum_copy
        || ((row.maximum_specified || maxDaily != null) ? (num(maxDaily) + " " + display(row.daily_unit || "")) : "—");
      var minText = (reqDaily != null)
        ? (num(reqDaily) + " " + display(row.daily_unit))
        : (row.minimum_copy || "—");
      var cover = row.percent_of_minimum != null ? (Math.round(row.percent_of_minimum) + "%") : "—";
      return "<tr class=\"" + statusClass(row.status) + "\"><td>" + esc(display(row.display || row.nutrient_name || row.nutrient)) + star + "</td><td>" +
        esc(num(daily)) + " " + esc(display(row.daily_unit)) + "</td><td>" +
        esc(minText) +
        "</td><td>" + esc(maxText) + "</td><td>" + esc(cover) + "</td><td>" + esc(nutrientStatusText(row)) + "</td></tr>";
    }).join("");
    var products = opt.products || [];
    var contrib = products.map(function (item) {
      return "<li><strong>" + esc(productName(item, nameOpts)) + "</strong> · " +
        esc(yen(item.monthly_cost)) + "/mo · daily DM " + esc(num(item.daily_dm_g != null ? item.daily_dm_g : item.daily_amount)) + " g" +
        "<br>" + esc(display(item.selection_reason, "Included by the ranked optimizer.")) + "</li>";
    }).join("");
    var legend = (opt.tier === "balanced" || opt.tier === "optimal")
      ? '<p class="wb-legend">* Breed-specific preventative target</p>'
      : "";
    var dmG = opt.daily_dm_g != null ? opt.daily_dm_g : (opt.nutrition_ledger && opt.nutrition_ledger.daily_dm_g);
    var basis = display((opt.nutrition_ledger && opt.nutrition_ledger.daily_requirement_note) || "Dry matter basis. Required daily amount is derived from modeled daily dry-matter intake × source density.");
    return (
      "<h2 id=\"nutrition-modal-title\">Nutrition Facts</h2>" +
      "<p class=\"wb-facts-kicker\">Daily Care Package</p>" +
      "<p>Products: " + esc(productNamesLine(opt, nameOpts)) + "</p>" +
      "<p>Daily package amount: " + esc(num(dmG)) + " g/day</p>" +
      '<p class="wb-muted">' + esc(basis) + "</p>" +
      '<div class="wb-facts-scroll"><table class="wb-table wb-facts-table"><thead><tr><th>Nutrient</th><th>Per Package</th><th>Required Daily</th><th>Maximum Daily</th><th>Coverage</th><th>Status</th></tr></thead><tbody>' +
      body + "</tbody></table></div>" + legend +
      (contrib ? ("<h3>What each product contributes</h3><ul>" + contrib + "</ul>") : "")
    );
  }

  function closeNutritionModal() {
    selectedBundleForNutrition = null;
    var modal = $("nutrition-modal");
    var body = $("nutrition-modal-body");
    if (body) body.innerHTML = "";
    if (modal) modal.hidden = true;
    document.body.classList.remove("wb-modal-open");
  }

  function openNutritionModal(key) {
    var stored = nutritionStore[key];
    var modal = $("nutrition-modal");
    var body = $("nutrition-modal-body");
    if (!stored || !modal || !body) return;
    selectedBundleForNutrition = key;
    body.innerHTML = renderNutritionFacts(stored.opt, key, stored.opts);
    modal.hidden = false;
    document.body.classList.add("wb-modal-open");
    var closeBtn = modal.querySelector(".wb-modal-close");
    if (closeBtn) closeBtn.focus();
  }

  function renderBundleReasoning(opt, id) {
    var r = opt.bundle_reasoning || {};
    var preventative = r.preventative_care || [];
    var html = '<div class="wb-why-body wb-reason-panel" id="' + id + '" hidden>';
    html += "<h4>Why this bundle?</h4>";
    html += "<h5>Health fit</h5><ul>" +
      (r.health_fit || []).map(function (line) { return "<li>" + esc(line) + "</li>"; }).join("") +
      "</ul>";
    html += "<h5>Nutrition</h5><ul>" +
      (r.nutrition || r.baseline_nutrition || []).map(function (line) { return "<li>" + esc(line) + "</li>"; }).join("") +
      "</ul>";
    if (preventative.length) {
      html += "<h5>Preventative care</h5>";
      preventative.forEach(function (item) {
        html += "<p><strong>" + esc(display(item.label || item.pathway)) + "</strong></p>";
        html += "<p>" + esc(display(item.copy)) + "</p>";
        var contrib = (item.contributing_products || []).map(function (prod) {
          return esc(display(prod.product_name || prod.role));
        }).join(", ");
        if (contrib) html += '<p class="wb-muted">Contributing products: ' + contrib + "</p>";
        var targets = (item.preventative_targets || []).map(function (t) { return t.display || t.nutrient_id; }).join(", ");
        if (targets) html += '<p class="wb-muted">Preventative targets: ' + esc(targets) + "</p>";
      });
    }
    html += "<h5>Budget</h5><ul>" +
      (r.budget || []).map(function (line) { return "<li>" + esc(line) + "</li>"; }).join("") +
      "</ul>";
    html += "<h5>Ranking</h5><ul>" +
      (r.ranking || []).map(function (line) { return "<li>" + esc(line) + "</li>"; }).join("") +
      (opt.ranking_rule ? "<li>" + esc(opt.ranking_rule) + "</li>" : "") +
      "</ul>";
    html += "<h5>Why it beat alternatives</h5><ul>" +
      (r.why_outranked || opt.why_outranked || []).map(function (line) { return "<li>" + esc(line) + "</li>"; }).join("") +
      "</ul>";
    var evidence = (opt.preventative_pathways || []).filter(function (item) {
      return item.scientific_quote || item.paper_name || item.paper_link;
    });
    if (evidence.length) {
      var evId = id + "-evidence";
      html += '<button type="button" class="wb-action" data-toggle="' + evId + '">Scientific basis</button>';
      html += '<div class="wb-why-body" id="' + evId + '" hidden>' + evidence.map(function (item) {
        return "<p><strong>" + esc(display(item.label || item.pathway)) + "</strong><br>" +
          esc(display(item.scientific_quote)) + "<br>" +
          esc(display(item.paper_name)) + " " + esc(display(item.publication_year)) +
          (item.paper_link ? ' · <a href="' + esc(item.paper_link) + '" target="_blank" rel="noreferrer">paper</a>' : "") +
          "</p>";
      }).join("") + "</div>";
    }
    html += "</div>";
    return html;
  }

  function renderWhyBalanced(briefing) {
    if (!briefing || !(briefing.pathways || []).length) return "";
    var dog = display(briefing.dog_name, "This dog");
    var breeds = display(briefing.breeds);
    var html = '<article class="wb-card wb-briefing"><h2>' + esc(display(briefing.title, "WHY BALANCED CARE?")) + "</h2>";
    html += "<p>" + esc(dog) + "'s breed profile: " + esc(breeds) + "</p>";
    html += "<p>The biological analysis identified these preventative-care pathways as priorities:</p>";
    html += '<div class="wb-path-grid">' + (briefing.pathways || []).map(function (path) {
      return '<div class="wb-path-card"><h3>' + esc(display(path.label || path.pathway)) + "</h3>" +
        "<p>Associated with the dog's modeled breed profile.</p>" +
        "<p>" + esc(display(path.copy)) + "</p></div>";
    }).join("") + "</div>";
    html += '<p class="wb-muted">' + esc(display(briefing.disclaimer)) + "</p>";
    html += '<p><a class="wb-link" href="' + esc(briefing.health_analysis_anchor || "#health-analysis") + '">' +
      esc(display(briefing.health_analysis_label, "View Health Analysis →")) + "</a></p>";
    if (briefing.demo_synthetic) {
      html += '<p class="wb-banner">DEMO SYNTHETIC BREED-CARE MODEL — not warehouse evidence</p>';
    }
    html += "<h3>TARGETED CARE TARGETS</h3>";
    html += (briefing.pathways || []).map(function (path) {
      var targets = (path.preventative_targets || []).map(function (t) { return t.display || t.nutrient_id; }).join(", ");
      return "<p><strong>" + esc(display(path.label || path.pathway)) + "</strong><br>" +
        (targets ? "Target nutrients / ingredients: " + esc(targets) : "Pathway product function is the preventative target.") +
        "</p>";
    }).join("");
    html += "<p>Balanced Care therefore prioritizes nutritional/product targets associated with these pathways.</p></article>";
    return html;
  }

  function renderHealthAnalysis(report) {
    if (!report) return "";
    var html = '<article class="wb-card" id="health-analysis"><h2>' + esc(display(report.title, "Health Analysis")) + "</h2>";
    html += '<p class="wb-muted">' + esc(display(report.disclaimer, "These are preventative considerations. They do not mean your dog currently has these conditions.")) + "</p>";
    html += "<p>" + esc(display(report.warehouse_status, "Not available from current scientific warehouse.")) + "</p>";
    (report.findings || []).forEach(function (row) {
      html += '<div class="wb-finding"><h3>' + esc(display(row.label || row.condition || row.title || row.pathway)) + "</h3>";
      html += "<p><strong>Why this matters</strong><br>" + esc(display(row.why_this_matters, "Your dog's breed profile is associated with this condition based on warehouse evidence.")) + "</p>";
      html += "<p><strong>Observed prevalence</strong><br>";
      var byBreed = row.observed_by_breed || [];
      if (byBreed.length) {
        html += byBreed.map(function (item) {
          var pct = item.percent != null ? (item.percent + "%") : "NOT_AVAILABLE";
          return esc(display(item.breed)) + ": " + esc(pct);
        }).join("<br>");
      } else {
        html += esc(display(row.observed_prevalence, "NOT_AVAILABLE"));
      }
      html += "</p>";
      html += "<p><strong>Estimated prevalence</strong><br>" + esc(display(row.estimated_prevalence, "NOT_AVAILABLE")) + "</p>";
      html += "<p><strong>Evidence</strong><br>";
      if (row.scientific_quote) html += esc(row.scientific_quote) + "<br>";
      html += esc(display(row.paper_name));
      if (row.publication_year) html += " (" + esc(String(row.publication_year)) + ")";
      if (row.paper_link) html += ' · <a href="' + esc(row.paper_link) + '" target="_blank" rel="noreferrer">paper</a>';
      html += "</p>";
      html += "<p><strong>Preventative implication</strong><br>" +
        esc(display(row.preventative_implication || row.preventative_relevance,
          "This package prioritizes nutritional support associated with this pathway.")) + "</p>";
      html += "</div>";
    });
    if ((report.mixed_breed_flagged || []).length) {
      html += "<h3>Mixed-breed rows requiring validation</h3>";
      (report.mixed_breed_flagged || []).forEach(function (item) {
        html += "<p>" + esc(display(item.trait_a)) + " × " + esc(display(item.trait_b)) +
          " → " + esc(display(item.condition)) + " (" + esc(display(item.status)) + ")</p>";
      });
    }
    if (!(report.findings || []).length) {
      html += "<p>Not available from current scientific warehouse.</p>";
    }
    html += "</article>";
    return html;
  }

  function renderOptions(optionsByTier, opts) {
    opts = opts || {};
    var stats = opts.stats || {};
    var tierValid = stats.tier_valid_counts || {};
    var displayed = stats.displayed_count || {};
    var tiers = [
      { key: "essential", title: "Essential Care", blurb: "Baseline nutritional care" },
      { key: "balanced", title: "Balanced Care", blurb: "Baseline + breed-specific preventive considerations" },
      { key: "optimal", title: "Optimal Care", blurb: "Most balanced overall care" }
    ];
    var html = "";
    if (stats.evaluated_count != null && stats.valid_count != null) {
      html += '<article class="wb-card"><h2>Evaluated combinations</h2><p>' +
        "The optimizer evaluated " + esc(display(stats.evaluated_count)) +
        " combinations, rejected those that failed nutritional or structural constraints, and ranked the remaining valid combinations by care level" +
        (opts.budgetStatus ? " and budget." : ".") +
        "</p><p>" +
        esc(display(tierValid.essential)) + " valid Essential · " +
        esc(display(tierValid.balanced)) + " valid Balanced · " +
        esc(display(tierValid.optimal)) + " valid Optimal." +
        "</p><p class=\"wb-muted\">Displayed counts are a display limit, not the full valid set. Nutrient-valid total: " +
        esc(display(stats.valid_count)) +
        ". Non-dominated frontier (audit only): " + esc(display(stats.non_dominated_count)) + ".</p></article>";
    }
    tiers.forEach(function (tier) {
      var rows = (optionsByTier && optionsByTier[tier.key]) || [];
      var validN = tierValid[tier.key];
      var shownN = displayed[tier.key] != null ? displayed[tier.key] : rows.length;
      html += "<h2>" + esc(tier.title) + "</h2>";
      html += '<p class="wb-muted">' + esc(tier.blurb) + "</p>";
      if (tier.key === "balanced") html += renderWhyBalanced(opts.briefing);
      if (validN != null) {
        html += "<p>Showing " + esc(String(shownN)) + " of " + esc(String(validN)) + " valid combinations</p>";
      }
      if (!rows.length) {
        var budgetNote = ((tier.key === "balanced" || tier.key === "essential") && opts.budgetStatus === "NO_VALID_BUNDLE_WITHIN_BUDGET")
          ? '<p class="wb-muted">No valid bundle within the stated budget (budget_status = NO_VALID_BUNDLE_WITHIN_BUDGET).</p>'
          : '<p class="wb-muted">No valid bundles for this tier.</p>';
        html += budgetNote;
        return;
      }
      var shown = opts.showAll === false ? rows.slice(0, 8) : rows;
      html += '<div class="wb-packages">';
      shown.forEach(function (opt, idx) {
        var whyId = "why-" + String(opt.bundle_id || (tier.key + "-" + idx)).replace(/\W+/g, "-");
        var nutId = "nut-" + String(opt.bundle_id || (tier.key + "-" + idx)).replace(/\W+/g, "-");
        nutritionStore[opt.bundle_id || nutId] = { opt: opt, opts: opts };
        var selected = selectedBundleId && selectedBundleId === opt.bundle_id;
        var compared = !!compareIds[opt.bundle_id];
        var overBudget = opt.budget_status === "OVER_BUDGET";
        var badge = idx === 0 ? " · RECOMMENDED" : "";
        html +=
          '<article class="wb-card wb-option' + (idx === 0 ? " is-recommended" : "") + (selected ? " is-selected" : "") + '" data-bundle="' + esc(opt.bundle_id || "") + '">' +
            "<h3>OPTION " + (opt.rank || (idx + 1)) + badge + (selected ? " · selected" : "") + "</h3>" +
            '<p class="wb-price">' + esc(yen(opt.monthly_cost)) + "</p>" +
            productListHtml(opt, opts) +
            coverageChecks(opt) +
            pathwayChips(opt) +
            (overBudget && tier.key !== "optimal" ? '<p class="wb-fail">Over your budget</p>' :
              (opt.budget_status === "WITHIN_BUDGET" ? '<p class="wb-pass">Fits budget</p>' :
                (overBudget && tier.key === "optimal" ? '<p class="wb-muted">Above stated budget (Optimal has no ceiling)</p>' : ""))) +
            '<div class="wb-actions">' +
              '<button type="button" class="wb-action wb-why-btn" data-toggle="' + whyId + '">Why this bundle?</button>' +
              '<button type="button" class="wb-action wb-nut-btn" data-open-nutrition="' + esc(opt.bundle_id || nutId) + '" aria-label="Nutrition Facts">View nutrition</button>' +
            "</div>" +
            renderBundleReasoning(opt, whyId) +
            '<label class="wb-check"><input type="checkbox" data-compare-bundle="' + esc(opt.bundle_id || "") + '"' +
              (compared ? " checked" : "") + "> Compare</label>" +
            (overBudget && tier.key !== "optimal"
              ? '<p class="wb-muted">Not selectable — outside the stated budget ceiling.</p>'
              : '<button type="button" class="wb-ghost" data-select-bundle="' + esc(opt.bundle_id || "") + '">' +
                  (selected ? "Selected" : "Choose") +
                "</button>") +
          "</article>";
      });
      html += "</div>";
    });
    html += '<p><button type="button" class="wb-ghost" id="compare-bundles">Compare selected bundles</button></p>';
    html += '<div class="wb-card" id="compare-panel" hidden></div>';
    return html;
  }

  function renderCompare(optionsByTier) {
    var wanted = Object.keys(compareIds).filter(function (id) { return compareIds[id]; });
    var rows = [];
    ["essential", "balanced", "optimal"].forEach(function (tier) {
      ((optionsByTier && optionsByTier[tier]) || []).forEach(function (opt) {
        if (wanted.indexOf(opt.bundle_id) >= 0) rows.push(opt);
      });
    });
    if (!rows.length) return "<p>Select two or more bundles with Compare, then click Compare selected bundles.</p>";
    var nutrientNames = [];
    rows.forEach(function (opt) {
      ((opt.nutrition_facts || [])).forEach(function (row) {
        var name = row.display || row.nutrient;
        if (nutrientNames.indexOf(name) < 0) nutrientNames.push(name);
      });
    });
    var head = "<tr><th></th>" + rows.map(function (opt) {
      return "<th>" + esc(display(opt.tier)) + " · " + esc(productNamesLine(opt)) + "</th>";
    }).join("") + "</tr>";
    function cells(fn) {
      return rows.map(function (opt) { return "<td>" + fn(opt) + "</td>"; }).join("");
    }
    var body = "<tr><th>Price</th>" + cells(function (opt) { return esc(yen(opt.monthly_cost)); }) + "</tr>";
    body += "<tr><th>Products</th>" + cells(function (opt) { return esc(productNames(opt).join(", ")); }) + "</tr>";
    body += "<tr><th>Budget</th>" + cells(function (opt) { return esc(display(opt.budget_status)); }) + "</tr>";
    body += "<tr><th>Care pathways</th>" + cells(function (opt) { return esc((opt.care_pathways || []).join(", ") || "—"); }) + "</tr>";
    body += "<tr><th>Minimums</th>" + cells(function (opt) {
      return esc((opt.minimums_passed != null) ? (opt.minimums_passed + " / " + opt.minimums_total) : "—");
    }) + "</tr>";
    nutrientNames.slice(0, 12).forEach(function (name) {
      body += "<tr><th>" + esc(name) + "</th>" + cells(function (opt) {
        var hit = (opt.nutrition_facts || []).filter(function (r) { return (r.display || r.nutrient) === name; })[0] || {};
        var pct = hit.percent_of_minimum != null ? (Math.round(hit.percent_of_minimum) + "%") : "—";
        return esc(num(hit.actual_per_day != null ? hit.actual_per_day : hit.daily_amount)) + " · " + esc(pct);
      }) + "</tr>";
    });
    return "<h3>Compare bundles</h3><table class=\"wb-table\"><thead>" + head + "</thead><tbody>" + body + "</tbody></table>";
  }

  function renderExplorer(search) {
    var explorer = (search && search.explorer) || {};
    var failures = (search && search.failures_by_nutrient) || {};
    var counts = (search && search.constraint_failures) || {};
    var funnel = (search && search.filter_funnel) || {};
    function sampleList(rows) {
      if (!rows || !rows.length) return '<p class="wb-muted">No samples stored for this bucket.</p>';
      return rows.map(function (row) {
        var extra = "";
        if (row.exceeded_maximums && row.exceeded_maximums.length) extra += " · " + esc(JSON.stringify(row.exceeded_maximums));
        if (row.failed_minimums && row.failed_minimums.length) extra += " · " + esc(JSON.stringify(row.failed_minimums));
        return "<p><code>" + esc((row.product_ids || []).join(" + ")) + "</code> → " +
          esc(display(row.reason)) + " · " + esc(display(row.constraint_status)) +
          " · " + esc(display(row.decision)) + extra + "</p>";
      }).join("");
    }
    function nutrientCounts(obj) {
      var keys = Object.keys(obj || {});
      if (!keys.length) return '<p class="wb-muted">None</p>';
      return "<ul>" + keys.map(function (k) {
        return "<li>" + esc(k) + ": " + esc(String(obj[k])) + "</li>";
      }).join("") + "</ul>";
    }
    return (
      '<article class="wb-card"><h2>Exhaustive search explorer</h2>' +
        "<p>Combinations evaluated: " + esc(display(search && search.evaluated_count)) +
          " · expected 2^N−1: " + esc(display(search && search.total_possible_subsets)) + "</p>" +
        '<div class="wb-kv">' +
          "<span>ALL</span><span>" + esc(display(search && search.evaluated_count)) + "</span>" +
          "<span>VALID</span><span>" + esc(display(search && search.valid_count)) + "</span>" +
          "<span>MINIMUM FAILURES</span><span>" + esc(display(counts.minimum_nutrient_failure)) + "</span>" +
          "<span>MAXIMUM FAILURES</span><span>" + esc(display(counts.maximum_nutrient_exceeded)) + "</span>" +
          "<span>MISSING STAPLE</span><span>" + esc(display(counts.missing_required_category)) + "</span>" +
          "<span>BUDGET FAILURES</span><span>" + esc(display(counts.budget_exceeded)) + "</span>" +
          "<span>NON-DOMINATED</span><span>" + esc(display(search && search.non_dominated_count)) + "</span>" +
        "</div>" +
        "<h3>Minimum failures by nutrient</h3>" + nutrientCounts(failures.minimum) +
        "<h3>Maximum failures by nutrient</h3>" + nutrientCounts(failures.maximum) +
        '<details class="wb-node"><summary>VALID (displayed options are ranked; this is not the full valid set)</summary>' +
          "<p class=\"wb-muted\">" + esc(display(funnel.note)) + "</p></details>" +
        '<details class="wb-node"><summary>MINIMUM FAILURES — samples</summary>' + sampleList(explorer.minimum_failures) + "</details>" +
        '<details class="wb-node"><summary>MAXIMUM FAILURES — samples</summary>' + sampleList(explorer.maximum_failures) + "</details>" +
        '<details class="wb-node"><summary>MISSING STAPLE — samples</summary>' + sampleList(explorer.missing_staple) + "</details>" +
        '<details class="wb-node"><summary>BUDGET FAILURES — samples</summary>' + sampleList(explorer.budget_failures) + "</details>" +
        '<details class="wb-node"><summary>NON-DOMINATED sample</summary>' +
          ((search && search.non_dominated_sample) || []).map(function (row) {
            return "<p><code>" + esc((row.product_ids || []).join(" + ")) + "</code> · " + esc(yen(row.monthly_cost)) + "</p>";
          }).join("") +
        "</details>" +
      "</article>"
    );
  }

  function renderSearchAudit(payload) {
    var opt = (payload && payload.package_optimization) || {};
    var search = opt.search || {};
    var failures = search.constraint_failures || {};
    var funnel = search.filter_funnel || {};
    return (
      '<article class="wb-card"><h2>Package search</h2>' +
        '<p class="wb-funnel">' +
          esc(display(funnel.generated != null ? funnel.generated : search.total_possible_subsets)) +
          " ↓ " +
          esc(display(funnel.life_stage_species_structurally_eligible != null ? funnel.life_stage_species_structurally_eligible : search.structurally_eligible)) +
          " structurally eligible ↓ " +
          esc(display(failures.minimum_nutrient_failure)) +
          " minimum failures ↓ " +
          esc(display(failures.maximum_nutrient_exceeded)) +
          " maximum failures ↓ " +
          esc(display(funnel.nutrient_valid != null ? funnel.nutrient_valid : search.valid_count)) +
          " valid ↓ " +
          esc(display(funnel.non_dominated != null ? funnel.non_dominated : search.non_dominated_count)) +
          " non-dominated ↓ " +
          esc(display(((search.returned_options || {}).essential || 0) + ((search.returned_options || {}).balanced || 0) + ((search.returned_options || {}).optimal || 0))) +
          " returned</p>" +
        '<div class="wb-kv">' +
          "<span>Search method</span><span>" + esc(display(search.search_method, "EXHAUSTIVE_ENUMERATION")) + "</span>" +
          "<span>Optimizer</span><span>PACKAGE_OPTIMIZER_V2_1</span>" +
          "<span>Raw candidates</span><span>" + esc(display(funnel.generated != null ? funnel.generated : search.total_possible_subsets)) + "</span>" +
          "<span>Structurally eligible</span><span>" + esc(display(funnel.life_stage_species_structurally_eligible != null ? funnel.life_stage_species_structurally_eligible : search.structurally_eligible)) + "</span>" +
          "<span>Nutrient calculated</span><span>" + esc(display(funnel.nutrient_calculated != null ? funnel.nutrient_calculated : search.evaluated_count)) + "</span>" +
          "<span>Passed minimums</span><span>" + esc(display(funnel.passed_minimum_filter)) + "</span>" +
          "<span>Passed maximums</span><span>" + esc(display(funnel.passed_maximum_filter)) + "</span>" +
          "<span>Nutrient valid</span><span>" + esc(display(funnel.nutrient_valid != null ? funnel.nutrient_valid : search.valid_count)) + "</span>" +
          "<span>Essential valid</span><span>" + esc(display((search.tier_valid_counts || {}).essential != null ? search.tier_valid_counts.essential : funnel.satisfy_essential)) + "</span>" +
          "<span>Balanced valid</span><span>" + esc(display((search.tier_valid_counts || {}).balanced != null ? search.tier_valid_counts.balanced : funnel.satisfy_balanced)) + "</span>" +
          "<span>Optimal valid</span><span>" + esc(display((search.tier_valid_counts || {}).optimal != null ? search.tier_valid_counts.optimal : funnel.satisfy_optimal)) + "</span>" +
          "<span>Non-dominated (audit)</span><span>" + esc(display(funnel.non_dominated != null ? funnel.non_dominated : search.non_dominated_count)) + "</span>" +
          "<span>Displayed</span><span>" + esc(display(JSON.stringify(search.displayed_count || search.returned_options || {}))) + "</span>" +
          "<span>Dominance used as display filter</span><span>" + esc(display(search.dominance_is_display_filter)) + "</span>" +
          "<span>Rejected</span><span>" + esc(display(search.rejected_count)) + "</span>" +
          "<span>Min failures</span><span>" + esc(display(failures.minimum_nutrient_failure)) + "</span>" +
          "<span>Max failures</span><span>" + esc(display(failures.maximum_nutrient_exceeded)) + "</span>" +
          "<span>Missing data</span><span>" + esc(display(failures.missing_nutrient_data)) + "</span>" +
          "<span>Category</span><span>" + esc(display(failures.missing_required_category)) + "</span>" +
          "<span>Budget (nutrient-valid over budget)</span><span>" + esc(display(failures.budget_exceeded)) + "</span>" +
          "<span>Essential options</span><span>" + esc(display((search.returned_options || {}).essential)) + "</span>" +
          "<span>Balanced options</span><span>" + esc(display((search.returned_options || {}).balanced)) + "</span>" +
          "<span>Optimal options</span><span>" + esc(display((search.returned_options || {}).optimal)) + "</span>" +
          "<span>Balanced budget status</span><span>" + esc(display(search.balanced_budget_status)) + "</span>" +
          "<span>LLM used</span><span>false</span>" +
          "<span>Synthetic demo data</span><span>" + esc(display(search.synthetic_demo_data)) + "</span>" +
        "</div></article>"
    );
  }

  function renderNutrientTable(rows) {
    if (!rows || !rows.length) return '<p class="wb-muted">No nutrient rows on this bundle.</p>';
    return '<table class="wb-table"><thead><tr><th>Nutrient</th><th>Min</th><th>Max</th><th>Actual</th><th>Min margin</th><th>Max margin</th><th>Status</th></tr></thead><tbody>' +
      rows.map(function (row) {
        return "<tr><td>" + esc(row.nutrient) + "</td><td>" + esc(display(row.required_minimum)) +
          "</td><td>" + esc(display(row.allowed_maximum)) + "</td><td>" + esc(display(row.actual)) +
          "</td><td>" + esc(display(row.minimum_margin)) + "</td><td>" + esc(display(row.maximum_margin)) +
          "</td><td>" + esc(display(row.status)) + "</td></tr>";
      }).join("") + "</tbody></table>";
  }

  function renderProvenance(rows) {
    if (!rows || !rows.length) return '<p class="wb-muted">No product provenance on this bundle.</p>';
    return rows.map(function (row) {
      return '<article class="wb-card">' +
        "<h3>" + esc(row.product_id) + " · " + esc(display(row.role)) + "</h3>" +
        "<p>" + esc(display(row.selection_reason)) + "</p>" +
        "<p class=\"wb-muted\">Pathways: " + esc((row.care_pathways || []).join(", ")) + "</p>" +
        "<p>Without this product: valid=" + esc(String(row.still_valid)) +
          " · status=" + esc(display(row.without_constraint_status)) +
          " · coverage=" + esc(display(row.without_care_coverage)) +
          " · cost=" + esc(yen(row.without_monthly_cost)) + "</p>" +
        "<ul>" + (row.marginal_contribution || []).map(function (line) {
          return "<li>" + esc(line) + "</li>";
        }).join("") + "</ul></article>";
    }).join("");
  }

  function renderWhyNot(rows) {
    if (!rows || !rows.length) return '<p class="wb-muted">No why-not rows.</p>';
    return "<ul>" + rows.map(function (row) {
      return "<li><code>" + esc(row.product_id) + "</code> — " + esc((row.reasons || []).join("; ")) +
        " · valid_if_added=" + esc(String(row.valid_if_added)) + "</li>";
    }).join("") + "</ul>";
  }

  function renderContributionMatrix(opt) {
    var rows = opt.nutrient_rows || [];
    if (!rows.length) return "";
    var html = "<h3>Product × nutrient contributions (daily amount)</h3><table class=\"wb-table\"><thead><tr><th>Nutrient</th><th>Min</th><th>Max</th><th>Actual (DM)</th>";
    (opt.product_ids || []).forEach(function (pid) { html += "<th>" + esc(pid) + "</th>"; });
    html += "</tr></thead><tbody>";
    rows.forEach(function (row) {
      html += "<tr><td>" + esc(row.display || row.nutrient) + "</td><td>" + esc(display(row.required_minimum)) +
        "</td><td>" + esc(row.maximum_specified ? display(row.allowed_maximum) : "not specified") +
        "</td><td>" + esc(display(row.actual)) + " " + esc(display(row.status)) + "</td>";
      (opt.product_ids || []).forEach(function (pid) {
        var hit = (row.products_contributing || []).filter(function (c) { return c.product_id === pid; })[0];
        html += "<td>" + esc(hit ? hit.daily_amount : "0") + "</td>";
      });
      html += "</tr>";
    });
    html += "</tbody></table>";
    return html;
  }

  function flattenOptions(optionsByTier) {
    var out = [];
    ["essential", "balanced", "optimal"].forEach(function (tier) {
      ((optionsByTier && optionsByTier[tier]) || []).forEach(function (opt) { out.push(opt); });
    });
    return out;
  }

  function renderDelta(optionsByTier) {
    var all = flattenOptions(optionsByTier);
    if (all.length < 2) return "";
    var a = all[0];
    var b = (optionsByTier.balanced && optionsByTier.balanced[0]) || all[1];
    var idsA = a.product_ids || [];
    var idsB = b.product_ids || [];
    var onlyA = idsA.filter(function (id) { return idsB.indexOf(id) < 0; });
    var onlyB = idsB.filter(function (id) { return idsA.indexOf(id) < 0; });
    var nut = "";
    (a.nutrient_rows || []).slice(0, 8).forEach(function (row) {
      var match = (b.nutrient_rows || []).filter(function (r) { return r.nutrient === row.nutrient; })[0] || {};
      var da = (match.actual != null && row.actual != null) ? (Math.round((match.actual - row.actual) * 1000) / 1000) : "—";
      nut += "<li>" + esc(row.display || row.nutrient) + ": " + esc(display(row.actual)) + " → " + esc(display(match.actual)) + " (Δ " + esc(String(da)) + ")</li>";
    });
    return '<article class="wb-card"><h2>Bundle delta (top Essential vs top Balanced)</h2>' +
      "<p>A: <code>" + esc(idsA.join(" + ")) + "</code> · " + esc(yen(a.monthly_cost)) + "</p>" +
      "<p>B: <code>" + esc(idsB.join(" + ")) + "</code> · " + esc(yen(b.monthly_cost)) + "</p>" +
      "<p>Only in A: " + esc(onlyA.join(", ") || "—") + " · Only in B: " + esc(onlyB.join(", ") || "—") + "</p>" +
      "<p>Care: " + esc((a.care_pathways || []).join(", ") || "—") + " → " + esc((b.care_pathways || []).join(", ") || "—") + "</p>" +
      "<p>Score: " + esc(display(a.overall_score)) + " → " + esc(display(b.overall_score)) + "</p>" +
      "<p class=\"wb-muted\">Deltas subtract backend actuals. The frontend does not recompute nutrients.</p>" +
      "<ul>" + nut + "</ul></article>";
  }

  function renderBundleInspector(optionsByTier, rejections) {
    var html = '<article class="wb-card"><h2>Inspect a returned bundle</h2>' +
      '<p class="wb-muted">Select a ranked option to see nutrients, requirements, margins, cost, and why each product is in the bundle. Rejected combinations are listed below — they never reach Customer.</p>';
    ["essential", "balanced", "optimal"].forEach(function (tier) {
      ((optionsByTier && optionsByTier[tier]) || []).forEach(function (opt, idx) {
        html +=
          '<details class="wb-node"><summary>' + esc(tier.toUpperCase()) + " · Option " + (idx + 1) +
            " · " + esc(opt.bundle_id) + " · " + esc(yen(opt.monthly_cost)) + "/mo · " +
            esc((opt.product_ids || []).join(", ")) +
          "</summary>" +
          '<div class="wb-inspect">' +
            '<div class="wb-kv">' +
              "<span>Constraint</span><span>" + esc(display(opt.constraint_status)) + "</span>" +
              "<span>Monthly</span><span>" + esc(yen(opt.monthly_cost)) + "</span>" +
              "<span>Annual</span><span>" + esc(yen(opt.annual_cost)) + "</span>" +
              "<span>Balance</span><span>" + esc(display(opt.nutrition_balance_score)) + "</span>" +
              "<span>Care coverage</span><span>" + esc(display(opt.care_coverage_score)) + "</span>" +
              "<span>Overall score</span><span>" + esc(display(opt.overall_score)) + "</span>" +
              "<span>Basis</span><span>" + esc(display((opt.nutrient_totals || {}).basis)) + "</span>" +
              "<span>Conversion</span><span>" + esc(display(((opt.nutrient_totals || {}).conversion || {}).protein_pct_dm)) + "</span>" +
              "<span>Synthetic demo data</span><span>" + esc(display(opt.synthetic_demo_data)) + "</span>" +
            "</div>" +
            "<h3>Nutrient constraints</h3>" + renderNutrientTable(opt.nutrient_rows) +
            renderContributionMatrix(opt) +
            "<h3>Why selected</h3><ul>" + (opt.why_selected || []).map(function (line) {
              return "<li>" + esc(line) + "</li>";
            }).join("") + "</ul>" +
            "<p>" + esc(display(opt.why_ranked_here)) + "</p>" +
            "<h3>Why each product is in this bundle</h3>" + renderProvenance(opt.product_provenance) +
            "<h3>Why not other products</h3>" + renderWhyNot(opt.why_not_included) +
            node("Raw bundle JSON", pretty(opt)) +
          "</div></details>";
      });
    });
    html += "</article>";
    if (rejections && rejections.length) {
      html += '<article class="wb-card"><h2>Example rejected combinations</h2><p class="wb-muted">These failed hard constraints and are not Customer options.</p>';
      rejections.forEach(function (row) {
        html += "<p><code>" + esc((row.product_ids || []).join(" + ")) + "</code> → " +
          esc(display(row.reason)) + " · " + esc(display(row.constraint_status));
        if (row.exceeded_maximums && row.exceeded_maximums.length) {
          html += " · " + esc(JSON.stringify(row.exceeded_maximums));
        }
        if (row.failed_minimums && row.failed_minimums.length) {
          html += " · " + esc(JSON.stringify(row.failed_minimums));
        }
        html += "</p>";
      });
      html += "</article>";
    }
    return html;
  }

  function renderPackages(packages, opts) {
    opts = opts || {};
    if (!packages || !packages.length) {
      return '<p class="wb-muted">No packages in this analysis.</p>';
    }
    return '<div class="wb-packages">' + packages.map(function (pkg) {
      var products = pkg.products || [];
      var whyId = "why-" + String(pkg.tier || pkg.package_id || "pkg").replace(/\W+/g, "-");
      var why = products.map(function (item) {
        return "<li><strong>" + esc(display(item.name)) + "</strong> — " + esc(display(item.why_selected, "No selection reason exposed by the optimizer."));
      }).join("");
      return (
        '<article class="wb-card' + (pkg.recommended ? " is-recommended" : "") + '">' +
          "<h3>" + esc(display(pkg.title || pkg.tier)) + (pkg.recommended ? " · recommended" : "") + "</h3>" +
          '<p class="wb-muted">' + esc(display(pkg.purpose, "Algorithmically composed care package.")) + "</p>" +
          products.map(function (item) {
            return '<div class="wb-product"><span>' + esc(display(item.name || item.product_name)) +
              (opts.showIds && item.product_id ? " <code>" + esc(display(item.product_id)) + "</code>" : "") +
              "</span><span>" + esc(yen(item.monthly_cost)) + "</span></div>";
          }).join("") +
          '<p class="wb-price">' + esc(yen(pkg.monthly_cost)) + " / month</p>" +
          "<p>" + esc(yen(pkg.yearly_cost)) + " / year" +
            (isMissing(pkg.savings) ? "" : " · save " + esc(yen(pkg.savings))) +
          "</p>" +
          (opts.why ? (
            '<button type="button" class="wb-action" data-toggle="' + whyId + '">Why this package?</button>' +
            '<div class="wb-why-body" id="' + whyId + '" hidden><ul>' + why + "</ul></div>"
          ) : "") +
        "</article>"
      );
    }).join("") + "</div>";
  }

  function renderCustomer(payload, canonical) {
    var dog = (payload && payload.dog) || {};
    var boundary = (payload && payload.scientific_boundary) || {};
    var insights = ((payload && payload.wellness) || {}).health_insights || [];
    var summary = insights[0] && (insights[0].explanation || insights[0].why || insights[0].title);
    var stats = searchStats(payload && payload.wellness, canonical);
    return (
      '<p class="wb-banner" ' + (payload && payload.demo_catalog ? "" : "hidden") + ">DEMO CATALOG — demonstration data, not scientific evidence. Product nutrient data in this demo are synthetic.</p>" +
      '<div class="wb-grid">' +
        '<article class="wb-card"><h2>Your dog</h2>' +
          '<div class="wb-kv"><span>Name</span><span>' + esc(display(dog.name)) + "</span>" +
          "<span>Breed</span><span>" + esc(display(dog.breeds)) + "</span>" +
          "<span>Weight</span><span>" + esc(display(dog.weight_kg)) + " kg</span>" +
          "<span>Life stage</span><span>" + esc(display(dog.life_stage || dog.age_years)) + "</span>" +
          "<span>Activity</span><span>" + esc(display(dog.activity_level)) + "</span></div></article>" +
        '<article class="wb-card"><h2>Choose your care level</h2>' +
          "<p><strong>Essential</strong> — baseline nutritional care (size, life stage, modeled minima/maxima). No breed-prevention ranking.</p>" +
          "<p><strong>Balanced</strong> — baseline + breed-specific preventative considerations from the warehouse. * marks evidence-backed preventative nutritional targets.</p>" +
          "<p><strong>Optimal</strong> — most balanced overall valid care. No customer budget ceiling.</p>" +
          '<p class="wb-muted">Set monthly budget in the intake panel and re-run analysis. The backend filters eligibility; this page does not recalculate nutrients.</p>' +
        "</article>" +
        '<article class="wb-card"><h2>Personalized summary</h2><p>' +
          esc(display(summary, "No scientific matcher recommendations. Care direction is commercial-catalog composition.")) +
        "</p><p class=\"wb-muted\">" + esc(display(boundary.science_copy)) + "</p>" +
        "<p class=\"wb-muted\">" + esc(display(boundary.package_copy)) + "</p>" +
        "<p class=\"wb-muted\">Meets modeled baseline nutrient constraints. Not a guaranteed complete diet. Breed-specific preventative targets shown with * come from warehouse ingredient–condition evidence for this dog.</p></article>" +
        "<h2>Care packages</h2>" +
        renderOptions((payload && payload.wellness && payload.wellness.package_options) || {}, {
          showAll: showAllOptions,
          budgetStatus: (((canonical || {}).package_optimization || {}).search || {}).balanced_budget_status || (stats.tier_valid_counts && stats.balanced_budget_status),
          stats: stats,
          briefing: payload && payload.preventative_briefing
        }) +
        renderHealthAnalysis(payload && payload.health_analysis) +
      "</div>"
    );
  }

  function renderGroomer(payload, canonical) {
    var dog = (payload && payload.dog) || {};
    var obs = (payload && payload.observations) || {};
    var flags = Array.isArray(payload && payload.flags) ? payload.flags : [];
    var context = (((canonical || {}).input || {}).role_context || {}).groomer || {};
    return (
      '<div class="wb-grid">' +
        '<article class="wb-card"><h2>Dog profile</h2>' +
          '<div class="wb-kv"><span>Name</span><span>' + esc(display(dog.name)) + "</span>" +
          "<span>Breed</span><span>" + esc(display(dog.breeds)) + "</span>" +
          "<span>Weight</span><span>" + esc(display(dog.weight_kg)) + "</span>" +
          "<span>Age</span><span>" + esc(display(dog.age_years)) + "</span>" +
          "<span>Sex</span><span>" + esc(display(dog.sex)) + "</span>" +
          "<span>Observed</span><span>" + esc(display(dog.observed_conditions)) + "</span></div></article>" +
        '<article class="wb-card"><h2>Observations</h2>' +
          "<p class=\"wb-muted\">Staff notes are additional input. Changing them re-runs analysis because they belong on the request.</p>" +
          '<label>Professional observations<textarea id="groomer-observations" rows="3">' + esc(formValue(context.observations || obs.groomer_observations)) + "</textarea></label>" +
          '<label>Condition flags (comma-separated, existing backend field)<input id="groomer-flags" type="text" value="' + esc((context.observed_conditions || []).join(", ")) + '"></label>' +
          '<p><button type="button" class="wb-ghost" id="groomer-rerun">Re-run with observations</button></p>' +
          "<p>" + esc(display(obs.groomer_observations, "No observations stored on this analysis.")) + "</p></article>" +
        '<article class="wb-card"><h2>Health / care flags</h2>' +
          (flags.length ? flags.map(function (flag) {
            return "<p><strong>" + esc(display(flag.title)) + "</strong> — " + esc(display(flag.explanation)) + "</p>";
          }).join("") : '<p class="wb-muted">No flags from this analysis.</p>') +
        "</article>" +
        "<h2>Package recommendation</h2>" +
        renderOptions((payload && payload.package_options) || {}, {
          showAll: true,
          stats: searchStats(payload, canonical),
          briefing: payload && payload.preventative_briefing
        }) +
        '<article class="wb-card"><h2>Rationale</h2>' +
          ((payload && payload.product_rationale) || []).map(function (item) {
            return "<p><strong>" + esc(display(item.name)) + "</strong> — " + esc(display(item.why_selected)) + "</p>";
          }).join("") +
        "</article>" +
        '<article class="wb-card"><h2>Follow-up</h2><p>' + esc(display(payload && payload.follow_up)) + "</p></article>" +
        renderHealthAnalysis(payload && payload.health_analysis) +
      "</div>"
    );
  }

  function renderBusiness(payload) {
    var overview = (payload && payload.overview) || {};
    var dataset = (payload && payload.commercial_dataset) || {};
    var financial = (payload && payload.financial_model) || {};
    var portfolio = (payload && payload.portfolio) || {};
    var products = portfolio.recommended_products || portfolio.products || [];
    return (
      '<div class="wb-grid">' +
        '<article class="wb-card"><h2>Customer snapshot</h2>' +
          "<p class=\"wb-muted\">" + esc(display(dataset.status, "Demo commercial dataset not loaded")) + "</p>" +
          '<div class="wb-kv"><span>This analysis</span><span>' + esc(display(overview.dogs_analyzed, "1")) + " dog</span>" +
          "<span>Breed distribution</span><span>" + esc(display(dataset.breed_distribution)) + "</span>" +
          "<span>Package adoption</span><span>" + esc(display(dataset.package_adoption)) + "</span>" +
          "<span>Sales</span><span>" + esc(display(dataset.sales)) + "</span></div>" +
          '<label>Business segment (context only)<input id="business-segment" type="text" placeholder="not used by the optimizer"></label>' +
        "</article>" +
        '<article class="wb-card"><h2>Product portfolio</h2>' +
          (products.length ? products.map(function (item) {
            return '<div class="wb-product"><span>' + esc(display(item.name)) +
              " · " + esc(display(item.category)) + "</span><span>" + esc(yen(item.price || item.monthly_cost)) + "</span></div>";
          }).join("") : '<p class="wb-muted">Matcher recommendations empty. Portfolio below is package composition from the catalog.</p>') +
          "<p class=\"wb-muted\">Gaps: " + esc(display(portfolio.product_gaps)) + "</p>" +
        "</article>" +
        "<h2>Care package opportunities</h2>" +
        renderPackages(rolePackages(payload), { showIds: true }) +
        renderOptions((payload && payload.portfolio && payload.portfolio.package_options) || {}, {
          showAll: true,
          stats: searchStats(payload && payload.portfolio),
          briefing: payload && payload.preventative_briefing,
          showInternalId: true
        }) +
        '<article class="wb-card"><h2>Commercial insights</h2>' +
          '<div class="wb-kv"><span>Monthly</span><span>' + esc(yen(financial.monthly_total)) + "</span>" +
          "<span>Yearly</span><span>" + esc(yen(financial.yearly_total)) + "</span>" +
          "<span>Discount</span><span>" + esc(display(financial.discount)) + "</span>" +
          "<span>Margin</span><span>" + esc(display(financial.margin)) + "</span></div>" +
          "<p class=\"wb-muted\">" + esc(display(dataset.note)) + "</p></article>" +
      "</div>"
    );
  }

  function pretty(value) {
    try {
      return JSON.stringify(value, null, 2);
    } catch (err) {
      return String(value);
    }
  }

  function node(title, body) {
    return '<details class="wb-node"><summary>' + esc(title) + "</summary><pre>" + esc(body) + "</pre></details>";
  }

  function renderDeveloper(payload, canonical, envelope) {
    var match = (payload && payload.product_match) || {};
    var opt = (payload && payload.package_optimization) || {};
    var catalog = (payload && payload.catalog_input) || {};
    var corr = (payload && payload.correlation_id) || (envelope && envelope.presentation_correlation_id);
    var input = (canonical && canonical.input) || {};
    var science = (canonical && canonical.scientific_analysis) || {};
    var system = (canonical && canonical.system) || {};
    var composition = opt.composition || [];
    return (
      '<div class="wb-grid">' +
        '<article class="wb-card"><h2>Analysis</h2>' +
          '<div class="wb-kv"><span>Correlation ID</span><span id="dev-correlation">' + esc(display(corr)) + "</span>" +
          "<span>Signature</span><span>" + esc(display(payload && payload.analysis_signature)) + "</span>" +
          "<span>Catalog</span><span>" + esc(display(catalog.source || system.catalog_source)) + "</span>" +
          "<span>Demo mode</span><span>" + esc(String(!!(envelope && envelope.demo_catalog))) + "</span>" +
          "<span>Matcher</span><span>" + esc(display(match.formula_id, "PRODUCT_MATCH_V2_1")) + "</span>" +
          "<span>Optimizer</span><span>" + esc(display(opt.formula_id, "PACKAGE_OPTIMIZER_V2_1")) + "</span>" +
          "<span>LLM used</span><span>" + esc(display(system.ai && system.ai.llm_used, "false")) + "</span></div>" +
          "<p class=\"wb-muted\">" + esc(display(opt.scientific_boundary)) + "</p>" +
          '<p><a class="wb-link" href="/docs" target="_blank" rel="noreferrer">VIEW RAW API / docs</a></p>' +
        "</article>" +
        renderSearchAudit(payload) +
        renderExplorer(opt.search || {}) +
        '<div class="wb-pipeline">' +
          node("DOG REQUIREMENTS", pretty(opt.requirement_profile || {})) +
          node("BASELINE NUTRIENT REQUIREMENTS", pretty(((opt.requirement_profile || {}).nutrients) || {})) +
          node("BREED/CARE REQUIREMENTS", pretty(opt.care_model || { note: "NOT_AVAILABLE_FROM_SCIENTIFIC_WAREHOUSE" })) +
          node("CANDIDATE GENERATION / ALL COMBINATIONS", pretty((opt.search || {}).filter_funnel || opt.search || {})) +
          node("NUTRIENT CALCULATION", pretty((((opt.package_options || {}).essential || [])[0] || {}).nutrient_totals && (((opt.package_options || {}).essential || [])[0] || {}).nutrient_totals.conversion)) +
          node("MINIMUM FILTER", pretty({ passed: ((opt.search || {}).filter_funnel || {}).passed_minimum_filter, failed: ((opt.search || {}).constraint_failures || {}).minimum_nutrient_failure })) +
          node("MAXIMUM FILTER", pretty({ passed: ((opt.search || {}).filter_funnel || {}).passed_maximum_filter, failed: ((opt.search || {}).constraint_failures || {}).maximum_nutrient_exceeded })) +
          node("COMPATIBILITY FILTER", pretty({ structurally_eligible: (opt.search || {}).structurally_eligible, missing_required_category: ((opt.search || {}).constraint_failures || {}).missing_required_category })) +
          node("CARE-PATHWAY SCORING", pretty({ weights: opt.scoring_weights, pathways: (opt.care_model || {}).pathways })) +
          node("BUDGET RANKING", pretty(opt.tier_budget || {})) +
          node("FINAL RANKING", pretty({ returned: (opt.search || {}).returned_options, non_dominated: (opt.search || {}).non_dominated_count })) +
          node("SCORING WEIGHTS", pretty(opt.scoring_weights || (opt.search || {}).scoring_weights)) +
        "</div>" +
        renderDelta(opt.package_options || {}) +
        renderBundleInspector(opt.package_options || {}, (opt.search || {}).example_rejections || []) +
        '<article class="wb-card"><h2>Returned options (full JSON)</h2>' +
          node("ESSENTIAL OPTIONS", pretty((opt.package_options || {}).essential)) +
          node("BALANCED OPTIONS", pretty((opt.package_options || {}).balanced)) +
          node("OPTIMAL OPTIONS", pretty((opt.package_options || {}).optimal)) +
        "</article>" +
      "</div>"
    );
  }

  function bindToggles(root) {
    root.querySelectorAll("[data-open-nutrition]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        openNutritionModal(btn.getAttribute("data-open-nutrition") || "");
      });
    });
    root.querySelectorAll("[data-toggle]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var target = document.getElementById(btn.getAttribute("data-toggle"));
        if (target) target.hidden = !target.hidden;
      });
    });
    var rerun = document.getElementById("groomer-rerun");
    if (rerun) rerun.addEventListener("click", runAnalysis);
    var compare = document.getElementById("compare-bundles");
    if (compare) {
      compare.addEventListener("click", function () {
        var panel = document.getElementById("compare-panel");
        if (!panel || !currentAnalysis) return;
        var options = (((currentAnalysis.roles || {}).customer || {}).wellness || {}).package_options || {};
        panel.hidden = !panel.hidden;
        panel.innerHTML = renderCompare(options);
      });
    }
    root.querySelectorAll("[data-show-more]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        showAllOptions = true;
        renderRoleView();
      });
    });
    root.querySelectorAll("[data-compare-bundle]").forEach(function (box) {
      box.addEventListener("change", function () {
        var id = box.getAttribute("data-compare-bundle") || "";
        if (!id) return;
        if (box.checked) compareIds[id] = true;
        else delete compareIds[id];
      });
    });
    root.querySelectorAll("[data-select-bundle]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        selectedBundleId = btn.getAttribute("data-select-bundle") || "";
        renderRoleView();
      });
    });
  }

  function renderRoleView() {
    var views = {
      customer: $("page-module").querySelector('[data-view="customer"]'),
      groomer: $("page-module").querySelector('[data-view="groomer"]'),
      business: $("page-module").querySelector('[data-view="business"]'),
      developer: $("page-module").querySelector('[data-view="developer"]')
    };
    if (!currentAnalysis) {
      Object.keys(views).forEach(function (role) {
        views[role].innerHTML = emptyState(role);
      });
      return;
    }
    var roles = currentAnalysis.roles || {};
    var canonical = currentAnalysis.canonical || {};
    views.customer.innerHTML = renderCustomer(roles.customer, canonical);
    views.groomer.innerHTML = renderGroomer(roles.groomer, canonical);
    views.business.innerHTML = renderBusiness(roles.business);
    views.developer.innerHTML = renderDeveloper(roles.developer, canonical, currentAnalysis);
    bindToggles(views[currentRole] || views.customer);
    var banner = $("demo-catalog-banner");
    banner.hidden = !currentAnalysis.demo_catalog;
    $("wb-meta").textContent =
      "Analysis " + display(currentAnalysis.presentation_correlation_id) +
      " · role " + currentRole +
      " · runs " + analysisRunCount;
  }

  async function runAnalysis() {
    setError("");
    setStatus("Running one analysis…");
    var body = readForm();
    body.role_context = roleContext();
    body.correlation_id = nextCorrelationId();
    var endpoint = API_BASE + WORKBENCH_PATH;
    analysisRunCount += 1;
    showAllOptions = true;
    selectedBundleId = "";
    compareIds = {};
    try {
      var response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      var text = await response.text();
      if (!response.ok) {
        setStatus("");
        setError(
          "API failure " + response.status + " " + response.statusText +
          " · endpoint " + WORKBENCH_PATH +
          " · origin " + API_BASE +
          (text ? " · " + text.slice(0, 280) : "")
        );
        return;
      }
      currentAnalysis = JSON.parse(text);
      setStatus("Canonical analysis stored. Switching roles does not recompute.");
      renderRoleView();
    } catch (err) {
      setStatus("");
      setError(
        "Network failure contacting " + endpoint +
        " from origin " + API_BASE +
        ". Retry the analysis when the service is available. " +
        (err && err.message ? err.message : "")
      );
    }
  }

  document.querySelectorAll(".wb-role").forEach(function (btn) {
    btn.addEventListener("click", function () {
      switchRole(btn.getAttribute("data-role"));
    });
  });
  $("module-load-demo").addEventListener("click", function () {
    fillForm(DEMO_PROFILE);
  });
  $("module-analyze").addEventListener("click", runAnalysis);
  $("intake-form").addEventListener("submit", function (event) {
    event.preventDefault();
    runAnalysis();
  });

  fillForm(DEMO_PROFILE);
  switchRole("customer");

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && selectedBundleForNutrition) closeNutritionModal();
  });
  document.addEventListener("click", function (event) {
    if (!selectedBundleForNutrition) return;
    if (event.target.closest("[data-close-nutrition]")) {
      event.preventDefault();
      closeNutritionModal();
    }
  });
  var nutritionPanel = document.querySelector("#nutrition-modal .wb-modal-panel");
  if (nutritionPanel) {
    nutritionPanel.addEventListener("click", function (event) {
      if (!event.target.closest("[data-close-nutrition]")) event.stopPropagation();
    });
  }

  window.WagtopiaWorkbench = {
    getAnalysis: function () { return currentAnalysis; },
    getRole: function () { return currentRole; },
    getRunCount: function () { return analysisRunCount; },
    getSelectedNutritionBundle: function () { return selectedBundleForNutrition; },
    packageIds: function (role) {
      var roles = (currentAnalysis && currentAnalysis.roles) || {};
      return packageIds(roles[role || currentRole]);
    }
  };
})();
