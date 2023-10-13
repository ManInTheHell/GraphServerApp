import zmq
import asyncio
import json


async def worker(task_queue, result_queue):
    while True:
        request = await task_queue.get()
        if request is None:
            # Signal to exit the worker
            break
        # Simulate some processing (you can replace this with your actual processing logic)
        result = process_request(request)
        await result_queue.put(result)


def process_request(request):
    # Simulate processing here
    return {"response": f"Processed {request}"}


async def main():
    context = zmq.Context()
    frontend = context.socket(zmq.REP)
    frontend.bind("tcp://127.0.0.1:80")

    task_queue = asyncio.Queue()
    result_queue = asyncio.Queue()

    # Start worker tasks
    workers = []
    for _ in range(3):  # You can adjust the number of worker tasks
        task = asyncio.create_task(worker(task_queue, result_queue))
        workers.append(task)

    try:
        while True:
            message = await asyncio.to_thread(frontend.recv)
            request = json.loads(message.decode("utf-8"))
            await task_queue.put(request)
            await frontend.send(b"OK")  # Send an acknowledgment to the client
    except KeyboardInterrupt:
        pass

    # Signal the workers to exit
    for _ in range(len(workers)):
        await task_queue.put(None)

    # Wait for all workers to finish
    await asyncio.gather(*workers)

    # Process and respond to results
    while not result_queue.empty():
        result = await result_queue.get()
        print(f"Response: {result}")

if __name__ == "__main__":
    asyncio.run(main())


# async def worker():
#     context = zmq.Context()
#     socket = context.socket(zmq.REP)
#     socket.bind("tcp://127.0.0.1:80")
#
#     while True:
#         message = socket.recv().decode()
#         json_data = json.loads(message)
#         print(f"Received request: {json_data}")
#         response = await handle_request(json_data)
#         socket.send(response.encode())
#
#
# async def main():
#     loop = asyncio.get_event_loop()
#     for _ in range(5):
#         loop.create_task(worker())
#     loop.run_forever()
#
# if __name__ == "__main__":
#     print('server started, waiting for requests')
#     # asyncio.run(main())
#     loop = asyncio.get_event_loop()
#     for _ in range(5):
#         loop.create_task(worker())
#     loop.run_forever()


# async def handle_request(socket):
#     while True:
#         message = socket.recv().decode()
#         json_data = json.loads(message)
#         print(f"Received request: {json_data}")
#         if json_data['command_type'] == 'os':
#             time.sleep(15)
#         else:
#             pass
#         response = "Hello, client!"
#         socket.send(response.encode())
#
#
# async def main():
#     context = zmq.Context()
#     socket = context.socket(zmq.REP)
#     socket.bind("tcp://127.0.0.1:80")
#
#     try:
#         while True:
#             task = asyncio.create_task(handle_request(socket))
#             await asyncio.gather(task)
#     except KeyboardInterrupt:
#         pass
#     finally:
#         socket.close()
#         context.term()
#
# if __name__ == "__main__":
#     print('server started, waiting for requests')
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
