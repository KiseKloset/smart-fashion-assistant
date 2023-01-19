import torch
import torch.nn as nn
import numpy as np

from collections import OrderedDict


class LayerNorm(nn.LayerNorm):
    def forward(self, x: torch.Tensor):
        orig_type = x.dtype
        ret = super().forward(x.type(torch.float32))
        return ret.type(orig_type)


class QuickGELU(nn.Module):
    def forward(self, x: torch.Tensor):
        return x * torch.sigmoid(1.702 * x)


class ResidualAttentionBlock(nn.Module):
    def __init__(self, d_model: int, n_head: int):
        super().__init__()

        self.attn = nn.MultiheadAttention(d_model, n_head, batch_first=True)
        self.attn_mask = None
        self.ln_1 = LayerNorm(d_model)
        self.mlp = nn.Sequential(OrderedDict([
            ("c_fc", nn.Linear(d_model, d_model * 4)),
            ("gelu", QuickGELU()),
            ("c_proj", nn.Linear(d_model * 4, d_model))
        ]))
        self.ln_2 = LayerNorm(d_model)


    def set_attn_mask(self, attn_mask: torch.Tensor):
        self.attn_mask = attn_mask


    def attention(self, x: torch.Tensor, attn_mask: torch.Tensor):
        attn_mask = attn_mask.to(dtype=x.dtype, device=x.device) if attn_mask is not None else None
        return self.attn(x, x, x, need_weights=False, attn_mask=attn_mask)[0]


    def forward(self, x: torch.Tensor):
        x = x + self.attention(self.ln_1(x), self.attn_mask)
        x = x + self.mlp(self.ln_2(x))
        return x


class OutfitsTransformer(nn.Module):

    def __init__(self, n_categories: int, d_model: int, n_heads: int, n_layers: int):
        super().__init__()
        self.n_heads = n_heads
        self.positional_embedding = nn.Parameter(torch.empty(n_categories, d_model))
        nn.init.normal_(self.positional_embedding, std=0.01)

        self.encoders = [ResidualAttentionBlock(d_model, n_heads) for _ in range(n_layers)]
        self.transformer = nn.Sequential(*self.encoders)


    # embeddings: [batch_size, num_categories, d_model]
    def forward(self, embeddings, input_mask):
        # Calculate the attention mask
        attn_mask = input_mask[:, :, None].float()
        attn_mask = torch.bmm(attn_mask, attn_mask.transpose(1, 2)).repeat(self.n_heads, 1, 1)

        # Add positional encoding
        embeddings = embeddings + self.positional_embedding

        # Pass the embeddings through encoders
        for encoder in self.encoders:
            encoder.set_attn_mask(attn_mask)

        return self.transformer(embeddings)


    def __str__(self):
        model_parameters = filter(lambda p: p.requires_grad, self.parameters())
        params = sum([np.prod(p.size()) for p in model_parameters])
        return super().__str__() + '\nTrainable parameters: {}'.format(params)


class OutfitsTransformerModule:
    def __init__(self, pretrained_path, device):
        self.device = device
        self.model = OutfitsTransformer(11, 640, 16, 6).to(device)
        state_dict = torch.load(pretrained_path, map_location=device)
        self.model.load_state_dict(state_dict)
        self.model.eval()

    
    def __call__(self, embedding, input_mask):
        output = self.model(
            embedding.to(self.device).unsqueeze(0), input_mask.to(self.device).unsqueeze(0)
        )
        return output.squeeze(0)