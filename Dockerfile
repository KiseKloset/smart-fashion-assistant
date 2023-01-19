FROM python:3.9

# Prepare work directory
WORKDIR /code
COPY ./src/requirements.txt /code/requirements.txt

# Install dependencies
RUN apt-get update && apt-get install -y unzip
RUN pip install gdown
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Download data
RUN mkdir -p /code/app/api/retrieval
RUN gdown "1h_WfmgaLyRNI26hsQk7I0RRFnnpcQrZr&confirm=t" -O /code/app/api/retrieval/dataset.zip
RUN unzip /code/app/api/retrieval/dataset.zip -d /code/app/api/retrieval
RUN rm /code/app/api/retrieval/dataset.zip

RUN mkdir -p /code/app/api/retrieval
RUN gdown "1JoLjDV7pf9DinRJL4h1b9MJ-nWII6D_S&confirm=t" -O /code/app/api/retrieval/pretrained.zip
RUN unzip /code/app/api/retrieval/pretrained.zip -d /code/app/api/retrieval
RUN rm /code/app/api/retrieval/pretrained.zip

RUN mkdir -p /code/app/static
RUN gdown "1BsXmArHxCFHez3f0mFhNRmcg-THCxCj7&confirm=t" -O /code/app/static/images.zip
RUN unzip /code/app/static/images.zip -d /code/app/static
RUN rm /code/app/static/images.zip

RUN mkdir -p /code/app/api/tryon/u2net/ckp/u2netp
RUN gdown '1rbSTGKAE-MTxBYHd-51l2hMOQPT_7EPy&confirm=t' -O '/code/app/api/tryon/u2net/ckp/u2netp/u2netp.pth'

RUN mkdir -p /code/app/api/tryon/inference_flow_style_vton
RUN gdown "1pYrLujkd2gmQGqtnROCzSSnVwbMh9DnP&confirm=t" -O '/code/app/api/tryon/inference_flow_style_vton/ckp.zip'
RUN unzip /code/app/api/tryon/inference_flow_style_vton/ckp.zip -d /code/app/api/tryon/inference_flow_style_vton/
RUN rm /code/app/api/tryon/inference_flow_style_vton/ckp.zip

COPY ./src /code/app
RUN mv /code/app/.env.sample /code/app/.env

CMD ["python", "/code/app/main.py"]


