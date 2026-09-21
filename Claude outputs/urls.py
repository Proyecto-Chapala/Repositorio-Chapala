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

    # --- Wizard de Nuevo Pozo (shell SPA) ---
    path('pozos/nuevo/', views.pozo_wizard_view, name='pozo_wizard_nuevo'),
    path('pozos/<int:pk>/continuar/', views.pozo_wizard_view, name='pozo_wizard_continuar'),

    # --- API Wizard de Pozo ---
    path('api/pozos/plantillas/', views.api_pozos_plantillas, name='api_pozos_plantillas'),
    path('api/pozos/<int:pk>/', views.api_pozo_detail, name='api_pozo_detail'),
    path('api/pozos/paso1/', views.api_pozo_paso1, name='api_pozo_paso1_crear'),
    path('api/pozos/<int:pk>/paso1/', views.api_pozo_paso1, name='api_pozo_paso1_actualizar'),
    path('api/pozos/<int:pk>/paso2/', views.api_pozo_paso2, name='api_pozo_paso2'),
    path('api/pozos/<int:pk>/paso3/', views.api_pozo_paso3, name='api_pozo_paso3'),
    path('api/pozos/<int:pk>/confirmar/', views.api_pozo_confirmar, name='api_pozo_confirmar'),

    # --- Spud Date (pantalla única al abrir el pozo por primera vez) ---
    path('pozos/<int:pk>/spud-date/', views.pozo_spud_date_view, name='pozo_spud_date'),
    path('api/pozos/<int:pk>/spud-date/', views.api_pozo_spud_date, name='api_pozo_spud_date'),
]
