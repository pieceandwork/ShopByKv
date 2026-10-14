from shop.views import menu


def menu_context(request):
    return {'menu': menu}

def cart_count(request):
    cart = request.session.get('cart', {})
    count = sum(cart.values())
    return {'cart_count': count}

def cart_count(request):
    cart = request.session.get('cart', {})
    return {'cart_count': sum(cart.values())}
