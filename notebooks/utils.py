from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.chat_models.base import BaseChatModel
from langchain.schema import (BaseMessage, ChatResult, AIMessage,
                              ChatGeneration, HumanMessage, SystemMessage,
                              ChatMessage, FunctionMessage)

from langchain.pydantic_v1 import BaseModel, Extra, Field, root_validator
from langchain.utils import get_from_dict_or_env, get_pydantic_field_names

# import numpy as np
import dataclasses
from typing import Any, List, Dict, Union, Optional
# from typing import (
#     Callable,
#     Literal,
#     Optional,
#     Sequence,
#     Set,
#     Tuple,
# )

import requests
import os


@dataclasses.dataclass
class ChatGPTEntry:
    '''
    Зачем тебе читать эту документацию? 
    Лучше подписывайся на канал datafeeling в телеграм!
    '''
    role: str
    content: str

@dataclasses.dataclass
class ResponseSchema:
    '''
    Зачем тебе читать эту документацию? 
    Лучше подписывайся на канал datafeeling в телеграм!
    '''
    id : str
    object: str
    created: int
    model: str
    choices: Union[ChatGPTEntry, dict]
    usage: dict
    prompt_tokens: int
    completion_tokens: int
    available_tokens: int
    
    # def __post_init__(self):
        # self.choices = ChatGPTEntry(**self.choices[0])

class completions:
    '''
    Класс ChatCompletion по аналогии с одноименным классом из библиотеки openai
    '''
    
    _server = "https://api.neuraldeep.tech/" 
    _session = requests.Session()
    # course_api_key = None

    def __init__(self, provider_url: str = "https://api.neuraldeep.tech/", **kwargs):
        self._server = provider_url
        self._session = requests.Session()

    @classmethod 
    def create(cls, messages: List[Dict[str, Any]],
               model="gpt-3.5-turbo",
               course_api_key: str = 'course_api_key', **kwargs) -> ResponseSchema:

        assert cls.course_api_key != 'course_api_key', 'Для генерации требуется ввести токен'
        
        messages = {'messages' : messages}
        messages.update(kwargs)

        cls._auth = cls.course_api_key
        response = cls._session.post(os.path.join(cls._server, "chatgpt"), json=messages,
                                      headers={"Authorization": f"Bearer {cls._auth}"})

        response.raise_for_status()
        json_response = response.json()

        # print(json_response)
        final_response = {}
        for k,v in json_response['raw_openai_response'].items():
            final_response[k] = v

        final_response['available_tokens'] = json_response['available_tokens'] 
        final_response['completion_tokens'] = json_response['completion_tokens'] 
        final_response['prompt_tokens'] = json_response['prompt_tokens']  

        return ResponseSchema(**final_response)

    def __del__(self):
        self._session.close()
            
class chat:
    completions = completions
    
class OpenAI:
    def __init__(self, course_api_key="api"):
        self.course_api_key=course_api_key
        self.chat = chat
        self.chat.completions.course_api_key = course_api_key  

class Embedding:
    
    '''
    Класс Embedding по аналогии с одноименным классом из библиотеки openai
    '''

    # _session = requests.Session()
    model="text-embedding-ada-002"
    
    def __init__(self,
                 course_api_key : str,
                 provider_url: str = "https://api.neuraldeep.tech/", 
                 **kwargs):
        self._server = provider_url
        self._session = requests.Session()
        self.course_api_key = course_api_key
         # cls._auth = course_api_key
        
    # @classmethod 
    def create(self, input: str, **kwargs) -> ResponseSchema:
        
        # cls._auth = self.course_api_key
        # print(input)
        messange = {'str_to_vec' : input}
        response = self._session.post(os.path.join(self._server, "embeddings"), json=messange,
                                      headers={"Authorization": f"Bearer {self.course_api_key}"})
        
        response.raise_for_status()
        json_response = response.json()
        
        # print(json_response)
        # final_response = {}
        # for k,v in json_response['raw_openai_response'].items():
        #     final_response[k] = v

        # final_response['embedding'] = json_response['embedding'] 
        # final_response['available_tokens'] = json_response['available_tokens'] 
        # final_response['prompt_tokens'] = json_response['prompt_tokens']  
        
        return json_response['raw_openai_response']

from langchain.embeddings import OpenAIEmbeddings

class OpenAIEmbeddings(OpenAIEmbeddings):
    
    course_api_key : str
    provider_url: str = "https://api.neuraldeep.tech/"
    # client: Embedding 
    
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = Embedding(provider_url=self.provider_url, **kwargs)

    
    
    @root_validator(pre=True)
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        values["course_api_key"] = get_from_dict_or_env(
            values, "course_api_key", "COURSE_API_KEY"
        )
        values["openai_api_base"] = get_from_dict_or_env(
            values,
            "openai_api_base",
            "OPENAI_API_BASE",
            default="",
        )
        values["openai_api_type"] = get_from_dict_or_env(
            values,
            "openai_api_type",
            "OPENAI_API_TYPE",
            default="",
        )
        values["openai_proxy"] = get_from_dict_or_env(
            values,
            "openai_proxy",
            "OPENAI_PROXY",
            default="",
        )
        if values["openai_api_type"] in ("azure", "azure_ad", "azuread"):
            default_api_version = "2022-12-01"
            # Azure OpenAI embedding models allow a maximum of 16 texts
            # at a time in each batch
            # See: https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#embeddings
            default_chunk_size = 16
        else:
            default_api_version = ""
            default_chunk_size = 1000
        values["openai_api_version"] = get_from_dict_or_env(
            values,
            "openai_api_version",
            "OPENAI_API_VERSION",
            default=default_api_version,
        )
        values["openai_organization"] = get_from_dict_or_env(
            values,
            "openai_organization",
            "OPENAI_ORGANIZATION",
            default="",
        )
        if "chunk_size" not in values:
            values["chunk_size"] = default_chunk_size

        return values
    
# messages = [{"role": "user", "content": prompt}]
# response = ChatCompletion().create(course_api_key=course_api_key,
#                                    model = model,
#                                    messages = messages,
#                                    temperature=0)

# print(response)
    
# llm_chat = ChatOpenAI(course_api_key="вставь сюда токен курса")
# res = llm_chat(messages=[HumanMessage(content="Translate this sentence")])
# print(res)
