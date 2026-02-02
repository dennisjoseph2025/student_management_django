from django.shortcuts import redirect
from django.contrib import messages


class RedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):

        if "admin" in request.path:
            return None
        # Skip for login, logout, registration, and landing pages
        public_views = ["login", "logout_view", "registration", "landing"]
        if view_func.__name__ in public_views:
            return None

        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this page.")
            return redirect("login")
        
        if hasattr(request.user, "role"):
            if request.user.role == "STUDENT" and "management" in request.path:
                messages.error(request, "Access denied. Principal access only.")
                return redirect("student_dashboard")

            elif request.user.role == "PRINCIPAL" and "student" in request.path:
                messages.error(request, "Access denied. Student access only.")
                return redirect("principal_dashboard")

        return None
