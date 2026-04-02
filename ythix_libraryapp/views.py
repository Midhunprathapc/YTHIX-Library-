import random
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout 
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import *
from datetime import timedelta, date
from decimal import Decimal
from datetime import datetime
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render
from .models import Book, User, Profile, Rental, Order
from django.db.models import Sum
import re
# Create your views here.

def usersignup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        address = request.POST.get('address')
        contact_no = request.POST.get('contact_no')
        image = request.FILES.get('image')


        
        if User.objects.filter(username=username).exists():
            messages.info(request, 'Username already exists')
            return redirect('signup')
        elif User.objects.filter(email=email).exists():
            messages.info(request, 'Email already exists')
            return redirect('signup')
        elif Profile.objects.filter(contact_no=contact_no).exists():
            messages.info(request, 'Contact number already exists')
            return redirect('signup')
        elif len(contact_no) != 10:
            messages.info(request, 'Mobile number must be 10 digits')
            return redirect('signup')
        elif not email.endswith('@gmail.com'):
            messages.info(request, 'Invalid email format')
            return redirect('signup')
        

        else:
            user = User.objects.create_user(
                username=username,  
                email=email, 
                first_name=first_name, 
                last_name=last_name)
            user.save()
            profile = Profile(user=user, address=address, contact_no=contact_no, image=image)
            profile.save()
            messages.info(request, 'Registration successfully ! please wait for admin approval.')
            return redirect('login_view')
        
       
    return render(request, 'signup.html')

def login_view(request): 
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff:
                auth_login(request, user) 
                return redirect('admin_dashboard')
            else:
                auth_login(request, user) 
                messages.info(request, f'welcome {username}',extra_tags='password_update')
                return redirect('user_home')
        else:
            messages.error(request, 'invalid username or password',extra_tags='password_update')
            return redirect('login_view')
    return render(request, 'login.html')




def logout_user(request):
    logout(request)
    return redirect('login_view')




# admin 



def approve_user(request,k):
    profile=Profile.objects.get(user_id=k)
    user=profile.user
    password = str(random.randint(100000, 999999))  
    user.set_password(password)
    user.is_active = True 
    user.save()

    profile.status = 1
    profile.save()

    try:
        send_mail(
            'Account Approved',
            f'username : {user.username}\npassword : {password}',
            settings.EMAIL_HOST_USER,
            [user.email],
        )
        messages.success(request, f'User {user.username} approved and password emailed.')
    except:
        messages.error(request, 'User approved but email failed to send.')

    return redirect('admin_approve_list')

def admin_approve_list(request):
    pending_list = Profile.objects.filter(status=0)
    return render(request, 'admin_approve_list.html', {'profiles': pending_list})


def delete_user(request, k):
    user = get_object_or_404(User, id=k)
    username = user.username
    user_email = user.email

    try:
        send_mail(
            'Registration Update - YTHIX University',
            f'Dear {username},\n\nWe regret to inform you that your registration request for YTHIX University has not been approved by the Administrator.',
            settings.EMAIL_HOST_USER,
            [user_email],
        )
        messages.success(request, f'Rejection email sent to {username}.')
    except Exception as e:
        messages.error(request, f'User {username} will be deleted, but the notification email failed to send.')

    user.delete()
    return redirect('admin_approve_list')

def view_users(request):
    if not request.user.is_staff:
        return redirect('user_home')
    profiles = Profile.objects.all()
    pending_count = Profile.objects.filter(status=0).count()
    context = {
        'profiles': profiles,
        'pending_count': pending_count
    }
    return render(request, 'view_users.html', context)






def add_author_category(request):
    pending_count = Profile.objects.filter(status=0).count()
    
    if request.method == "POST":
        if 'submit_author' in request.POST:
            name = request.POST.get('author_name')
            if Author.objects.filter(name__iexact=name).exists():
                messages.error(request, f"The author '{name}' already exists!")
            else:
                Author.objects.create(name=name)
                messages.success(request, f"Author '{name}' added successfully.")
            return redirect('add_author_category')

        elif 'submit_bookcatg' in request.POST:
            name = request.POST.get('type_name')
            if BookType.objects.filter(name__iexact=name).exists():
                messages.error(request, f"The category '{name}' already exists!")
            elif name:
                BookType.objects.create(name=name)
                messages.success(request, f"Category '{name}' added successfully.")
            return redirect('add_author_category')
            
        elif 'submit_publisher' in request.POST:
            name = request.POST.get('publisher_name')
            if Publisher.objects.filter(name__iexact=name).exists():
                messages.error(request, f"The publisher '{name}' already exists!")
            elif name:
                Publisher.objects.create(name=name)
                messages.success(request, f"Publisher '{name}' added successfully.")
            return redirect('add_author_category')

    context = {
        'authors': Author.objects.all(),
        'booktypes': BookType.objects.all(),
        'publishers': Publisher.objects.all(), 
        'pending_count': pending_count,
    }
    return render(request, 'add_author_category.html', context)


