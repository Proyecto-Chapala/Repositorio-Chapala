from django.urls import path
from . import views
from . import views_daily_reports

app_name = 'operaciones'

urlpatterns = [
    path('', views.index, name='index'),
    # API Productos
    path('api/productos/', views.api_productos_list, name='api_productos_list'),
    path('api/productos/crear/', views.api_producto_create, name='api_producto_create'),
    path('api/productos/<int:pk>/', views.api_producto_detail, name='api_producto_detail'),
    path('api/productos/<int:pk>/modificar/', views.api_producto_update, name='api_producto_update'),
    path('api/productos/<int:pk>/eliminar/', views.api_producto_delete, name='api_producto_delete'),

    # --- Lista de Pozos (Temporal) ---
    path('pozos/', views.pozos_list_view, name='pozos_list'),

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

    # --- Project Main Screen ---
    path('pozos/<int:pk>/', views.pozo_main_view, name='pozo_main'),

# --- Drilling Fluids and Equipment (Avances) ---
    path('pozos/<int:pk>/drilling-fluids-equipment/', views_daily_reports.daily_reports_hub_view, name='daily_reports_hub'),
    path('pozos/<int:pk>/daily-reports/', views_daily_reports.daily_reports_hub_view, name='daily_reports_hub_alias'),
    path('pozos/<int:pk>/daily-report/<int:reporte_pk>/', views_daily_reports.reporte_diario_detalle_view, name='reporte_diario_detalle'),
    
    path('api/pozos/<int:pk>/reportes-diarios/', views_daily_reports.api_reportes_diarios_list, name='api_reportes_diarios_list'),
    path('api/pozos/<int:pk>/reportes-diarios/crear/', views_daily_reports.api_reporte_diario_crear, name='api_reporte_diario_crear'),
    path('api/pozos/<int:pk>/reportes-diarios/<int:reporte_pk>/eliminar/', views_daily_reports.api_reporte_diario_eliminar, name='api_reporte_diario_eliminar'),
    path('api/pozos/<int:pk>/reportes-diarios/<int:reporte_pk>/general/guardar/', views_daily_reports.api_reporte_diario_general_guardar, name='api_reporte_diario_general_guardar'),
    path('pozos/<int:pk>/daily-report/<int:reporte_pk>/excel/', views_daily_reports.reporte_diario_excel_view, name='reporte_diario_excel'),
    path('api/pozos/<int:pk>/survey-stations/', views_daily_reports.api_well_survey_list, name='api_well_survey_list'),
    path('api/pozos/<int:pk>/survey-stations/guardar/', views_daily_reports.api_well_survey_guardar, name='api_well_survey_guardar'),
    path('api/pozos/<int:pk>/daily-report/<int:reporte_pk>/cost-overview/', views_daily_reports.api_cost_overview_detail, name='api_cost_overview_detail'),
    
    path('api/pozos/<int:pk>/propiedades-extra/', views_daily_reports.api_propiedades_extra_list, name='api_propiedades_extra_list'),
    path('api/pozos/<int:pk>/propiedades-extra/guardar/', views_daily_reports.api_propiedades_extra_guardar, name='api_propiedades_extra_guardar'),
    path('api/pozos/<int:pk>/formation-tops/', views_daily_reports.api_formation_tops_list, name='api_formation_tops_list'),
    path('api/pozos/<int:pk>/formation-tops/guardar/', views_daily_reports.api_formation_tops_guardar, name='api_formation_tops_guardar'),
    path('api/pozos/<int:pk>/daily-report/<int:reporte_pk>/pumps-bits/', views_daily_reports.api_pumps_bits_detail, name='api_pumps_bits_detail'),
    path('api/pozos/<int:pk>/daily-report/<int:reporte_pk>/pumps-bits/guardar/', views_daily_reports.api_pumps_bits_guardar, name='api_pumps_bits_guardar'),
    path('api/pozos/<int:pk>/daily-report/<int:reporte_pk>/mud-properties/', views_daily_reports.api_mud_properties_detail, name='api_mud_properties_detail'),
    path('api/pozos/<int:pk>/daily-report/<int:reporte_pk>/mud-properties/guardar/', views_daily_reports.api_mud_properties_guardar, name='api_mud_properties_guardar'),

    # --- Pestaña 4: Geometría del Pozo (Well Geometry) ---
    path('api/pozos/<int:pk>/daily-report/<int:reporte_pk>/well-geometry/', views_daily_reports.api_well_geometry_detail, name='api_well_geometry_detail'),
    path('api/pozos/<int:pk>/daily-report/<int:reporte_pk>/well-geometry/guardar/', views_daily_reports.api_well_geometry_guardar, name='api_well_geometry_guardar'),
    path('api/pozos/<int:pk>/daily-report/<int:reporte_pk>/well-geometry/sarta-anterior/', views_daily_reports.api_sarta_reporte_anterior, name='api_sarta_reporte_anterior'),

    # --- Pestaña 5: Comentarios (Comments) ---
    path('api/pozos/<int:pk>/daily-report/<int:reporte_pk>/comentarios/', views_daily_reports.api_comentarios_detail, name='api_comentarios_detail'),
    path('api/pozos/<int:pk>/daily-report/<int:reporte_pk>/comentarios/guardar/', views_daily_reports.api_comentarios_guardar, name='api_comentarios_guardar'),

    # --- Well Header Information ---

    path('pozos/<int:pk>/well-header/', views.well_header_view, name='well_header'),
    path('api/pozos/<int:pk>/well-header/', views.api_well_header_detail, name='api_well_header_detail'),
    path('api/pozos/<int:pk>/well-header/guardar/', views.api_well_header_guardar, name='api_well_header_guardar'),
    path('api/pozos/<int:pk>/marketing-codes/guardar/', views.api_marketing_codes_guardar, name='api_marketing_codes_guardar'),

    # --- Well Casing Intervals (Cost) ---
    path('pozos/<int:pk>/casing-intervals/', views.casing_intervals_view, name='casing_intervals'),
    path('api/pozos/<int:pk>/casing-intervals/', views.api_intervalos_list, name='api_intervalos_list'),
    path('api/pozos/<int:pk>/casing-intervals/crear/', views.api_intervalo_crear, name='api_intervalo_crear'),
    path('api/pozos/<int:pk>/casing-intervals/<int:intervalo_pk>/', views.api_intervalo_actualizar, name='api_intervalo_actualizar'),
    path('api/pozos/<int:pk>/casing-intervals/<int:intervalo_pk>/eliminar/', views.api_intervalo_eliminar, name='api_intervalo_eliminar'),

    # --- Pit Information ---
    path('pozos/<int:pk>/pits/', views.pits_view, name='pits'),
    path('api/pozos/<int:pk>/pits/', views.api_pits_list, name='api_pits_list'),
    path('api/pozos/<int:pk>/pits/guardar/', views.api_fosas_guardar, name='api_fosas_guardar'),
    path('api/pozos/<int:pk>/pit-types/guardar/', views.api_tipos_fosa_guardar, name='api_tipos_fosa_guardar'),

    # --- Configuración de Pérdidas (Loss Setup) ---
    path('pozos/<int:pk>/loss-setup/', views.loss_setup_view, name='loss_setup'),
    path('api/pozos/<int:pk>/loss-setup/', views.api_categorias_perdida_list, name='api_categorias_perdida_list'),
    path('api/pozos/<int:pk>/loss-setup/guardar/', views.api_categorias_perdida_guardar, name='api_categorias_perdida_guardar'),

    # --- Configuración General (General Setup) ---
    path('pozos/<int:pk>/general-setup/', views.general_setup_view, name='general_setup'),
    path('api/pozos/<int:pk>/general-setup/', views.api_general_setup_detail, name='api_general_setup_detail'),
    path('api/pozos/<int:pk>/general-setup/guardar/', views.api_general_setup_guardar, name='api_general_setup_guardar'),
    path('api/pozos/<int:pk>/almacenes/', views.api_almacenes_list, name='api_almacenes_list'),
    path('api/pozos/<int:pk>/almacenes/guardar/', views.api_almacenes_guardar, name='api_almacenes_guardar'),
    path('api/pozos/<int:pk>/tipos-distribucion/', views.api_tipos_distribucion_list, name='api_tipos_distribucion_list'),
    path('api/pozos/<int:pk>/tipos-distribucion/guardar/', views.api_tipos_distribucion_guardar, name='api_tipos_distribucion_guardar'),

    # --- Productos / Equipos / Mallas Activos ---
    path('pozos/<int:pk>/active-items/', views.active_items_view, name='active_items'),
    path('api/equipos/', views.api_equipos_list, name='api_equipos_list'),
    path('api/mallas/', views.api_mallas_list, name='api_mallas_list'),
    path('api/pozos/<int:pk>/productos-activos/', views.api_productos_activos_list, name='api_productos_activos_list'),
    path('api/pozos/<int:pk>/productos-activos/guardar/', views.api_productos_activos_guardar, name='api_productos_activos_guardar'),
    path('api/pozos/<int:pk>/equipos-activos/', views.api_equipos_activos_list, name='api_equipos_activos_list'),
    path('api/pozos/<int:pk>/equipos-activos/guardar/', views.api_equipos_activos_guardar, name='api_equipos_activos_guardar'),
    path('api/pozos/<int:pk>/mallas-activas/', views.api_mallas_activas_list, name='api_mallas_activas_list'),
    path('api/pozos/<int:pk>/mallas-activas/guardar/', views.api_mallas_activas_guardar, name='api_mallas_activas_guardar'),

    # --- Catálogos Maestros (Equipos y Mallas de Zaranda) ---
    path('catalogos-maestros/', views.catalogos_maestros_view, name='catalogos_maestros'),
    path('api/equipos/crear/', views.api_equipo_create, name='api_equipo_create'),
    path('api/equipos/<int:pk>/modificar/', views.api_equipo_update, name='api_equipo_update'),
    path('api/equipos/<int:pk>/eliminar/', views.api_equipo_delete, name='api_equipo_delete'),
    path('api/mallas/crear/', views.api_malla_create, name='api_malla_create'),
    path('api/mallas/<int:pk>/modificar/', views.api_malla_update, name='api_malla_update'),
    path('api/mallas/<int:pk>/eliminar/', views.api_malla_delete, name='api_malla_delete'),

    # --- Catálogos Maestros: Propiedades de Equipo y Parámetros de Benchmark ---
    path('api/propiedades-equipo/', views.api_propiedades_equipo_list, name='api_propiedades_equipo_list'),
    path('api/propiedades-equipo/crear/', views.api_propiedad_equipo_create, name='api_propiedad_equipo_create'),
    path('api/propiedades-equipo/<int:pk>/modificar/', views.api_propiedad_equipo_update, name='api_propiedad_equipo_update'),
    path('api/propiedades-equipo/<int:pk>/eliminar/', views.api_propiedad_equipo_delete, name='api_propiedad_equipo_delete'),
    path('api/parametros-benchmark/', views.api_parametros_benchmark_list, name='api_parametros_benchmark_list'),
    path('api/parametros-benchmark/crear/', views.api_parametro_benchmark_create, name='api_parametro_benchmark_create'),
    path('api/parametros-benchmark/<int:pk>/modificar/', views.api_parametro_benchmark_update, name='api_parametro_benchmark_update'),
    path('api/parametros-benchmark/<int:pk>/eliminar/', views.api_parametro_benchmark_delete, name='api_parametro_benchmark_delete'),

    # --- Catálogo Maestro: Componentes de Sarta ---
    path('api/componentes-sarta/', views.api_componentes_sarta_list, name='api_componentes_sarta_list'),
    path('api/componentes-sarta/crear/', views.api_componente_sarta_create, name='api_componente_sarta_create'),
    path('api/componentes-sarta/<int:pk>/modificar/', views.api_componente_sarta_update, name='api_componente_sarta_update'),
    path('api/componentes-sarta/<int:pk>/eliminar/', views.api_componente_sarta_delete, name='api_componente_sarta_delete'),

    # --- Equipment Properties Setup ---
    path('pozos/<int:pk>/equipment-properties-setup/', views.equipment_properties_setup_view, name='equipment_properties_setup'),
    path('api/pozos/<int:pk>/equipment-properties-setup/', views.api_equipment_properties_detail, name='api_equipment_properties_detail'),
    path('api/pozos/<int:pk>/equipment-properties-setup/guardar/', views.api_equipment_properties_guardar, name='api_equipment_properties_guardar'),

    # --- Benchmark Setup ---
    path('pozos/<int:pk>/benchmark-setup/', views.benchmark_setup_view, name='benchmark_setup'),
    path('api/pozos/<int:pk>/benchmark-setup/definiciones/', views.api_benchmark_definiciones_detail, name='api_benchmark_definiciones_detail'),
    path('api/pozos/<int:pk>/benchmark-setup/definiciones/guardar/', views.api_benchmark_definiciones_guardar, name='api_benchmark_definiciones_guardar'),
    path('api/pozos/<int:pk>/benchmark-setup/targets/', views.api_benchmark_targets_detail, name='api_benchmark_targets_detail'),
    path('api/pozos/<int:pk>/benchmark-setup/targets/guardar/', views.api_benchmark_targets_guardar, name='api_benchmark_targets_guardar'),
]
