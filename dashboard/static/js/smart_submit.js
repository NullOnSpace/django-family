/*
    * Smart Submit JavaScript
    * 对于所有smart-submit类的表单 监听字段的change事件
    * 当字段发生变化时 将字段所在表单提交到指定URL
    * URL由字段最近的[data-ss-id]属性的元素的[data-ss-target]属性值指定
    * 除了表单内字段键值对外，还提交[data-ss-id]的值作为id
    * 提交后调用showMessage函数显示成功信息
*/
document.addEventListener('DOMContentLoaded', function () {
    let smartSubmitForms = document.querySelectorAll('.smart-submit');
    smartSubmitForms.forEach(function (form) {
        form.addEventListener('change', function () {
            let formData = new FormData(form);
            let parentDiv = form.closest('[data-ss-id]');
            formData.append('id', parentDiv.getAttribute('data-ss-id'));
            fetch(parentDiv.getAttribute('data-ss-target'), {
                method: 'POST',
                body: formData,
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showMessage(data.message || '修改成功', 1000, 'success');
                    } else {
                        showMessage(data.error || 'An error occurred while saving changes.', 3000, 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('An unexpected error occurred.', 5000);
                });
        });
    });
});