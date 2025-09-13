from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path('tasks/', include('tasks.urls')),
    path('quiz/', include('quiz.urls')),
    path('wallet/', include('wallet.urls')),
    path('offers/', include('systemsetting.urls')),
    # path('logs/', include('dailyofferlog.urls')),
    path('contact/', include('contactmessage.urls')),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
