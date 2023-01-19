import torch
import torch.nn as nn

from .models.afwm import AFWM
from .models.networks import ResUnetGenerator


def load_checkpoint(model, checkpoint_path, device=torch.device('cpu')):
    checkpoint = torch.load(checkpoint_path, map_location=device)
    checkpoint_new = model.state_dict()
    for param in checkpoint_new:
        checkpoint_new[param] = checkpoint[param]

    model.load_state_dict(checkpoint_new)


def load_model(checkpoints, device=torch.device('cpu')):
    warp_model = AFWM(input_nc=3)
    warp_model.eval()
    warp_model.to(device)
    load_checkpoint(warp_model, checkpoints['warp'], device)
    gen_model = ResUnetGenerator(7, 4, 5, ngf=64, norm_layer=nn.BatchNorm2d)
    gen_model.eval()
    gen_model.to(device)
    load_checkpoint(gen_model, checkpoints['gen'], device)

    return {'warp': warp_model, 'gen': gen_model}


# from PIL import Image
# from torchvision import utils
# from torchvision.transforms import ToTensor
# if __name__=='__main__':
#     models = load_model(
#             checkpoints={'warp': 'inference_flow_style_vton/ckp/aug/PFAFN_warp_epoch_101.pth',
#                 'gen': 'inference_flow_style_vton/ckp/aug/PFAFN_gen_epoch_101.pth'},    
#         )


#     real_image = ToTensor()(Image.open('data/test_img/000129_0.jpg'))
#     clothes = ToTensor()(Image.open('data/test_clothes/007741_1.jpg'))
#     edge = ToTensor()(Image.open('data/test_edge/007741_1.jpg'))
#     input_images = {
#         'image': real_image[None, :],
#         'cloth': clothes[None, :],
#         'edge': edge[None, :],
#     }

#     tryon = infer(models, input_images)[0, :]
    
#     utils.save_image(tryon, 'tryon.jpg')