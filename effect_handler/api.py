"""
Defines the api for the effect handler

This is where we can

1. register effects
2. report completions
3. set what happens on errors
"""
from datetime import datetime

from maxim8_server.celery import app
from celery import task
from django.shortcuts import get_object_or_404

import effect_handler.models as models

import logging
log = logging.getLogger(__name__)


fx_registry = {}

def register_fx(kind: str, fx: callable) -> None:
    """
    registers a kind and the callable that will be called when an event arrives

    The callable will recieve the payload
    """
    fx_registry[kind] = fx


@task
def fx_callback(result_payload: any,
                fx_id: int):
    log.info("fx_id %s finished"%fx_id, 
             extra={'payload': {'result':result_payload}})
    fx = get_object_or_404(models.FXTable, pk=fx_id)
    fx.completed = datetime.now()
    fx.completion_payload = result_payload
    fx.save()
    return fx_id
