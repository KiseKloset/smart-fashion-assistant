FROM continuumio/miniconda3

# Prepare work directory
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt

# Install fastapi
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Install dependencies
RUN conda install -y -c pytorch pytorch=1.11.0 torchvision=0.12.0
RUN conda install -y -c anaconda pandas=1.4.2
RUN pip install git+https://github.com/openai/CLIP.git

# Download dataset 
RUN pip install gdown
RUN mkdir -p /code/app/src/dataset
RUN gdown "1DwRzT0kddWBnydYe80hPJHEamnNQddNE&confirm=t" -O /code/app/src/dataset/fashion-iq.zip
RUN apt-get update && apt-get install -y unzip
RUN unzip /code/app/src/dataset/fashion-iq.zip -d /code/app/src/dataset
RUN rm /code/app/src/dataset/fashion-iq.zip
RUN mv /code/app/src/dataset/fashion-iq /code/app/src/dataset/fashioniq

# Download preprocess dataset
RUN gdown "1C8nYeSn6o8rbd17sTTowae4o8AdTk-iv&confirm=t" -O /code/app/src/dataset/fashioniq/FashionIQ_index_features.pt
RUN gdown "1M2-bMgI9OWqhHpY70A9fEIAK8XtvLN1f&confirm=t" -O /code/app/src/dataset/fashioniq/FashionIQ_index_names.pkl

# Download pretrained model
RUN mkdir -p /code/app/src/tgir/clip4cir
RUN gdown "1cQS8vFhNBpZOhyDNe15STz00wMvYEQEb&confirm=t" -O /code/app/src/tgir/clip4cir/fiq_clip_RN50x4_fullft.pt
RUN gdown "1MxFkozS7RJy5VOoDBC2gJkoYqB4jD5tB&confirm=t" -O /code/app/src/tgir/clip4cir/fiq_comb_RN50x4_fullft.pt
RUN wget "https://openaipublic.azureedge.net/clip/models/7e526bd135e493cef0776de27d5f42653e6b4c8bf9e0f653bb11773263205fdd/RN50x4.pt" -P /code/app/src/tgir/clip4cir

COPY . /code/app

CMD ["python", "/code/app/src/main.py"]