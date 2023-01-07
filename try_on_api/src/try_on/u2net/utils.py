import torch

from u2net import U2NET, U2NETP  # 173.6 MB and 4.7 MB


# normalize the predicted SOD probability map
def normPRED(d):
    ma = torch.max(d)
    mi = torch.min(d)

    dn = (d-mi)/(ma-mi)

    return dn


def load_model(model_name, checkpoint, device=torch.device('cuda')):
    if torch.cuda.is_available()==False:
        print('[!] Load model: You do not have a GPU, convert device to CPU')
        device = torch.device('cpu')

    if(model_name=='u2net'):
        print("\t[-] Lload U2NET---173.6 MB")
        net = U2NET(3,1)
    elif(model_name=='u2netp'):
        print("\t[-] Load U2NEP---4.7 MB")
        net = U2NETP(3,1)

    net.load_state_dict(torch.load(checkpoint, map_location=device))
    net.to(device)
    net.eval()

    return net

# from PIL import Image
# from torchvision import utils
# from torchvision.transforms import ToTensor
# if __name__=='__main__':
#     net = load_model(model_name='u2netp', model_path='u2net/ckp/u2netp/u2netp.pth')

#     clothes = ToTensor()(Image.open('data/test_clothes/007856_1.jpg'))
#     pred = infer(net, clothes[None, :])[0, :]

#     utils.save_image(pred, 'a.jpg')