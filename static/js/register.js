const form = document.querySelector("form");

const password = document.querySelector("#password");
const confirmPassword = document.querySelector("#confirm-password");

form.addEventListener("submit", function (event) {

    // التأكد من تطابق الباسورد
    if (password.value !== confirmPassword.value) {

        event.preventDefault();

        alert("كلمة المرور وتأكيد كلمة المرور غير متطابقين ❌");

        confirmPassword.focus();

        return;
    }

});