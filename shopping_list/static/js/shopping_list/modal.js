document.addEventListener('DOMContentLoaded', function () {
    const newCateModal = document.getElementById("new-item-category");
    const submitBtn = newCateModal.querySelector("#btn-add-category");
    const modalForm = newCateModal.querySelector("form");
    submitBtn.addEventListener("click", () => {
        var formdata = new FormData(modalForm);
        fetch(modalForm.action, {
            method: "POST",
            body: formdata
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.status === 'success') location.reload()
                else console.log(data.message);
            });
    });
});