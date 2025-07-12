import google.generativeai as genai
# from PIL import Image
# image = Image.open("image.png")
# print(image.size)

genai.configure(api_key="AIzaSyBTnIxeeI2IbOdlxbG1trcbZOMvxQ946cA")

models = genai.list_models()
print("Available models:")
for model in models:
    # print(model.name, "-", model.supported_generation_methods)
    if 'generateContent' in model.supported_generation_methods:
        print(f"'{model.name}',")


