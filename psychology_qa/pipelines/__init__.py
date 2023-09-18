import gc

import torch
from haystack.pipelines import Pipeline


def empty_memory(pipeline: Pipeline) -> None:
    retriever = pipeline.get_node("Retriever")
    del retriever.embedding_encoder.embedding_model
    del retriever.embedding_encoder

    torch.cuda.empty_cache()
    gc.collect()
