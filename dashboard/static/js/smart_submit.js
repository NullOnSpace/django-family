document.addEventListener('DOMContentLoaded', function () {
    let smartSubmitFields = document.querySelectorAll('.smart-submit');
    smartSubmitFields.forEach(function (field) {
        field.addEventListener('change', function () {
            let form = field.closest('form');
            if (form) {
                let formData = new FormData(form);
                let parentDiv = field.closest('[data-ss-id]');
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
            }
        });
    });
});