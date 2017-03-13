from django.core.exceptions import PermissionDenied


def memoize(f):
    memo = {}

    def helper(*x):
        key = str(x)
        if key not in memo:
            memo[key] = f(*x)
        return memo[key]

    return helper


def superadmin(handler):
    """
        Checks if a user is a super admin.
    """

    def helper(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return handler(request, *args, **kwargs)

    return helper


def is_elevated(user):
    if not user.is_superuser:
        if not user.admin_set.count() > 0:
            return False
    return True


def priviliged(handler):
    """
        Checks that a user has elevated priviliges.
    """

    def helper(request, *args, **kwargs):
        if not is_elevated(request.user):
            raise PermissionDenied

        return handler(request, *args, **kwargs)

    return helper


def get_user_details(user):
    import json

    try:
        data = user.socialaccount_set.get(provider="dreamjub").extra_data
        return data
    except:
        return {}


def is_admin_for(user, system):
    """
        Checks if this user can administer a certain voting system.
    """
    return system in get_administrated_systems(user)


def get_administrated_systems(user):
    from settings.models import VotingSystem, Admin
    """
        Returns all voting systems this user can administer.
    """
    # if we are a superadmin we can manage all systems
    if user.is_superuser:
        return VotingSystem.objects.all()

    # else return only the systems we are an admin for.
    else:
        return list(map(lambda x: x.system, Admin.objects.filter(
            user=user)))


def get_all_systems(user):
    from settings.models import VotingSystem
    """
        Gets the editable filters for this user.
    """

    # get all the voting systems for this user
    admin_systems = get_administrated_systems(user)

    # and all the other ones also
    other_systems = list(filter(lambda a: not a in admin_systems, VotingSystem.objects.all()))

    return admin_systems, other_systems
