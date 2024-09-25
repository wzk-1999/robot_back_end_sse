"""
ASGI config for back_end_sse project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""
import asyncio
import os

from django.core.asgi import get_asgi_application

from chatapp.redis_utils import RedisUtils
#
#
# Initialize the Redis client
# async def init():
#     await RedisUtils.init_redis()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back_end_sse.settings')

application = get_asgi_application()

# asyncio.run(init())
