from django.shortcuts import render
from django.views.generic.base import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.db.models import Q

from .models import *
from operation.models import *
from utils.mixin_utils import LoginRequiredMixin


# Create your views here.
class CourseListView(View):
    def get(self, request):
        all_courses = Course.objects.all().order_by('-add_time')
        hot_courses = Course.objects.all().order_by('-click_nums')[:3]
        # 课程搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_courses = all_courses.filter(Q(name__icontains=search_keywords)|Q(desc__icontains=search_keywords)|Q(detail__icontains=search_keywords))
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_courses = all_courses.order_by('-students')
            elif sort == 'hot':
                all_courses = all_courses.order_by('-click_nums')

        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_courses, 3, request=request)
        courses = p.page(page)

        return render(request, 'course-list.html', locals())


class CourseDetailView(View):
    def get(self, request, course_id):
        c = Course.objects.get(id=course_id)
        c.click_nums += 1
        c.save()
        # 读取收藏
        has_fav_course = False
        has_fav_org = False

        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course_id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=c.course_org.id, fav_type=2):
                has_fav_org = True

        tag = c.tag
        if tag:
            relate_courses = Course.objects.exclude(id=course_id).filter(tag=tag)[:1]
        else:
            relate_courses = []
        return render(request, 'course-detail.html', locals())


class CourseInfoView(LoginRequiredMixin, View):
    # 章节信息
    def get(self, request, course_id):
        # 课程用户关系
        c = Course.objects.get(id=course_id)
        user_courses = UserCourse.objects.filter(user=request.user, course=c)
        if not user_courses:
            c.students += 1
            c.save()
            user_course = UserCourse(user=request.user, course=c)
            user_course.save()

        lessons = c.lesson_set.all()
        # 找出学过的学生
        user_courses = UserCourse.objects.filter(course=c)
        user_ids = [uc.user.id for uc in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出学过该课的学生学过的课程id
        course_ids = [uc.course.id for uc in all_user_courses]
        # 获取学过的课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        all_resources = CourseResource.objects.filter(course=c)

        return render(request, 'course-video.html', locals())


class CourseCommentView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        c = Course.objects.get(id=course_id)
        comments = CourseComments.objects.filter(course=c)
        return render(request, 'course-comment.html', locals())


class AddCommentsView(View):

    def post(self, request):
        if not request.user.is_authenticated():
            return JsonResponse({'status': 'fail', 'msg': '用户未登录'})

        course_id = request.POST.get('course_id', 0)
        comment = request.POST.get('comments', '')
        if int(course_id) > 0 and comment:
            course_comment = CourseComments()
            course = Course.objects.get(id=course_id)
            course_comment.course = course
            course_comment.user = request.user
            course_comment.comments = comment
            course_comment.save()
            return JsonResponse({'status': 'success', 'msg': '评论成功'})
        return JsonResponse({'status': 'fail', 'msg': '评论失败'})


class VideoPlayView(View):
    def get(self, request, video_id):
        video = Video.objects.get(id=video_id)
        c = video.lesson.course

        user_courses = UserCourse.objects.filter(user=request.user, course=c)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=c)
            user_course.save()

        lessons = c.lesson_set.all()
        # 找出学过的学生
        user_courses = UserCourse.objects.filter(course=c)
        user_ids = [uc.user.id for uc in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出学过该课的学生学过的课程id
        course_ids = [uc.course.id for uc in all_user_courses]
        # 获取学过的课程
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        all_resources = CourseResource.objects.filter(course=c)

        return render(request, 'course-play.html', locals())
