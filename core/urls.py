from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
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
