import os
import warnings
import concurrent.futures
import ffmpeg
import whisper
import yt_dlp

from dotenv import load_dotenv
from tqdm import tqdm
from openai import AzureOpenAI

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")


def download(url: str) -> None:
    # 設定下載選項
    ydl_opts = {
        'format': 'best',  # 選擇最佳格式
        'outtmpl': '%(title)s.%(ext)s',  # 設定下載檔案名稱
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def process_segment(i, input_file, segment_duration, output_file_template):
    start_time = i * segment_duration
    output_file = f'./audio/{output_file_template.format(i)}'
    ffmpeg.input(input_file, ss=start_time, t=segment_duration).output(output_file, acodec='pcm_s16le', ac=1, ar='16000').overwrite_output().run(quiet=False)

def process_video_segments(input_file, segment_duration=600):
    output_file_template = "audio_cut_{}.wav"

    # 獲取影片總時長
    probe = ffmpeg.probe(input_file)
    duration = float(probe['format']['duration'])

    # 計算分割數量
    num_segments = int(duration // segment_duration) + 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_segment, i, input_file, segment_duration, output_file_template) for i in range(num_segments)]
        for future in concurrent.futures.as_completed(futures):
            future.result()

def transcribe_audio_files():
    model = whisper.load_model("turbo")
    file_list = []
    for i in os.walk("./audio"):
        for j in i[2]:
            file_list.append(os.path.join(i[0], j))
    sorted_file_list = sorted(file_list, key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split('_')[-1]))
    with open("transcript.txt", "w") as f:
        for i in tqdm(sorted_file_list, desc="Transcribing"):
            result = model.transcribe(i, language='Chinese')
            text = result["text"]
            f.write(f"{text.strip()}\n")
            f.flush()
            os.remove(i)

def download_and_transcribe(url):
    download(url)
    process_video_segments("video.mp4")
    transcribe_audio_files()

def clean_context(context: str) -> str:
    load_dotenv()
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
        api_version="2024-10-01-preview",
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    
    deployment = 'gpt4o'
    chat_prompt = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "請幫我加上標點符號，並移除不重要的文本，回應請使用繁體中文。"
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": context
                }
            ]
        }
    ]

    # 產生完成  
    completion = client.chat.completions.create(  
        model=deployment,
        messages=chat_prompt,
        max_tokens=4096,
        temperature=0.7
    )
    return completion.choices[0].message.content

def clean_contexts() -> list:
    context_list = []
    with open("transcript.txt", "r") as f:
        index = 1
        for i in f.readlines():
            try:
                context = clean_context(i)
            except Exception as e:
                print(f"index {index} Error: {e}")
                continue
            context_list.append(context)
    for i in context_list:
        with open("clean_transcript.txt", "a") as f:
            f.write(f"{i}\n")

if __name__ == "__main__":
    url = 'https://www.youtube.com/watch?v=21WCOWCK3lQ'
    download_and_transcribe(url)
    clean_contexts()
