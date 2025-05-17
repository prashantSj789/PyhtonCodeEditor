import json
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

@csrf_exempt
def run_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            stdin_input = data.get('input', '') + '\n'  # Add newline if missing

            process = subprocess.run(
                ['python3', '-c', code],
                input=stdin_input,
                text=True,  # Handle strings instead of bytes
                capture_output=True,
                timeout=5
            )

            output = process.stdout
            errors = process.stderr

            if process.returncode != 0:
                return JsonResponse({'output': errors or output}, status=400)

            return JsonResponse({'output': output})

        except subprocess.TimeoutExpired:
            return JsonResponse({'output': 'Error: Execution timed out'}, status=408)
        except Exception as e:
            return JsonResponse({'output': f'Error: {str(e)}'}, status=500)

    return JsonResponse({'output': 'Invalid request method'}, status=405)
