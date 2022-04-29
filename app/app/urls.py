from django.contrib import admin
from django.urls import include, path
from app.views import BacktestList, BacktestDetail
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('generate/', views.generate),
    path('backtest/', views.start_execution),
    path('backtests/', BacktestList.as_view()),
    path('backtests/<int:id>/', BacktestDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
