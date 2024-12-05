import asyncio
import websockets
import json
import requests
from io import BytesIO
from PIL import Image

api_key = "tsk_zsy5lsqHwjofjcylnN3Gs9idLTfN_VDVtUjKHOx9UZ0"
# task_id = "6712001c-70df-4c24-98c2-1e60198c1cdd"
tripo3d_url = "https://api.tripo3d.ai/v2/openapi/task"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

def call_tripo3d(prompt):
    data = {
        "type": "text_to_model",
        "prompt": prompt
    }

    response = requests.post(tripo3d_url, headers=headers, json=data)

    return response.json()

# async def receive_one(tid):
#     url = f"wss://api.tripo3d.ai/v2/openapi/task/watch/{tid}"
#     headers = {
#         "Authorization": f"Bearer {api_key}"
#     }
#     async with websockets.connect(url, additional_headers=headers) as websocket:
#         while True:
#             message = await websocket.recv()
#             try:
#                 data = json.loads(message)
#                 status = data['data']['status']
#                 print(status)
#                 if status not in ['running', 'queued']:
#                     break
#             except json.JSONDecodeError:
#                 print("Received non-JSON message:", message)
#                 break
#     return data


def process_and_save_image(result):
    try:
        image_url = result['data']['result']['rendered_image']['url']
        print(f"Downloading image from: {image_url}")

        response = requests.get(image_url)
        if response.status_code == 200:
            # 从二进制数据加载图片
            image = Image.open(BytesIO(response.content))

            # 获取非透明区域的边界框
            if image.mode in ('RGBA', 'LA'):
                # 获取alpha通道
                alpha = image.split()[-1]
                # 获取非透明像素的边界框
                bbox = alpha.getbbox()
                if bbox:
                    # 裁剪到主体区域
                    image = image.crop(bbox)

            # 计算新的尺寸（放大1.5倍）
            new_size = (int(image.size[0] * 2), int(image.size[1] * 2))
            # 使用LANCZOS重采样方法放大图像
            image = image.resize(new_size, Image.Resampling.LANCZOS)

            # 创建一个更大的黑色背景（为了保持居中，加上额外的边距）
            padding = 100  # 可以调整这个值来改变边距
            background_size = (image.size[0] + padding * 2, image.size[1] + padding * 2)
            background = Image.new('RGB', background_size, (0, 0, 0))

            # 将放大后的图像粘贴到背景中央
            paste_position = ((background_size[0] - image.size[0]) // 2,
                              (background_size[1] - image.size[1]) // 2)

            if image.mode in ('RGBA', 'LA'):
                background.paste(image, paste_position, mask=image.convert('RGBA').split()[-1])
            else:
                background.paste(image, paste_position)

            # 保存为PNG
            output_path = 'output.png'
            background.save(output_path, 'PNG')
            print(f"Image saved as {output_path}")
            return True
        else:
            print(f"Failed to download image: {response.status_code}")
            return False

    except Exception as e:
        print(f"Error processing image: {e}")
        return False


# 主程序
# def get_and_save_image(task_id):
#     result = asyncio.run(receive_one(task_id))
#     print(result)
#     if result:
#         return process_and_save_image(result)
#     return False


# 运行代码
# prompt = "A beautiful woman with long black hair and blue eyes, wearing a red dress"
# print(prompt)
# response = call_tripo3d(prompt)
# print(response)
# success = get_and_save_image(response['data']['task_id'])
# if success:
#     print("Image processing completed successfully")
# else:
#     print("Failed to process image")

def get_tripo3d_result_polling(tid):
    url = f"https://api.tripo3d.ai/v2/openapi/task/{tid}"
    response = requests.get(url, headers=headers)
    return response.json()

async def receive_one():
  url = f"wss://api.tripo3d.ai/v2/openapi/task/watch/all/1997-07-16T19:20:30+01:00"
  headers = {
      "Authorization": f"Bearer {api_key}"
  }
  print("start")
  async with websockets.connect(url, additional_headers=headers) as websocket:
      print("connected")
      while True:
          message = await websocket.recv()
          print(message)
          try:
              data = json.loads(message)
              status = data['data']['status']
              if status not in ['running', 'queued']:
                  break
          except json.JSONDecodeError:
              print("Received non-JSON message:", message)
              break
  return data

# result = asyncio.run(receive_one())
result = get_tripo3d_result_polling("75a9aa77-3222-4b96-9a90-f1208c623c05")
print(result)
