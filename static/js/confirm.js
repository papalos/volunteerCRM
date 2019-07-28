"use strict"
function conf_del() {
    if (confirm("Вы действительно хотите удалить элемент?")) {
        return true;
    }
    else {
        return false;
    }
}