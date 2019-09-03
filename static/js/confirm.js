"use strict"
function conf_del() {
    if (confirm("Вы действительно хотите удалить элемент?")) {
        return true;
    }
    else {
        return false;
    }
}

function conf_cancel() {
    if (confirm("Ты уверен, что хочешь отказаться от участия в этом мероприятии? Помни, что оргкомитет рассчитывает на тебя и каждый раз, когда ты отменяешь участие, расстраивается один организатор")) {
        return true;
    }
    else {
        return false;
    }
}