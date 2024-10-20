import os
from django.http import JsonResponse
from django.shortcuts import render
from .forms import CodeFileForm
from huggingface_hub import InferenceClient
from django.conf import settings

from django.shortcuts import redirect

def upload_code(request):
    if request.method == 'POST':
        form = CodeFileForm(request.POST, request.FILES)
        if form.is_valid():
            code_file = form.save()

            # Read the uploaded code file
            with open(code_file.file.path, 'r') as file:
                code_content = file.read()

            # Save the code content to the session
            request.session['code_content'] = code_content
            request.session['conversation_history'] = []  # Initialize conversation history

            # Redirect to the chat page after successful upload
            return redirect('chat_page')

    else:
        form = CodeFileForm()

    return render(request, 'upload.html', {'form': form})

def chat_page(request):
    # Ensure the code content is available in the session
    if 'code_content' not in request.session:
        return redirect('upload_code')  # Redirect to upload page if no code file has been uploaded
    
    return render(request, 'chat.html')  # Render the chat page template

def chat_with_model(request):
    if request.method == 'POST':
        user_question = request.POST.get('question')

        # Retrieve the code content and conversation history from the session
        code_content = request.session.get('code_content')
        conversation_history = request.session.get('conversation_history', [])

        # Append the user's new question to the conversation history
        conversation_history.append({"role": "user", "content": user_question})

        # Include the code content as context for the first message
        if len(conversation_history) == 1:  # first question
            conversation_history.insert(0, {"role": "system", "content": f"Here is the code you will discuss:\n{code_content}"})

        # Initialize Hugging Face Inference Client
        client = InferenceClient(api_key=settings.HUGGINGFACE_API_KEY)

        try:
            # Make the API call to the model with the conversation history
            response_content = ""
            for message in client.chat_completion(
                model="mistralai/Mistral-7B-Instruct-v0.3",
                messages=conversation_history,
                max_tokens=500,
                stream=True,
            ):
                response_content += message.choices[0].delta.content

            # Add the model's response to the conversation history
            conversation_history.append({"role": "assistant", "content": response_content})

            # Save the updated conversation history to the session
            request.session['conversation_history'] = conversation_history

            return JsonResponse({'result': response_content}, status=200)

        except Exception as e:
            return JsonResponse({'error': 'Error with Hugging Face API', 'details': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method. Only POST is allowed.'}, status=405)
