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
        if not request.user.profile.isSuperAdmin():
            raise PermissionDenied
        return handler(request, *args, **kwargs)
    
    return helper

def priviliged(handler):
    """
        Checks that a user has elevated priviliges. 
    """
    def helper(request, *args, **kwargs):
        if not request.user.profile.isElevated():
            raise PermissionDenied
        
        return handler(request, *args, **kwargs)
    
    return helper