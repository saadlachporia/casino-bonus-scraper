
const casinoList = document.getElementById("casino-list");
const statusElement = document.getElementById("status");
const casinoCount = document.getElementById("casino-count");
const casinoTableBody = document.getElementById("casino-table-body");

// ---------------------------------------
// HELPER FUNCTIONS
// ---------------------------------------

function createElement(tag, className = "", text = null) {
  const element = document.createElement(tag);

  if (className) {
    element.className = className;
  }

  if (text !== null && text !== undefined) {
    element.textContent = String(text);
  }

  return element;
}

function getSourceUrl(sourceUrl) {
  if (typeof sourceUrl !== "string") {
    throw new Error("Missing source URL");
  }

  const url = new URL(sourceUrl);

  if (!["https:", "http:"].includes(url.protocol)) {
    throw new Error("Invalid source URL");
  }

  return url.href;
}

function createSourceLink(sourceUrl, className, text) {
  const link = createElement("a", className, text);

  link.href = getSourceUrl(sourceUrl);
  link.target = "_blank";
  link.rel = "noopener noreferrer";

  return link;
}

// ---------------------------------------
// CREATE CASINO DETAILS
// ---------------------------------------

function createDetail(label, value) {
  const wrapper = createElement("div", "detail");

  wrapper.appendChild(
    createElement("span", "field-label", label)
  );

  wrapper.appendChild(
    createElement(
      "div",
      "detail-value",
      value ?? "Not specified"
    )
  );

  return wrapper;
}

// ---------------------------------------
// CREATE CASINO CARDS
// ---------------------------------------

function createCasinoCard(casino) {
  const card = createElement("article", "casino-card");

  card.appendChild(
    createElement("h3", "", casino.casino)
  );

  card.appendChild(
    createElement(
      "span",
      "field-label",
      "Welcome bonus"
    )
  );

  card.appendChild(
    createElement(
      "p",
      "bonus",
      casino.welcome_bonus ?? "Not specified"
    )
  );

  const details = createElement("div", "details");

  details.appendChild(
    createDetail(
      "Wagering requirement",
      casino.wagering_requirement
    )
  );

  details.appendChild(
    createDetail(
      "Minimum deposit",
      casino.minimum_deposit
    )
  );

  card.appendChild(details);

  const sourceLink = createSourceLink(
    casino.source_url,
    "source-link",
    "View original source ↗"
  );

  card.appendChild(sourceLink);

  return card;
}

// ---------------------------------------
// POPULATE COMPARISON TABLE
// ---------------------------------------

function populateComparisonTable(casinos) {
  if (!casinoTableBody) {
    throw new Error(
      "Comparison table body not found in index.html"
    );
  }

  const fragment = document.createDocumentFragment();

  casinos.forEach((casino) => {
    const row = document.createElement("tr");

    const values = [
      casino.casino,
      casino.welcome_bonus,
      casino.wagering_requirement,
      casino.minimum_deposit
    ];

    values.forEach((value) => {
      const cell = document.createElement("td");

      cell.textContent = value ?? "Not specified";

      row.appendChild(cell);
    });

    const sourceCell = document.createElement("td");

    const sourceLink = createSourceLink(
      casino.source_url,
      "",
      "View source ↗"
    );

    sourceCell.appendChild(sourceLink);
    row.appendChild(sourceCell);

    fragment.appendChild(row);
  });

  casinoTableBody.replaceChildren(fragment);
}

// ---------------------------------------
// LOAD CASINOS FROM JSON
// ---------------------------------------

async function loadCasinos() {
  try {
    statusElement.textContent = "Loading casino bonuses...";

    const response = await fetch("./casinos.json", {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(
        `Failed to fetch casinos.json: HTTP ${response.status}`
      );
    }

    const casinos = await response.json();

    if (!Array.isArray(casinos)) {
      throw new Error(
        "Invalid JSON format: expected an array"
      );
    }

    // Validate all records before rendering.
    casinos.forEach((casino) => {
      if (
        !casino ||
        typeof casino.casino !== "string" ||
        typeof casino.source_url !== "string"
      ) {
        throw new Error("Invalid casino record");
      }

      getSourceUrl(casino.source_url);
    });

    // Create casino cards.
    const cardsFragment = document.createDocumentFragment();

    casinos.forEach((casino) => {
      cardsFragment.appendChild(
        createCasinoCard(casino)
      );
    });

    casinoList.replaceChildren(cardsFragment);

    // Populate comparison table.
    populateComparisonTable(casinos);

    // Update casino count.
    casinoCount.textContent = casinos.length;

    // Update status message.
    statusElement.textContent = casinos.length
      ? ""
      : "No casino offers available.";

    console.log(
      `Successfully loaded ${casinos.length} casinos.`
    );

  } catch (error) {
    console.error("Unable to load casinos:", error);

    casinoList.replaceChildren();

    if (casinoTableBody) {
      casinoTableBody.replaceChildren();
    }

    casinoCount.textContent = "—";

    statusElement.textContent =
      "Unable to load casino data. Please try again later.";
  }
}

// ---------------------------------------
// INITIALISE WEBSITE
// ---------------------------------------

loadCasinos();
