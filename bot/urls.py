from django.urls import path
from . import views


urlpatterns = [
        path('', views.home, name='home'),
        path('login/', views.loginUser, name='login'),
        path('logout/', views.logoutUser, name='logout'),
        path('license/', views.license, name='license'),

        #Accounts Paths

        path('ac/', views.nl_accounts, name='nairaland-accounts'),
        path('ac/add/', views.NairalandAccountCreate.as_view(), name='add_nairaland-account'),
        path('ac/<int:pk>/', views.NairalandAccountDetail.as_view(), name='nairaland-account-detail'),
        path('ac/<int:pk>/edit/', views.NairalandAccountUpdate.as_view(), name='nairaland-account-update'),
        path('ac/<int:pk>/delete', views.NairalandAccountDelete.as_view(), name='nairaland-account-delete'),

        #Jobs Paths

        path('jobs/', views.jobs, name='jobs'),
        path('jobs/bj/add/', views.BoardJobCreate.as_view(), name='add_boardreplyjob'),
        path('jobs/bj/<int:pk>/', views.BoardJobDetail.as_view(), name='boardreplyjob-detail'),
        path('jobs/bj/<int:pk>/edit/', views.BoardJobUpdate.as_view(), name='boardreplyjob-update'),
        path('jobs/bj/<int:pk>/delete', views.BoardJobDelete.as_view(), name='boardreplyjob-delete'),
        path('jobs/td/add/', views.ThreadJobCreate.as_view(), name='add_threadreplyjob'),
        path('jobs/td/<int:pk>/', views.ThreadJobDetail.as_view(), name='threadreplyjob-detail'),
        path('jobs/td/<int:pk>/edit/', views.ThreadJobUpdate.as_view(), name='threadreplyjob-update'),
        path('jobs/td/<int:pk>/delete', views.ThreadJobDelete.as_view(), name='threadreplyjob-delete'),
        path('jobs/fp/add/', views.FrontPageMonitorJobCreate.as_view(), name='add_frontpagemonitorjob'),
        path('jobs/fp/<int:pk>/', views.FrontPageMonitorJobDetail.as_view(), name='frontpagemonitorjob-detail'),
        path('jobs/fp/<int:pk>/edit/', views.FrontPageMonitorJobUpdate.as_view(), name='frontpagemonitorjob-update'),
        path('jobs/fp/<int:pk>/delete', views.FrontPageMonitorJobDelete.as_view(), name='frontpagemonitorjob-delete'), 


        #Activate Jobs paths
        

        path('jobs/bj/<int:pk>/activate/', views.activateBjJob, name='activate-bj-job'),
        path('jobs/td/<int:pk>/activate/', views.activateTdJob, name='activate-td-job'),
        path('jobs/fp/<int:pk>/activate/', views.activateFpJob, name='activate-fp-job'),
         
               
        #Deactivate Jobs

        path('jobs/td/<int:pk>/deactivate/', views.deactivateTdJob, name='deactivate-td-job'),
        path('jobs/bj/<int:pk>/deactivate/', views.deactivateBjJob, name='deactivate-bj-job'),
        path('jobs/fp/<int:pk>/deactivate/', views.deactivateFpJob, name='deactivate-fp-job'),
         
          

      
        path('account/', views.account, name='account'),
        path('change_password/', views.changePassword, name='change pwd'),
        ]


