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
function addRoleCheck (forActor, already) {
    var nID;
    if (forActor) {
        nID = document.getElementById("movieIDInput").value;
    } else {
        nID = document.getElementById("actorIDInput").value;
    }
    if (isNaN(nID) || nID == "") {
        alert("Invalid input.");
        return false;
    }
    if (already.includes(parseInt(nID))) {
        alert("Role is already in database.");
        return false;
    }
    return checkBase("Add Role?");
}
function deleteRoleCheck () {
    return checkBase("Delete Role?");
}















