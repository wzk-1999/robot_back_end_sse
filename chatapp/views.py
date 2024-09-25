# chatapp/views.py
import json
import os

import aiohttp
from asgiref.sync import sync_to_async
from django.http import JsonResponse, StreamingHttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .redis_utils import RedisUtils
import uuid
async def get_recent_messages(request):
    session_id = request.GET.get('session_id')
    # print(session_id)
    if not session_id:
        # Generate a new session_id if it doesn't exist
        session_id = str(uuid.uuid4())
        recent_messages = []
    else:
        # Fetch the recent 10 messages from Redis
        recent_messages = await RedisUtils.get_messages(session_id)

    return JsonResponse({
        'session_id': session_id,
        'messages': recent_messages
    })

@csrf_exempt
# @method_decorator(csrf_exempt, name='dispatch')
async def handle_chat_sse(request):

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    question = body.get('question')
    session_id = body.get('session_id')

    if not session_id:
        return JsonResponse({'error': 'Session ID is required'}, status=400)

    # Store the user's question in Redis asynchronously
    await RedisUtils.store_message(session_id, question, 'user')

    # Here, we return a success response indicating the message was stored.
    return JsonResponse({'message': 'Question submitted successfully'}, status=200)
    # async def ai_response_stream():
    #     api_url = f"https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    #     headers = {
    #         "Authorization": f"Bearer {os.getenv('API_KEY')}",
    #         "Content-Type": "application/json"
    #     }
    #     data = {
    #         "model": "ep-20240922110810-8njsc",
    #         "messages": [{"role": "user", "content": question}],
    #         "stream": True
    #     }
    #
    #     try:
    #         async with aiohttp.ClientSession() as session:
    #             async with session.post(api_url, headers=headers, json=data) as response:
    #                 if response.status == 200:
    #                     full_answer = ""
    #                     async for chunk in response.content.iter_any():
    #                         decoded_chunk = chunk.decode('utf-8').strip()
    #                         if decoded_chunk:
    #                             for line in decoded_chunk.splitlines():
    #                                 if line.startswith('data:'):
    #                                     line = line[len('data:'):].strip()
    #                                 try:
    #                                     line_data = json.loads(line)
    #                                     if 'choices' in line_data and line_data['choices']:
    #                                         chunk_message = line_data['choices'][0]['delta'].get('content', '')
    #                                         full_answer += chunk_message
    #                                         # Yield chunk message to the client
    #                                         yield f"data: {json.dumps({'message': chunk_message})}\n\n"
    #
    #                                         # Check if streaming is finished
    #                                         if line_data['choices'][0].get('finish_reason') == 'stop':
    #                                             break
    #                                 except json.JSONDecodeError:
    #                                     continue
    #                     # Save the full answer in Redis
    #                     await RedisUtils.store_message(session_id, full_answer, 'bot')
    #     except aiohttp.ClientError as e:
    #         yield f"data: {json.dumps({'error': str(e)})}\n\n"
    #
    # # Return a StreamingHttpResponse with an async generator
    # return StreamingHttpResponse(ai_response_stream(), content_type='text/event-stream')

async def handle_chat_stream_sse(request):

    # Get the session ID from the query parameters
    session_id = request.GET.get('session_id')
    if not session_id:
        return JsonResponse({'error': 'Session ID is required'}, status=400)

    async def ai_response_stream():
        api_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('API_KEY')}",
            "Content-Type": "application/json"
        }

        # We need to fetch the last question or keep it as a placeholder.
        last_question = await RedisUtils.get_last_question(session_id)  # Implement this method as needed

        data = {
            "model": "ep-20240922110810-8njsc",
            "messages": [{"role": "user", "content": last_question}],
            "stream": True
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, json=data) as response:
                    if response.status == 200:
                        async for chunk in response.content.iter_any():
                            decoded_chunk = chunk.decode('utf-8').strip()
                            if decoded_chunk:
                                for line in decoded_chunk.splitlines():
                                    if line.startswith('data:'):
                                        line = line[len('data:'):].strip()
                                    try:
                                        line_data = json.loads(line)
                                        if 'choices' in line_data and line_data['choices']:
                                            chunk_message = line_data['choices'][0]['delta'].get('content', '')
                                            # Yield chunk message to the client
                                            yield f"data: {json.dumps({'message': chunk_message})}\n\n"

                                            # Check if streaming is finished
                                            if line_data['choices'][0].get('finish_reason') == 'stop':
                                                break
                                    except json.JSONDecodeError:
                                        continue
        except aiohttp.ClientError as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    # Return a StreamingHttpResponse with an async generator
    return StreamingHttpResponse(ai_response_stream(), content_type='text/event-stream')