def delete_author(request, a_id):
    author = get_object_or_404(Author, id=a_id)
    name = author.name
    author.delete()
    messages.success(request, f"Author '{name}' deleted.")
    return redirect('add_author_category')

def delete_book_category(request, bt_id):
    category = get_object_or_404(BookType, id=bt_id)
    category_name = category.name
    category.delete()
    messages.success(request, f"Category '{category_name}' deleted successfully.")
    return redirect('add_author_category')

def delete_publisher(request, p_id):
    publisher = get_object_or_404(Publisher, id=p_id)
    name = publisher.name
    publisher.delete()
    messages.success(request, f"Publisher '{name}' deleted successfully.")
    return redirect('add_author_category')







def admin_dashboard(request):
 
    total_books = Book.objects.count()
    total_members = User.objects.filter(is_staff=False).count()
    total_orders = Order.objects.count()
    pending_approvals = Profile.objects.filter(status=0).count()
    total_rental_books = Rental.objects.filter(status=0).count()
    sales_data = Order.objects.aggregate(total=Sum('total_price'))
    total_sales_amount = sales_data['total'] or 0
    fine_data = Rental.objects.filter(status=1).aggregate(total=Sum('fine_paid'))
    total_fines_collected = fine_data['total'] or 0
    fine_paying_list = Rental.objects.filter(status__in=[0, 2], fine_paid__gt=0).order_by('-rent_date')
    fine_paid_list = Rental.objects.filter(status=1, fine_paid__gt=0).order_by('-rent_date')
    total_fines_count = fine_paid_list.count()
    active_rentals_list = Rental.objects.filter(status=0).select_related('user', 'book').order_by('due_date')
    
    context = {
        'total_books': total_books,
        'total_members': total_members,
        'total_orders': total_orders,
        'pending_approvals': pending_approvals,
        'total_rental_books': total_rental_books,
        'total_sales_amount': total_sales_amount,
        'total_fines_collected': total_fines_collected,
        'pending_count': pending_approvals,
        'fine_paying_list': fine_paying_list,
        'fine_paid_list': fine_paid_list,
        'total_fines_count': total_fines_count,
        'active_rentals_list': active_rentals_list,
        'today': timezone.now().date(),
    }
    return render(request, 'admin_dashboard.html', context)



def add_book(request): 
    pending_count = Profile.objects.filter(status=0).count()
    authors = Author.objects.all()
    publishers = Publisher.objects.all()
    types = BookType.objects.all()
    
    if request.method == "POST":
        name=request.POST.get('name')
        author_id=request.POST.get('author') 
        publisher_id=request.POST.get('publisher')
        book_type_id=request.POST.get('type')
        price=request.POST.get('price')
        stock=request.POST.get('stock')  
        description=request.POST.get('description')
        image=request.FILES.get('image')
        
        exists = Book.objects.filter(name__iexact=name, author_id=author_id).exists()
            
        if exists:
            messages.error(request, f'The book "{name}" already exists in the library.')
            return redirect('add_book')
        
        Book.objects.create(
            name=name,
            author_id=author_id,
            publisher_id=publisher_id, 
            book_type_id=book_type_id,
            price=price, 
            stock=stock,   
            description=description,
            image=image
        )
      
        messages.success(request, "Book added successfully!")
        return redirect('show_books')
    
        
    return render(request, 'add_book.html', {
        'authors': authors,
        'publishers': publishers, 
        'types': types,
        'pending_count': pending_count
    })


def show_books(request):
    query = request.GET.get('q', '')
    categories_data = []
    all_categories = BookType.objects.all()
    
    for category in all_categories:
        category_books = Book.objects.filter(book_type=category).select_related('author', 'publisher')
        
        if query:
            category_books = category_books.filter(
                Q(name__icontains=query) | 
                Q(author__name__icontains=query) |
                Q(book_type__name__icontains=query)
            )
        
        if category_books.exists():
            category.filtered_books = category_books
            categories_data.append(category)

    context = {
        'categories_data': categories_data,
        'query': query,
    }
    return render(request, 'show_books.html', context)


