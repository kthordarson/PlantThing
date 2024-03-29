from django.urls import path
from Vokvarinn import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.plants_list_all_view, name='plants_list_all_view'),
    path('all_view/', views.all_view, name='all_view'),
    path('plant/', views.plant_detail_view, name='plant_detail'),
    path('plant/all/', views.plants_list_all_view, name='plants_list_all_view'),
    path('plant/<int:pk>', views.plant_detail_view, name='plant_detail'),
    path('plant/<int:pk>/water', views.plant_water_view, name='plant_water_view'),
    path('plant/do_water/<int:pk>/', views.plant_do_water, name='plant_do_water'),
    path('plant/<int:pk>/edit/', views.plant_edit_view, name='plant_edit_view'),
    path('plant/create', views.plant_create_view, name='plant_create_view'),
    path('plant/viewlog', views.plant_view_waterlog, name='plant_view_waterlog'),
    path('edit_schedule', views.edit_schedule, name='edit_schedule'),
    path('datatable', views.DatatableView.as_view(), name='ZeroConfigurationDatatableView'),
]

if settings.DEBUG:  # new
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
