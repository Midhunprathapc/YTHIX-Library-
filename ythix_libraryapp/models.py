from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=200, null=True)
    contact_no = models.CharField(max_length=20, null=True, unique=True)
    image = models.ImageField(upload_to='images/profile_images/', null=True, blank=True)
    Residential_Address = models.TextField()
    status = models.IntegerField(default=0) 

    def __str__(self):
        return self.user.username

class Publisher(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
class Author(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
    
class BookType(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100) 
    
    def __str__(self):
        if self.author:
            return f"{self.author.name} - {self.name}"
        return self.name
    
class Book(models.Model):
    name = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    book_type = models.ForeignKey(BookType, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='images/books/')
    
    def __str__(self):
        return self.name

class Rental(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rent_date = models.DateField(auto_now_add=True)
    due_date = models.DateField() 
    return_date = models.DateField(null=True, blank=True)
    is_lost = models.BooleanField(default=False) 
    fine_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.IntegerField(default=0)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items_details = models.TextField() 
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.book.price