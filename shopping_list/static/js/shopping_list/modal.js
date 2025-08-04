document.addEventListener('DOMContentLoaded', function () {
    // add cate modal
    (function () {
        const modalAddCate = document.getElementById("add-item-category");
        const btnSubmit = modalAddCate.querySelector("#btn-add-category");
        const modalForm = modalAddCate.querySelector("form");
        btnSubmit.addEventListener("click", () => {
            var formData = new FormData(modalForm);
            fetch(modalForm.action, {
                method: "POST",
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    if (data.status === 'success') location.reload()
                    else console.log(data.message);
                });
        });
    })();

    // del cate modal
    (function () {
        // 模态框
        const modalDelCate = document.getElementById("del-item-category");
        // 触发模态框的按钮
        const modalBtns = document.querySelectorAll(".del-cate-btn");
        modalBtns.forEach(function(btn) {
            btn.addEventListener("click", () => {
                const parentNode = btn.closest("[data-cate-name]");
                if (parentNode !== null) {
                    // 修改模态框的显示文本
                    const cateName = parentNode.getAttribute("data-cate-name");
                    const modalCateNameNode = document.getElementById("to-del-cate-name");
                    modalCateNameNode.innerText = cateName;
                    // 修改模态框表单的id字段数据
                    const cateId = parentNode.getAttribute("data-ss-id");
                    const modalIdField = modalDelCate.querySelector("input[name='id']");
                    modalIdField.value = cateId;
                }
            });
        });

        // 模态框的提交按钮
        const btnSubmit = modalDelCate.querySelector("#btn-del-category");
        btnSubmit.addEventListener("click", () => {
            const modalForm = modalDelCate.querySelector("form");
            const formData = new FormData(modalForm);
            fetch(modalForm.action, {
                method: "POST",
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    if (data.status === 'success') location.reload()
                    else console.log(data.message);
                });
        });
    })();
});