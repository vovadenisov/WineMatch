from django import template

register = template.Library()


def get_color(value):
    if value == 'красное':
        return 'red'
    if value == 'розовое':
        return 'pink'
    return 'white'


def is_even(value):
    return not (len(value) % 2)

register.filter('color', get_color)
register.filter("is_even", is_even)
