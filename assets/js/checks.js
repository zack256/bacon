function checkBase (msg) {
    var res = confirm(msg);
    return res
}
function addActorCheck () {
    return checkBase("Add Actor?");
}
function addMovieCheck () {
    return checkBase("Add Movie?");
}
function addRoleCheck () {
    return checkBase("Add Role?");
}
function editActorCheck () {
    return checkBase("Edit Actor?");
}
function editMovieCheck () {
    return checkBase("Edit Movie?");
}
function deleteActorCheck (mode) {
    if (mode == 0) {
        alert("Can't delete an actor that was initially added to the database.");
        return false;
    } else if (mode == 1) {
        alert("Can't delete an actor that was has movies, to prevent accidents. Please delete each role manually.");
        return false;
    } else {
        return checkBase("Delete Actor?");
    }
}
function deleteMovieCheck (mode) {
    if (mode == 0) {
        alert("Can't delete a movie that was initially added to the database.");
        return false;
    } else if (mode == 1) {
        alert("Can't delete a movie that was has actors, to prevent accidents. Please delete each role manually.");
        return false;
    } else {
        return checkBase("Delete Movie?");
    }
}