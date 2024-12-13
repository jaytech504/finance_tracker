from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('dashboard/', views.home, name='home'),
    path('summary/', views.summary, name='summary'),
    path('report/', views.report, name='report'),
    path('download-transaction/', views.download_transactions, name='download_transactions'),
    path('download-csv/', views.download_transactions_csv, name='download_transactions_csv'),
    path('download-pdf/', views.download_transactions_pdf, name='download_transactions_pdf'),

]
