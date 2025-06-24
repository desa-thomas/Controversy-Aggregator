/**
 * Thomas De Sa - 2025-06-23
 */
const URL = "http://127.0.0.1:6969";
window.onload = () => {
  const searchButton = document.getElementById("search-button");
  const searchBar = document.getElementById("search-bar");

  searchBar.oninput = async () => {
    query = searchBar.value;
    if (query) {
      loader();
      document.getElementById("results-container").style.visibility = "visible";
      json = await search_endpoint(query);

      if (json) {
        //server sent results
        remove_loader();
        if (json.results.length == 0) {
          no_results(query);
        } else {
          display_results(json, query);
        }
      } else {
        //error
        delete_results();
        err_card();
      }
    } else {
      document.getElementById("results-container").style.visibility = "hidden";
    }
  };
};

async function search_endpoint(search) {
  /**
   * Search database for company.
   */
  const url = URL + `/search?query=${search}`;
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    const json = await response.json();
    return json;
  } catch (error) {
    console.error(error.message);
  }

  return null;
}

function highlightMatch(text, search) {
  /**
   * Highlight matched search in result
   */
  search = search.trim()
  const escapedSearch = search.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(${escapedSearch})`, "gi");
  const pre_format = text.replace(regex, "<mark>$1</mark>");

  return `<p>${pre_format}</p>`
}

//-----Functions for updated search results-------
function display_results(json, search) {
  /**
   * Display the search results from returned json
   */
  const container = document.getElementById("results-container");
  const existing_cards = Array.from(container.children);
  const len = json.results.length;

  json.results.forEach((result, i) => {
    if (existing_cards[i]) {
      existing_cards[i].innerHTML = highlightMatch(result, search);
      existing_cards[i].className = "result";
    } else {
      create_result(json.results[i], search);
    }
  });

  while (container.children.length > len) {
    container.removeChild(container.lastChild);
  }
  container.firstChild.classList.add("top-result");
  container.lastChild.classList.add("bottom-result");
}

function create_result(name, search) {
  const div = document.createElement("div");
  div.classList.add("result");

  div.innerHTML = highlightMatch(name, search);

  document.getElementById("results-container").appendChild(div);
  return;
}

function delete_results() {
  container = document.getElementById("results-container");
  while (container.firstChild) {
    container.removeChild(container.firstChild);
  }
  return;
}

function no_results(search) {
  const container = document.getElementById("results-container");
  if (!container.firstChild) {
    div = document.createElement("div");
    container.appendChild(div);
  }

  container.firstChild.innerHTML = `No results for \`${search}\` in database`;
  container.firstChild.className = "result top-result bottom-result";

  while (container.children.length > 1) {
    container.removeChild(container.lastChild);
  }
}

function err_card() {
  const container = document.getElementById("results-container");
  const card = document.createElement("div");
  card.className = "result top-result bottom-result";
  card.innerHTML = "Cannot connect to server. Try again later";
  container.appendChild(card);
  return;
}

function remove_loader() {
  return;
}

function loader() {
  const container = document.getElementById("results-container");

  if (!container.firstChild) {
    //if no card, create one
    div = document.createElement("div");
    div.className = "result loading top-result bottom-result"
    container.appendChild(div);
  }

  container.childNodes.forEach((child) => {
    child.innerHTML = "";
    child.classList.add("loading");
  });
  return;
}

//Button functions

function x_button() {
  delete_results();
  document.getElementById("search-bar").value = "";
  document.getElementById("results-container").style.visibility = "hidden";
}
