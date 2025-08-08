function showMessage(message, duration = 1000, status = "info") {
    const statusClasses = {
        info: 'alert-info',
        success: 'alert-success',
        warning: 'alert-warning',
        error: 'alert-danger'
    };
    const messageBox = document.getElementById('messageBox');
    messageBox.textContent = message;
    // toggle status
    for (const statusClass of Object.values(statusClasses)) {
        messageBox.classList.remove(statusClass);
    }
    messageBox.classList.add(statusClasses[status] || 'alert-info');

    // 显示消息框
    messageBox.classList.add('show');

    // 设置定时器渐变消失
    setTimeout(() => {
        messageBox.classList.remove('show');

        // 可选：完全移除消息框内容
        setTimeout(() => {
            messageBox.textContent = '';
        }, 500); // 这个时间应该与CSS过渡时间一致
    }, duration);
}
