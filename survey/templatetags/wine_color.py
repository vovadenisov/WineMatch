from django import template

register = template.Library()


def get_color(value):
    if value == 'красное':
        return 'red'
    if value == 'розовое':
        return 'pink'
    return 'white'

register.filter('color', get_color)
