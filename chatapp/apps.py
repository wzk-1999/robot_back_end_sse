# from django.apps import AppConfig


# class ChatappConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'chatapp'
#
#     def ready(self):
#         from .redis_utils import RedisUtils
#         import asyncio
#
#         # Initialize Redis when the app is ready
#         asyncio.run(RedisUtils.init_redis())