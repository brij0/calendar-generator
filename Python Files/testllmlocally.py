from transformers import AutoProcessor, AutoModelForImageTextToText

processor = AutoProcessor.from_pretrained("meta-llama/Llama-3.2-11B-Vision-Instruct")
model = AutoModelForImageTextToText.from_pretrained("meta-llama/Llama-3.2-11B-Vision-Instruct")

# classifier = pipeline('sentiment-analysis')
# print(classifier(['We are very happy to show you the 🤗 Transformers library.', 'I hate my life']))


# response = ollama.chat (
#     model="llama3.2-vision",
#     messages=[{
#         "role": "user",
#         "content": "Hello, how can I assist you today?"
#         # "images: [Course Content/ENGG_4450/testing.png]"
#     }]
# )

# print(response)





# model_name = "meta-llama/llama3.2"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name)

# model.save_pretrained("./llama3_model")
# tokenizer.save_pretrained("./llama3_tokenizer")

# # Load the model and tokenizer
# model_name = "./llama3_model"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModelForCausalLM.from_pretrained(model_name)

# # Set the model to evaluation mode and move it to GPU
# model.eval()
# model.to('cuda')

# # Function to generate text
# def generate_text(prompt):
#     inputs = tokenizer(prompt, return_tensors="pt").to('cuda')
#     outputs = model.generate(inputs.input_ids, max_length=50)
#     return tokenizer.decode(outputs[0], skip_special_tokens=True)

# # Example usage
# prompt = "Hello, how can I assist you today?"
# print(generate_text(prompt))