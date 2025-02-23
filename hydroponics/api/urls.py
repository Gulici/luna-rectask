from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserView, HydroponicsSystemView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', UserView.as_view(), name='users_list'),
    path('users/<int:user_id>/', UserView.as_view(), name='user_detail'),
    path('systems/', HydroponicsSystemView.as_view(), name='systems_list'),
    path('systems/<int:pk>/', HydroponicsSystemView.as_view(), name='system_detail'),    
]
