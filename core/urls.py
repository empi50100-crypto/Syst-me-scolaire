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
    path('eleves/', include('eleves.urls')),
    path('academics/', include('academics.urls', namespace='academics')),
    path('presences/', include('presences.urls')),
    path('finances/', include('finances.urls', namespace='finances')),
    path('rapports/', include('rapports.urls')),
    path('ressources-humaines/', include('ressources_humaines.urls', namespace='ressources_humaines')),
    path('api/auth/', include('authentification.api_urls')),
    path('api/eleves/', include('eleves.api_urls')),
    path('api/academics/', include('academics.api_urls')),
    path('api/finances/', include('finances.api_urls')),
    path('api/', include('rapports.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
