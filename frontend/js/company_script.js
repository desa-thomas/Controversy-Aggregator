const params = new URLSearchParams(window.location.search);
const company = params.get("company");
let page = params.get("page");
let category = params.get("category");

if (!page) {
  page = 1;
}

const categories = [
  "All",
  "Labor",
  "Environment",
  "Privacy",
  "Governance",
  "Diversity",
  "Human Rights",
  "Consumer Safety",
  "Animal Welfare",
];

window.onload = async () => {
  //get company data
  article_loader_on()
  document.getElementById("company-info").classList.add("loading");
  const json = await get_data();

  if (json) {
    //server responded/ company found
    document.getElementById("company-info").classList.remove("loading");
    populate_data(json);

    const articles_json = await get_articles();
    if (articles_json) populate_article_data(articles_json);
    article_loader_off()
  }

  const searchBar = document.getElementById("search-bar");
  const container = document.getElementById("results-container");

  searchBar.oninput = searchBarInput;
  searchBar.onkeydown = (e) => {
    //enter button clicked, select first choice
    if ((e.key == "Enter") & (container.style.visibility == "visible"))
      container.firstChild.click();
  };

  create_buttons();
  document.addEventListener("click", click_off); //click off of search bar
  //dropdown
  const dropdown_container =
    document.getElementsByClassName("dropdown-container")[0];
  dropdown_container.onmouseleave = () => {
    document.getElementById("dropdown-content").style.display = "none";
  };
};

async function get_data() {
  try {
    const url = `${API_URL}/company/${encodeURIComponent(company)}`;
    const res = await fetch(url); //URL is in 'functions'js'
    if (res.status == 404) {
      console.log(res);
      location.replace(`${location.origin}/frontend/404.html`);
    } else if (!res.ok) {
      throw new Error(`Response status: ${res.status}`);
    }
    const json = await res.json();
    return json;
  } catch (error) {
    console.error(error);
  }
  return 0;
}

function return_to_home() {
  /**return to search page */
  location.replace(`${location.origin}/frontend`);
}

function populate_data(json) {
  /**Populate COMPANY DATA from json returned from server */
  if (json.industries) {
    document.getElementById("industries").textContent =
      json.industries.join(", ");
  }

  if (json.logo) {
    document.getElementById("logo").src = json.logo;
  }

  document.getElementById("company-name").textContent = json.name;

  if (json.website) {
    const link = document.getElementById("link");
    link.innerHTML = json.website;
    link.href = json.website;
  }

  document.getElementById("description").textContent = json.description;
}

function create_buttons() {
  /**
   * Create dropdown category select buttons
   */
  const container = document.getElementById("dropdown-content");
  categories.forEach((category) => {
    const butt = document.createElement("div");
    butt.className = "dropdown-item";
    butt.innerHTML = `${category}`;
    butt.id = category.toLowerCase();
    butt.onclick = () => {
      click_category(category.toLowerCase());
    };
    container.appendChild(butt);
  });
}

function click_category(category) {
  /**
   * Function for when a category button is clicked
   */
  console.log(`${category} - clicked`);
}

function click_select_category() {
  /**Click the button that drops the dropdown menu */
  dropdown = document.getElementById("dropdown-content");
  if (dropdown.style.display == "none") dropdown.style.display = "flex";
  else dropdown.style.display = "none";
}

async function get_articles() {
  /**
   * Get articles from server article endpoint. See `/backend/server.py`
   */
  const url = `${API_URL}/articles/?company=${encodeURIComponent(
    company
  )}&page=${encodeURIComponent(page)}&category=${encodeURIComponent(category)}`;
  try {
    const res = await fetch(url);
    if (!res.status == 400) {
      console.log(res.json.error);
    } else if (!res.ok) {
      throw new Error(`Response status: ${res.status}`);
    }

    const json = await res.json();
    return json;
  } catch (error) {
    console.error(error);
  }
  return 0;
}

/**
 *  toggle article loading animation
 */
function article_loader_on() {
  const container = document.getElementById("articles-container");
  container.classList.add("loading");
  if (!container.firstChild) {
  }

  Array.from(container.children).forEach((child) => {
    child.style.visibility = "hidden";
  });
}
function article_loader_off() {
  const container = document.getElementById("articles-container");
  container.classList.remove("loading");
  Array.from(container.children).forEach((child) => {
    child.style.visibility = "visible";
  });
}

function populate_article_data(json) {
  /**Turn json object with articles into article cards */
  const articles = json.articles;
  const articles_container = document.getElementById("articles-container");
  const existing_cards = Array.from(articles_container.children);

  console.log(articles);

  articles.forEach((article, i) => {
    if (existing_cards[i]) {
      overwrite_article_card(existing_cards[i], article);
    } else {
      card = create_article_card(article);
      
      if (i == 9){
        card.classList.add("bottom-card")
      }
      articles_container.appendChild(card);
    }
  });
}

/**
 * Create a new article card
 * @param {object} article
 */
function create_article_card(article) {
  const card = document.createElement("div");
  card.className = "article-card";

  const article_info = document.createElement("div");
  article_info.className = "article-info";

  const col1 = document.createElement("div");
  col1.className = "col";

  const headline = document.createElement("a");
  const source_name = document.createElement("em");

  col1.appendChild(source_name);
  col1.appendChild(headline);

  const col2 = document.createElement("div");
  col2.className = "col2";

  const sourceinfo = document.createElement("div");
  sourceinfo.className = "source-info";

  const pub_date = document.createElement("em");
  const cate = document.createElement("p");

  sourceinfo.appendChild(pub_date);

  col2.appendChild(sourceinfo);
  col2.appendChild(cate);

  article_info.appendChild(col1);
  article_info.appendChild(col2);

  const desc_container = document.createElement("div");
  desc_container.className = "article-description";

  const desc = document.createElement("p");

  desc_container.appendChild(desc);

  card.appendChild(article_info);
  card.appendChild(desc_container);
  if (article) {
    headline.textContent = article.headline;
    headline.href = article.url
    headline.target = "_blank"
    source_name.textContent = `${article.source}`;
    desc.textContent = article.description;
    pub_date.textContent = new Date(article.date_published).toLocaleDateString(
      "en-CA"
    );
    cate.textContent = article.categories.join(", ");
  }

  return card;
}

/**
 * Overwrite an existing article card with new article
 * @param {HTMLElement} card
 * @param {object} article
 */
function overwrite_article_card(card, article) {
  const ems = card.getElementsByTagName("em")
  ems[0].textContent = article.source
  ems[1].textContent = new Date(article.date_published).toLocaleDateString(
      "en-CA")

  const ps = card.getElementsByTagName("p")
  ps[0].textContent = article.categories.join(", ")
  ps[1].textContent = article.description

  const a = card.getElementsByTagName("a")
  
  a[0].href = article.website
  a[0].textContent = article.headline
  return
}
