from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views

from budget.views import BudgetViewSet, ExpensesViewSet

api_router = routers.DefaultRouter()
api_router.register(r"budgets", BudgetViewSet, basename="budgets")
api_router.register(r"expenses", ExpensesViewSet, basename="expenses")

urlpatterns = [
    path("admin/", admin.site.urls),
    path(r"", include(api_router.urls)),
    path("api/token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