def edit_book(request, id):
    book = get_object_or_404(Book, id=id)
    types = BookType.objects.all()
    publishers = Publisher.objects.all()
    authors = Author.objects.all() 

    if request.method == "POST":
        name = request.POST.get('name')
        author_id = request.POST.get('author')
        
        exists = Book.objects.filter(
            name__iexact=name, 
            author_id=author_id
        ).exclude(id=id).exists()
            
        if exists:
            messages.error(request, f'Another book with the name "{name}" by this author already exists.')
            return redirect('edit_book', id=id)

     
        book.name = name
        book.author_id = author_id 
        book.book_type_id = request.POST.get('type')
        book.publisher_id = request.POST.get('publisher')  
        book.price = request.POST.get('price')
        book.stock = request.POST.get('stock')
        book.description = request.POST.get('description')
        
        if request.FILES.get('image'):
            book.image = request.FILES.get('image')

        book.save()
        messages.success(request, f"Book '{book.name}' updated successfully!")
        return redirect('show_books')

    return render(request, 'edit_book.html', {
        'book': book,
        'types': types,
        'publishers': publishers,
        'authors': authors  
    })

def delete_book(request, id):
    book = get_object_or_404(Book, id=id)
    book.delete()
    return redirect('show_books')






def admin_rental_history(request):
    all_rentals = Rental.objects.all().select_related('user', 'book', 'book__author').order_by('-rent_date')
    return render(request, 'admin_rental_history.html', {
        'all_rentals': all_rentals
    })
    
    
def admin_purchase_history(request):
    if not request.user.is_staff:
        return redirect('user_home')
    orders = Order.objects.all().select_related('user').order_by('-purchase_date')
    pending_count = Profile.objects.filter(status=0).count()

    return render(request, 'admin_purchase_history.html', {
        'orders': orders,
        'pending_count': pending_count
    })
    





# user 

def home(request):
    books = Book.objects.all().select_related('author', 'book_type')
    
    return render(request,'home.html',{'books': books, })


def user_home(request):
    categories = BookType.objects.all()
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
    books = Book.objects.all().select_related('author', 'book_type')

    return render(request, 'user_home.html', {
        'categories': categories,
        'cart_count': cart_count,
        'books': books, 
    })



def user_dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)
    today = timezone.now().date()
    
    recent_rentals = Rental.objects.filter(
        user=request.user, 
        status__in=[0, 3]
    ).order_by('-rent_date')[:5]

    all_active = Rental.objects.filter(user=request.user, status=0)
    remaining_fines = []
    calculated_total_fines = Decimal('0.00')

    for rental in all_active:
        usage_charge = Decimal('0.00')
        overdue_penalty = Decimal('0.00')
        
        
        days_held = (today - rental.rent_date).days
        if days_held > 10:
            usage_charge = Decimal('20.00')
            
       
        if rental.due_date < today:
            overdue_penalty = Decimal('50.00')
            
        total_due = usage_charge + overdue_penalty
        
        if total_due > 0:
            rental.total_due = total_due
            rental.usage_charge = usage_charge
            rental.overdue_penalty = overdue_penalty
            remaining_fines.append(rental)
            calculated_total_fines += total_due

    active_rentals_count = Rental.objects.filter(user=request.user, status__in=[0, 3]).count()
    total_purchases_count = Order.objects.filter(user=request.user).count()
    cart_count = Cart.objects.filter(user=request.user).count()
    recent_orders = Order.objects.filter(user=request.user).order_by('-purchase_date')[:5]
    
    overdue_rentals = Rental.objects.filter(user=request.user, status=0, due_date__lt=today)
    fine_history = Rental.objects.filter(user=request.user, status=1, fine_paid__gt=0).order_by('-return_date')

    context = {
        'profile': profile,
        'active_rentals_count': active_rentals_count,
        'total_purchases_count': total_purchases_count,
        'cart_count': cart_count,
        'recent_rentals': recent_rentals,
        'recent_orders': recent_orders,
        'remaining_fines': remaining_fines,
        'pending_fines_total': calculated_total_fines, 
        'today': today,
        'fine_history': fine_history,
        'overdue_rentals': overdue_rentals,
    }
    return render(request, 'user_dashboard.html', context)

def user_profile(request):
    categories = BookType.objects.all()
    cart_count = Cart.objects.filter(user=request.user).count()
    profile = get_object_or_404(Profile, user=request.user)

    return render(request, 'user_profile.html', {
        'profile': profile,
        'categories': categories,
        'cart_count': cart_count
          
    })  


