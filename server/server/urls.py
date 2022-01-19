from django.contrib import admin
from django.urls import include, re_path
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views

from budget.views import BudgetViewSet, ExpensesViewSet

api_router = routers.DefaultRouter()
api_router.register(r"budgets", BudgetViewSet, basename="budgets")
api_router.register(r"expenses", ExpensesViewSet, basename="expenses")

urlpatterns = [
    re_path("^admin/", admin.site.urls),
    re_path(r"^", include(api_router.urls)),
    re_path("^api/token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    re_path("^api/token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
]
