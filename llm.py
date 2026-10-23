"""Ollama adapter. Loopback only; no cloud credentials or implicit fallback."""
import json
import os
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import URLError

BASE = 'http://127.0.0.1:11434'

def chat(model, system, prompt, timeout=90, response_format=None):
    if not model.strip(): raise RuntimeError('Choose a locally installed model name.')
    body = {'model':model, 'messages':[{'role':'system','content':system},{'role':'user','content':prompt}],
            'stream':False, 'options':{'temperature':0, 'num_predict':500}, 'keep_alive':'5m'}
    if response_format is not None: body['format'] = response_format
    request = Request(BASE+'/api/chat',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'},method='POST')
    try:
        with build_opener(ProxyHandler({})).open(request,timeout=timeout) as response:
            payload = json.loads(response.read(1_000_000))
        if payload.get('error'): raise RuntimeError('Local model reported an error: '+str(payload['error']))
        content=payload.get('message',{}).get('content','').strip()
        if not content: raise RuntimeError('The model returned an empty answer.')
        return content
    except (URLError,TimeoutError,OSError,ValueError) as error:
        raise RuntimeError('Local model unavailable. Start Ollama and install the selected model; the deterministic workflow still works.') from error
