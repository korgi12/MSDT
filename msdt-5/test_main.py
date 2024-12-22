import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from main import Product, CartItem, ShoppingCart, Coupon, Order


def test_product_creation():
    product = Product("Laptop", 1500.0, "Electronics", 10)
    assert product.name == "Laptop"
    assert product.price == 1500.0
    assert product.category == "Electronics"
    assert product.stock == 10


def test_product_stock_reduction():
    product = Product("Book", 20.0, "Books", 5)
    product.reduce_stock(3)
    assert product.stock == 2

    with pytest.raises(ValueError):
        product.reduce_stock(3)  # Not enough stock


def test_cart_item_total_price():
    product = Product("Book", 20.0, "Books", 10)
    item = CartItem(product, 2)
    assert item.total_price == 40.0


def test_shopping_cart_add_item():
    cart = ShoppingCart()
    product = Product("Pen", 2.0, "Stationery", 5)
    cart.add_item(product, 3)
    assert len(cart.items) == 1
    assert cart.items[0].quantity == 3
    assert product.stock == 2  # Stock should decrease


def test_shopping_cart_update_quantity():
    cart = ShoppingCart()
    product = Product("Notebook", 5.0, "Stationery", 10)
    cart.add_item(product, 2)
    cart.update_quantity(product, 5)
    assert cart.items[0].quantity == 5
    assert product.stock == 5

    with pytest.raises(ValueError):
        cart.update_quantity(product, 0)  # Invalid quantity


def test_order_discount_calculation():
    cart = ShoppingCart()
    cart.add_item(Product("Phone", 1000.0, "Electronics", 5), 1)
    order = Order(cart, discount=0.1)
    assert order.total == 900.0


def test_coupon_application():
    cart = ShoppingCart()
    product = Product("Tablet", 500.0, "Electronics", 5)
    cart.add_item(product, 2)
    coupon = Coupon("SAVE10", 0.1, datetime.now() + timedelta(days=1))
    order = Order(cart, discount=0.0, coupon=coupon)
    assert order.total == 900.0  # 10% discount

    expired_coupon = Coupon("EXPIRED", 0.2, datetime.now() - timedelta(days=1))
    with pytest.raises(ValueError):
        Order(cart, discount=0.0, coupon=expired_coupon)  # Expired coupon


@pytest.mark.parametrize(
    "price, quantity, stock, expected_total",
    [
        (100.0, 1, 10, 100.0),
        (50.0, 2, 20, 100.0),
        (30.0, 5, 15, 150.0),
    ],
)
def test_cart_item_parametrized(price, quantity, stock, expected_total):
    product = Product("Gadget", price, "Electronics", stock)
    item = CartItem(product, quantity)
    assert item.total_price == expected_total


@pytest.mark.parametrize(
    "discount, expected_error",
    [
        (0.2, None),
        (1.2, ValueError),
        (-0.1, ValueError),
    ],
)
def test_order_discount_validation(discount, expected_error):
    cart = ShoppingCart()
    cart.add_item(Product("Game", 60.0, "Entertainment", 5), 1)

    if expected_error:
        with pytest.raises(expected_error):
            Order(cart, discount=discount)
    else:
        order = Order(cart, discount=discount)
        assert 0.0 <= order.discount <= 1.0


def test_mock_cart_calculation():
    cart = MagicMock()
    cart.calculate_total.return_value = 500.0
    order = Order(cart, discount=0.1)
    cart.calculate_total.assert_called_once()
    assert order.total == 450.0


def test_cart_logs():
    cart = ShoppingCart()
    product = Product("Keyboard", 50.0, "Electronics", 10)
    cart.add_item(product, 2)
    cart.update_quantity(product, 5)
    cart.clear_cart()

    assert "Added 2 of Keyboard to the cart" in cart.logs
    assert "Updated quantity for Keyboard to 5" in cart.logs
    assert "Cleared the cart" in cart.logs