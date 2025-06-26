

const API_URL = "http://127.0.0.1:6969";

async function searchBarInput() {
  /**
   * Function called every time there is input in the search bar. Updates
   * search results with every input
   */
  const searchBar = document.getElementById("search-bar")
  query = searchBar.value;

  if (query) {
    loader();
    document.getElementById("results-container").style.visibility = "visible";
    const json = await search_endpoint(query);

    if (json) {
      if (json.results.length == 0) {
        no_results(query);
      } else {
        display_results(json, query);
      }
    } else {
      //error
      err_card();
    }
  } else { // Input is empty i.e., deleted
    document.getElementById("results-container").style.visibility = "hidden";
  }
}
async function search_endpoint(search) {
  /**
   * Search database for company.
   */
  const url = API_URL + `/search?query=${encodeURIComponent(search)}`;
  
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
  search = search.trim();
  const escapedSearch = search.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const regex = new RegExp(`(${escapedSearch})`, "gi");
  const pre_format = text.replace(regex, "<mark>$1</mark>");

  return `<p>${pre_format}</p>`;
}

//-----Functions for updated search results-------
//NOTE: changed some stuff to only create new divs when needed, and reuse old ones where possible
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
      existing_cards[i].onclick = ()=>{card_click(result)}
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
  /**
   * Create card with search query highlighted
   */
  const div = document.createElement("div");
  div.classList.add("result");

  div.innerHTML = highlightMatch(name, search);
  div.onclick = ()=>{card_click(name)}

  document.getElementById("results-container").appendChild(div);
  return;
}

function delete_results() {
  /**
   * Delete all cards from 'results-container'
   */
  container = document.getElementById("results-container");
  while (container.firstChild) {
    container.removeChild(container.firstChild);
  }
  return;
}

function no_results(search) {
  /**
   * create a card that says 'no results found' etc.
   * called when no results are found
   */

  const container = document.getElementById("results-container");
  if (!container.firstChild) {
    //if there is already a card, reuse it
    div = document.createElement("div");
    container.appendChild(div);
  }

  container.firstChild.innerHTML = `No results for \`${search}\` in database`;
  container.firstChild.className = "result top-result bottom-result";
  container.firstChild.onclick = null

  while (container.children.length > 1) {
    container.removeChild(container.lastChild);
  }
}

function err_card() {
  /**
   * create card with error message. Used when frontend cannot connect to server
   */
  const container = document.getElementById("results-container");

  if (!container.firstChild){
    const card = document.createElement("div");
    container.appendChild(card)
  }
  
  container.firstChild.className = "result top-result bottom-result no-results";
  container.firstChild.innerHTML = "Cannot connect to server. Try again later";
  container.firstChild.onclick = null
  
  while (container.children.length > 1){
    container.removeChild(container.lastChild)
  }
  return;
}

function loader() {
  /**
   * Add loading animation to search result cards.
   * loader is removed when the card's classes are overridden (in 'display_results')
   */
  const container = document.getElementById("results-container");

  if (!container.firstChild) {
    //if no card, create one
    div = document.createElement("div");
    div.className = "result loading top-result bottom-result";
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
  /**
   * Function for the 'X' button
   */
  delete_results();
  document.getElementById("search-bar").value = "";
  document.getElementById("results-container").style.visibility = "hidden";
}

function card_click(name){
  console.log(`${name} - clicked`)
  const encoded = encodeURIComponent(name);
  location.replace(`${location.origin}/frontend/company/?company=${encoded}`)
}

function click_off(event){
  const input = document.getElementById("search-bar-container")
  const results  = document.getElementById("results-container")

  if (!input.contains(event.target) && !results.contains(event.target)){
    results.style.visibility = "hidden"
  }
  else{
    results.style.visibility = "visible"
  }
}