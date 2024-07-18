from django.urls import path
from .views import (
    base,
    delete_data,
    upload_data,
    view_data,
    retrieve_data_by_id,
    analysis,
    change_password,
    login2,
    account_details,
    about,
    dashboard,
    userLogout,
    reports,
    upload_credit_data,
    
)

urlpatterns = [
    path('', base, name='base'),
    path('delete_data/<int:id>/', delete_data, name='delete_data'),
    path('upload_data/', upload_data, name='upload_data'),
    path('view_data/<int:id>/', view_data, name='view_data'),
    path('retrieve_data_by_id/<int:id>/', retrieve_data_by_id, name='retrieve_data_by_id'),
    path('analysis/<int:id>/', analysis, name='analysis'),
    path('change_password/', change_password, name='change_password'),
    path('login2/', login2, name='login2'),
    path('account_details/', account_details, name='account_details'),
    path('about/', about, name='about'),
    path('dashboard/', dashboard, name='dashboard'),
    path('userLogout/', userLogout, name='userLogout'),
    path('reports/', reports, name='reports'),
    path('upload_credit_data/', upload_credit_data, name='upload_credit_data'),

]
