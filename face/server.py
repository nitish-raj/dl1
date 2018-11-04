from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Router, Mount
from starlette.staticfiles import StaticFiles
from binascii import a2b_base64
from io import BytesIO
import requests
import os
import uvicorn
from fastai import *
from fastai.vision import *

classes = ['duck', 'fish']
data = ImageDataBunch.single_from_classes('', classes, tfms=get_transforms(), size=224).normalize(imagenet_stats)
learner = create_cnn(data, models.resnet34)
learner.load('duck-post-clean-stage-2')

app = Router(routes=[
    Mount('/static', app=StaticFiles(directory='static')),
])
@app.route('/')
async def homepage(request):
    return JSONResponse({'hello': 'world'})


@app.route('/face', methods=["GET","POST"])
async def face(request):
    body = await request.form()
    binary_data = a2b_base64(body['imgBase64'])
    # fd = open('image.png', 'wb')
    # fd.write(binary_data)
    # fd.close()
    img = open_image(BytesIO(binary_data))
    _,_,losses = learner.predict(img)
    analysis = {
        "predictions": dict(sorted(
            zip(learner.data.classes, map(float, losses)),
            key=lambda p: p[1],
            reverse=True
        ))}
    print("analysis!!", analysis)
    return JSONResponse(analysis)
    # params = {
    #     'returnFaceId': 'true',
    #     'returnFaceLandmarks': 'false',
    #     'returnFaceAttributes': 'emotion'
    # }
    # headers  = {'Ocp-Apim-Subscription-Key': os.environ['MSKEY'], "Content-Type": "application/octet-stream" }
    # response = requests.post("https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect", params=params, headers=headers, data=binary_data)
    # response.raise_for_status()
    # analysis = response.json()
    
    # return JSONResponse(analysis)



if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
