from django.conf.urls import url
from manager.viewsets import LevelViewset, ProjectViewset, SoldierKitCollectionViewset
from django.urls import path, include
from rest_framework import routers
from . import views
from django.conf import settings

import manager

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('levels', LevelViewset, basename='level')
router.register('projects', ProjectViewset, basename='project')
router.register('soldierkitcollections', SoldierKitCollectionViewset, basename='soldierkitcollection')


urlpatterns = [
    path("manager-base/", views.manager_base, name="manager-base"),
    path("login/", views.manager_login, name="manager-login"),
    path("create-project/", views.manager_create_project, name="manager-create-project"),
    path("emit/", views.manager_emit_event, name='manager-emit-event'),
    path("clear-tasks/", views.manager_clear_tasks, name="manager-clear-tasks"),
    path("project/", views.manager_get_projects, name = 'manager-get-projects'),
    path('assets/', views.manager_get_assets, name='manager-get-assets'),
    path('players/', views.manager_get_players, name='manager-get-players'),
    # path('levels/', views.manager_get_level_internal, name='manager-get-level-internal'),

    path("project/<int:project_id>/", views.manager_get_project, name='manager-get-project'),
    path("project/<int:project_id>/record/", views.manager_record_player_path, name='manager-record'),
    path("project/<int:project_id>/finish-record/", views.manager_on_recorded_path, name='manager-finish-record'),
    path("project/<int:project_id>/export/", views.manager_export_project, name='manager-export-project'),
    path("project/<int:project_id>/level/", views.manager_get_levels, name='manager-get-levels'),
    path("project/<int:project_id>/level/<int:level_id>/add-spawn-point/<int:faction>/", views.manager_add_spawn_point, name='manager-add-spawn-point'),
    path("project/<int:project_id>/level/<int:level_id>/", views.manager_get_level, name='manager-get-level'),
    path("project/<int:project_id>/level/<int:level_id>/render/<int:raster_type>/<int:raster_layer>/", views.manager_render_level, name='manager-render-level'),
    path("project/<int:project_id>/level/add/", views.manager_add_level, name="manager-add-level"),
    path("project/<int:project_id>/level/<int:level_id>/add-feature/<str:feature_type>/", views.manager_add_level_feature, name="manager-add-level-feature"),
    path("project/<int:project_id>/level/add-block/", views.manager_add_level_block, name="manager-add-level-block"),
    path("project/<int:project_id>/level/add-block/complete/", views.manager_complete_level_block, name="manager-add-level-block"),
    path("project/<int:project_id>/level/reset/rasters/", views.manager_clear_level_data, name = 'manager-clear-level-rasters'),
    path("project/<int:project_id>/tasks/", views.manager_get_tasks, name='manager-get-tasks'),
    path("project/<int:project_id>/tasks/start/", views.manager_start_all_tasks, name='manager-start-tasks-all'),
    path("project/<int:project_id>/level/update/", views.manager_update_level, name='manager-update-level'),
    path("project/<int:project_id>/level/<int:level_id>/reset/", views.manager_reset_level_data, name='manager-reset-level-data'),
    path("project/<int:project_id>/level/<int:level_id>/on-level-loaded/", views.manager_on_level_loaded, name='manager-on-level-loaded'),
    path("project/<int:project_id>/level/<int:level_id>/recalculate/", views.manager_recalculate_costs, name='manager-recalculate-costs'),
    path("project/<int:project_id>/level/<int:level_id>/kits/", views.manager_push_soldier_kit_data, name="manager-push-kit-data"),
    path("project/<int:project_id>/level/<int:level_id>/export/", views.manager_export_level, name='manager-export-level'),
    path("project/<int:project_id>/get-level-id/", views.manager_get_level_id, name="manager-get-level-id"),

    path("utils/assets/import-from-csv/", views.manager_import_asset_from_csv, name="manager-import-asset-from-csv"),
    path("utils/assets/clear/", views.manager_clear_assets, name="manager-clear-assets")
]

urlpatterns += router.urls