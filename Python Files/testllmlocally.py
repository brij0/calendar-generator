from json import load
from dotenv import load_dotenv
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoConfig, AutoModelForCausalLM

# Load model directly
from transformers import AutoProcessor, AutoModelForImageTextToText
load_dotenv()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu") 

model = AutoModelForImageTextToText.from_pretrained("meta-llama/Llama-3.2-11B-Vision-Instruct")

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-11B-Vision-Instruct")

input = tokenizer("she is ", return_tensors="pt").to(device)

print(input)