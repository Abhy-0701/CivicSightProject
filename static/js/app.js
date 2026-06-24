// Photo capture
const cameraBtn = document.getElementById('camera-btn');
const photoInput = document.getElementById('photo-input');
const photoPreview = document.getElementById('photo-preview');
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
let photoBlob = null;

cameraBtn.addEventListener('click', async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' }
        });
        video.srcObject = stream;
        video.hidden = false;

        setTimeout(() => {
            const ctx = canvas.getContext('2d');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0);

            canvas.toBlob(blob => {
                photoBlob = blob;
                photoPreview.src = canvas.toDataURL();
                photoPreview.hidden = false;
                video.hidden = true;
                stream.getTracks().forEach(track => track.stop());
                cameraBtn.textContent = 'OK Photo Captured';
            });
        }, 100);
    } catch (err) {
        showError('Camera access denied or not available');
    }
});

// Fallback: File upload
photoInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            photoPreview.src = event.target.result;
            photoPreview.hidden = false;

            file.slice().arrayBuffer().then(buffer => {
                photoBlob = new Blob([buffer], { type: file.type });
            });

            cameraBtn.textContent = 'OK Photo Uploaded';
        };
        reader.readAsDataURL(file);
    }
});

// Geolocation
const locationBtn = document.getElementById('location-btn');
locationBtn.addEventListener('click', () => {
    if (navigator.geolocation) {
        locationBtn.textContent = 'Getting location...';
        navigator.geolocation.getCurrentPosition(
            (position) => {
                document.getElementById('latitude').value = position.coords.latitude.toFixed(6);
                document.getElementById('longitude').value = position.coords.longitude.toFixed(6);
                locationBtn.textContent = 'OK Location Found';
            },
            (error) => {
                showError('Could not get location. Enter manually. Error: ' + error.message);
                locationBtn.textContent = 'Get My Location';
            }
        );
    } else {
        showError('Geolocation not supported by this browser');
    }
});

// Submit for analysis
const submitBtn = document.getElementById('submit-btn');
submitBtn.addEventListener('click', async () => {
    if (!photoBlob) {
        showError('Please capture or upload a photo');
        return;
    }

    const lat = parseFloat(document.getElementById('latitude').value);
    const lng = parseFloat(document.getElementById('longitude').value);

    if (isNaN(lat) || isNaN(lng)) {
        showError('Please enter valid latitude and longitude');
        return;
    }

    // Convert image to base64
    const reader = new FileReader();
    reader.onload = async (e) => {
        try {
            submitBtn.disabled = true;
            document.getElementById('loading-spinner').hidden = false;

            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: e.target.result,
                    latitude: lat,
                    longitude: lng
                })
            });

            const result = await response.json();
            document.getElementById('loading-spinner').hidden = true;

            if (result.success) {
                displayReview(result.report);
                document.getElementById('capture-form').hidden = true;
                document.getElementById('review-section').hidden = false;
            } else {
                showError(result.error || 'Analysis failed');
                submitBtn.disabled = false;
            }
        } catch (err) {
            showError('Analysis failed: ' + err.message);
            document.getElementById('loading-spinner').hidden = true;
            submitBtn.disabled = false;
        }
    };
    reader.readAsDataURL(photoBlob);
});

function displayReview(report) {
    document.getElementById('review-address').textContent =
        report.location.full_address || 'Address not found';
    document.getElementById('review-issue').textContent =
        report.vision_analysis.issue_type || 'Unknown';
    document.getElementById('review-severity').textContent =
        report.vision_analysis.severity || 'Unknown';

    const authority = report.authority && report.authority.responsible_authority
        ? report.authority.responsible_authority
        : 'Unknown';
    document.getElementById('review-authority').textContent = authority;

    const confidence = report.vision_analysis.confidence_score
        ? (report.vision_analysis.confidence_score * 100).toFixed(0)
        : 'N/A';
    document.getElementById('review-confidence').textContent = confidence + '%';

    document.getElementById('description-text').value =
        report.vision_analysis.description || 'No description available';

    window.currentReport = report;
}

// Edit description
const editBtn = document.getElementById('edit-btn');
editBtn.addEventListener('click', function() {
    const descTextarea = document.getElementById('description-text');

    if (descTextarea.disabled) {
        descTextarea.disabled = false;
        descTextarea.focus();
        editBtn.textContent = 'OK Done Editing';
    } else {
        descTextarea.disabled = true;
        editBtn.textContent = 'Edit';
    }
});

// Confirm and create ticket
const confirmBtn = document.getElementById('confirm-btn');
confirmBtn.addEventListener('click', async () => {
    try {
        confirmBtn.disabled = true;
        document.getElementById('loading-spinner').hidden = false;

        // Get updated description if user edited it
        const updatedDescription = document.getElementById('description-text').value;
        window.currentReport.vision_analysis.description = updatedDescription;

        const response = await fetch('/api/ticket/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                report: window.currentReport,
                latitude: window.currentReport.location.latitude ||
                          parseFloat(document.getElementById('latitude').value),
                longitude: window.currentReport.location.longitude ||
                           parseFloat(document.getElementById('longitude').value),
                image: canvas.toDataURL()
            })
        });

        const result = await response.json();
        document.getElementById('loading-spinner').hidden = true;

        if (result.success) {
            document.getElementById('ticket-id-display').textContent = result.ticket_id;
            document.getElementById('review-section').hidden = true;
            document.getElementById('success-section').hidden = false;
        } else {
            showError('Ticket creation failed: ' + (result.error || 'Unknown error'));
            confirmBtn.disabled = false;
        }
    } catch (err) {
        showError('Error: ' + err.message);
        document.getElementById('loading-spinner').hidden = true;
        confirmBtn.disabled = false;
    }
});

// Report another issue
const newReportBtn = document.getElementById('new-report-btn');
newReportBtn.addEventListener('click', () => {
    location.reload();
});

function showError(message) {
    const errorBox = document.getElementById('error-message');
    errorBox.textContent = message;
    errorBox.hidden = false;
    setTimeout(() => { errorBox.hidden = true; }, 6000);
}
