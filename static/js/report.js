document.addEventListener('DOMContentLoaded', function() {
    // Handle file input previews
    const imageInputs = document.querySelectorAll('input[type="file"]');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            // Check file type
            if (!file.type.match('image.*')) {
                alert('Please select an image file (JPG, PNG)');
                e.target.value = '';
                return;
            }
            
            // Check file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('File is too large. Maximum size is 5MB.');
                e.target.value = '';
                return;
            }
            
            // Get the preview container ID based on the input ID
            const inputId = e.target.id;
            const previewId = inputId + '_preview';
            const previewContainer = document.getElementById(previewId);
            
            if (previewContainer) {
                // Clear previous preview
                previewContainer.innerHTML = '';
                
                // Create image preview
                const img = document.createElement('img');
                img.classList.add('img-thumbnail', 'mt-2');
                img.style.maxHeight = '150px';
                
                // Create file reader to read the image
                const reader = new FileReader();
                reader.onload = function(event) {
                    img.src = event.target.result;
                };
                reader.readAsDataURL(file);
                
                // Add image and remove button to preview container
                previewContainer.appendChild(img);
                
                // Add remove button
                const removeBtn = document.createElement('button');
                removeBtn.textContent = 'Remove';
                removeBtn.classList.add('btn', 'btn-sm', 'btn-danger', 'mt-1');
                removeBtn.addEventListener('click', function() {
                    previewContainer.innerHTML = '';
                    e.target.value = '';
                });
                previewContainer.appendChild(removeBtn);
            }
        });
    });
    
    // Form validation
    const reportForm = document.getElementById('report-form');
    if (reportForm) {
        reportForm.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Check if at least one image is uploaded
            const hasImage = Array.from(imageInputs).some(input => input.files.length > 0);
            
            if (!hasImage) {
                alert('Please upload at least one image of the waste');
                isValid = false;
            }
            
            // Check if title is filled
            const title = document.getElementById('title');
            if (title && title.value.trim() === '') {
                alert('Please enter a title for the report');
                isValid = false;
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    }
    
    // Display image gallery for reports
    const reportGalleries = document.querySelectorAll('.report-gallery');
    reportGalleries.forEach(gallery => {
        const images = gallery.querySelectorAll('img');
        const mainImage = gallery.querySelector('.main-image');
        
        // Set click events for thumbnails
        images.forEach(img => {
            img.addEventListener('click', function() {
                // Update main image
                if (mainImage) {
                    mainImage.src = this.src;
                }
                
                // Update active thumbnail
                images.forEach(i => i.classList.remove('active'));
                this.classList.add('active');
            });
        });
    });
});
