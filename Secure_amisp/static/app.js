// app.js

// The base URL for the Flask API endpoints
const API_BASE_URL = 'http://127.0.0.1:8000/api'; 

// --- General Functions ---

function openTab(tabName) {
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(content => content.classList.remove('active'));

    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(button => button.classList.remove('active'));

    document.getElementById(tabName).classList.add('active');
    document.querySelector(`.tab-menu button[onclick="openTab('${tabName}')"]`).classList.add('active');
}

function updateAuditLog(url, headers, body, status, data) {
    document.getElementById('lastUrl').textContent = url;
    document.getElementById('lastHeaders').textContent = JSON.stringify(headers);
    document.getElementById('lastBody').textContent = JSON.stringify(body);
    
    const statusSpan = document.getElementById('lastStatus');
    statusSpan.textContent = status;
    statusSpan.className = (status >= 200 && status < 300) ? '' : 'error';
    
    document.getElementById('lastData').textContent = JSON.stringify(data, null, 2);
}

// Main function to handle all API requests
// CHANGED: apiKey parameter is now vendorId
async function sendRequest(endpoint, method, vendorId, body, responseElementId) {
    const url = API_BASE_URL + endpoint;
    
    // CHANGED: Set X-Vendor-ID header instead of X-API-Key
    const headers = {
        'Content-Type': 'application/json',
        'X-Vendor-ID': vendorId
    };
    
    const responseElement = document.getElementById(responseElementId);
    responseElement.textContent = 'Sending request...';

    let responseData = {};
    let responseStatus = 0;

    try {
        const response = await fetch(url, {
            method: method,
            headers: headers,
            body: JSON.stringify(body)
        });

        responseStatus = response.status;
        
        // Handle cases where the response might not have a body (e.g., 204 No Content)
        if (responseStatus === 204) {
             responseData = { message: "No Content (204)" };
        } else {
             responseData = await response.json();
        }
        
        // Display the response
        responseElement.textContent = `Status: ${responseStatus}\n${JSON.stringify(responseData, null, 2)}`;
        
    } catch (error) {
        // Handle network or JSON parsing errors
        responseStatus = 'Network Error';
        responseData = { error: error.message };
        responseElement.textContent = `Error: ${error.message}`;
    }

    // Update the Audit Log area
    updateAuditLog(url, headers, body, responseStatus, responseData);
}

// --- Form Handlers ---

document.getElementById('installForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // CHANGED: Read from the new input ID 'install_vendor_id'
    const vendorId = document.getElementById('install_vendor_id').value; 
    const consumerId = document.getElementById('install_consumer_id').value;
    const meterId = document.getElementById('install_meter_id').value;
    
    // Format the date to ISO 8601 string for Flask/Pydantic
    const installDate = new Date(document.getElementById('install_date').value).toISOString(); 

    const body = {
        consumer_id: consumerId,
        meter_id: meterId,
        install_date: installDate
    };
    
    // CHANGED: Pass vendorId
    sendRequest('/install-meter', 'POST', vendorId, body, 'installResponse');
});

document.getElementById('readingForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // CHANGED: Read from the new input ID 'reading_vendor_id'
    const vendorId = document.getElementById('reading_vendor_id').value;
    const meterId = document.getElementById('reading_meter_id').value;
    const readingDatetime = new Date(document.getElementById('reading_datetime').value).toISOString();
    const kwh = parseFloat(document.getElementById('reading_kwh').value);

    const body = {
        meter_id: meterId,
        reading_datetime: readingDatetime,
        kwh: kwh
    };
    
    // CHANGED: Pass vendorId
    sendRequest('/upload-reading', 'POST', vendorId, body, 'readingResponse');
});

document.getElementById('rechargeForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // CHANGED: Read from the new input ID 'recharge_vendor_id'
    const vendorId = document.getElementById('recharge_vendor_id').value;
    const consumerId = document.getElementById('recharge_consumer_id').value;
    const amount = parseFloat(document.getElementById('recharge_amount').value);
    const transactionRef = document.getElementById('recharge_txn_ref').value;

    const minimalBody = {
        consumer_id: consumerId,
        amount: amount,
        transaction_ref: transactionRef
    };
    
    // CHANGED: Pass vendorId
    sendRequest('/recharge', 'POST', vendorId, minimalBody, 'rechargeResponse');
});

document.getElementById('commandForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // CHANGED: Read from the new input ID 'command_vendor_id'
    const vendorId = document.getElementById('command_vendor_id').value;
    const meterId = document.getElementById('command_meter_id').value;
    const commandType = document.getElementById('command_type').value;

    const body = {
        meter_id: meterId,
        command_type: commandType
    };
    
    // CHANGED: Pass vendorId
    sendRequest('/meter-command', 'POST', vendorId, body, 'commandResponse');
});

// Initialize the first tab on load
document.addEventListener('DOMContentLoaded', () => {
    openTab('install-meter');
});
