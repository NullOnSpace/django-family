document.addEventListener('DOMContentLoaded', function () {
    // 激活Bootstrap的ToolTip
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))
    // 处理切换器的逻辑
    let switchers = document.querySelectorAll('.switcher');
    switchers.forEach(function (switcher) {
        let buttons = switcher.querySelector(".switcher-buttons");
        let contents = switcher.querySelector(".switcher-contents");
        let activeButton = buttons.querySelector(".active-button");
        buttons.addEventListener('click', function (event) {
            if (event.target.classList.contains('switcher-button')) {
                // 切换按钮状态
                activeButton.classList.remove('active-button');
                event.target.classList.add('active-button');
                activeButton = event.target;

                // 切换内容显示
                contents.querySelectorAll('.switcher-content').forEach(function (content) {
                    content.classList.remove('active-content');
                });
                let targetContentId = event.target.getAttribute('data-target');
                let targetContent = contents.querySelector('#' + targetContentId);
                targetContent.classList.add('active-content');
            }
        });
    });
});