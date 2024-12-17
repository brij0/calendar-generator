from datetime import datetime, timedelta
from langchain_groq import ChatGroq  # type: ignore
from langchain_core.prompts import PromptTemplate  # type: ignore
import fitz  # type: ignore
from groq import Groq  # type: ignore
import os
import io 
from PIL import Image
from dotenv import load_dotenv
import re
from datetime import datetime
import time
import tiktoken # type: ignore
import base64

# from ollama import OllamaModel  # type: ignore

def invoke_llm(content):
    # Load environment variables for API key
    load_dotenv()

    # Initialize the LLM (LLaMA 3.2 model)
    llm = ChatGroq(
        temperature=0,
        groq_api_key=os.getenv('GROQ_API_KEY'),  # API key loaded from environment variable
        model_name="llama3-70b-8192"
    )
    
    response = llm.invoke(content)
    return response.content

def summarize_image(image_path):
    load_dotenv()
    base64_image = encode_image(image_path)
    client = Groq(api_key=os.getenv('groq_api_key1'))

    chat_completion = client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analyze the attached image and provide a concise summary of all key elements or information it conveys. "
                            "List important details in short bullet points or a brief paragraph. "
                            "Avoid adding extraneous headings like 'Summary of the Image' or final concluding statements. "
                            "Focus solely on the essential content depicted in the image. "
                            "Keep the description succinct yet thorough."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
    )
    return chat_completion.choices[0].message.content


def clean_text(text):
    # Ensure the text is encoded in UTF-8 and decoded back to a string
    encoded_text = text.encode('utf-8', errors='ignore')
    utf8_text = encoded_text.decode('utf-8', errors='ignore')

    # Optionally replace ligatures or unsupported characters
    utf8_text = utf8_text.replace("\ufb01", "fi").replace("\ufb02", "fl")

    # Clean up the text by removing excessive newlines and spaces
    cleaned_text = utf8_text.replace('\n', ' ').replace('\r', '').strip()

    return cleaned_text


def encode_image(image_path):
    
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def extract_lecture_content(file_path):
    # Open the PDF file
    doc = fitz.open(file_path)
    lecture_content = []

    for page_num in (range(len(doc)-1)):
        print(f"Processing page {page_num+1}..." + "\n")
        page = doc.load_page(page_num + 1)
        image_list = page.get_images(full=True)

        if image_list:
            print(f"Found {len(image_list)} image(s) on {page_num + 1} page." + "\n")
            # If there are multiple images on this page, process each one
            for img_index, img_info in enumerate(image_list, start=1):
                # xref is the image reference inside the PDF
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                # Convert raw image bytes to a PIL Image
                pil_image = Image.open(io.BytesIO(image_bytes))
                
                # Save the image to disk if you want a local file
                image_path = f"image_page{page_num+1}_{img_index}.png"
                pil_image.save(image_path)

                # Summarize this image (assuming summarize_image() is defined)
                image_summary = summarize_image(image_path)
                lecture_content.append(image_summary)
                print(f"Image summary for page {page_num+1}, image {img_index}:", image_summary)
                continue

        else:
            # If no images on this page, extract text instead
            text = page.get_text()
            cleaned_text = clean_text(text)  # assuming you have clean_text() function
            lecture_content.append(cleaned_text)

    doc.close()
    return lecture_content



if __name__ == "__main__":

    # Extract lecture content from a PDF file
    content = extract_lecture_content("Course Content\ENGG_4450\Lec03 Semiconductors Ch3.pdf")
    print(content, "\n")
    print(len(content))