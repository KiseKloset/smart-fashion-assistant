# How to use

## First time
1. `conda create -n smart_fashion python=3.8`
2. `conda activate smart_fashion`
3. `pip install -r ./main_entry/requirements.txt`
4. Setup `env`
    ```
    cp ./main_entry/.env.sample ./main_entry/.env
    cp ./tryon_api/.env.sample ./tryon_api/.env
    cp ./retrieval_api/.env.sample ./retrieval_api/.env
    ```
5. `bash ./main.sh`

## Afterward
1. `conda activate smart_fashion`
2. `./main.sh`