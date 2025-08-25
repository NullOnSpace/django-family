/*
 * 有auto-submit类的form在input变动时自动提交
*/
document.addEventListener('DOMContentLoaded', function () {
    const autoSubmitForms = document.querySelectorAll('form.auto-submit');
    autoSubmitForms.forEach(function (form) {
        const inputs = form.querySelectorAll("input");
        inputs.forEach(function (input) {
            input.addEventListener('change', function () {
                form.submit();
                console.log("form submit");
            });
        });
    });
});