from django.contrib import admin
from django.urls import path,include, re_path
from django.conf import settings
from django.views.static import serve
from django.conf.urls.static import static
from django.views.generic import RedirectView


urlpatterns = [
  path('', RedirectView.as_view(url='recursos/login/', permanent=False)),
    path('admin/', admin.site.urls),
    path('recursos/',include('recursos.urls')),
    path('auth/', include('usuarios.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]


urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
