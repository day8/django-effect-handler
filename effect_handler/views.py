from rest_framework.decorators import api_view
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from effect_handler.api import fx_registry, fx_callback

import logging
log = logging.getLogger(__name__)

@api_view(['POST'])
def new_effect_handler(request, format=None):
    effect_data = request.data['event']['data']['new']
    fx_id = effect_data['id']
    log.info("New FX Arrives ", extra={'payload': {'effect_data': effect_data}})
    kind = effect_data['kind']
    payload = effect_data['payload']
    if kind in fx_registry:
        fx_registry[kind](payload, callback=fx_callback.s(fx_id=fx_id))
    else:
        return Response("Unknown kind: %s id: %s"%(kind, fx_id), status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return Response("Effect recieved kind: %s id: %s"%(kind, fx_id), status=status.HTTP_202_ACCEPTED)
