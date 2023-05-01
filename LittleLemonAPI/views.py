from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.forms.models import model_to_dict
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.pagination import PageNumberPagination
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer, UserSerializer
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

# Create your views here.
class MenuItemsView(generics.ListCreateAPIView):
    serializer_class = MenuItemSerializer
    pagination_class = PageNumberPagination
    queryset = MenuItem.objects.all()
    def get(self, request): # Fetch certain menu items
        # No ulterior permissions required (anyone can view menu items)
        queryset = MenuItem.objects.select_related('category').all()
        category_name = request.query_params.get('category')
        ordering = request.query_params.get('ordering')
        to_price = request.query_params.get('to_price')
        featured = request.query_params.get('featured')
        per_page = request.query_params.get('perpage', default=2)

        # Filter/order results if necessary
        if category_name: # There is a specified category
            queryset = queryset.filter(category__title=category_name)
        if to_price: # There is a price upper bound
            queryset = queryset.filter(price__lte=to_price)
        if ordering: # The query is to be ordered
            ordering_fields = ordering.split(",")
            queryset = queryset.order_by(*ordering_fields)
        if featured: # Fetch only featured/non-featured items
            queryset = queryset.filter(featured=featured)    

        # Paginate
        paginator = PageNumberPagination()
        paginator.page_size=per_page
        try: # Try to populate page
            queryset = paginator.paginate_queryset(queryset, request)
        except EmptyPage: # If the page is empty
            queryset = []
        
        # TODO: Error Handling (Invalid Queries)
        serialized_item = self.serializer_class(queryset, many=True)
        return paginator.get_paginated_response(serialized_item.data)

    def post(self, request):
        # Permissions required: Admin   
        if not request.user.is_superuser:
            return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
        serialized_item = MenuItemSerializer(data=request.data) # Create entry
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save() # Save Entry
        return Response(serialized_item.validated_data, status.HTTP_201_CREATED)
    
    def patch(self, request):
        # Permissions required: Manager or Admin
        if (not request.user.is_superuser) and (not request.user.groups.filter(name='Manager')):
            return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
        pk = request.data.get('id')
        obj = get_object_or_404(MenuItem, pk=pk) # Fetch item
        featured = request.data.get('featured')
        obj.featured = featured # Update item
        obj.save()  
        return Response(MenuItemSerializer(obj).data, status.HTTP_202_ACCEPTED)
    
class CategoriesView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    queryset = Category.objects.all()
    def get(self, request): # Fetch categories 
        # No ulterior permissions required (anyone can view menu items)
        queryset = Category.objects.all()
        per_page = request.query_params.get('perpage', default=2)
        category_name = request.query_params.get('category')
        if category_name: # There is a specified category
            queryset = queryset.filter(title=category_name)
        
        # Paginate
        paginator = PageNumberPagination()
        paginator.page_size=per_page
        try: # Try to populate page
            queryset = paginator.paginate_queryset(queryset, request)
        except EmptyPage: # If the page is empty
            queryset = []
        # TODO: Error Handling (Invalid Queries)
        serialized_item = self.serializer_class(queryset, many=True)
        return paginator.get_paginated_response(serialized_item.data)
    def post(self, request):
         # Permissions required: Admin   
        if not request.user.is_superuser:
            return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
        serialized_item = CategorySerializer(data=request.data) # Create entry
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save() # Save Entry
        return Response(serialized_item.validated_data, status.HTTP_201_CREATED)
    
