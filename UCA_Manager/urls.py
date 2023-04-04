from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


from UCA_Manager import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('account.urls')),
    path('', include('workspace_editor.urls')),
    path('', include('loader.urls')),
]

urlpatterns += staticfiles_urlpatterns()

# if settings.DEBUG:
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
