from django.urls import path, include
from . import views
from django.conf import settings



urlpatterns = [
    path("manager-base/", views.manager_base, name="manager-base"),
    path("login/", views.manager_login, name="manager-login"),
    path("create-project/", views.manager_create_project, name="manager-create-project"),
    path("project/", views.manager_get_projects, name = 'manager-get-projects'),

    path("project/<int:project_id>/", views.manager_get_project, name='manager-get-project'),
    path("project/<int:project_id>/level/", views.manager_get_levels, name='manager-get-levels'),
    path("project/<int:project_id>/level/<int:level_id>/", views.manager_get_level, name='manager-get-level'),
    path("project/<int:project_id>/level/<int:level_id>/render/<int:raster_type>/<int:raster_layer>/", views.manager_render_level, name='manager-render-level'),
    path("project/<int:project_id>/level/add/", views.manager_add_level, name="manager-add-level"),
    path("project/<int:project_id>/level/add-block/", views.manager_add_level_block, name="manager-add-level-block"),
    path("project/<int:project_id>/level/add-block/complete/", views.manager_complete_level_block, name="manager-add-level-block"),
    path("project/<int:project_id>/level/reset/rasters/", views.manager_clear_level_data, name = 'manager-clear-level-rasters')

]