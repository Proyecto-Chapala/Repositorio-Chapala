from django.urls import path
from . import views

app_name = 'operaciones'

urlpatterns = [
    path('', views.index, name='index'),
    # API Productos
    path('api/productos/', views.api_productos_list, name='api_productos_list'),
    path('api/productos/crear/', views.api_producto_create, name='api_producto_create'),
    path('api/productos/<int:pk>/', views.api_producto_detail, name='api_producto_detail'),
    path('api/productos/<int:pk>/modificar/', views.api_producto_update, name='api_producto_update'),
    path('api/productos/<int:pk>/eliminar/', views.api_producto_delete, name='api_producto_delete'),
]
