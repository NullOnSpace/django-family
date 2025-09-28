from django import template
from django.utils.safestring import mark_safe
from django.http import HttpRequest

register = template.Library()


@register.filter
def theme(request: HttpRequest):
    themes = {
        'light': 'sun-fill',
        'dark': 'moon-stars-fill',
        'auto': 'circle-half',
    }
    theme = request.COOKIES.setdefault('theme', 'light')
    if theme not in themes:
        theme = 'light'
    icon = themes[theme]
    dropdown = f"""
<li class="nav-item dropdown" id="theme-dropdown">
  <button id="theme-dropdown-button" class="btn justify-content-end dropdown-toggle" type="button" data-theme="{theme}" data-bs-toggle="dropdown" aria-expanded="false">
    <i class="bi bi-{icon}"></i>
  </button>
  <ul class="dropdown-menu">
    <li><a data-theme="light" class="dropdown-item" href="#"><i class="bi bi-sun-fill"></i></a></li>
    <li><a data-theme="dark" class="dropdown-item" href="#"><i class="bi bi-moon-stars-fill"></i></a></li>
    <li><a data-theme="auto" class="dropdown-item" href="#"><i class="bi bi-circle-half"></i></a></li>
  </ul>
</li>
"""
    return mark_safe(dropdown)
