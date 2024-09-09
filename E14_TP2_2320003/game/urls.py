from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('buy/<int:drug_id>/', views.buy_drug, name='buy_drug'),
    path('sell/<int:drug_id>/', views.sell_drug, name='sell_drug'),
    path('change_zone/', views.change_zone, name='change_zone'),
    path('clear_session/', views.clear_session, name='clear_session'),
]