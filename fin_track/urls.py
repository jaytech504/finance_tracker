from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('transaction/', views.add_transaction, name='transact'),
    path('summary/', views.summary, name='summary'),
    path('fetch-bank-transactions/', views.fetch_bank_transactions, name='fetch_bank_transactions'),  # Fetch transactions via Yodlee
    path('link-bank-card/', views.link_bank_card, name='link_bank_card'),
    path('save-linked-card/', views.save_linked_card, name='save_linked_card'),

]
