document.addEventListener('DOMContentLoaded', function () {
    console.log('页面加载完成');
    
    // 展示清单的表项和表单间的转化
    let displayInputToggles = document.querySelectorAll('.display-input-toggle');
    displayInputToggles.forEach(function (toggle) {
        let displayValue = toggle.querySelector('.display-value');
        let inputValue = toggle.querySelector('.input-value');
        displayValue.parentElement.addEventListener('click', function () {
            displayValue.style.display = 'none';
            inputValue.style.display = 'inline-block';
            inputValue.focus();
        });
        function OnInputChange() {
            displayValue.style.display = 'inline-block';
            inputValue.style.display = 'none';
            // 还有ajax的逻辑
            let xhr = new XMLHttpRequest();
            xhr.open('POST', inputValue.getAttribute('data-target'), true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader('X-CSRFToken', '{{ csrf_token }}');
            xhr.send(JSON.stringify({
                'value': inputValue.value,
                'target_id': inputValue.getAttribute('data-target-id')
            }));
            xhr.onreadystatechange = function () {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    let response = JSON.parse(xhr.responseText);
                    if (xhr.status === 200 && response.success) {
                        // 成功处理
                        console.log('状态更新成功');
                        if (response.css_class) {
                            let trs = document.querySelectorAll('tr[data-item-category-id="' + inputValue.getAttribute('data-target-id') + '"]');
                            trs.forEach(function (tr) {
                                tr.className = response.css_class;
                            });
                        }
                        if (response.value) {
                            displayValue.textContent = response.value;
                        } else {
                            displayValue.textContent = inputValue.value;
                        }
                    } else {
                        // 错误处理
                        console.error('状态更新失败:', xhr.responseText);
                    }
                }
            };
        };
        inputValue.addEventListener('blur', OnInputChange);
        inputValue.addEventListener('keydown', function (event) {
            if (event.key === 'Enter' || event.key === 'Escape') {
                OnInputChange();
            }
        });
    });
    // 购物清单新增品类的modal
    // 阻止触发modal的按钮的冒泡
    let modalButtons = document.querySelectorAll('.modal-button');
    modalButtons.forEach(function (button) {
        button.addEventListener('click', function (event) {
            event.stopPropagation();
        })
    });
    // 处理modal的提交按钮
    let modalSubmitButtons = document.querySelectorAll('.modal-footer button[data-target-id]');
    modalSubmitButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            let form = document.getElementById(button.getAttribute('data-target-id'));
            let xhr = new XMLHttpRequest();
            xhr.open('POST', button.getAttribute('data-target-src'), true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader('X-CSRFToken', '{{ csrf_token }}');
            xhr.send(JSON.stringify(Object.fromEntries(new FormData(form))));
            xhr.onreadystatechange = function () {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status === 200) {
                        let response = JSON.parse(xhr.responseText);
                        if (response.success) {
                            window.location.href = button.getAttribute('data-success-src');
                        } else {
                            console.error('创建失败:', response.error);
                        }
                    } else {
                        console.error('请求失败:', xhr.status, xhr.statusText);
                    }
                }
            };
        });
    });
    // 处理购物清单的新增单品的modal
    // 点击新增单品按钮时，设置modal标题和品类ID
    let itemRecordAddModalButtons = document.querySelectorAll(".add-record-button");
    itemRecordAddModalButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            let itemRecordAddModal = document.getElementById('item-record-add-modal');
            let cateId = button.getAttribute('data-bs-cate-id');
            let modalTitle = itemRecordAddModal.querySelector('.modal-title');
            modalTitle.textContent = '为 ' + button.closest('td').querySelector('.display-value').textContent + ' 添加新单品';
            let itemCategoryIdInput = itemRecordAddModal.querySelector('#item-category-id');
            itemCategoryIdInput.value = cateId; // 设置品类ID
            // 清空modal中的输入框
            itemRecordAddModal.querySelector('#item-name').value = '';
            itemRecordAddModal.querySelector('#item-quantity').value = 1;
            itemRecordAddModal.querySelector('#item-record-note').value = '';
        });
    });
});