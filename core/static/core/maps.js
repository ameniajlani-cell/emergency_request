// Google Maps Integration for Emergency Request Location Selection

let mapInstances = {};
let selectedMarkers = {};

const DEFAULT_LAT = 40.7128;  // Default to New York
const DEFAULT_LNG = -74.0060;

function initMap() {
    // Get the hidden input fields for coordinates
    const requesterLatField = document.getElementById('id_requester-latitude');
    const requesterLngField = document.getElementById('id_requester-longitude');
    const requestLatField = document.getElementById('id_request-latitude');
    const requestLngField = document.getElementById('id_request-longitude');

    // Initialize Requester Map
    const requesterMapContainer = document.getElementById('map-container-requester');
    if (requesterMapContainer) {
        initializeMap('requester', requesterMapContainer, requesterLatField, requesterLngField);
    }

    // Initialize Request Map
    const requestMapContainer = document.getElementById('map-container-request');
    if (requestMapContainer) {
        initializeMap('request', requestMapContainer, requestLatField, requestLngField);
    }
}

function initializeMap(mapType, container, latField, lngField) {
    // Get initial coordinates if available
    let initialLat = (latField && latField.value) ? parseFloat(latField.value) : DEFAULT_LAT;
    let initialLng = (lngField && lngField.value) ? parseFloat(lngField.value) : DEFAULT_LNG;

    // Create map instance
    const mapInstance = new google.maps.Map(container, {
        zoom: 13,
        center: { lat: initialLat, lng: initialLng },
        mapTypeControl: true,
        fullscreenControl: true,
        streetViewControl: false,
    });

    // Create marker at initial location if coordinates exist
    let initialMarker = null;
    if (latField && latField.value && lngField && lngField.value) {
        initialMarker = new google.maps.Marker({
            position: { lat: initialLat, lng: initialLng },
            map: mapInstance,
            title: 'Selected Location',
        });
        selectedMarkers[mapType] = initialMarker;
        updateLocationDisplay(mapType, initialLat, initialLng);
    }

    // Handle map clicks to set marker
    mapInstance.addListener('click', function (event) {
        const lat = event.latLng.lat();
        const lng = event.latLng.lng();

        // Remove previous marker
        if (selectedMarkers[mapType]) {
            selectedMarkers[mapType].setMap(null);
        }

        // Create new marker
        const newMarker = new google.maps.Marker({
            position: { lat: lat, lng: lng },
            map: mapInstance,
            title: 'Selected Location',
            animation: google.maps.Animation.DROP,
        });

        selectedMarkers[mapType] = newMarker;

        // Update hidden fields
        if (latField) latField.value = lat.toFixed(6);
        if (lngField) lngField.value = lng.toFixed(6);

        updateLocationDisplay(mapType, lat, lng);
    });

    // Store map instance
    mapInstances[mapType] = mapInstance;
}

function updateLocationDisplay(mapType, lat, lng) {
    // Create or update location info div
    const mapContainer = mapType === 'requester' 
        ? document.getElementById('map-container-requester') 
        : document.getElementById('map-container-request');
    
    if (mapContainer && mapContainer.parentElement) {
        let infoDiv = mapContainer.parentElement.querySelector('.location-info');
        
        if (!infoDiv) {
            infoDiv = document.createElement('div');
            infoDiv.className = 'location-info alert alert-info mt-2';
            infoDiv.innerHTML = '<strong>Selected Location:</strong> <span id="location-coords"></span>';
            mapContainer.parentElement.insertBefore(infoDiv, mapContainer.nextSibling);
        }
        
        const coordsSpan = infoDiv.querySelector('#location-coords');
        if (coordsSpan) {
            coordsSpan.textContent = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
        }
    }
}

// Initialize map when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMap);
} else {
    initMap();
}

// Reinitialize maps after 500ms to ensure all elements are loaded
setTimeout(initMap, 500);
        if (coordsSpan) {
            coordsSpan.textContent = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
        }
        infoDiv.classList.remove('d-none');


// Initialize map when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    initMap();
});

// Handle form submission - ensure coordinates are captured
document.addEventListener('submit', function (e) {
    if (e.target.dataset.validate === 'emergency') {
        if (selectedMarker) {
            const position = selectedMarker.getPosition();
            if (requesterLatField) requesterLatField.value = position.lat();
            if (requesterLngField) requesterLngField.value = position.lng();
            if (requestLatField) requestLatField.value = position.lat();
            if (requestLngField) requestLngField.value = position.lng();
        }
    }
});
