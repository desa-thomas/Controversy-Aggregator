/**
 * Thomas De Sa - 2025-06-23
 */
sessionStorage.removeItem("search");

window.onload = () => {
  const searchBar = document.getElementById("search-bar");
  const container = document.getElementById("results-container");
  searchBar.oninput = searchBarInput;
  searchBar.onkeydown = (e) => {
    if ((e.key == "Enter") & (container.style.visibility == "visible"))
      container.firstChild.click();
  };
  document.addEventListener("click", click_off);
};
