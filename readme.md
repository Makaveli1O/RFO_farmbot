## Working environment:
```python 3.9 windows store```


nvcc: NVIDIA (R) Cuda compiler driver
*Build cuda_11.8.r11.8/compiler.31833905_0*


## Install instructions
*note: important to install ultralytics before torch! Since ultarlytics will install cpu version of torch that has to be overriden.*

`pip install numpy`

`pip install ultralytics`

`pip install pypiwin32`

`pip install supervision`

`pip install pyautogui`


install corresponding torch version that supports *CUDA*

`pip install torch==1.13.0+cu117 torchvision==0.14.0+cu117 torchaudio==0.13.0 --extra-index-url https://download.pytorch.org/whl/cu117`

### OR

`pip install -r requirements.txt`
