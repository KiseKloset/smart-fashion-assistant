import sys
import clip
import torch
import pickle
import numpy as np

from typing import Tuple
from pathlib import Path
from torch import nn
from torch.utils.data import DataLoader
from tqdm import tqdm


FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH


from clip4cir.utils import collate_fn
from clip4cir.combiner import Combiner
from clip4cir.data_utils import *


clip_model: nn.Module = None
combiner: Combiner = None

dataset_name = "FashionIQ"
base_path = str(FILE.parent.parent)
data_path = f"{base_path}/dataset/fashioniq"
pretrained_path = f"{base_path}/tgir/clip4cir"
clip_pretrained_path = f"{pretrained_path}/fiq_clip_RN50x4_fullft.pt"
comb_pretrained_path = f"{pretrained_path}/fiq_comb_RN50x4_fullft.pt"


def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def get_data_type():
    if torch.cuda.is_available():
        return torch.float16
    return torch.float32


def load_models() -> Tuple[nn.Module, Combiner]:
    device = get_device()

    clip_model, _ = clip.load(f"{pretrained_path}/RN50x4.pt", device=device, jit=False)
    clip_state_dict = torch.load(clip_pretrained_path, map_location=device)
    clip_model.load_state_dict(clip_state_dict["CLIP"])

    # To load a trained combiner network
    feature_dim = clip_model.visual.output_dim
    combiner = Combiner(feature_dim, 2560, 5120)
    combiner.to(device)
    combiner_state_dict = torch.load(comb_pretrained_path, map_location=device)
    combiner.load_state_dict(combiner_state_dict["Combiner"])
    combiner.eval()

    return clip_model, combiner


def extract_and_save_index_features(
    dataset: FashionIQDataset, clip_model: nn.Module, feature_dim: int, file_name: str
):
    device = get_device()

    dataloader = DataLoader(
        dataset=dataset,
        batch_size=32,
        num_workers=8,
        pin_memory=True,
        collate_fn=collate_fn,
    )
    index_features = torch.empty((0, feature_dim), dtype=torch.float16).to(device)
    index_names = []

    # iterate over the dataset object
    for names, images in tqdm(dataloader):
        images = images.to(device)

        # extract and concatenate features and names
        with torch.no_grad():
            batch_features = clip_model.encode_image(images)
            index_features = torch.vstack((index_features, batch_features))
            index_names.extend(names)

    # save the extracted features
    out_path = Path(data_path).absolute()
    out_path.mkdir(exist_ok=True, parents=True)
    torch.save(index_features, out_path / f"{file_name}_index_features.pt")
    with open(out_path / f"{file_name}_index_names.pkl", "wb+") as f:
        pickle.dump(index_names, f)


def preprocess_dataset(clip_model: nn.Module):
    input_dim = clip_model.visual.input_resolution
    feature_dim = clip_model.visual.output_dim

    preprocess = targetpad_transform(1.25, input_dim)
    test_dataset = FashionIQDataset(data_path, "test", preprocess)
    extract_and_save_index_features(test_dataset, clip_model, feature_dim, dataset_name)


def load_preprocess_dataset() -> Tuple[list, torch.Tensor]:
    path = Path(data_path).absolute()
    device = get_device()
    data_type = get_data_type()

    dataset_index_features = (
        torch.load(path / f"{dataset_name}_index_features.pt", map_location=device)
        .type(data_type)
        .cpu()
    )

    with open(path / f"{dataset_name}_index_names.pkl", "rb") as f:
        dataset_index_names = pickle.load(f)
    
    return dataset_index_names, dataset_index_features


def load_dataset_metadata() -> dict:
    dataset_metadata = {}

    dress_types = ["dress", "shirt", "toptee"]
    for dress_type in dress_types:
        splits = ["train", "val", "test"]
        for split in splits:
            with open(f"{data_path}/image_splits/split.{dress_type}.{split}.json") as f:
                images = json.load(f)
                for image in images:
                    dataset_metadata[image] = {
                        "category": dress_type,
                        "url": f"/static/{image}.png",
                    }

    return dataset_metadata


def compute_fashionIQ_results(
    image: bytes, 
    caption: str, 
    n_retrieved: int, 
    clip_model: nn.Module,
    combiner: Combiner,
    dataset_index_names: list, 
    dataset_index_features: torch.Tensor
):
    device = get_device()
    data_type = get_data_type()

    index_names = dataset_index_names
    index_features = dataset_index_features.to(device)

    pil_image = PIL.Image.open(image).convert("RGB")
    input_dim = clip_model.visual.input_resolution
    image = targetpad_transform(1.25, input_dim)(pil_image).to(device)
    reference_features = clip_model.encode_image(image.unsqueeze(0))

    text_inputs = clip.tokenize(caption, truncate=True).to(device)

    with torch.no_grad():
        text_features = clip_model.encode_text(text_inputs)
        predicted_features = combiner.combine_features(
            reference_features.float(), text_features.float()
        ).to(data_type).squeeze(0)

    index_features = torch.nn.functional.normalize(index_features)
    cos_similarity = index_features @ predicted_features.T
    sorted_indices = torch.topk(cos_similarity, n_retrieved, largest=True).indices.cpu()
    sorted_index_names = np.array(index_names)[sorted_indices].flatten()

    return sorted_index_names