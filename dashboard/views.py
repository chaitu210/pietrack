from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from piebase.models import Project, User, Role


@login_required
def profile_activity(request):
    user_obj = request.user
    project_list = user_obj.projects.all()
    project_count = len(project_list)
    member_dict = {}
    for project_iter in user_obj.projects.all():
        for member_iter in project_iter.members.all():
            roles_list = member_iter.user_roles.all()
            if roles_list:
                member_dict[member_iter.email] = list(set(role.name for role in roles_list))
    member_count = len(member_dict)
    return render(request, 'profile_activity.html',
                  {'project_list': project_list, 'member_dict': member_dict, 'project_count': project_count,
                   'member_count': member_count})
