import os

import bentoml

import torch

from transformers import AutoTokenizer

if torch.cuda.is_available():
    from transformers import AutoModel, AutoModelForSequenceClassification, BitsAndBytesConfig #type: ignore
else:
    from optimum.onnxruntime import ORTModel, ORTModelForSequenceClassification, ORTQuantizer # type: ignore
    from optimum.onnxruntime.configuration import AutoQuantizationConfig # type: ignore

def load_onnx_emb(path, save_dir):
    if os.path.exists(save_dir):
        os.makedirs(save_dir)
    model = ORTModel.from_pretrained(path, export=True)
    quantizer = ORTQuantizer.from_pretrained(model)
    dpconf = AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=False)
    path = quantizer.quantize(save_dir=save_dir, quantization_config=dpconf)
    model = ORTModel.from_pretrained(path)

    return model

def load_onnx_reranker(path, save_dir):
    if os.path.exists(save_dir):
        os.makedirs(save_dir)
    model = ORTModelForSequenceClassification.from_pretrained(path, export=True)
    quantizer = ORTQuantizer.from_pretrained(model)
    dpconf = AutoQuantizationConfig.avx512_vnni(is_static=False, per_channel=False)
    path = quantizer.quantize(save_dir=save_dir, quantization_config=dpconf)
    model = ORTModelForSequenceClassification.from_pretrained(path)

    return model


@bentoml.service
class Models:

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    def __init__(self):
        emb_path = '/workspaces/model_full/emb'
        reranker_path = '/workspaces/model_full/reranker'

        print(f'Found device: {self.device}')
        
        if self.device == 'cpu':
            emb_save_dir = '/cache/models/emb/'
            reranker_save_dir = '/cache/models/reranker/'

            self.emb_model = load_onnx_emb(emb_path, emb_save_dir)
            self.reranker_model = load_onnx_reranker(reranker_path, reranker_save_dir)
        else:
            quantization_config = BitsAndBytesConfig(load_in_8bit=True)
            self.emb_model = AutoModel.from_pretrained(emb_path, quantization_config=quantization_config, low_cpu_mem_usage=True)
            self.reranker_model = AutoModelForSequenceClassification.from_pretrained(reranker_path, quantization_config=quantization_config, low_cpu_mem_usage=True)
        
        print(f'Embedding model: {self.emb_model.get_memory_footprint() / 1024**3}GB')
        self.emb_tokenizer = AutoTokenizer.from_pretrained(emb_path)

        print(f'Reranker model: {self.reranker_model.get_memory_footprint() / 1024**3}GB')
        self.reranker_tokenizer = AutoTokenizer.from_pretrained(reranker_path)

    @bentoml.api(route='/emb')
    def embedding(self, text):
        with torch.no_grad():
            with torch.backends.cuda.sdp_kernel(enable_flash=True, enable_math=False, enable_mem_efficient=False):
                encoded_input = self.emb_tokenizer(text, padding=True, truncation=True, return_tensors='pt').to(self.device)
                model_output = self.emb_model(encoded_input['input_ids'], encoded_input['attention_mask'])
                sentence_embeddings = model_output[0][:, 0]
                sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1).to('cpu').tolist()
        return {'embedding': sentence_embeddings}
        

    def __build_pair(self, q: str, docs: list[str]):
        return [(q, d) for d in docs]
    
    def __sort_results(self, docs: list[str], scores: list[float]):
        ordered = sorted([(d, s) for d, s in zip(docs, scores)], key=lambda x: x[1], reverse=True)
        return [{'content': d, 'score':s} for d, s in ordered]

    @bentoml.api(route='/rerank')
    def rerank(self, text: str, docs: list[str]):
        pairs = self.__build_pair(text, docs)
        with torch.no_grad():
            with torch.backends.cuda.sdp_kernel(enable_flash=True, enable_math=False, enable_mem_efficient=False):
                encoded_input = self.reranker_tokenizer(pairs, padding=True, truncation=True, return_tensors='pt').to(self.device)
                model_output = self.reranker_model(encoded_input['input_ids'], encoded_input['attention_mask']).logits.view(-1).to('cpu').detach().float()
                scores = [s.item() for s in model_output]
                ret_docs = self.__sort_results(docs, scores)
        return {'scores': ret_docs}
    
# @bentoml.service()
# class Control:
#     embedding = bentoml.depends(Embedding)
#     reranker = bentoml.depends(Reranker)

#     @bentoml.api
#     async def emb(self, text: str):
#         return await self.embedding.embedding(text)
    
#     @bentoml.api
#     async def rerank(self, text: str, docs: list[str]):
#         return await self.reranker.rerank(text, docs)