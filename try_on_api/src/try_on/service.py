from PIL import Image

import numpy as np
import torch
from torch.autograd import Variable
import torch.nn.functional as F
import torchvision.transforms as transforms

import u2net.utils as u2nu
import inference_flow_style_vton.utils as fsvu


u2net_model = None
fsvton_model = {
                'warp': None,
                'gen': None,
            }

u2net_pretrained_path = 'code/app/src/try_on/u2net/ckp/u2netp.pth'
fsvton_pretrained_path = {
                            'warp': 'code/app/src/try_on/inference_flow_style_vton/aug/PFAFN_warp_epoch_101.pth',
                            'gen': 'code/app/src/try_on/inference_flow_style_vton/aug/PFAFN_gen_epoch_101.pth',
                        }


def get_device():
    if torch.cuda.is_available():
        return torch.device('cuda')
    return torch.device('cpu')


def load_models():
    global u2net_model, fsvton_model
    device = get_device()
    u2net_model = u2nu.load_model(model_name='u2netp', checkpoint=u2net_pretrained_path, device=device)
    fsvton_model = fsvu.load_model(checkpoints=fsvton_pretrained_path, device=device)


def infer_u2net(image):
    device = get_device()

    # [c, h, w] -> [1, c, h, w] 
    images = images.clone().detach()[None, :]
    images = images.type(torch.FloatTensor)

    images = Variable(images.to(device))

    d1, d2, d3, d4, d5, d6, d7 = u2net_model(images)
    pred_mask = d1[:,0,:,:]
    pred_mask = u2nu.normPRED(pred_mask)
    
    # [1, c, h, w] -> [c, h, w] 
    return pred_mask[0, :]


def infer_tryon(images):
    device = get_device()

    warp_model, gen_model = fsvton_model['warp'], fsvton_model['gen']
    
    # [c, h, w] -> [1, c, h, w] 
    real_image = images['image'][None, :]
    clothes = images['cloth'][None, :]
    edge = images['edge'][None, :]
    
    edge = torch.FloatTensor((edge.detach().numpy() > 0.5).astype(np.int64))
    clothes = clothes * edge   

    warped_cloth, last_flow  = warp_model(real_image.to(device), clothes.to(device))
    warped_edge = F.grid_sample(edge.to(device), last_flow.permute(0, 2, 3, 1),
                        mode='bilinear', padding_mode='zeros')

    gen_inputs = torch.cat([real_image.to(device), warped_cloth, warped_edge], 1)
    gen_outputs = gen_model(gen_inputs)
    p_rendered, m_composite = torch.split(gen_outputs, [3, 1], 1)
    p_rendered = torch.tanh(p_rendered)
    m_composite = torch.sigmoid(m_composite)
    m_composite = m_composite * warped_edge

    p_tryon = warped_cloth * m_composite + p_rendered * (1 - m_composite)

    # [1, c, h, w] -> [c, h, w] 
    return p_tryon[0, :]


def run_tryon(person_image: bytes, cloth_image: bytes):
    convert_tensor = transforms.ToTensor()
    to_pil = transforms.ToPILImage()

    person = convert_tensor(Image.open(person_image).convert("RGB"))
    cloth = convert_tensor(Image.open(cloth_image).convert("RGB"))

    # Segment cloth
    edge = infer_u2net(cloth)
    
    # Try on
    result = infer_tryon(images={'image': person, 'cloth': cloth, 'edge': edge})

    return to_pil(result)


if __name__=='__main__':
    load_models()