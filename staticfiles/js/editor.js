// Helper function to get CSRF token from cookies (for Django POST)
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

let editor;

// Initialize Monaco Editor
window.onload = function() {
  require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.21.2/min/vs' }});
  require(['vs/editor/editor.main'], function() {
    editor = monaco.editor.create(document.getElementById('editor'), {
      value: '# Write your Python code here\nprint("Hello, World!")',
      language: 'python',
      theme: 'vs-light',
      automaticLayout: true,
      minimap: { enabled: false }
    });
  });
};

document.addEventListener('DOMContentLoaded', () => {
  const runButton = document.getElementById('run-button');
  const inputArea = document.getElementById('input');
  const outputArea = document.getElementById('output');

  runButton.addEventListener('click', async () => {
    const code = editor.getValue();
    let input = inputArea.value;
    
    // Ensure input ends with newline if it's not empty
    if (input && !input.endsWith('\n')) {
      input += '\n';
    }

    outputArea.textContent = 'Running...';
    outputArea.style.color = 'black';

    try {
      const response = await fetch('/run/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ 
          code: code, 
          input: input 
        })
      });

      const data = await response.json();
      
      if (!response.ok) {
        outputArea.style.color = 'red';
        outputArea.textContent = data.output || `Error: ${response.statusText}`;
      } else {
        outputArea.textContent = data.output || 'Program executed with no output';
      }
    } catch (error) {
      outputArea.style.color = 'red';
      outputArea.textContent = `Request failed: ${error.message}`;
    }
  });
});