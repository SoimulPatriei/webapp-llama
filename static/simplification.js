function llamaSimplifyText() { 
  const inputText = document.getElementById('inputText').value;

  // Show the spinner when simplification starts
  showSpinner();

  fetch('http://mavs.hpc.ut.ee:5000/llama_simplify', {  // Llama Simplification
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ text: inputText })
  })
  .then(response => response.json())
  .then(data => {
    console.log('Success:', data);

    // Update the output text with automatic simplification
    const outputText = document.getElementById('outputText');
    outputText.value = data.translation;
    outputText.dataset.original = data.translation; // Store original simplification for reference
    outputText.setAttribute('readonly', true); // Ensure it starts as readonly

    // Hide the spinner
    hideSpinner();
  })
  .catch((error) => {
    console.error('Error:', error);

    // Show error in the output and hide the spinner
    const outputText = document.getElementById('outputText');
    outputText.value = "Error occurred: " + error;
    hideSpinner();
  });
}

function enableEditing() {
  const outputText = document.getElementById('outputText');
  outputText.removeAttribute('readonly'); // Enable editing
  outputText.focus();
  document.getElementById('saveButton').style.display = 'inline-block'; // Show save button
}

function saveEditedSimplification() {
  const outputText = document.getElementById('outputText');
  const editedText = outputText.value;
  const originalText = outputText.dataset.original;
  const originalSentence = document.getElementById('inputText').value;

  // Save the edited text along with the original sentence, simplification, and IP address
  fetch('/save_simplification', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      original_sentence: originalSentence,
      original: originalText,
      edited: editedText
    })
  })
  .then(response => response.json())
  .then(data => {
    console.log('Save success:', data);

    // Notify user and reset the UI
    alert('Simplification saved successfully.\n Thank you for your contribution! ');
    outputText.setAttribute('readonly', true);
    document.getElementById('saveButton').style.display = 'none';
  })
  .catch(error => {
    console.error('Save error:', error);
    alert('Error saving simplification.');
  });
}

