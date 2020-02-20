function selectCurrentPage (page) {
    var blocks = document.getElementsByClassName("pagination-link");
    var block;
    for (var i = 0; i < blocks.length; i++) {
        block = blocks[i];
        if (block.innerHTML == page) {
            block.classList.add("is-current");
            break;
        }
    }
}