class CartView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    pagination_class = PageNumberPagination
    queryset = Cart.objects.all()
    def get(self, request): # Fetch carts
        if not request.user.is_authenticated: # User must be signed in
            return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
        queryset = Cart.objects.all()   
        if not request.user.is_superuser: # Return only the customer's cart unless the user is an admin
            queryset = queryset.filter(user=request.user.id)
        per_page = request.query_params.get('perpage', default=2)
        
        # Paginate
        paginator = PageNumberPagination()
        paginator.page_size=per_page
        try: # Try to populate page
            queryset = paginator.paginate_queryset(queryset, request)
        except EmptyPage: # If the page is empty
            queryset = []
        serialized_item = self.serializer_class(queryset, many=True)
        return paginator.get_paginated_response(serialized_item.data)
    
    def post(self, request): # Add items to cart
        if not request.user.is_authenticated: # User must be signed in
            return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
        menu_item = get_object_or_404(MenuItem, pk=request.data.get('menuitem_id')) # fetch menu item
        # Construct the request carefully (prevent tampering by the customer, such as setting the unit price to to 0)
        serialized_item = CartSerializer(data={
            "user_id": request.user.id,
            "quantity": request.data.get('quantity'),
            "menuitem_id": request.data.get('menuitem_id'),
            "unit_price": menu_item.price
        })
        serialized_item.is_valid(raise_exception=True) # Validate
        serialized_item.save() # Save entry
        return Response(serialized_item.validated_data, status.HTTP_201_CREATED)
    
    def patch(self, request): # Change quantity of items ordered
        if not request.user.is_authenticated: # User must be signed in
            return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
        pk = request.data.get('cart_id')
        cart_object = get_object_or_404(Cart, pk=pk) # Fetch Cart
        if (not request.user.is_superuser) and (not cart_object.user.id == request.user.id): # Prevent customers from modifying each other's carts
            return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
        new_quantity = int(request.data.get('new_quantity')) # Fetch new quantity
        cart_object.quantity = new_quantity
        cart_object.save() # Update and save
        return Response(CartSerializer(cart_object).data, status.HTTP_202_ACCEPTED) # Confirmation message
    
    def delete(self, request): # Delete the cart
        if not request.user.is_authenticated: # User must be signed in
            return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
        pk = request.data.get('cart_id')
        cart_object = get_object_or_404(Cart, pk=pk) # Fetch Cart
        if (not request.user.is_superuser) and (not cart_object.user.id == request.user.id): # Prevent customers from modifying each other's carts
            return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
        cart_object.delete() # Delete object
        return Response(status.HTTP_200_OK)

class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    pagination_class = PageNumberPagination
    queryset = Order.objects.all()
    def get(self, request): # View orders
        if not request.user.is_authenticated: # User must be signed in, at least
            return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
        pk = request.data.get('order_id')
        # Permissions required: admin, manager or delivery crew
        queryset = Order.objects.all()
        if (not request.user.is_superuser) and (not request.user.groups.filter(name='Manager')):
            # Check if the request is from someone from delivery crew
            if (not request.user.groups.filter(name='Delivery Crew')):
                return HttpResponseForbidden("Sorry, you aren't allowed to do that.") 
            # Filter orders based on those this person is responsible for
            queryset = queryset.filter(delivery_crew__id=request.user.id)
        
        # Paginate
        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('perpage', default=2)
        try: # Try to populate page
            queryset = paginator.paginate_queryset(queryset, request)
        except EmptyPage: # If the page is empty
            queryset = []
        serialized_item = self.serializer_class(queryset, many=True)
        return paginator.get_paginated_response(serialized_item.data) # Return data
        
    def post(self, request): # Make an order
        if not request.user.is_authenticated: # User must be signed in
            return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
        pk = request.data.get('cart_id')
        if pk != None: # Make one singular order for a cart item
            cart_object = get_object_or_404(Cart, pk=pk) # Fetch cart
            if (not request.user.is_superuser) and (not cart_object.user.id == request.user.id): # Prevent customers from modifying each other's carts
                return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
            # Step 1: Make an order and order item
            serialized_order = OrderSerializer(data={
                "user_id": request.user.id,
                "total": cart_object.price,
                "price": cart_object.price # Can add taxes if needed
            })
            serialized_order.is_valid(raise_exception=True) # Validate
            order_obj = serialized_order.save()
            serialized_order_item = OrderItemSerializer(data={
                "menuitem_id": cart_object.menuitem.id,
                "order_id": order_obj.id,
                "total": cart_object.price,
                "date": timezone.now().date()
            })
            serialized_order_item.is_valid(raise_exception=True) # Validate
            serialized_order_item.save() # Save object
            cart_object.delete() # Delete Cart object
            return Response(serialized_order.validated_data, status.HTTP_201_CREATED)
        else: # Make one order for all current cart items
            cart_set = Cart.objects.filter(user__id=request.user.id)
            if not cart_set:
                return Response("Cart is Empty!")
            # Loop over cart_set and make an order item for each, adding cost to an aggregated price
            orderDict = { # Dict used to store parameters for the order
                "user_id": request.user.id,
                "total": 0,
                "price": 0 # Can calculate taxes later if needed
            }
            orderItemList = [] # List of dicts storing parameters for order items
            total_cost = 0
            for cart_object in cart_set:
                orderItemList.append({
                    "menuitem_id": cart_object.menuitem.id,
                    "order_id": "Placeholder",
                    "total": cart_object.price,
                    "date": timezone.now().date()
                })
                total_cost += cart_object.price
                # cart_object.delete() # Delete cart object
            orderDict["total"] = orderDict["price"] = total_cost # Initialize total cost
            # Add taxes if necessary
            serialized_order = OrderSerializer(data=orderDict) # Make order
            serialized_order.is_valid(raise_exception=True) # Validate
            order_obj = serialized_order.save()
            for order_item_obj in orderItemList:
                order_item_obj["order_id"] = order_obj.id
                serialized_order_item = OrderItemSerializer(data=order_item_obj) # Serialize
                serialized_order_item.is_valid(raise_exception=True) # Validate
                serialized_order_item.save() # Save object
            return Response(serialized_order.validated_data, status.HTTP_201_CREATED) # Return confirmation message
    def patch(self, request): # Update an order
        if not request.user.is_authenticated: # User must be signed in
            return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
        # Permissions Required: Admin, Manager or Delivery Crew
        if (not request.user.is_superuser) and (not request.user.groups.filter(name='Manager')) and (not request.user.groups.filter(name='Delivery Crew')):
            return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
        pk = request.data.get('order_id')
        if pk == None:
            return HttpResponseBadRequest("Please Provide a valid Order ID")
        order_obj = get_object_or_404(Order, pk=pk)
        if request.data.get('status'): # update status
            order_obj.status = request.data.get('status')
        if request.data.get('delivery_crew'): # Assign delivery 
            # Permissions Required: Admin or Manager
            if (not request.user.is_superuser) and (not request.user.groups.filter(name='Manager')):
                return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
            order_obj.delivery_crew = get_object_or_404(get_user_model(), username=request.data.get('delivery_crew')) # Assign delivery crew
            if (not order_obj.delivery_crew.groups.filter(name='Delivery Crew')):
                return HttpResponseBadRequest("User is not a part of the delivery crew") # tried assigning to a non-delivery crew
        order_obj.save()
        return Response(OrderSerializer(order_obj).data, status.HTTP_202_ACCEPTED) # Confirmation message


