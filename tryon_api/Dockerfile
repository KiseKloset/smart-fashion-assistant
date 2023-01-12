FROM python:3.9

# Prepare work directory
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Download pretrained model
RUN pip install gdown
RUN apt-get update && apt-get install -y unzip
RUN mkdir -p /code/app/src/tryon/u2net/ckp/u2netp
RUN gdown '1rbSTGKAE-MTxBYHd-51l2hMOQPT_7EPy&confirm=t' -O '/code/app/src/tryon/u2net/ckp/u2netp/u2netp.pth'
RUN mkdir -p /code/app/src/tryon/inference_flow_style_vton
RUN gdown "1pYrLujkd2gmQGqtnROCzSSnVwbMh9DnP&confirm=t" -O '/code/app/src/tryon/inference_flow_style_vton/ckp.zip'
RUN unzip /code/app/src/tryon/inference_flow_style_vton/ckp.zip -d /code/app/src/tryon/inference_flow_style_vton/
RUN rm /code/app/src/tryon/inference_flow_style_vton/ckp.zip

COPY . /code/app

CMD ["python", "/code/app/src/main.py"]
