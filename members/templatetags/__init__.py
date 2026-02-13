from django import template

register = template.Library()

@register.filter
def add_amount(order, total_price):
    """Calculate seller amount after 5% commission"""
    return f"{order.get_seller_amount():.2f}"
