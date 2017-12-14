from rest_framework import views
from channels import Group
from rest_framework.response import Response

# Create your views here.


class ARIRestViewSet(views.APIView):

    def get(self, request, ):
        status = request.query_params.get('status')
        Group("console").send({
            "text": status if not status in ['Ring', 'Up'] else '{}&{}'.format(status, request.query_params.get('number')),
        })
        return Response()
