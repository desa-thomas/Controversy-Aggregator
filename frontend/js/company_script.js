const params = new URLSearchParams(window.location.search);
const company = params.get("company");

window.onload = async () => {
  document.getElementById("company-info").classList.add("loading");
  const json = await get_data();

  if (json) {
    document.getElementById("company-info").classList.remove("loading")

    populate_data(json);
  }

  const searchBar = document.getElementById("search-bar");
  const container = document.getElementById("results-container");

  searchBar.oninput = searchBarInput;
  searchBar.onkeydown = (e) => {
    //enter button clicked, select first choice
    if ((e.key == "Enter") & (container.style.visibility == "visible"))
      container.firstChild.click();
  };
};

async function get_data() {
  try {
    const res = await fetch(`${API_URL}/company/${company}`); //URL is in 'functions'js'
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
  location.replace(`${location.origin}/frontend`);
}

function populate_data(json) {
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
