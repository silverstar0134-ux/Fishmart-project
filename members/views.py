from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from datetime import date
from .models import customer_sign, Fish, Order, Category
from .models import AboutMessage
from .forms import ContactForm, AdminReplyForm



def intex_view(request):
    """Landing page / Index page"""
    return render(request, "intex.html")

def about_view(request):
    """About page"""
    return render(request, "about.html")

def contact_view(request):
    """Contact page - handle contact form submission"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you! Your message has been sent to the admin. We will reply shortly.")
            return redirect('contact')
        else:
            messages.error(request, "Please fill all required fields correctly.")
    else:
        form = ContactForm()
    
    return render(request, "contact.html", {'form': form})



def is_superadmin(user):
    """Check if user is superadmin"""
    return user and user.role == 'superadmin'

def is_admin(user):
    """Check if user is admin or superadmin"""
    return user and user.role in ['admin', 'superadmin']

def superadmin_redirect(request):
    """Redirect /superadmin/ to /superadmin/dashboard/"""
    return redirect('/superadmin/dashboard/')


def superadmin_login(request):
    """Superadmin login page"""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = customer_sign.objects.get(email=email, password=password, role='superadmin')
            request.session['user_id'] = user.id
            request.session['user_email'] = user.email
            request.session['user_type'] = user.user_type
            request.session['user_role'] = user.role
            
            return redirect("/superadmin/dashboard/")
        except customer_sign.DoesNotExist:
            messages.error(request, "Invalid email or password. Superadmin account not found.")
    
    return render(request, "superadmin_login.html")


def registerview(request):
  if request.method == 'POST':
        userna = request.POST.get('fullname')
        email = request.POST.get('emailname')
        mobile_n = request.POST.get('mobile')
        passwo = request.POST.get('passw')
        user_type = request.POST.get('user_type', 'customer')
        role = request.POST.get('role', 'user')

        user = customer_sign(
            username=userna,
            email=email,
            mobile_number=mobile_n,
            password=passwo,
            user_type=user_type,
            role=role
        )

        user.save()
        
        # Redirect based on user_type
        if user_type == 'seller':
            return redirect("/sellerlogin")
        else:
            return redirect("/login")

  return render(request,"register.html")

def loginview(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = customer_sign.objects.get(email=email, password=password, user_type='customer')
            request.session['user_id'] = user.id
            request.session['user_email'] = user.email
            request.session['user_type'] = user.user_type
            request.session['user_role'] = user.role  # Store role in session
            
            # Redirect based on role
            if user.role == 'superadmin':
                return redirect("/superadmin/dashboard/")
            elif user.role == 'admin':
                return redirect("/admin")
            else:
                return redirect("/cdashboard/")
        except customer_sign.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return render(request, "clogin.html")
    
    return render(request, "clogin.html")

def sellerloginview(request):
    """Handle seller login"""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            seller = customer_sign.objects.get(email=email, password=password, user_type='seller')
            request.session['user_id'] = seller.id
            request.session['user_email'] = seller.email
            request.session['user_type'] = seller.user_type
            request.session['user_role'] = seller.role
            
            # Redirect to seller dashboard
            return redirect("/seller/dashboard/")
        except customer_sign.DoesNotExist:
            messages.error(request, "Invalid email or password for seller account")
            return render(request, "sellerlogin_new.html")
    
    return render(request, "sellerlogin_new.html")

def dashboard_view(request):
    """Customer dashboard with fish browsing and ordering"""
    userdetails = customer_sign.objects.filter(user_type='customer')
    
    # Get location filter from request
    location_filter = request.GET.get('location', '')
    
    # Get all active fish products with seller info
    fish_products = Fish.objects.filter(is_active=True).select_related('seller')
    
    # Filter by location if provided
    if location_filter:
        fish_products = fish_products.filter(seller__area__icontains=location_filter)
    
    # Get customer's cart (session based)
    cart = request.session.get('cart', [])
    cart_total = sum(item.get('subtotal', 0) for item in cart)
    
    # Get customer's orders
    customer_id = request.session.get('user_id')
    customer_orders = []
    if customer_id:
        customer_orders = Order.objects.filter(customer_id=customer_id).order_by('-created_at')
    
    # Get unique locations for filter dropdown
    locations = customer_sign.objects.filter(user_type='seller').values_list('area', flat=True).distinct()
    
    context = {
        'userdetails': userdetails,
        'fish_products': fish_products,
        'cart': cart,
        'cart_total': cart_total,
        'cart_count': len(cart),
        'customer_orders': customer_orders,
        'locations': locations,
        'selected_location': location_filter,
    }
    return render(request, 'cdashboard_new.html', context)


def customer_orders_view(request):
    """Customer orders page - displays all customer orders"""
    try:
        customer_id = request.session.get('user_id')
        userdetails = customer_sign.objects.get(id=customer_id)
        
        # Get customer's orders
        customer_orders = Order.objects.filter(customer_id=customer_id).order_by('-created_at')
        
        context = {
            'userdetails': userdetails,
            'customer_orders': customer_orders,
        }
        return render(request, 'customer_orders.html', context)
    except customer_sign.DoesNotExist:
        return redirect('/login')


def shopping_cart_view(request):
    """Shopping cart page - displays cart and checkout form"""
    try:
        customer_id = request.session.get('user_id')
        userdetails = customer_sign.objects.get(id=customer_id)
        
        # Get customer's cart from session
        cart = request.session.get('cart', [])
        cart_total = sum(item.get('subtotal', 0) for item in cart)
        
        context = {
            'userdetails': userdetails,
            'cart': cart,
            'cart_total': cart_total,
            'cart_count': len(cart),
        }
        return render(request, 'shopping_cart.html', context)
    except customer_sign.DoesNotExist:
        return redirect('/login')


# Superadmin Dashboard Views
def superadmin_dashboard(request):
    """Superadmin dashboard - view all users and statistics"""
    try:
        user = customer_sign.objects.get(id=request.session.get('user_id'))
        if not is_superadmin(user):
            return HttpResponse("Access Denied: Only superadmin can access this page")
        
        total_customers = customer_sign.objects.filter(user_type='customer').count()
        total_sellers = customer_sign.objects.filter(user_type='seller').count()
        total_admins = customer_sign.objects.filter(role__in=['admin', 'superadmin']).count()
        total_moderators = customer_sign.objects.filter(role='moderator').count()
        
        context = {
            'user': user,
            'total_customers': total_customers,
            'total_sellers': total_sellers,
            'total_admins': total_admins,
            'total_moderators': total_moderators,
            'total_users': total_customers + total_sellers,
        }
        return render(request, 'superadmin_dashboard.html', context)
    except customer_sign.DoesNotExist:
        return HttpResponse("User not found")


def superadmin_manage_users(request):
    """Manage all users - superadmin only"""
    try:
        user = customer_sign.objects.get(id=request.session.get('user_id'))
        if not is_superadmin(user):
            return HttpResponse("Access Denied: Only superadmin can access this page")
        
        all_users = customer_sign.objects.all()
        context = {
            'user': user,
            'all_users': all_users,
        }
        return render(request, 'superadmin_manage_users.html', context)
    except customer_sign.DoesNotExist:
        return HttpResponse("User not found")


def superadmin_edit_user(request, user_id):
    """Edit user details - superadmin only"""
    try:
        current_user = customer_sign.objects.get(id=request.session.get('user_id'))
        if not is_superadmin(current_user):
            return HttpResponse("Access Denied: Only superadmin can access this page")
        
        target_user = get_object_or_404(customer_sign, id=user_id)
        
        if request.method == 'POST':
            target_user.username = request.POST.get('username', target_user.username)
            target_user.email = request.POST.get('email', target_user.email)
            target_user.mobile_number = request.POST.get('mobile_number', target_user.mobile_number)
            target_user.user_type = request.POST.get('user_type', target_user.user_type)
            target_user.role = request.POST.get('role', target_user.role)
            target_user.is_active = request.POST.get('is_active') == 'on'
            target_user.save()
            messages.success(request, 'User updated successfully')
            return redirect('/superadmin/manage-users/')
        
        context = {
            'user': current_user,
            'target_user': target_user,
        }
        return render(request, 'superadmin_edit_user.html', context)
    except customer_sign.DoesNotExist:
        return HttpResponse("User not found")


def superadmin_delete_user(request, user_id):
    """Delete user - superadmin only"""
    try:
        current_user = customer_sign.objects.get(id=request.session.get('user_id'))
        if not is_superadmin(current_user):
            return HttpResponse("Access Denied: Only superadmin can access this page")
        
        target_user = get_object_or_404(customer_sign, id=user_id)
        target_user.delete()
        messages.success(request, 'User deleted successfully')
        return redirect('/superadmin/manage-users/')
    except customer_sign.DoesNotExist:
        return HttpResponse("User not found")


def superadmin_approve_sellers(request):
    """Approve or reject pending sellers"""
    try:
        user = customer_sign.objects.get(id=request.session.get('user_id'))
        if not is_superadmin(user):
            return HttpResponse("Access Denied: Only superadmin can access this page")
        
        # Get all unverified sellers
        pending_sellers = customer_sign.objects.filter(user_type='seller', is_verified=False)
        verified_sellers = customer_sign.objects.filter(user_type='seller', is_verified=True)
        
        context = {
            'pending_sellers': pending_sellers,
            'verified_sellers': verified_sellers,
            'pending_count': pending_sellers.count(),
            'verified_count': verified_sellers.count(),
        }
        return render(request, 'superadmin_approve_sellers.html', context)
    except customer_sign.DoesNotExist:
        return HttpResponse("Access Denied")


def superadmin_approve_seller(request, seller_id):
    """Approve a seller"""
    try:
        user = customer_sign.objects.get(id=request.session.get('user_id'))
        if not is_superadmin(user):
            return HttpResponse("Access Denied")
        
        seller = get_object_or_404(customer_sign, id=seller_id, user_type='seller')
        seller.is_verified = True
        seller.save()
        messages.success(request, f'Seller {seller.username} approved successfully!')
        return redirect('/superadmin/approve-sellers/')
    except customer_sign.DoesNotExist:
        return HttpResponse("User not found")


def superadmin_reject_seller(request, seller_id):
    """Reject/block a seller"""
    try:
        user = customer_sign.objects.get(id=request.session.get('user_id'))
        if not is_superadmin(user):
            return HttpResponse("Access Denied")
        
        seller = get_object_or_404(customer_sign, id=seller_id, user_type='seller')
        seller.is_blocked = True
        seller.save()
        messages.success(request, f'Seller {seller.username} rejected/blocked!')
        return redirect('/superadmin/approve-sellers/')
    except customer_sign.DoesNotExist:
        return HttpResponse("User not found")


def superadmin_view_all_orders(request):
    """View all orders in the system"""
    try:
        user = customer_sign.objects.get(id=request.session.get('user_id'))
        if not is_superadmin(user):
            return HttpResponse("Access Denied: Only superadmin can access this page")
        
        # Get all orders with optional status filter
        orders = Order.objects.all().select_related('seller', 'customer', 'fish')
        status_filter = request.GET.get('status')
        order_id_search = request.GET.get('order_id')
        
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        if order_id_search:
            orders = orders.filter(id=order_id_search)
        
        # Stats
        stats = {
            'total_orders': Order.objects.count(),
            'pending': Order.objects.filter(status='pending').count(),
            'accepted': Order.objects.filter(status='accepted').count(),
            'rejected': Order.objects.filter(status='rejected').count(),
            'delivered': Order.objects.filter(status='delivered').count(),
        }
        
        context = {
            'orders': orders,
            'stats': stats,
            'current_status': status_filter,
            'order_id_search': order_id_search,
        }
        return render(request, 'superadmin_all_orders.html', context)
    except customer_sign.DoesNotExist:
        return HttpResponse("Access Denied")


def superadmin_manage_categories(request):
    """Manage fish categories"""
    try:
        user = customer_sign.objects.get(id=request.session.get('user_id'))
        if not is_superadmin(user):
            return HttpResponse("Access Denied: Only superadmin can access this page")
        
        categories = Category.objects.all()
        
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'add':
                name = request.POST.get('name')
                description = request.POST.get('description')
                icon = request.POST.get('icon', '🐟')
                
                if Category.objects.filter(name=name).exists():
                    messages.error(request, 'Category already exists')
                else:
                    Category.objects.create(
                        name=name,
                        description=description,
                        icon=icon
                    )
                    messages.success(request, 'Category added successfully!')
            
            elif action == 'edit':
                category_id = request.POST.get('category_id')
                category = get_object_or_404(Category, id=category_id)
                category.name = request.POST.get('name', category.name)
                category.description = request.POST.get('description', category.description)
                category.icon = request.POST.get('icon', category.icon)
                category.save()
                messages.success(request, 'Category updated successfully!')
            
            elif action == 'delete':
                category_id = request.POST.get('category_id')
                category = get_object_or_404(Category, id=category_id)
                category.delete()
                messages.success(request, 'Category deleted successfully!')
            
            return redirect('/superadmin/manage-categories/')
        
        context = {
            'categories': categories,
            'total_categories': categories.count(),
        }
        return render(request, 'superadmin_manage_categories.html', context)
    except customer_sign.DoesNotExist:
        return HttpResponse("Access Denied")


def superadmin_block_user(request, user_id):
    """Block a fake/suspicious user"""
    try:
        current_user = customer_sign.objects.get(id=request.session.get('user_id'))
        if not is_superadmin(current_user):
            return HttpResponse("Access Denied")
        
        target_user = get_object_or_404(customer_sign, id=user_id)
        target_user.is_blocked = True
        target_user.is_active = False
        target_user.save()
        messages.success(request, f'User {target_user.username} has been blocked!')
        return redirect('/superadmin/manage-users/')
    except customer_sign.DoesNotExist:
        return HttpResponse("User not found")


def superadmin_unblock_user(request, user_id):
    """Unblock a user"""
    try:
        current_user = customer_sign.objects.get(id=request.session.get('user_id'))
        if not is_superadmin(current_user):
            return HttpResponse("Access Denied")
        
        target_user = get_object_or_404(customer_sign, id=user_id)
        target_user.is_blocked = False
        target_user.is_active = True
        target_user.save()
        messages.success(request, f'User {target_user.username} has been unblocked!')
        return redirect('/superadmin/manage-users/')
    except customer_sign.DoesNotExist:
        return HttpResponse("User not found")

def seller_register(request):
    """Seller registration with location"""
    if request.method == 'POST':
        userna = request.POST.get('fullname')
        email = request.POST.get('emailname')
        mobile_n = request.POST.get('mobile')
        passwo = request.POST.get('passw')
        area = request.POST.get('area')
        district = request.POST.get('district')
        state = request.POST.get('state')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        try:
            # Check if email already exists
            if customer_sign.objects.filter(email=email).exists():
                messages.error(request, "Email already registered!")
                return render(request, 'seller_register.html')
            
            seller = customer_sign(
                username=userna,
                email=email,
                mobile_number=mobile_n,
                password=passwo,
                user_type='seller',
                role='user',
                area=area,
                district=district,
                state=state,
                latitude=float(latitude) if latitude else None,
                longitude=float(longitude) if longitude else None,
            )
            seller.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect("/sellerlogin")
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return render(request, 'seller_register.html')

    return render(request, "seller_register.html")

# Seller Dashboard Views
def seller_dashboard(request):
    """Main seller dashboard"""
    try:
        seller = customer_sign.objects.get(id=request.session.get('user_id'), user_type='seller')
    except customer_sign.DoesNotExist:
        return HttpResponse("Access Denied: Only sellers can access this page")

    fish_products = Fish.objects.filter(seller=seller)
    pending_orders = Order.objects.filter(seller=seller, status='pending').count()
    total_orders = Order.objects.filter(seller=seller).count()
    
    stats = {
        'total_products': fish_products.count(),
        'active_products': fish_products.filter(is_active=True).count(),
        'pending_orders': pending_orders,
        'total_orders': total_orders,
        'total_revenue': sum([order.total_price for order in Order.objects.filter(seller=seller, status='accepted')])
    }

    context = {
        'seller': seller,
        'stats': stats,
        'recent_orders': Order.objects.filter(seller=seller)[:5]
    }
    return render(request, 'seller_dashboard.html', context)


def seller_add_fish(request):
    """Add new fish product"""
    try:
        seller = customer_sign.objects.get(id=request.session.get('user_id'), user_type='seller')
    except customer_sign.DoesNotExist:
        return HttpResponse("Access Denied: Only sellers can access this page")

    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        available_kg = request.POST.get('available_kg')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        try:
            Fish.objects.create(
                seller=seller,
                name=name,
                price=price,
                available_kg=available_kg,
                description=description,
                image=image,
                is_active=True
            )
            messages.success(request, 'Fish product added successfully!')
            return redirect('/seller/dashboard/')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    context = {'seller': seller}
    return render(request, 'seller_add_fish.html', context)


def seller_manage_fish(request):
    """Manage fish products"""
    try:
        seller = customer_sign.objects.get(id=request.session.get('user_id'), user_type='seller')
    except customer_sign.DoesNotExist:
        return HttpResponse("Access Denied: Only sellers can access this page")

    fish_products = Fish.objects.filter(seller=seller)
    context = {
        'seller': seller,
        'fish_products': fish_products
    }
    return render(request, 'seller_manage_fish.html', context)


def seller_edit_fish(request, fish_id):
    """Edit fish product"""
    try:
        seller = customer_sign.objects.get(id=request.session.get('user_id'), user_type='seller')
    except customer_sign.DoesNotExist:
        return HttpResponse("Access Denied: Only sellers can access this page")

    fish = get_object_or_404(Fish, id=fish_id, seller=seller)

    if request.method == 'POST':
        fish.name = request.POST.get('name', fish.name)
        fish.price = request.POST.get('price', fish.price)
        fish.available_kg = request.POST.get('available_kg', fish.available_kg)
        fish.description = request.POST.get('description', fish.description)
        
        if request.FILES.get('image'):
            fish.image = request.FILES.get('image')
        
        fish.save()
        messages.success(request, 'Fish product updated successfully!')
        return redirect('/seller/manage-fish/')

    context = {'seller': seller, 'fish': fish}
    return render(request, 'seller_edit_fish.html', context)


def seller_delete_fish(request, fish_id):
    """Delete fish product"""
    try:
        seller = customer_sign.objects.get(id=request.session.get('user_id'), user_type='seller')
    except customer_sign.DoesNotExist:
        return HttpResponse("Access Denied: Only sellers can access this page")

    fish = get_object_or_404(Fish, id=fish_id, seller=seller)
    fish.delete()
    messages.success(request, 'Fish product deleted successfully!')
    return redirect('/seller/manage-fish/')


def seller_orders(request):
    """View all orders for seller"""
    try:
        seller = customer_sign.objects.get(id=request.session.get('user_id'), user_type='seller')
    except customer_sign.DoesNotExist:
        return HttpResponse("Access Denied: Only sellers can access this page")

    orders = Order.objects.filter(seller=seller).order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    stats = {
        'pending': Order.objects.filter(seller=seller, status='pending').count(),
        'accepted': Order.objects.filter(seller=seller, status='accepted').count(),
        'rejected': Order.objects.filter(seller=seller, status='rejected').count(),
        'delivered': Order.objects.filter(seller=seller, status='delivered').count(),
    }

    # Calculate commission totals and seller amounts
    total_commission = sum(float(o.commission_5_percent or 0) for o in orders)
    total_seller_amount = sum(float((o.total_price or 0)) - float(o.commission_5_percent or 0) for o in orders)

    # Add seller_amount attribute to each order for easy template access
    for o in orders:
        o.seller_amount = (o.total_price or 0) - (o.commission_5_percent or 0)

    context = {
        'seller': seller,
        'orders': orders,
        'stats': stats,
        'current_status': status_filter,
        'total_commission': total_commission,
        'total_seller_amount': total_seller_amount,
    }
    return render(request, 'seller_orders.html', context)


def seller_order_action(request, order_id, action):
    """Accept or Reject order"""
    try:
        seller = customer_sign.objects.get(id=request.session.get('user_id'), user_type='seller')
    except customer_sign.DoesNotExist:
        return HttpResponse("Access Denied: Only sellers can access this page")

    order = get_object_or_404(Order, id=order_id, seller=seller)

    if action == 'accept':
        order.status = 'accepted'
        message = 'Order accepted successfully!'
    elif action == 'reject':
        order.status = 'rejected'
        message = 'Order rejected successfully!'
    elif action == 'deliver':
        order.status = 'delivered'
        message = 'Order marked as delivered!'
    else:
        return HttpResponse("Invalid action")

    order.save()
    messages.success(request, message)
    return redirect('/seller/orders/')


# Customer Cart and Order Views
def add_to_cart(request, fish_id):
    """Add fish to cart"""
    try:
        fish = Fish.objects.get(id=fish_id)
        quantity = float(request.POST.get('quantity', 1))
        
        # Get or create cart in session
        cart = request.session.get('cart', [])
        
        # Check if fish already in cart
        cart_item = None
        for item in cart:
            if item['fish_id'] == fish_id:
                cart_item = item
                break
        
        if cart_item:
            cart_item['quantity'] += quantity
            cart_item['subtotal'] = cart_item['quantity'] * float(fish.price)
        else:
            cart.append({
                'fish_id': fish_id,
                'fish_name': fish.name,
                'price': float(fish.price),
                'quantity': quantity,
                'subtotal': quantity * float(fish.price),
                'seller_name': fish.seller.username,
            })
        
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, f"{fish.name} added to cart!")
        
    except Fish.DoesNotExist:
        messages.error(request, "Fish not found")
    
    return redirect(request.META.get('HTTP_REFERER', '/cdashboard/'))


def remove_from_cart(request, cart_index):
    """Remove item from cart"""
    try:
        cart = request.session.get('cart', [])
        if 0 <= cart_index < len(cart):
            removed = cart.pop(cart_index)
            request.session['cart'] = cart
            request.session.modified = True
            messages.success(request, f"{removed['fish_name']} removed from cart!")
    except:
        messages.error(request, "Error removing item")
    
    return redirect(request.META.get('HTTP_REFERER', '/cdashboard/'))


def place_order(request):
    """Place order from cart"""
    if request.method == 'POST':
        customer_id = request.session.get('user_id')
        if not customer_id:
            messages.error(request, "Please login to place an order")
            return redirect('/clogin/')
        
        try:
            customer = customer_sign.objects.get(id=customer_id)
        except customer_sign.DoesNotExist:
            messages.error(request, "Customer not found")
            return redirect('/clogin/')
        
        cart = request.session.get('cart', [])
        if not cart:
            messages.error(request, "Cart is empty")
            return redirect('/cdashboard/')
        
        # Get form data
        customer_name = request.POST.get('customer_name', customer.username)
        customer_email = request.POST.get('customer_email', customer.email)
        customer_phone = request.POST.get('customer_phone', customer.mobile_number)
        payment_method = request.POST.get('payment_method', 'cash_on_delivery')
        notes = request.POST.get('notes', '')
        
        # Get delivery location details
        delivery_state = request.POST.get('delivery_state', '')
        delivery_city = request.POST.get('delivery_city', '')
        delivery_district = request.POST.get('delivery_district', '')
        delivery_village = request.POST.get('delivery_village', '')
        
        # Create orders for each cart item
        orders_created = 0
        for item in cart:
            try:
                fish = Fish.objects.get(id=item['fish_id'])
                order = Order.objects.create(
                    seller=fish.seller,
                    customer=customer,
                    fish=fish,
                    quantity_kg=item['quantity'],
                    total_price=item['subtotal'],
                    customer_name=customer_name,
                    customer_email=customer_email,
                    customer_phone=customer_phone,
                    delivery_state=delivery_state,
                    delivery_city=delivery_city,
                    delivery_district=delivery_district,
                    delivery_village=delivery_village,
                    payment_method=payment_method,
                    status='pending',
                    notes=notes
                )
                # Calculate 5% commission
                order.calculate_commission()
                order.save()
                orders_created += 1
            except Fish.DoesNotExist:
                continue
        
        if orders_created > 0:
            # Clear cart
            request.session['cart'] = []
            request.session.modified = True
            messages.success(request, f"Order placed successfully! {orders_created} item(s) ordered.")
            return redirect('/cdashboard/')
        else:
            messages.error(request, "Error creating orders")
            return redirect('/cdashboard/')
    
    return redirect('/cdashboard/')


def customer_confirm_delivery(request, order_id):
    """Customer confirms they have received the order"""
    try:
        order = Order.objects.get(id=order_id)
        
        # Check if order belongs to logged-in customer
        customer_id = request.session.get('user_id')
        if not customer_id or order.customer_id != customer_id:
            messages.error(request, "You can only confirm your own orders")
            return redirect('/cdashboard/')
        
        # Check if order is in accepted status
        if order.status != 'accepted':
            messages.error(request, "Can only confirm accepted orders")
            return redirect('/cdashboard/')
        
        # Update order status to delivered
        order.status = 'delivered'
        order.save()
        messages.success(request, f"✓ Order #{order.id} confirmed as received! Thank you for your purchase.")
        return redirect('/cdashboard/')
        
    except Order.DoesNotExist:
        messages.error(request, "Order not found")
        return redirect('/cdashboard/')
def superadmin_seller_commission(request):
    """View seller sales and commission tracking"""
    try:
        user = customer_sign.objects.get(id=request.session.get('user_id'))
        if not is_superadmin(user):
            return HttpResponse("Access Denied: Only superadmin can access this page")
        
        # Get all sellers
        sellers = customer_sign.objects.filter(user_type='seller')
        
        seller_stats = []
        total_commission = 0
        total_sales = 0
        total_kg_sold = 0
        commission_per_kg = 0
        
        for seller in sellers:
            # Get all orders for this seller
            orders = Order.objects.filter(seller=seller)
            
            # Calculate totals
            seller_total_sales = sum(float(order.total_price) for order in orders)
            seller_total_commission = sum(float(order.commission_5_percent or 0) for order in orders)
            seller_received = seller_total_sales - seller_total_commission
            seller_total_kg = sum(float(order.quantity_kg) for order in orders)
            
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
                    'total_kg_sold': seller_total_kg,
                    'commission_per_kg': seller_total_commission / seller_total_kg if seller_total_kg > 0 else 0,
                })
            
            total_commission += seller_total_commission
            total_sales += seller_total_sales
            total_kg_sold += seller_total_kg
        
        # Sort by total sales descending
        seller_stats.sort(key=lambda x: x['total_sales'], reverse=True)
        
        # Calculate overall commission per kg
        commission_per_kg = total_commission / total_kg_sold if total_kg_sold > 0 else 0
        
        context = {
            'user': user,
            'seller_stats': seller_stats,
            'total_sales': total_sales,
            'total_commission': total_commission,
            'total_seller_amount': total_sales - total_commission,
            'total_kg_sold': total_kg_sold,
            'commission_per_kg': commission_per_kg,
        }
        return render(request, 'superadmin_seller_commission.html', context)
    except customer_sign.DoesNotExist:
        return HttpResponse("User not found")


def superadmin_commission_details(request):
    """Detailed view of 5% commission per order"""
    try:
        user = customer_sign.objects.get(id=request.session.get('user_id'))
        if not is_superadmin(user):
            return HttpResponse("Access Denied: Only superadmin can access this page")
        
        # Get all orders with commission details
        orders = Order.objects.select_related('seller', 'customer', 'fish').order_by('-created_at')
        
        # Filter by seller if specified
        seller_filter = request.GET.get('seller')
        if seller_filter:
            orders = orders.filter(seller_id=seller_filter)
        
        # Filter by status if specified
        status_filter = request.GET.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        # Get all sellers for filter dropdown
        sellers = customer_sign.objects.filter(user_type='seller')
        
        # Calculate totals and add seller_amount to each order
        total_commission = 0
        total_kg = 0
        total_sales = 0
        
        for order in orders:
            order.seller_amount = float(order.total_price or 0) - float(order.commission_5_percent or 0)
            total_commission += float(order.commission_5_percent or 0)
            total_kg += float(order.quantity_kg or 0)
            total_sales += float(order.total_price or 0)
        
        # Calculate average commission
        avg_commission = total_commission / orders.count() if orders.count() > 0 else 0
        
        context = {
            'user': user,
            'orders': orders,
            'sellers': sellers,
            'total_commission': total_commission,
            'total_kg': total_kg,
            'total_sales': total_sales,
            'avg_commission': avg_commission,
            'selected_seller': seller_filter,
            'selected_status': status_filter,
        }
        return render(request, 'superadmin_commission_details.html', context)
    except customer_sign.DoesNotExist:
        return HttpResponse("User not found")


# Contact Message Views for Superadmin
def admin_messages(request):
    """Superadmin view - List all contact messages"""
    try:
        user = customer_sign.objects.get(id=request.session.get('user_id'))
        if not is_superadmin(user):
            messages.error(request, "Access Denied: Only superadmin can access this page")
            return redirect('home')
        
        # Get all messages, ordered by newest first
        all_messages = AboutMessage.objects.all().order_by('-created_at')
        
        # Filter by status (replied/unanswered)
        status_filter = request.GET.get('status', 'all')
        if status_filter == 'unanswered':
            all_messages = all_messages.filter(reply__isnull=True)
        elif status_filter == 'answered':
            all_messages = all_messages.filter(reply__isnull=False)
        
        context = {
            'user': user,
            'messages': all_messages,
            'status_filter': status_filter,
        }
        return render(request, 'admin_messages.html', context)
    except customer_sign.DoesNotExist:
        messages.error(request, "User not found")
        return redirect('home')


def admin_reply_message(request, message_id):
    """Superadmin view - Reply to a contact message"""
    try:
        user = customer_sign.objects.get(id=request.session.get('user_id'))
        if not is_superadmin(user):
            messages.error(request, "Access Denied: Only superadmin can access this page")
            return redirect('home')
        
        message = get_object_or_404(AboutMessage, id=message_id)
        
        if request.method == 'POST':
            form = AdminReplyForm(request.POST, instance=message)
            if form.is_valid():
                form.save()
                messages.success(request, "Reply sent successfully!")
                return redirect('admin_messages')
            else:
                messages.error(request, "Error sending reply. Please try again.")
        else:
            form = AdminReplyForm(instance=message)
        
        context = {
            'user': user,
            'message': message,
            'form': form,
        }
        return render(request, 'admin_reply_message.html', context)
    except customer_sign.DoesNotExist:
        messages.error(request, "User not found")
        return redirect('home')
