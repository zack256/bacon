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