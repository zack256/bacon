function resetBacon (which) {
    if (which == 1) {
        document.getElementById('actor1input').value = '';
        document.getElementById('baconMsg1').innerHTML = '';
    } else {
        document.getElementById('actor2input').value = '';
        document.getElementById('baconMsg2').innerHTML = '';
    }
}

function setBaconMsg (which, name, aID, success) {
    var msgP;
    if (which == 1) {
        msgP = document.getElementById("baconMsg1");
        if (success) {
            msgP.innerHTML = "Actor 1: <a href = '/db/actors/" + aID + "/' target = '_blank'>" + name + "</a>";
        } else {
            msgP.innerHTML = name;  // error msg if not success.
        }
    } else {
        msgP = document.getElementById("baconMsg2");
        if (success) {
            msgP.innerHTML = "Actor 2: <a href = '/db/actors/" + aID + "/' target = '_blank'>" + name + "</a>";
        } else {
            msgP.innerHTML = name;  // error msg if not success.
        }
    }
}

function baconSearch () {
    var actor1 = document.getElementById("actor1input").value;
    var actor2 = document.getElementById("actor2input").value;
    if (isNaN(actor1) || isNaN(actor2) || actor1 == "" || actor2 == "") {
        alert("Invalid input(s).");
        return false;
    } else {
        window.location.href = "/db/bacon/?a1=" + actor1 + "&a2=" + actor2;
    }
}