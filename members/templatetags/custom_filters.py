from django import template

register = template.Library()

@register.filter
def add_amount(order):
    """Calculate seller amount after 5% commission"""
    try:
        if hasattr(order, 'get_seller_amount'):
            return f"{float(order.get_seller_amount()):.2f}"
        else:
            # Fallback calculation
            total = float(order.total_price or 0)
            commission = float(order.commission_5_percent or 0)
            return f"{(total - commission):.2f}"
    except:
        return "0.00"
