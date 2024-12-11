from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('summary/', views.summary, name='summary'),
    path('report/', views.report, name='report'),
    path('fetch-transactions/', views.fetch_transactions, name='fetch_transactions'),
    path('download-transaction/', views.download_transactions, name='download_transactions'),
    path('download-csv/', views.download_transactions_csv, name='download_transactions_csv'),
    path('download-pdf/', views.download_transactions_pdf, name='download_transactions_pdf'),

]
