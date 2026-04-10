from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('accounts/', include('accounts.urls')),
    path('eleves/', include('eleves.urls')),
    path('academics/', include('academics.urls', namespace='academics')),
    path('presences/', include('presences.urls')),
    path('finances/', include('finances.urls', namespace='finances')),
    path('rapports/', include('rapports.urls')),
    path('api/', include('rapports.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