class OrderItemView(generics.ListCreateAPIView):
    serializer_class = OrderItemSerializer
    pagination_class = PageNumberPagination
    queryset = OrderItem.objects.all()
    def get(self, request): # Fetch Orders
        # Shows order items corresponding to a customer
        if not request.user.is_authenticated: # User must be signed in
            return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
        queryset = OrderItem.objects.filter(order__user__id=request.user.id)
        if request.user.is_superuser:
            queryset = OrderItem.objects.all()
        
        ordering = request.query_params.get('ordering')
        is_delivered = request.query_params.get('isdelivered')
        per_page = request.query_params.get('perpage', default=2)
        if is_delivered != None:
            queryset = queryset.filter(status=is_delivered)
        if ordering: # The query is to be ordered
            ordering_fields = ordering.split(",")
            queryset = queryset.order_by(*ordering_fields)
        
        # Paginate
        paginator = PageNumberPagination()
        paginator.page_size=per_page
        try: # Try to populate page
            queryset = paginator.paginate_queryset(queryset, request)
        except EmptyPage: # If the page is empty
            queryset = []
        serialized_item = self.serializer_class(queryset, many=True)
        return paginator.get_paginated_response(serialized_item.data)
    
class AssignView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    model = get_user_model()
    queryset = model.objects.all()
    def patch(self, request): # Modify Groups
        if not request.user.is_authenticated: # User must be signed in
            return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
        if (not request.user.is_superuser) and (not request.user.groups.filter(name='Manager')):
             return HttpResponseForbidden("Sorry, you aren't allowed to do that.")
        requested_user = get_object_or_404(self.model, username=request.data.get('username')) # Fetch user
        is_delivery_crew = request.data.get('is_delivery_crew')
        if is_delivery_crew != "False":
            requested_user.groups.add(Group.objects.get(name='Delivery Crew'))
        else:
            requested_user.groups.remove(Group.objects.get(name='Delivery Crew'))
        print("Hi!")
        return Response(UserSerializer(requested_user).data, status.HTTP_202_ACCEPTED) # Confirmation message