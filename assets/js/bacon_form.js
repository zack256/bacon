function resetBaconForm () {
    document.getElementById("doBaconActor1").value = "";
    document.getElementById("doBaconActor2").value = "";
}
function clickBaconForm (actorObj) {
    var actor1ID = actorObj[document.getElementById("doBaconActor1").value];
    var actor2ID = actorObj[document.getElementById("doBaconActor2").value];
    var url = "/manual/bacon/?a1=" + actor1ID + "&a2=" + actor2ID;
    window.location.href = url;
}