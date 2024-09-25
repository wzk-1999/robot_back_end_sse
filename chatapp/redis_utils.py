# chatapp/redis_utils.py
import json
import redis.asyncio as aioredis
import time

class RedisUtils:
    redis_client = None

    @staticmethod
    async def get_redis_client():
        # print("run")
        # if RedisUtils.redis_client is None or RedisUtils.redis_client.connection_pool._available_connections == []:
        #     print("Redis client connected successfully")
        RedisUtils.redis_client = await aioredis.from_url('redis://localhost:6379/0')
        return RedisUtils.redis_client

    @staticmethod
    async def store_message(user_id, message, message_type):
        redis_client = await RedisUtils.get_redis_client()

        timestamp = int(time.time())
        key = f"{user_id}:messages"
        message_data = json.dumps({'text': message, 'type': message_type})
        await redis_client.zadd(key, {message_data: timestamp})
        await redis_client.expire(key, 259200)

    @staticmethod
    async def get_messages(user_id, count=10):
        redis_client = await RedisUtils.get_redis_client()

        key = f"{user_id}:messages"
        messages = await redis_client.zrange(key, -count, -1)

        if messages is None:
            return []

        return [json.loads(message.decode('utf-8')) for message in messages]

    @staticmethod
    async def delete_temp_user_key(user_id):
        redis_client = await RedisUtils.get_redis_client()

        key = f"{user_id}:messages"
        await redis_client.delete(key)