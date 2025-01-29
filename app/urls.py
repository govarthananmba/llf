from django.urls import path
from.import views

urlpatterns = [

    path('',views.home, name="home"),
    path('front/',views.front, name="front"),
    path('frontpage/', views.frontpage, name= "frontpage"), 
    path('get_suggestions/', views.get_suggestions, name='get_suggestions'),
    path('logout/',views.logout_user, name="logout"),
    path('register/',views.register_user, name="register"),
    path('record/<int:pk>', views.student_record, name='record'),
    path('delete_record/<int:pk>', views.delete_record, name='delete_record'),
    path('add_record/', views.add_record, name='add_record'),
    path('update_record/<int:pk>', views.update_record, name='update_record'),
    path('download/', views.export_csv, name='export_csv'),
    path('get_states/', views.get_states, name='get_states'),
    path('get_cities/', views.get_cities, name='get_cities'),
    path('students/', views.student_list, name='student-list'),
    path('form/<int:standard>/<int:student_id>/', views.open_form, name='open_form'),
    path('submit_form/<int:student_id>/', views.submit_form, name='submit_form'),
    path('dashboardd/', views.dashboardd, name='dashboardd'),
   

    
    
]