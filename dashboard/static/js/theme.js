document.addEventListener('DOMContentLoaded', function () {
    function setThemeBasedOnSystem() {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (prefersDark) {
            document.documentElement.setAttribute('data-bs-theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-bs-theme', 'light');
        }
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', setThemeBasedOnSystem);
    }

    function setFixedTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', setThemeBasedOnSystem);
    }
    
    function onThemeChange() {
        const themeButton = document.getElementById('theme-dropdown-button');
        const currentTheme = themeButton.dataset.theme;
        switch (currentTheme) {
            case 'light':
                setFixedTheme('light');
                break;
            case 'dark':
                setFixedTheme('dark');
                break;
            case 'auto':
                setThemeBasedOnSystem();
                break;
            default:
                setFixedTheme('light');
                break;
        }
        setCookie('theme', currentTheme);
    }

    onThemeChange();
    const themeDropdown = document.getElementById('theme-dropdown');
    themeDropdown.querySelectorAll('a').forEach(function (item) {
        item.addEventListener('click', function (event) {
            event.preventDefault();
            const themeButton = document.getElementById('theme-dropdown-button');
            const themeButtonIcon = themeButton.querySelector('i');
            const themeClickedIcon = item.querySelector('i');
            themeButton.dataset.theme = item.dataset.theme;
            themeButtonIcon.className = themeClickedIcon.className;
            onThemeChange();
        });
    });
});