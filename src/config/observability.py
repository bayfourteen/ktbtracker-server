import functools
import json
import logging
import time
from logging import Logger
from typing import Any, Callable

from django.db.models.expressions import result
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message



LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(process)s %(levelname)s %(name)s %(module)s %(funcName)s %(lineno)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": [
            "console"
        ],
        "propagate": True
    }}


def debug(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logging.getLogger("uvicorn").setLevel(logging.ERROR)
        logging.info(f"ENTRY: {func.__name__}({args}, {kwargs})")
        result = func(*args, **kwargs)
        logging.info(f"EXIT:  {func.__name__} -> ({result})")
    return result

class AsyncIteratorWrapper:
    """The following is a utility class that transforms a
        regular iterable to an asynchronous one.

        link: https://www.python.org/dev/peps/pep-0492/#example-2
    """

    def __init__(self, obj):
        self._it = iter(obj)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            value = next(self._it)
        except StopIteration:
            raise StopAsyncIteration
        return value


class RequestLoggerMiddleware(BaseHTTPMiddleware):

    def __init__(self, app: FastAPI, *, logger: Logger):
        self._logger = logger
        super().__init__(app)

    async def dispatch(self, request, call_next) -> Response:
        await self.set_body(request)

        response, response_dict = await self._log_response(call_next, request)

        request_dict = await self._log_request(request)

        logging_dict = {
            "request": request_dict,
            "response": response_dict,
        }
        self._logger.log(logging.INFO, f"{logging_dict}")

        return response

    async def set_body(self, request: Request):
        _receive = await request._receive()

        async def receive() -> Message:
            return _receive

        request._receive = receive

    async def _log_request(self, request: Request) -> dict[str, Any]:
        try:
            body = await request.body()
        except:
            body = None

        request_logging = {
            "method": request.method,
            "path": f"{request.url.path}?{request.query_params}" if request.query_params else request.url.path,
            "client": f"{request.client.host}:{request.client.port}" if request.client.port else request.client.host,
            "headers": request.headers,
            "body": body,
        }
        return request_logging

    async def _log_response(self, call_next: Callable, request: Request) -> tuple[Response, dict[str, Any]]:

        start_time = time.perf_counter()
        response = await self._execute(call_next, request)
        end_time = time.perf_counter()

        resp_body = [section async for section in response.__dict__["body_iterator"]]
        response.__setattr__("body_iterator", AsyncIteratorWrapper(resp_body))

        try:
            resp_body = json.loads(resp_body[0].decode())
        except:
            resp_body = str(resp_body)

        request_logging = {
            "status_code": response.status_code,
            "elapsed": f"{(end_time - start_time):0.4f}s",
            "body": resp_body,
        }
        return response, request_logging

    async def _execute(self, call_next: Callable, request: Request) -> Response:
        response: Response = await call_next(request)

        return response
