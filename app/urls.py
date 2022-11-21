from django.urls import path
from . import views

urlpatterns =[
    path('login', views.login, name='login'),
    path('', views.home, name='home'),
    path('api/check_status/',views.check_status.as_view())
]