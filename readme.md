
# RFO FarmBot

_Automated farming bot for RF Online using YOLO-based object detection._

## Features

- ✅ Auto-detects enemies and engages in combat
- ✅ Uses YOLO-based perception for targeting
- ✅ Supports custom configurations
- ✅ Works with NVIDIA CUDA for fast processing

## Installation

1. Install Python 3.9 (3.10+ is not supported).
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```  
3. Install the correct CUDA-supported PyTorch:
   ```sh
   pip install torch==1.13.0+cu117 torchvision==0.14.0+cu117 --extra-index-url https://download.pytorch.org/whl/cu117
   ```

## Usage

1. Run the bot script:
   ```sh
   python rfbot.py
   ```  
2. Configure detection settings in `config.json`.
3. Monitor logs in `logger.py` for debugging.

## Troubleshooting

- Ensure your GPU drivers and CUDA are installed.
- Check logs for error messages.

## Contributions

Contributions are welcome! Fork the repo and submit a PR.
