def superadmin_seller_commission(request):
    """View seller sales and commission tracking"""
    from django.shortcuts import render, HttpResponse
    from .models import customer_sign, Order
    
    try:
        user = customer_sign.objects.get(id=request.session.get('user_id'))
        if not user or user.role != 'superadmin':
            return HttpResponse("Access Denied: Only superadmin can access this page")
        
        # Get all sellers
        sellers = customer_sign.objects.filter(user_type='seller')
        
        seller_stats = []
        total_commission = 0
        total_sales = 0
        
        for seller in sellers:
            # Get all orders for this seller
            orders = Order.objects.filter(seller=seller)
            
            # Calculate totals
            seller_total_sales = sum(float(order.total_price) for order in orders)
            seller_total_commission = sum(float(order.commission_5_percent or 0) for order in orders)
            seller_received = seller_total_sales - seller_total_commission
            
            # Count by status
            pending_orders = orders.filter(status='pending').count()
            accepted_orders = orders.filter(status='accepted').count()
            delivered_orders = orders.filter(status='delivered').count()
            rejected_orders = orders.filter(status='rejected').count()
            
            if seller_total_sales > 0:  # Only include sellers with sales
                seller_stats.append({
                    'seller': seller,
                    'total_sales': seller_total_sales,
                    'commission_5_percent': seller_total_commission,
                    'seller_amount': seller_received,
                    'total_orders': orders.count(),
                    'pending_orders': pending_orders,
                    'accepted_orders': accepted_orders,
                    'delivered_orders': delivered_orders,
                    'rejected_orders': rejected_orders,
                })
                
                total_commission += seller_total_commission
                total_sales += seller_total_sales
        
        # Sort by total sales descending
        seller_stats.sort(key=lambda x: x['total_sales'], reverse=True)
        
        context = {
            'user': user,
            'seller_stats': seller_stats,
            'total_sales': total_sales,
            'total_commission': total_commission,
            'total_seller_amount': total_sales - total_commission,
        }
        return render(request, 'superadmin_seller_commission.html', context)
    except customer_sign.DoesNotExist:
        return HttpResponse("User not found")
