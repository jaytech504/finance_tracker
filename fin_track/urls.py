from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('transaction/', views.add_transaction, name='transact'),
    path('summary/', views.summary, name='summary'),
    path('fetch-transactions/', views.fetch_transactions, name='fetch_transactions'),

]
