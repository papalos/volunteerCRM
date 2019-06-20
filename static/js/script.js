"use strict"
// шаблон для проверки почты
let regmail = /^([a-z0-9_-]+\.)*[a-z0-9_-]+@[a-z0-9_-]+(\.[a-z0-9_-]+)*\.[a-z]{2,6}$/;
// шаблон для проверки телефона
let regtel = /^(\+)?[0-9]{1,3}(\()?[0-9]{3}(\))?[\d-\s]{7,17}$/; //

function gId(id) {
    return document.getElementById(id);
}

// поле почты и его лейбл сообщения об ошибке
let email = gId("vltremail");
let errmail = gId("erremail");
let err2mail = gId("err2email");

// поле телефона и его лейбл сообщения об ошибке
let tel = gId("vltrtel");
let errtel = gId("errtel");

// поля логин и пароль и их лейбл сообщения об ошибке
let log = gId("vlrtlog");
let pass = gId("vltrpass");
let errpass = gId("errpass");

// объект AJAX
let ajax = new XMLHttpRequest();

ajax.onreadystatechange = function () {
    if (ajax.readyState != 4) return;

    if (ajax.status != 200) {
        alert(ajax.status + ': ' + ajax.statusText);
    } else {
        //alert(ajax.responseText);
        if (ajax.responseText == "True") {
            err2mail.style.display = 'inline';
        }
        else {
            err2mail.style.display = 'none';
        }
    }
}



email.onblur = function () {
    let flag = regmail.test(email.value);
    if (flag) {
        errmail.style.display = "none";
        ajax.open('get', '/xxx?mail=' + email.value, true);
        ajax.send();        
    }
    else {
        errmail.style.display = "inline";
        err2mail.style.display = 'none';
    }
    //console.log(flag);
}

tel.onblur = function(){
    let f = regtel.test(tel.value);
    if (f) {
        errtel.style.display = "none";
    }
    else {
        errtel.style.display = "inline";
    }
    //console.log(f);
    //console.log(tel.value);
}

pass.onblur = function () {
    let ecv = (log.value!==pass.value);
    if (ecv) {
        errpass.style.display = "none";
    }
    else {
        errpass.style.display = "block";
    }
    console.log(ecv);
    //console.log(tel.value);
}

