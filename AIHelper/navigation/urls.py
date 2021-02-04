from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test/', views.test, name='test'),
    path("find-path/", views.find_path, name="find_path"),
    path("update-level/", views.update_level, name="update_level"),
    path("render/", views.render_cost_surface, name="render"),
    path("export/", views.export, name="export"),
    path("import/", views.import_data, name="import"),
    path("modify/", views.modify_cost_surface, name="modify"),
    path("emit/", views.emit_action, name="emit"),
    
    path("close-faststream/", views.close_faststream, name="close faststream gate"),

    path('<str:level_name>/render/', views.render_level, name="render level"),
    path("register-user/", views.register_user, name='register-user'),
    # path("login-user/", views.login_user, name='login-user'),
    
    path("auth-test/", views.auth_test, name='auth-test')
]