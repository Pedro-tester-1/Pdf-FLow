from flujopdf import views
from django.urls import path, include
from django.contrib.auth.views import LogoutView

urlpatterns = [
 path(r'', views.main, name='main'),
 path(r'valida_user/', views.valida_user, name='valida_user'),
 path(r'login/', views.login_view, name='login'),
 path(r'register/', views.register, name='register'),
 path(r'crear_usuario/', views.crear_usuario, name='crear_usuario'),
 path(r'load_jobs/', views.load_jobs, name='load_jobs'),
 path(r'toggle_job_state/', views.toggle_job_state, name='toggle_job_state'),
 path(r'page_svg/<int:pageid>/', views.page_svg, name='page_svg'),
 path(r'deletejob/', views.deletejob, name='deletejob'),
 path(r'add_pages/', views.add_pages_to_job, name='add_pages_to_job'),
 path(r'pages/<int:jobid>/', views.pages, name='pages'),
 path(r'logout/', LogoutView.as_view(), name='logout'),
 path(r'scan_input/', views.scan_input, name='scan_input'),
 path(r'toggle_page_state/', views.toggle_page_state, name='toggle_page_state'),
 path(r'versions/', views.versions, name='versions'),
 path(r'versions/create/', views.create_version, name='create_version'),
 path(r'versions/<int:versionid>/', views.version_detail, name='version_detail'),
 path(r'versions/delete/', views.delete_version, name='delete_version'),
 path(r'versions/comentario/', views.add_comentario, name='add_comentario'),
]

