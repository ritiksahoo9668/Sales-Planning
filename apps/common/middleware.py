"""Development middleware for visible HTTP request logging in the terminal."""
import logging
import sys
import time

logger = logging.getLogger('erp.requests')


class RequestLoggingMiddleware:
    """Log every HTTP request/response to the terminal (development)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started = time.perf_counter()
        path = request.get_full_path()
        tag = '[API]' if path.startswith('/api/') else '[WEB]'

        line = f'>>> {tag} {request.method} {path}'
        logger.info(line)
        print(line, flush=True)
        sys.stdout.flush()

        response = self.get_response(request)

        elapsed_ms = (time.perf_counter() - started) * 1000
        done = f'<<< {tag} {request.method} {path} {response.status_code} ({elapsed_ms:.0f}ms)'
        logger.info(done)
        print(done, flush=True)
        sys.stdout.flush()

        return response
