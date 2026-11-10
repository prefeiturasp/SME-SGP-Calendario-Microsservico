"""Views HTTP do app core."""

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.serializers import HealthSerializer


class HealthView(APIView):
    """Informa que o serviço está no ar.

    Endpoint público, sem autenticação, usado por orquestradores para
    liveness e readiness.
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Health"],
        summary="Health Check",
        description="Endpoint público usado para liveness e readiness.",
        request=None,
        auth=[],
        responses={200: HealthSerializer},
        operation_id="health_check",
    )
    def get(self, request: Request) -> Response:
        """Retorna o status do serviço.

        Args:
            request: Requisição HTTP recebida.

        Returns:
            Resposta 200 com ``{"status": "ok"}``.
        """
        serializer = HealthSerializer({"status": "ok"})
        return Response(serializer.data)
