// Fallback Map Implementation using Coordinate Picker (no API key required)
// This is a simplified version that works without Google Maps API key

function initSimpleMap(mapType, container, latField, lngField) {
    const DEFAULT_LAT = 40.7128;
    const DEFAULT_LNG = -74.0060;
    
    // Get initial values from hidden fields
    let currentLat = (latField && latField.value) ? parseFloat(latField.value) : DEFAULT_LAT;
    let currentLng = (lngField && lngField.value) ? parseFloat(lngField.value) : DEFAULT_LNG;
    
    // Style the container
    container.style.backgroundColor = '#f9f9f9';
    container.style.padding = '20px';
    container.style.borderRadius = '4px';
    container.style.border = '1px solid #e0e0e0';
    
    // Create form for coordinate entry
    const formHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div>
                <label style="display: block; font-size: 12px; font-weight: 600; margin-bottom: 5px; color: #333;">
                    Latitude
                </label>
                <input type="number" class="form-control coordinates-lat" 
                       placeholder="40.7128" step="0.0001" 
                       value="${currentLat}" 
                       style="font-size: 13px; padding: 8px; font-family: monospace;">
                <small style="display: block; color: #999; margin-top: 3px;">-90 to 90</small>
            </div>
            <div>
                <label style="display: block; font-size: 12px; font-weight: 600; margin-bottom: 5px; color: #333;">
                    Longitude
                </label>
                <input type="number" class="form-control coordinates-lng" 
                       placeholder="-74.0060" step="0.0001" 
                       value="${currentLng}" 
                       style="font-size: 13px; padding: 8px; font-family: monospace;">
                <small style="display: block; color: #999; margin-top: 3px;">-180 to 180</small>
            </div>
        </div>
        <div style="margin-top: 12px;">
            <p style="margin: 0; font-size: 11px; color: #666; text-align: center;">
                📍 Need to find coordinates? 
                <a href="https://www.openstreetmap.org/" target="_blank" 
                   style="color: #007bff; text-decoration: none; font-weight: 500;">
                   OpenStreetMap
                </a>
                or
                <a href="https://www.google.com/maps" target="_blank" 
                   style="color: #007bff; text-decoration: none; font-weight: 500;">
                   Google Maps
                </a>
            </p>
        </div>
        <div style="margin-top: 10px; padding: 10px; background-color: #e3f2fd; border-radius: 4px; border-left: 3px solid #2196F3;">
            <small style="color: #1565c0; display: block;">
                💡 <strong>Tip:</strong> Right-click any location on a map to copy coordinates
            </small>
        </div>
    `;
    
    container.innerHTML = formHTML;
    
    // Get input elements
    const latInput = container.querySelector('.coordinates-lat');
    const lngInput = container.querySelector('.coordinates-lng');
    
    // Function to update hidden fields
    const updateHiddenFields = () => {
        const lat = latInput.value ? parseFloat(latInput.value) : '';
        const lng = lngInput.value ? parseFloat(lngInput.value) : '';
        
        if (latField) latField.value = lat;
        if (lngField) lngField.value = lng;
        
        // Log for debugging
        console.log(`[${mapType}] Updated coordinates: ${lat}, ${lng}`);
    };
    
    // Update on input events
    latInput.addEventListener('input', updateHiddenFields);
    lngInput.addEventListener('input', updateHiddenFields);
    latInput.addEventListener('change', updateHiddenFields);
    lngInput.addEventListener('change', updateHiddenFields);
    
    // Initial update
    updateHiddenFields();
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMaps);
} else {
    initMaps();
}

function initMaps() {
    const requesterLatField = document.getElementById('id_requester-latitude');
    const requesterLngField = document.getElementById('id_requester-longitude');
    const requestLatField = document.getElementById('id_request-latitude');
    const requestLngField = document.getElementById('id_request-longitude');
    
    const requesterMapContainer = document.getElementById('map-container-requester');
    if (requesterMapContainer) {
        initSimpleMap('requester', requesterMapContainer, requesterLatField, requesterLngField);
    }
    
    const requestMapContainer = document.getElementById('map-container-request');
    if (requestMapContainer) {
        initSimpleMap('request', requestMapContainer, requestLatField, requestLngField);
    }
}

// Also reinitialize after a short delay to handle dynamic content
setTimeout(() => {
    if (document.getElementById('map-container-requester') && 
        !document.querySelector('.coordinates-lat')) {
        initMaps();
    }
}, 500);
