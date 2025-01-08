from django.contrib import admin
from .models import Transaction, TotalIncome, Budget
# Register your models here.
admin.site.register(Transaction)
admin.site.register(TotalIncome)
admin.site.register(Budget)