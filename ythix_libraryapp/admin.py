from django.contrib import admin
from .models import *

admin.site.register(Profile)
admin.site.register(Publisher)
admin.site.register(Book)
admin.site.register(Rental)
admin.site.register(Cart)