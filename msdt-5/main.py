from datetime import datetime
from typing import List, Optional


class Product:
    def __init__(self, name: str, price: float, category: str, stock: int):
        self.name = name
        self.price = price
        self.category = category
        self.stock = stock

    def reduce_stock(self, quantity: int):
        if quantity > self.stock:
            raise ValueError(f"Not enough stock for {self.name}. Available: {self.stock}")
        self.stock -= quantity

    def __repr__(self):
        return f"Product(name={self.name}, price={self.price}, category={self.category}, stock={self.stock})"


class CartItem:
    def __init__(self, product: Product, quantity: int):
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")
        self.product = product
        self.quantity = quantity

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def __repr__(self):
        return f"CartItem(product={self.product}, quantity={self.quantity})"


class ShoppingCart:
    def __init__(self):
        self.items: List[CartItem] = []
        self.logs: List[str] = []

    def add_item(self, product: Product, quantity: int):
        if product.stock < quantity:
            raise ValueError(f"Not enough stock for {product.name}. Available: {product.stock}")

        for item in self.items:
            if item.product == product:
                item.quantity += quantity
                product.reduce_stock(quantity)
                self.logs.append(f"Updated quantity for {product.name} to {item.quantity}")
                return
        product.reduce_stock(quantity)
        self.items.append(CartItem(product, quantity))
        self.logs.append(f"Added {quantity} of {product.name} to the cart")

    def update_quantity(self, product: Product, quantity: int):
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")
        for item in self.items:
            if item.product == product:
                diff = quantity - item.quantity
                if diff > 0:
                    product.reduce_stock(diff)
                item.quantity = quantity
                self.logs.append(f"Updated quantity for {product.name} to {quantity}")
                return
        raise ValueError(f"Product {product.name} not found in cart")

    def remove_item(self, product: Product):
        self.items = [item for item in self.items if item.product != product]
        self.logs.append(f"Removed {product.name} from the cart")

    def calculate_total(self):
        return sum(item.total_price for item in self.items)

    def clear_cart(self):
        self.items = []
        self.logs.append("Cleared the cart")

    def print_logs(self):
        for log in self.logs:
            print(log)

    def __repr__(self):
        return f"ShoppingCart(items={self.items})"


class Coupon:
    def __init__(self, code: str, discount: float, expiry_date: datetime):
        self.code = code
        self.discount = discount
        self.expiry_date = expiry_date

    def is_valid(self):
        return datetime.now() <= self.expiry_date

    def apply_discount(self, total: float):
        if not self.is_valid():
            raise ValueError("Coupon is expired")
        return total * (1 - self.discount)

    def __repr__(self):
        return f"Coupon(code={self.code}, discount={self.discount}, expiry_date={self.expiry_date})"


class Order:
    def __init__(self, cart: ShoppingCart, discount: float = 0.0, coupon: Optional[Coupon] = None):
        if not (0.0 <= discount <= 1.0):
            raise ValueError("Discount must be between 0.0 and 1.0")
        self.cart = cart
        self.discount = discount
        self.coupon = coupon
        self.order_date = datetime.now()
        self.total = self.calculate_final_total()

    def calculate_final_total(self):
        total = self.cart.calculate_total() * (1 - self.discount)
        if self.coupon:
            total = self.coupon.apply_discount(total)
        return total

    def __repr__(self):
        return f"Order(total={self.total}, date={self.order_date}, coupon={self.coupon})"