def edit_profile(request):
    categories = BookType.objects.all()
    cart_count = Cart.objects.filter(user=request.user).count()
    profile = get_object_or_404(Profile, user=request.user)
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')  
        contact_no = request.POST.get('contact_no')
        address = request.POST.get('address')
        
       
        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            messages.error(request, 'Email already exists')
            return redirect('edit_profile')
        elif not email.endswith('@gmail.com'):
            messages.error(request, 'Invalid email format (Only @gmail.com allowed)')
            return redirect('edit_profile')
        elif Profile.objects.filter(contact_no=contact_no).exclude(id=profile.id).exists():
            messages.error(request, 'Contact number already exists')
            return redirect('edit_profile')
        elif len(contact_no) != 10:
            messages.error(request, 'Mobile number must be 10 digits')
            return redirect('edit_profile')
        

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()    
        profile.contact_no = contact_no
        profile.address = address
        if request.FILES.get('image'):
            profile.image = request.FILES.get('image')
        profile.save()
        
        messages.success(request, "Profile updated successfully!")
        return redirect('user_profile') 
        
    return render(request, 'user_edit_profile.html', {
        'user': request.user,
        'profile': profile,
        'categories': categories,
        'cart_count': cart_count
    })


def reset_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
       
        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect',extra_tags='password_update')
            return redirect('reset_password')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match',extra_tags='password_update')
            return redirect('reset_password')

        
        if len(new_password) < 8:
            messages.error(request, 'New password must be at least 8 characters',extra_tags='password_update')
            return redirect('reset_password')
        if not re.search(r"[0-9]", new_password):
            messages.error(request, 'New password must contain at least one number',extra_tags='password_update')
            return redirect('reset_password')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_password):
            messages.error(request, 'New password must contain at least one special character',extra_tags='password_update')
            return redirect('reset_password')

        
        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        
        messages.success(request, 'Password updated successfully',extra_tags='password_update')
        return redirect('login_view')

    return render(request, 'user_reset_password.html')






def user_showbooks(request):
    query = request.GET.get('q', '').strip()
    categories_data = []
    all_categories = BookType.objects.all()
    
    for category in all_categories:
        category_books = Book.objects.filter(book_type=category)
        
        if query:
            category_books = category_books.filter(
                Q(name__icontains=query) | 
                Q(author__name__icontains=query) | 
                Q(book_type__name__icontains=query) 
            )
        
        if category_books.exists():
            category.filtered_books = category_books
            categories_data.append(category)

    cart_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
    
    context = {
        'categories_data': categories_data, 
        'query': query,
        'cart_count': cart_count
    }
    return render(request, 'user_showbooks.html', context)


def rent_book(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)     
        taken_date_str = request.POST.get('taken_date')
        receiving_date_str = request.POST.get('receiving_date')
        taken_date = datetime.strptime(taken_date_str, '%Y-%m-%d').date()
        due_date = datetime.strptime(receiving_date_str, '%Y-%m-%d').date() 
        duration = (due_date - taken_date).days
        extra_charge = 20 if duration > 10 else 0
        
        if book.stock > 0:
            Rental.objects.create(
                user=request.user,
                book=book,
                rent_date=taken_date, 
                due_date=due_date,    
                fine_paid=0,
                status=0              
            )
            book.stock -= 1
            book.save()
            messages.success(request, "Book rented successfully.")
        else:
            messages.error(request, "Out of stock.")
            
    return redirect('rental_history')


def user_rental_book(request):
    categories = BookType.objects.all()
    cart_count = Cart.objects.filter(user=request.user).count()
    rentals = Rental.objects.filter(user=request.user).order_by('-rent_date')
    today = timezone.now().date()
    
    for r in rentals:
        if r.is_lost:
            r.total_bill = r.fine_paid
            r.late_fine = 0
        elif r.status == 1:
            r.total_bill = r.fine_paid
        else:
            days_held = (today - r.rent_date).days
            usage_charge = 20 if days_held > 10 else 0
            overdue_penalty = 50 if r.due_date < today else 0
            
        
            r.late_fine = usage_charge + overdue_penalty
            r.total_bill = r.late_fine           

    return render(request, 'user_rental_book.html', {
        'rentals': rentals, 
        'today': today, 
        'categories': categories,
        'cart_count': cart_count
    })


