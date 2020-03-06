function resetAddRole (forActor) {
    if (forActor) { // actor adding a movie role
        document.getElementById('movieNameMsg').innerHTML = '';
    } else {        // movie adding an actor role
        document.getElementById('actorNameMsg').innerHTML = '';
    }
}
function setAddRoleMsg (forActor, name, nID, success) {
    var msgElement;
    if (forActor) {
        msgElement = document.getElementById("movieNameMsg");
        if (success) {
            msgElement.innerHTML = "Movie : <a href = '/db/movies/" + nID + "/' target = '_blank'>" + name + "</a>";
        } else {
            msgElement.innerHTML = name;  // error msg if not success.
        }
    } else {
        msgElement = document.getElementById("actorNameMsg");
        if (success) {
            msgElement.innerHTML = "Actor : <a href = '/db/actors/" + nID + "/' target = '_blank'>" + name + "</a>";
        } else {
            msgElement.innerHTML = name;  // error msg if not success.
        }
    }
}
function initDeleteRole (nodeID) {
    document.getElementById("ajaxID").value = nodeID;
    document.getElementById("deleteRoleAjaxButton").click();
}
function deleteRoleRow (nodeID) {
    var rowID = "roleRow" + nodeID;
    document.getElementById(rowID).remove();
}