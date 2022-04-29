from django.contrib import admin
from app.models import Backtest

@admin.register(Backtest)
class BacktestAdmin(admin.ModelAdmin):
    list_display = ("symbol", "strategy", "start_time", "end_time", "bin_size", "result")
    search_fields = ("start_time", "end_time", "result")
    list_filter = ("symbol", "strategy")
    readonly_fields = ("symbol", "strategy", "start_time", "end_time", "bin_size", "result")
