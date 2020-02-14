function resetBaconForm () {
    document.getElementById("doBaconActor1").value = "";
    document.getElementById("doBaconActor2").value = "";
}
function clickBaconForm (actorObj, realDB = false) {
    var actor1ID = actorObj[document.getElementById("doBaconActor1").value];
    var actor2ID = actorObj[document.getElementById("doBaconActor2").value];
    var site;
    if (realDB) {
        site = "db";
    } else {
        site = "manual";
    }
    var url = "/" + site + "/bacon/?a1=" + actor1ID + "&a2=" + actor2ID;
    window.location.href = url;
}