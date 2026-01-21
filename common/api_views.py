from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from common.models import Notification

@method_decorator(login_required, name='dispatch')
class UnreadNotificationCountView(View):
    def get(self, request):
        user = request.user.user
        count = Notification.objects.filter(user=user, is_read=False).count()
        return JsonResponse({'unread_count': count})
