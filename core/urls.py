from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'core'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('core/cycles/', views.cycle_list, name='cycle_list'),
    path('core/cycles/ajouter/', views.cycle_create, name='cycle_create'),
    path('core/cycles/modifier/<int:pk>/', views.cycle_edit, name='cycle_edit'),
    path('core/cycles/supprimer/<int:pk>/', views.cycle_delete, name='cycle_delete'),
    path('core/niveaux/', views.niveau_list, name='niveau_list'),
    path('core/niveaux/ajouter/', views.niveau_create, name='niveau_create'),
    path('core/niveaux/modifier/<int:pk>/', views.niveau_edit, name='niveau_edit'),
    path('core/niveaux/supprimer/<int:pk>/', views.niveau_delete, name='niveau_delete'),
    path('core/periodes/', views.periode_list, name='periode_list'),
    path('core/periodes/ajouter/', views.periode_create, name='periode_create'),
    path('core/periodes/modifier/<int:pk>/', views.periode_edit, name='periode_edit'),
    path('core/periodes/supprimer/<int:pk>/', views.periode_delete, name='periode_delete'),
    path('authentification/', include('authentification.urls')),
    path('scolarite/', include('scolarite.urls')),
    path('enseignement/', include('enseignement.urls')),
    path('presences/', include('presences.urls')),
    path('finances/', include('finances.urls')),
    path('rapports/', include('rapports.urls')),
    path('ressources-humaines/', include('ressources_humaines.urls')),
    path('api/auth/', include('authentification.api_urls')),
    path('api/scolarite/', include('scolarite.api_urls')),
    path('api/enseignement/', include('enseignement.api_urls')),
    path('api/finances/', include('finances.api_urls')),
    path('api/', include('rapports.api_urls')),
]

if settings.DEBUG:
    if settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
