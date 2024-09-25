# middleware.py
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

class OptionsRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == 'OPTIONS':
            # 可以在这里添加CORS头部等
            response = JsonResponse({'message': 'OPTIONS request allowed'}, status=200)
            response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = '*'
            return response
        return None  # 如果没有处理，继续处理请求