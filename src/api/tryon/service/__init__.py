import datetime
from typing import Any
from PIL import Image

import cv2
import numpy as np
import torch
from torch.autograd import Variable

from .yolov7_pose import Yolov7PoseEstimation
from .u2net import load_model as load_edge_detect_model, norm_pred
from .dm_vton import DMVTON, get_transform


class TryonService:
    def __init__(self, tryon_ckpt, edge_detect_ckpt, yolo_ckpt, device, img_size=(192, 256)) -> None:
        self.device = device
        self.img_size = img_size
        self._load_model(tryon_ckpt, edge_detect_ckpt, device=device)
        self._load_yolov7(yolo_ckpt)

    def tryon_video(self, cap, pil_clothes, pil_edge=None, fps=30):
        transform_image = get_transform(train=False)
        transform_edge = get_transform(train=False, method=Image.NEAREST, normalize=False)
        
        # save_name = f'{datetime.datetime.now().strftime("%Y-%m-%d_%H%M-%S")}.mp4'
        save_name = 'aaaa.mp4'
        vid_writer = cv2.VideoWriter(save_name, cv2.VideoWriter_fourcc(*'mp4v'), fps, self.img_size) 
        
        pil_clothes = self._preprocess_image(pil_clothes)

        clothes = transform_image(pil_clothes)
        if pil_edge is not None:
            clothes_edge = self._preprocess_image(pil_clothes, color='L')
            clothes_edge = transform_edge(clothes_edge)
        else:
            clothes_edge = self._predict_edge(clothes)

        frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if ret == True:
                frame = frame[:, :, :]
                cropped_result, frame = self._preprocess_frame(frame)
                
                if frame is not None: 
                    pil_img = Image.fromarray(frame)
                    img = transform_image(pil_img)

                # TRYON
                original_image = cropped_result['origin_frame']
                if frame is not None: 
                    cv_img = (self._predict_tryon(img, clothes, clothes_edge).permute(1, 2, 0).detach().cpu().numpy() + 1) / 2
                    rgb = (cv_img*255).astype(np.uint8)
                    bgr = cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR)

                    # Re-mapping to original image
                    t, l, b, r = cropped_result['t'], cropped_result['l'], cropped_result['b'], cropped_result['r']
                    cropped_output = cv2.resize(bgr, (r - l, b - t))  
                    original_image[t:b, l:r, :] = cropped_output

                vid_writer.write(original_image)
            
            else:
                break
                    

    def tryon_image(self, pil_img, pil_clothes, pil_edge=None) -> Any:
        transform_image = get_transform(train=False)
        transform_edge = get_transform(train=False, method=Image.NEAREST, normalize=False)

        pil_img, pil_clothes = self._preprocess_image(pil_img), self._preprocess_image(pil_clothes)

        img = transform_image(pil_img)
        clothes = transform_image(pil_clothes)
        if pil_edge:
            clothes_edge = self._preprocess_image(pil_clothes, color='L')
            clothes_edge = transform_edge(clothes_edge)
        else:
            clothes_edge = self._predict_edge(clothes)
        
        return (self._predict_tryon(img, clothes, clothes_edge) + 1)/2

    def _preprocess_image(self, pil_img, color='RGB'):
        pil_img = pil_img.convert(color).resize(self.img_size)
        return pil_img

    def _preprocess_frame(self, frame):
        # Crop the image using pose
        cropped_result = crop_upper_body(frame, self.yolo_model)
        frame = cropped_result['cropped_frame']

        if frame is None:
            return cropped_result, None
        
        # Crop the image to have same ratio
        if frame.shape[0] * self.img_size[0] < frame.shape[1] * self.img_size[1]:
            height = frame.shape[0]
            width = int(self.img_size[0] * height / self.img_size[1])
        else:
            width = frame.shape[1]
            height = int(self.img_size[1] * width / self.img_size[0])
            
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        center = (frame.shape[0] // 2, frame.shape[1] // 2)
        x = center[1] - width // 2
        y = center[0] - height // 2
        frame = frame[y : y + height, x : x + width]
        frame = cv2.resize(frame, (self.img_size[0], self.img_size[1]))

        # Mapping bbox value
        cropped_result['t'] += y
        cropped_result['b'] = cropped_result['t'] + height
        cropped_result['l'] += x
        cropped_result['r'] = cropped_result['l'] + width

        return cropped_result, frame

    def _load_model(self, tryon_ckpt, edge_detect_ckpt, device):
        self.tryon_model = DMVTON(tryon_ckpt, device=device, align_corners=True)
        self.edge_detect_model = load_edge_detect_model(model_name='u2netp', checkpoint=edge_detect_ckpt, device=device)
    
    def _load_yolov7(self, yolo_ckpt):
        self.yolo_model = Yolov7PoseEstimation(
            weight_path=yolo_ckpt,
            device=self.device,
        )

    def _predict_edge(self, img):
        img = img.clone().unsqueeze(0)
        img = img.type(torch.FloatTensor)

        img = Variable(img.to(self.device))

        with torch.no_grad():
            d1 = self.edge_detect_model(img)

        pred_mask = d1[:,0,:,:]
        pred_mask = norm_pred(pred_mask)
        
        return pred_mask

    def _predict_tryon(self, img, clothes, clothes_edge):
        img = img.clone().unsqueeze(0)
        clothes = clothes.clone().unsqueeze(0)
        clothes_edge = clothes_edge.clone().unsqueeze(0)

        with torch.no_grad():
            p_tryon = self.tryon_model(img, clothes, clothes_edge)

        return p_tryon[0]


def crop_upper_body(frame, pose_detector):
    results = pose_detector.process(frame)
    h, w, _ = frame.shape
    
    # TUNGPNT2
    if results.pose_landmarks is None:
        return {'origin_frame': frame, 'cropped_frame': None, 't': 0, 'l': 0, 'b': 0, 'r': 0}
    # return {'origin_frame': frame, 'cropped_frame': frame, 't': 0, 'l': 0, 'b': h, 'r': w}
    
    landmarks = results.pose_landmarks.landmark

    # 2 lower points of upper body
    l1 = {'x': landmarks[23].x, 'y': landmarks[23].y}
    l2 = {'x': landmarks[24].x, 'y': landmarks[24].y}

    # 2 eyes
    e1 = {'x': landmarks[2].x, 'y': landmarks[2].y}
    e2 = {'x': landmarks[5].x, 'y': landmarks[5].y}

    points = [l1, l2, e1, e2]

    # bbox
    bbox = {}
    t = min([i['y'] for i in points])
    b = max([i['y'] for i in points])
    l = min([i['x'] for i in points])
    r = max([i['x'] for i in points])

    # de-normalize
    t = int(t * h)
    b = int(b * h)
    l = int(l * w)
    r = int(r * w)

    # padding
    bh = b - t
    bw = r - l
    b += bh // 5
    t -= bh // 5
    r += bw // 1
    l -= bw // 1

    # crop
    t = max(0, min(t, h))
    b = max(0, min(b, h))
    l = max(0, min(l, w))
    r = max(0, min(r, w))

    return {'origin_frame': frame, 'cropped_frame': frame[t:b, l:r, :], 't': t, 'l': l, 'b': b, 'r': r}