def return_book(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    if rental.status in [0, 3]:
        rental.status = 1
        rental.return_date = timezone.now().date()
        rental.book.stock += 1
        rental.book.save()
        rental.save()
        messages.success(request, "Book returned successfully.")
    return redirect('rental_history')


def report_lost(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    
    if not rental.is_lost:
        rental.is_lost = True
        penalty = Decimal('50.00')
        rental.fine_paid = rental.book.price + penalty 
        rental.status = 2 
        rental.save()
        
        messages.warning(request, f"Book marked as lost. Total Charge: ₹{rental.fine_paid}")
        
    return redirect('rental_history')


def rental_payment(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    today = timezone.now().date()
    late_fine = Decimal('0.00')
    total_to_pay = Decimal('0.00')

    if rental.is_lost:
        total_to_pay = rental.fine_paid
    else:
        days_held = (today - rental.rent_date).days
        usage_charge = Decimal('20.00') if days_held > 10 else Decimal('0.00')
        overdue_penalty = Decimal('50.00') if rental.due_date < today else Decimal('0.00')
        late_fine = usage_charge + overdue_penalty
        total_to_pay = late_fine

   
    if request.method == 'POST':
        rental.fine_paid = total_to_pay
        
        if rental.is_lost:
            rental.status = 1  
            rental.return_date = today
        else:  
            rental.status = 3    
        rental.save()

       
        subject = f"Payment Confirmation: {rental.book.name}"
        message = (
            f"Dear {request.user.first_name},\n\n"
            f"Your payment for '{rental.book.name}' was processed successfully.\n"
            f"Total Amount Paid: ₹{total_to_pay}\n\n"
            f"Thank you for using YTHIX Library!"
        )
        
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [request.user.email])
        except Exception as e:
            print(f"Email Error: {e}")

        messages.success(request, f"Payment of ₹{total_to_pay} successful!", extra_tags='payment_msg')
        return redirect('rental_history')

  
    transaction_type = "Lost Book Replacement" if rental.is_lost else "Rental Return Charges"
    
    return render(request, 'user_rentalbookpay.html', {
        'rental': rental,
        'total_to_pay': total_to_pay,
        'late_fine': late_fine, 
        'transaction_type': transaction_type,
        'is_lost_transaction': rental.is_lost
    })

# cart 


def cart_pg(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)
    count = cart_items.count()
    return render(request, 'cart_pg.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'count': count
    })

def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if book.stock > 0:
        cart_item, created = Cart.objects.get_or_create(user=request.user, book=book)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        book.stock -= 1
        book.save()
        
        messages.success(request, f"{book.name} added to cart.",extra_tags='cart_msg')
    else:
        messages.error(request, f"Sorry, {book.name} is currently out of stock.",extra_tags='cart_msg')
        
    return redirect('cart_pg')

def increase_qty(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)
    book = item.book
    if book.stock > 0:
        item.quantity += 1
        item.save()
        book.stock -= 1
        book.save()
    else:
        messages.warning(request, "Maximum stock reached. No more copies available.",extra_tags='cart_msg')
    return redirect('cart_pg')

def decrease_qty(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)
    book = item.book
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()
    book.stock += 1
    book.save()
    return redirect('cart_pg')

def remove_from_cart(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)
    book = item.book
    book.stock += item.quantity
    book.save()
    item.delete()
    messages.info(request, f"{book.name} removed from cart.")
    return redirect('cart_pg')

def checkout_view(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    cart_items = Cart.objects.filter(user=user)
    
    if not cart_items.exists():
        return redirect('user_home')

    total_price = sum(item.total_price() for item in cart_items)

    if request.method == 'POST':
        item_list = "".join([f"- {item.book.name} (Qty: {item.quantity}) : ₹{item.total_price()}\n" for item in cart_items])

        try:
            Order.objects.create(
                user=user,
                items_details=item_list,
                total_price=total_price,
                address=request.POST.get('address') or profile.address,
            )


            send_mail(
                'Order Confirmation - YTHIX Library',
                f"Dear {user.username},\n\nOrder Summary:\n{item_list}\nTotal: ₹{total_price}",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            cart_items.delete()
            messages.success(request, "Order placed successfully!",extra_tags='order_msg')
            
        except Exception as e:
            print(f"Error: {e}")
            cart_items.delete() 
            messages.error(request, 'Order processed but email failed.',extra_tags='order_msg')
            
        return redirect('user_home')

    return render(request, 'checkout.html', locals())







def category_filter(request, cat_id):
    categories = BookType.objects.all()
    selected_category = get_object_or_404(BookType, id=cat_id)
    filtered_books = Book.objects.filter(book_type_id=cat_id).select_related('author')
    categories_data = [{
        'name': selected_category.name,
        'filtered_books': filtered_books
    }]
    
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
    
    return render(request, 'user_showbooks.html', {
        'categories_data': categories_data, 
        'categories': categories,          
        'selected_cat_name': selected_category.name, 
        'cart_count': cart_count,
        'query': request.GET.get('q', '')  
    })

def user_base(request):
    return render(request,'user_base.html')