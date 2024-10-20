import os
from django.http import JsonResponse
from django.shortcuts import render
from .forms import CodeFileForm
from huggingface_hub import InferenceClient
from django.conf import settings

def upload_code(request):
    if request.method == 'POST':
        form = CodeFileForm(request.POST, request.FILES)
        if form.is_valid():
            code_file = form.save()

            # Read the uploaded code file
            with open(code_file.file.path, 'r') as file:
                code_content = file.read()

            # Initialize Hugging Face Inference Client
            client = InferenceClient(api_key=os.getenv("HUGGINGFACE_API_KEY"))

            # Set up the input messages (change 'role' or content as per your requirement)
            messages = [{"role": "user", "content": f"Explain the following code:\n{code_content}"}]

            try:
                # Make the API call to Mistral-7B model
                response_content = ""
                for message in client.chat_completion(
                    model="mistralai/Mistral-7B-Instruct-v0.3",
                    messages=messages,
                    max_tokens=500,
                    stream=True,
                ):
                    response_content += message.choices[0].delta.content

                # Return the response in JSON format
                return JsonResponse({'result': response_content}, status=200)

            except Exception as e:
                # Handle any API errors
                return JsonResponse({'error': 'Error with Hugging Face API', 'details': str(e)}, status=500)

    else:
        form = CodeFileForm()

    return render(request, 'upload.html', {'form': form})