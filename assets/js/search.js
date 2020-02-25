function clearSearch () {
    document.getElementById("searchBar").value = "";
}
function doSearch (actors = true) {
    var searchBar = document.getElementById("searchBar");
    var url;
    if (actors) {
        url = "/db/actors/?query=" + searchBar.value;
    } else {
        url = "/db/movies/?query=" + searchBar.value;
    }
    window.location.href = url;
}