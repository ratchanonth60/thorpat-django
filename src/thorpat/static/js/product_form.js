document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('id_primary_image');
    const imagePreview = document.getElementById('image-preview');
    const uploaderPrompt = document.getElementById('uploader-prompt');
    
    if (imageInput) {
        // We hide the original input and use the label as the trigger
        imageInput.style.display = 'none';

        imageInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file && imagePreview && uploaderPrompt) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.classList.remove('hidden');
                    uploaderPrompt.classList.add('hidden');
                }
                reader.readAsDataURL(file);
            }
        });
        
        // Initial state check for edit page
        if(imagePreview && imagePreview.src && imagePreview.getAttribute('src') && uploaderPrompt) {
             uploaderPrompt.classList.add('hidden');
             imagePreview.classList.remove('hidden');
        } else if (imagePreview && uploaderPrompt) {
             imagePreview.classList.add('hidden');
             uploaderPrompt.classList.remove('hidden');
        }
    }
});
