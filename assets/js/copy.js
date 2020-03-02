function copyTextFromElement (inputID) {
    var inp = document.getElementById(inputID);
    inp.select();
    document.execCommand("copy");
}