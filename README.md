# youtube2text

## 專案描述
這是一個用於下載、處理和轉錄影片音訊的專案。此專案使用 `ffmpeg` 進行影片處理，並使用 `whisper` 模型進行音訊轉錄。此外，還使用 Azure OpenAI 進行文本清理。

## 安裝指南

### 使用 Poetry 安裝套件

1. 安裝 [Poetry](https://python-poetry.org/docs/#installation)：
    ```sh
    curl -sSL https://install.python-poetry.org | python3 -
    ```

2. 安裝專案依賴：
    ```sh
    poetry install
    ```

### 安裝 FFmpeg

請依照您的作業系統安裝 FFmpeg：

- **macOS**：
    ```sh
    brew install ffmpeg
    ```

- **Ubuntu**：
    ```sh
    sudo apt update
    sudo apt install ffmpeg
    ```

- **Windows**：
    請參考 [FFmpeg 官網](https://ffmpeg.org/download.html) 下載並安裝。

### 安裝 Whisper

1. 安裝 Whisper：
    ```sh
    pip install git+https://github.com/openai/whisper.git
    ```

## 使用方法

1. 下載並轉錄影片音訊：
    ```python
    download_and_transcribe("影片網址")
    ```

2. 清理文本內容：
    ```python
    clean_context("需要清理的文本")
    ```

## 環境變數設定

請在專案根目錄下創建 [.env](https://learningsky.io/python-use-environmental-variables-to-hide-sensitive-information/) 檔案，並設定以下環境變數：
