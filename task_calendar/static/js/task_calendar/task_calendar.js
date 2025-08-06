document.addEventListener('DOMContentLoaded', function () {
    // 切换任务状态
    const taskStatusChangeButtons = document.querySelectorAll('.task-status');
    const STATUS_CLASSES = ['task-calendar-completed', 'task-calendar-outdated', 'task-calendar-active', 'task-calendar-coming'];
    taskStatusChangeButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const parentNode = this.closest('.task-calendar-item');
            const taskId = parentNode.dataset.id;
            const newStatus = parentNode.dataset.status === 'true' ? false : true;
            const iconNode = this.querySelector('i');

            const changeStatusUrl = document.getElementById('task-calendar-list').dataset.changeStatusUrl;

            fetch(changeStatusUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({ task_id: taskId, new_status: newStatus }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    console.log('Task status updated successfully');
                    parentNode.dataset.status = data.is_completed;
                    // 修改状态图标
                    if (data.is_completed) {
                        iconNode.classList.remove('bi-square');
                        iconNode.classList.add('bi-check-square');
                    } else {
                        iconNode.classList.remove('bi-check-square');
                        iconNode.classList.add('bi-square');
                    }
                    // 修改状态文字
                    const statusTextNode = this.querySelector('.status-text');
                    if (statusTextNode) {
                        statusTextNode.textContent = data.status_text;
                    }
                    // 修改状态样式
                    for (let i = 0; i < STATUS_CLASSES.length; i++) {
                        const statusClass = STATUS_CLASSES[i];
                        if (statusClass !== data.status_class) {
                            parentNode.classList.remove(STATUS_CLASSES[i]);
                        } else {
                            parentNode.classList.add(statusClass);
                        }
                    }
                } else {
                    console.error('Error updating task status:', data.message);
                }
            })
            .catch(error => console.error('Fetch error:', error));
        });
    });
    // 删除任务
    const deleteTaskButtons = document.querySelectorAll('.del-task');
    deleteTaskButtons.forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const parentNode = this.closest('.task-calendar-item');
            const delUrl = this.dataset.delUrl;

            if (confirm('确定要删除这个任务吗？')) {
                fetch(delUrl, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        parentNode.remove();
                        console.log('Task deleted successfully');
                    } else {
                        console.error('Error deleting task:', data.message);
                    }
                })
                .catch(error => console.error('Fetch error:', error));
            }
        });
    });
});