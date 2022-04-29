from app.models import Backtest
from app.serializers import BacktestSerializer
from rest_framework import generics

class BacktestList(generics.ListAPIView):
    queryset = Backtest.objects.all()
    serializer_class = BacktestSerializer

class BacktestDetail(generics.RetrieveAPIView):
    queryset = Backtest.objects.all()
    serializer_class = BacktestSerializer
    lookup_field = 'id'