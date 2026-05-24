from django.urls import path
from .views import (NotificationListView, NotificationMarquerLuView, NotificationToutLireView,)

urlpatterns = [

    path('notifications/',NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/lire/',NotificationMarquerLuView.as_view(), name='notification-lire'),
    path('notifications/tout-lire/',NotificationToutLireView.as_view(), name='notification-tout-lire'),

]