# This software is licensed with the Apache 2.0 license
#
# See the LICENSE file in the top level directory of this repository for
# license terms.
#
# Copyright 2024 David Wootton

import gc
import glob
import os
import time
import torch
from accelerate import infer_auto_device_map
from accelerate import init_empty_weights
from auto_gptq import AutoGPTQForCausalLM
from auto_gptq import BaseQuantizeConfig
from ctransformers import AutoModelForCausalLM as GGUFAutoModelForCausalLM
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_community.llms import LlamaCpp
from pathlib import Path
from Request.Request import Request
from transformers import AutoConfig
from transformers import AutoModelForCausalLM
from transformers import AutoTokenizer
from transformers import BitsAndBytesConfig
from Util.Globals import Globals

 
# This class is used as a callback when generating a LLM respose so output can vbe retried and displayed as it is generated rather than waiting for the
# query to complete before displaying anything. 
class ResultCallback(BaseCallbackHandler):
    def on_llm_new_token(self, token, **kwargs):
        Globals().postAnswer(token)

# Handle a request to load a LLM model
class LoadModelRequest(Request):
    def __init__(self):
        super().__init__()


    # Load the model when it is in GPTQ quantized format
    def gptqLoader(self):
        Globals().logMessage('Loading GPTQ model')
        startTime = time.time()
        model = None
        tokenizer = None
        params = {}
        params['trust_remote_code'] = self._trustRemoteCode
        # Some models, for example MPT models include an attn_config map in their configuration. If present, try to set attn_impl to 'triton'
        if (self._useTriton):
            try:
                params['use_triton'] = self._useTriton
            except AttributeError:
                pass

        # Set memory limits for CPU and/or GPU
        limits = {}
        for n in range(len(self._maxGPUMemory)):
            limits[n] = f'{self._maxGPUMemory[str(n)]}MiB'

        if (self._useCPU):
            limits['cpu'] = f'{self._maxCPUMemory}MiB'

        print('memLimits', limits)
        # Load the model and the tokenizer
        Globals().logMessage('Loading model and tokenizer')
        startTime = time.time()
        
        # Set up model parameters
        # If the model overflows to disk, then the specified directory must contain sufficient space. Otherwise, the python interpreter
        # may fail with a SIGBUS error.
        modelFile = None
        files = os.listdir(self._modelPath)
        for f in files:
            if (os.path.basename(self._modelPath) in f):
                modelFile = f
                break
        if (modelFile is not None):
            params['model_basename'] = Path(modelFile).stem
        
        if (self._useFloat16):
            torchDType = torch.float16
        else:
            torchDType = torch.float32
        params['model_name_or_path'] = self._modelPath
        params['max_memory'] = limits
        params['torch_dtype'] = torchDType
        params['use_safetensors'] = self._useSafeTensors
        params['max_memory'] = limits
        if (self._overflowToDisk):
            params['offload_folder'] = self._overflowPath
        if (self._autoDevice):
            Globals().logMessage('Using auto device map')
            params['device_map'] = 'auto'
            # The MPT-7B models fail to load if the device_map parameter is set to auto with an error stating the auto mode is not
            # implemented yet. This can be fixed by making the code change described in
            # https://huggingface.co/mosaicml/mpt-7b/discussions/23
            model = AutoGPTQForCausalLM.from_quantized(**params)
        else:
            params['pretrained_model_name_or_path'] = self._modelPath
            quantizeConfig = BaseQuantizeConfig(bits=4, group_size=128, desc_act=False)
            params['quantize_config'] = quantizeConfig
            model = AutoGPTQForCausalLM.from_quantized(**params)
            params['device_map'] = infer_auto_device_map(model, max_memory=params['max_memory'],
                                                         no_split_module_classes=model._no_split_modules, dtype=torchDType)
            print('params:', params['device_map'])
        
        # The MPT-7B models fail to load if the device_map parameter is set to auto with an error stating the auto mode is not implemented
        # yet. This can be fixed by making the code change described in https://huggingface.co/mosaicml/mpt-7b/discussions/23

        # Log the mapping of model modules to devices
        devices = {}
        for k, v in model.hf_device_map.items():
            if (v in devices):
                devices[v] = devices[v] + 1
            else:
                devices[v] = 1
        mapString = 'Module device map: '
        for k, v in devices.items():
            mapString = mapString + f'device: {k}, modules: {v} '
        Globals().logMessage("Model allocations: " + mapString)

        model.eval()

        tokenizer = AutoTokenizer.from_pretrained(self._modelPath)
        Globals().setModel(model)
        Globals().setTokenizer(tokenizer)
        elapsedTime = time.time() - startTime
        #memoryFootprint = model.get_memory_footprint()
        #bufferMemorySize = memoryFootprint - model.get_memory_footprint(return_buffers=False)
        logMessage = f'Loaded model and tokenizer in {elapsedTime:.3f} seconds'
        #logMessage = logMessage + f' memory footprint  {memoryFootprint / 1000000000.0:.3f}GB'
        #logMessage = logMessage + f' buffers {bufferMemorySize / 1000000000.0:.3f}GB'
        #logMessage = logMessage + f' max CUDA memory {torch.cuda.max_memory_allocated() / 1000000000.0:.3f}GB'
        Globals().logMessage(logMessage)

    # Load a quantized model that is in LlamaCPP format
    def llamaCppLoader(self):
        Globals().logMessage('Loading LlamaCpp model')
        files = glob.glob(self._modelPath + '/*ggmlv3*')
        if (len(files) == 0):
            logMessage = f'No model found in {self._modelPath}'
            return
        loadPath = files[0]
        startTime = time.time()
        #model = LlamaCpp(model_path=loadPath, streaming=True, max_tokens=1500, temperature=.001, n_threads=20, n_ctx=2048,
        #                callbacks=[ResultCallback()])
        model = LlamaCpp(model_path=loadPath, streaming=True, callbacks=[ResultCallback()])
        elapsedTime = time.time() - startTime
        logMessage = f'Loaded model and tokenizer in {elapsedTime:.3f} seconds'
        Globals().logMessage(logMessage)
        Globals().setModel(model)
        Globals().setTokenizer(None)

    # Load a non-quantized LLM model
    def standardLoader(self):
        startTime = time.time()
        model = None
        tokenizer = None
        params = {}
        params['trust_remote_code'] = self._trustRemoteCode
        if (self._useFloat16):
            torchDType = torch.float16
        else:
            torchDType = torch.float32
        params['torch_dtype'] = torchDType
        config = AutoConfig.from_pretrained(self._modelPath, **params)
        # Some models, for example MPT models include an attn_config map in their configuration. If present, try to set attn_impl to
        # 'triton'
        if (self._useTriton):
            try:
                config.attn_config['attn_impl'] = 'triton'
            except AttributeError:
                pass
        with init_empty_weights():
            model = AutoModelForCausalLM.from_config(config, **params)
        model.tie_weights()
        elapsedTime = time.time() - startTime
        Globals().logMessage(f'Initialized model in {elapsedTime:.3f} seconds')

        # Set memory limits for CPU and/or GPU
        limits = {}
        for n in range(len(self._maxGPUMemory)):
            limits[n] = f'{self._maxGPUMemory[str(n)]}MiB'

        if (self._useCPU):
            limits['cpu'] = f'{self._maxCPUMemory}MiB'
        params['max_memory'] = limits

        # Load the model and the tokenizer
        Globals().logMessage('Loading model and tokenizer')
        startTime = time.time()
        
        # Set up model parameters
        #params['quantization_config'] = BitsAndBytesConfig(load_in_8bit=self._use8Bit, llm_int8_enable_fp32_cpu_offload=self._useCPU)
        # If the model overflows to disk, then the specified directory must contain sufficient space. Otherwise, the python interpreter
        # may fail with a SIGBUS error.
        if (self._autoDevice):
            Globals().logMessage('Using auto device map')
            params['device_map'] = 'auto'
        else:
            # Set memory limits for determining model map
            params['device_map'] = infer_auto_device_map(model, max_memory=params['max_memory'],
                                   no_split_module_classes=model._no_split_modules, dtype=torchDType)
            print('device map:', params['device_map'])

        # Set parameters needed to load model
        if (self._overflowToDisk):
            params['offload_folder'] = self._overflowPath
        if (self._use8Bit):
            params['quantization_config'] = BitsAndBytesConfig(load_in_8bit=self._use8Bit, llm_int8_enable_fp32_cpu_offload=self._useCPU)
        elif (self._use4Bit):
            params['quantization_config'] = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4', bnb_4bit_use_double_quant=True, 
                                                               bnb_4bit_compute_dtype=torch.bfloat16)

        # The MPT-7B models fail to load if the device_map parameter is set to auto with an error stating the auto mode is not implemented
        # yet. This can be fixed by making the code change described in https://huggingface.co/mosaicml/mpt-7b/discussions/23
        model = AutoModelForCausalLM.from_pretrained(self._modelPath, **params)

        # Log the mapping of model modules to devices
        devices = {}
        for k, v in model.hf_device_map.items():
            if (v in devices):
                devices[v] = devices[v] + 1
            else:
                devices[v] = 1
        mapString = 'Module device map: '
        for k, v in devices.items():
            mapString = mapString + f'device: {k}, modules: {v} '
        Globals().logMessage("Model allocations: " + mapString)

        model.eval()

        tokenizer = AutoTokenizer.from_pretrained(self._modelPath, trust_remote_code=self._trustRemoteCode)
        Globals().setModel(model)
        Globals().setTokenizer(tokenizer)
        elapsedTime = time.time() - startTime
        memoryFootprint = model.get_memory_footprint()
        bufferMemorySize = memoryFootprint - model.get_memory_footprint(return_buffers=False)
        logMessage = f'Loaded model and tokenizer in {elapsedTime:.3f} seconds'
        logMessage = logMessage + f' memory footprint  {memoryFootprint / 1073741824.0:.3f}GB'
        logMessage = logMessage + f' buffers {bufferMemorySize / 1073741824.0:.3f}GB'
        logMessage = logMessage + f' max CUDA memory {torch.cuda.max_memory_allocated() / 1073741824.0:.3f}GB'
        Globals().logMessage(logMessage)

    def ggufLoader(self):
        modelParms = {}
        modelParms['model_type'] = 'llama'
        #modelParms['model_file'] = self._modelPath
        model = GGUFAutoModelForCausalLM.from_pretrained(self._modelPath, **modelParms)
        Globals().logMessage('GGUF model loaded')

    # Set the model loading parameters for this request                                                 
    def setModelParameters(self, profile):
        self._modelPath = profile['modelPath']
        self._overflowPath = profile['overflowPath']
        self._autoDevice = profile['autoDevice']
        self._overflowToDisk = profile['overflowToDisk']
        self._useCPU = profile['useCPU']
        self._useFloat16 = profile['use16Bit']
        self._use8Bit = profile['use8Bit']
        self._use4Bit = profile['use4Bit']
        self._maxCPUMemory = profile['maxCpuMemory']
        self._maxGPUMemory = profile['gpuMemory']
        self._trustRemoteCode = profile['trustRemoteCode']
        self._useSafeTensors = profile['useSafeTensors']
        self._useTriton = profile['useTriton']
        self._wbits = profile['wBits']
        self._groupSize = profile['groupSize']


    # Process a request to load a LLM model
    def processRequest(self):
        # Look at https://github.com/pinecone-io/examples/blob/master/generation/llm-field-guide/mpt-7b/mpt-7b-huggingface-langchain.ipynb
        # for setting up stopping criteria for text generation
        
        Globals().logMessage('Initializing model')
        # Recover storage fromn previously loaded model and tokenizer
        model = Globals().getModel()
        if (not model == None):
            del model
        Globals().setModel(None)
        gc.collect()
        torch.cuda.empty_cache()
        tokenizer = Globals().getTokenizer()
        if (not tokenizer == None):
            del tokenizer
        Globals().setTokenizer(None)
        gc.collect()
        torch.cuda.empty_cache()

        # Load model based on model type
        if ('GPTQ' in self._modelPath):
            modelLoader = self.gptqLoader
        elif ('gptq' in self._modelPath):
            modelLoader = self.gptqLoader
        elif ('ggmlv3' in self._modelPath):
            modelLoader = self.llamaCppLoader
        elif ('gguf' in self._modelPath):
            modelLoader = self.ggufLoader
        elif ('GGUF' in self._modelPath):
            modelLoader = self.ggufLoader
        elif (os.path.exists(os.path.join(self._modelPath, 'config.json'))):
            modelLoader = self.standardLoader
        else:
            Globals().logMessage(f'Unable to load model, unknown model type:, {self._modelPath}')
            return
        modelLoader()
        return
    
