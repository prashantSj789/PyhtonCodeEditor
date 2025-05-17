import json
import subprocess
import uuid
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings

def home(request):
    return render(request, 'index.html')

@csrf_exempt
def run_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            stdin_input = data.get('input', '') + '\n'

            # Write the code to a temporary file
            filename = f"/tmp/{uuid.uuid4().hex}.py"
            with open(filename, 'w') as f:
                f.write(code)

            # Run the code
            process = subprocess.run(
                ['python3', filename],
                input=stdin_input,
                text=True,
                capture_output=True,
                timeout=5
            )

            output = process.stdout
            errors = process.stderr

            # Run pylint for warnings
            pylint_process = subprocess.run(
                ['pylint', filename, '--disable=all', '--enable=E,W,C,R', '--output-format=json'],
                capture_output=True,
                text=True
            )

            try:
                pylint_output = json.loads(pylint_process.stdout)
                warnings = [
                    {
                        'type': msg['type'],
                        'line': msg['line'],
                        'message': msg['message'],
                        'symbol': msg['symbol']
                    }
                    for msg in pylint_output
                ]
            except json.JSONDecodeError:
                warnings = [{'type': 'error', 'message': 'Pylint failed to parse output'}]

            # Clean up the temp file
            os.remove(filename)

            if process.returncode != 0:
                return JsonResponse({'output': errors or output, 'warnings': warnings}, status=400)

            return JsonResponse({'output': output, 'warnings': warnings})

        except subprocess.TimeoutExpired:
            return JsonResponse({'output': 'Error: Execution timed out'}, status=408)
        except Exception as e:
            return JsonResponse({'output': f'Error: {str(e)}'}, status=500)

    return JsonResponse({'output': 'Invalid request method'}, status=405)
