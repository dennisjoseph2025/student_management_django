from datetime import datetime

class DateMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        request.current_date = datetime.now().strftime('%d/%m/%Y')
        response = self.get_response(request)
        return response