// static/js/upload.js
document.addEventListener('DOMContentLoaded', () => {
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('fileInput');
  const uploadBtn = document.getElementById('uploadBtn');
  const progressContainer = document.getElementById('progressContainer');

  if (!dropZone) {
    console.error('dropZone element not found');
    return;  // Early exit to prevent errors if element is missing
  }

  // Trigger file input on dropZone click
  dropZone.addEventListener('click', () => fileInput.click());

  // Prevent default drag behaviors
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  // Highlight drop zone on drag enter/over
  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.add('border-primary'), false);  // Use Bootstrap class for highlight
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => dropZone.classList.remove('border-primary'), false);
  });

  // Handle dropped files
  dropZone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    fileInput.files = files;  // Sync with input for consistency
    handleFiles(files);
  });

  // Handle selected files
  fileInput.addEventListener('change', (e) => {
    const files = e.target.files;
    handleFiles(files);
  });

  function handleFiles(files) {
    progressContainer.innerHTML = '';
    Array.from(files).forEach(file => {
      const progressBar = createProgressBar(file.name);
      progressContainer.appendChild(progressBar);
    });
  }

  function createProgressBar(filename) {
    const div = document.createElement('div');
    div.className = 'progress mt-2';
    div.innerHTML = `
      <div class="progress-bar" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0% - ${filename}</div>
    `;
    return div;
  }

  uploadBtn.addEventListener('click', () => {
    const files = fileInput.files;
    if (files.length === 0) {
      alert('No files selected');
      return;
    }
    Array.from(files).forEach((file, index) => {
      fetch('/get-sas-url/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: file.name })
      })
      .then(response => response.json())
      .then(data => {
        if (data.sasUrl) {
          uploadFile(file, data.sasUrl, index);
        } else {
          console.error('Error getting SAS URL:', data.error);
        }
      })
      .catch(error => console.error('Error:', error));
    });
  });

  function uploadFile(file, sasUrl, index) {
    const xhr = new XMLHttpRequest();
    xhr.open('PUT', sasUrl, true);
    // Required headers for Azure Blob PUT
    xhr.setRequestHeader('x-ms-blob-type', 'BlockBlob');
    xhr.setRequestHeader('x-ms-version', '2023-11-03');
    xhr.setRequestHeader('Content-Length', file.size);
    xhr.setRequestHeader('x-ms-date', new Date().toUTCString());
    // Optional but recommended
    xhr.setRequestHeader('Content-Type', file.type || 'application/octet-stream');
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        const percentComplete = (e.loaded / e.total) * 100;
        const progressBar = progressContainer.children[index].querySelector('.progress-bar');
        progressBar.style.width = percentComplete + '%';
        progressBar.setAttribute('aria-valuenow', percentComplete);
        progressBar.textContent = percentComplete.toFixed(2) + '% - ' + file.name;
      }
    };
    xhr.onload = () => {
      if (xhr.status === 201) {
        console.log('File uploaded successfully');
        const progressBar = progressContainer.children[index].querySelector('.progress-bar');
        progressBar.classList.add('bg-success');
      } else {
        console.error('Upload failed:', xhr.statusText);
      }
    };
    xhr.onerror = () => console.error('Upload error');
    xhr.send(file);
  }
});