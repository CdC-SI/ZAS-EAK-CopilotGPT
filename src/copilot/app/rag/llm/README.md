# Open Source Model Setup Guide

### Setup a llama.cpp server locally

#### Install llama.cpp
````
git clone git@github.com:ggerganov/llama.cpp.git
cd llama.cpp
make # for macos/linux
````

#### Run a local web server
````
./llama-server -m models/7b/qwen2.5-7b-instruct-q2_k.gguf --port 5000
```