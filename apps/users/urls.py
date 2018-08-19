from django.conf.urls import url
from .views import *

urlpatterns = [
    # 用户信息
    url(r'^info/$', UserinfoView.as_view(), name='user_info'),
    # 用户头像上传
    url(r'^image/upload/$',UploadImageView.as_view(),name='image_upload'),
    url(r'^update/pwd/$', UpdatePwdView.as_view(), name='update_pwd'),
    #发送邮箱验证码
    url(r'^sendemail_code/$', SendEmailView.as_view(), name='sendemail_code'),
    # 修改邮箱
    url(r'^update_email/$', UpdateEmailView.as_view(), name='update_email'),

    url(r'^mycourse/$', MyCourseView.as_view(), name='mycourse'),
    url(r'^myfav/org/$', MyFavOrgView.as_view(), name='myfav_org'),
    url(r'^myfav/teacher/$', MyFavTeacherView.as_view(), name='myfav_teacher'),
    url(r'^myfav/course/$', MyFavCourseView.as_view(), name='myfav_course'),
    url(r'^mymessage/$', MyMessageView.as_view(), name='mymessage'),
]
