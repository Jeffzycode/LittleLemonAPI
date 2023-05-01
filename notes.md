**ADMIN ACCOUNT:**
* USERNAME: `admin`
* PASSWORD: `123`

**MANAGER ACCOUNT:**
* USERNAME: `manager`
* PASSWORD: `123`

**CUSTOMER ACCOUNT:**
* USERNAME: `customer`
* PASSWORD: `a7bn9fcs`  

**DELIVERY CREW ACCOUNT:**
* USERNAME: `deliverycrew`
* PASSWORD: `a7bn9fcs`

1.	The admin can assign users to the manager group

Admins can log in to the admin portal to do this.

2.	You can access the manager group with an admin token

The admin token holds a superset of the manager group's permissions.

3.	The admin can add menu items 

The admin can send a POST request to http://127.0.0.1:8000/api/menu-items, and can also log into the admin portal.

4.	The admin can add categories

Admins can send a POST request to http://127.0.0.1:8000/api/categories. They can also log in to the admin portal to do this.

5.	Managers can log in

Managers can log in using the admin portal.

6.	Managers can update the item of the day

Managers can send a PATCH request to http://127.0.0.1:8000/api/menu-items
Required Fields: `id`, `featured` (The ID of the Menu Item and a Boolean indicating whether the item will be featured or not)

7.	Managers can assign users to the delivery crew

Managers can send a PATCH request to http://127.0.0.1:8000/api/assign
Required Fields: `username`, `is_delivery_crew` (The username of the User, and a Boolean indicating whether this user is being added to the delivery crew)
Note that anything other than "False" will be treated as True.

8.	Managers can assign orders to the delivery crew

Managers can send a PATCH request to http://127.0.0.1:8000/api/order to update an order.
A token is required.
Required Fields: `order_id`, `delivery_crew` (The ID of the Order and the username of the delivery crew being assigned)
Note that the user corresponding to the supplied username must be a part of the `delivery_crew` group.

9.	The delivery crew can access orders assigned to them

Delivery Crew can send a GET request to http://127.0.0.1:8000/api/order?perpage=ITEMSPERPAGE to view orders assigned to them.
A token is required.
Managers can also send a GET request to http://127.0.0.1:8000/api/order?perpage=ITEMSPERPAGE to view all orders.

10.	The delivery crew can update an order as delivered

Delivery Crew can send a PATCH request to http://127.0.0.1:8000/api/order to update an order.
A token is required.
Required Fields: `order_id`, `status` (The ID of the Order and a Boolean denoting the new status)

11.	Customers can register

Anyone can send a POST request to http://127.0.0.1:8000/auth/users/
Required Fields: `username`, `password`

12.	Customers can log in using their username and password and get access tokens

Anyone with an account can send a POST request to http://127.0.0.1:8000/api-token-auth/ to get an access token.
Required Fields: `username`, `password`

13.	Customers can browse all categories 

Anyone can browse http://127.0.0.1:8000/api/menu-items

14.	Customers can browse all the menu items at once

Anyone can browse http://127.0.0.1:8000/api/menu-items?perpage=1000

15.	Customers can browse menu items by category

Anyone can browse http://127.0.0.1:8000/api/menu-items?category=CATEGORY

16.	Customers can paginate menu items

Anyone can browse http://127.0.0.1:8000/api/menu-items?perpage=X

17.	Customers can sort menu items by price

Anyone can browse http://127.0.0.1:8000/api/menu-items?ordering=price

18.	Customers can add menu items to the cart

Customers can make a POST request to http://127.0.0.1:8000/api/cart
A Token is required to make this request.
Required Fields: `menuitem_id`, `quantity` (The ID of the item ordered, and the number of items ordered).

19.	Customers can access previously added items in the cart

Customers can make a GET request to http://127.0.0.1:8000/api/cart?perpage=ITEMSPERPAGE
A Token is required to make this request.
Customers can make a PATCH request to http://127.0.0.1:8000/api/cart
Required Fields: `cart_id`, `new_quantity` (ID of the Cart, New Quantity being ordered)
Customers can make a DELETE request to http://127.0.0.1:8000/api/cart
Required Fields: `cart_id` (ID of the Cart)

20.	Customers can place orders

Customers can make a POST request to http://127.0.0.1:8000/api/order, with an optional field `cart_id` (the ID of the cart whose contents are ordered).
If no field is provided, then an order is created consisting of all cart items. 

21.	Customers can browse their own orders

Customers can make a GET request to http://127.0.0.1:8000/api/order-items, with options to order, filter by status, and paginate.
A Token is required to make this request.