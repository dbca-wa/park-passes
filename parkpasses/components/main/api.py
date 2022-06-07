import traceback
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.db import transaction
from wsgiref.util import FileWrapper
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.decorators import (
    action as detail_route,
    renderer_classes,
    parser_classes,
)
from rest_framework.decorators import action as list_route
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAdminUser,
    BasePermission,
)
from rest_framework.pagination import PageNumberPagination
from django.urls import reverse
from parkpasses.components.main.models import (
    ApplicationType,
    RequiredDocument,
    Question,
    GlobalSettings,
    MapLayer,
)
from parkpasses.components.main.serializers import (
    ApplicationTypeSerializer,
    RequiredDocumentSerializer,
    QuestionSerializer,
    GlobalSettingsSerializer,
    OracleSerializer,
    BookingSettlementReportSerializer,
    MapLayerSerializer,
)
from django.core.exceptions import ValidationError
from django.db.models import Q
from parkpasses.components.proposals.models import Proposal
from parkpasses.components.proposals.serializers import ProposalSerializer
from parkpasses.components.bookings.utils import oracle_integration
from parkpasses.helpers import is_internal, is_customer

# from parkpasses.components.bookings import reports
from ledger_api_client.utils import (
    create_basket_session,
    create_checkout_session,
    place_order_submission,
)
from collections import namedtuple
import json
from decimal import Decimal

import logging

logger = logging.getLogger("payment_checkout")


class GlobalSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GlobalSettings.objects.all().order_by("id")
    serializer_class = GlobalSettingsSerializer


class RequiredDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RequiredDocument.objects.all()
    serializer_class = RequiredDocumentSerializer

    # def get_queryset(self):
    #     categories=ActivityCategory.objects.filter(activity_type='marine')
    #     return categories


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class MapLayerViewSet(viewsets.ModelViewSet):
    queryset = MapLayer.objects.none()
    serializer_class = MapLayerSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return MapLayer.objects.filter(option_for_internal=True)
        elif is_customer(self.request):
            return MapLayer.objects.filter(option_for_external=True)
        return MapLayer.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# class PaymentViewSet(viewsets.ModelViewSet):
#    #queryset = Proposal.objects.all()
#    queryset = Proposal.objects.none()
#    #serializer_class = ProposalSerializer
#    serializer_class = ProposalSerializer
#    lookup_field = 'id'
#
#    def create(self, request, *args, **kwargs):
#        response = super(PaymentViewSet, self).create(request, *args, **kwargs)
#        # here may be placed additional operations for
#        # extracting id of the object and using reverse()
#        fallback_url = request.build_absolute_uri('/')
#        return HttpResponseRedirect(redirect_to=fallback_url + '/success/')
#
#
# class BookingSettlementReportView(views.APIView):
#    renderer_classes = (JSONRenderer,)
#
#    def get(self,request,format=None):
#        try:
#            http_status = status.HTTP_200_OK
#            #parse and validate data
#            report = None
#            data = {
#                "date":request.GET.get('date'),
#            }
#            serializer = BookingSettlementReportSerializer(data=data)
#            serializer.is_valid(raise_exception=True)
#            filename = 'Booking Settlement Report-{}'.format(str(serializer.validated_data['date']))
#            # Generate Report
#            report = reports.booking_bpoint_settlement_report(serializer.validated_data['date'])
#            if report:
#                response = HttpResponse(FileWrapper(report), content_type='text/csv')
#                response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
#                return response
#            else:
#                raise serializers.ValidationError('No report was generated.')
#        except serializers.ValidationError:
#            raise
#        except Exception as e:
#            traceback.print_exc()
#
#
# class OracleJob(views.APIView):
#    renderer_classes = [JSONRenderer,]
#    def get(self, request, format=None):
#        try:
#            data = {
#                "date":request.GET.get("date"),
#                "override": request.GET.get("override")
#            }
#            serializer = OracleSerializer(data=data)
#            serializer.is_valid(raise_exception=True)
#            oracle_integration(serializer.validated_data['date'].strftime('%Y-%m-%d'),serializer.validated_data['override'])
#            data = {'successful':True}
#            return Response(data)
#        except serializers.ValidationError:
#            print(traceback.print_exc())
#            raise
#        except ValidationError as e:
#            raise serializers.ValidationError(repr(e.error_dict)) if hasattr(e, 'error_dict') else serializers.ValidationError(e)
#        except Exception as e:
#            print(traceback.print_exc())
#            raise serializers.ValidationError(str(e[0]))
