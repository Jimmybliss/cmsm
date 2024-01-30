// static/js/click_event.js

//logout function
function logout() {
    // Implement logic to log out the technician
    alert("Logout clicked");
}

//Buttons option in the technician dashboard
function assignAnother() {
    // Implement logic to assign the work to another technician
    alert("Assign Another clicked");
}

function markInProgress() {
    // Implement logic to indicate that the job is in progress
    alert("In Progress clicked");
}

function markFinished() {
    // Implement logic to conclude the work and notify the customer
    alert("Finished clicked");
}


//redirect on button click
function redirectToCheckStatus() {
    // Use Flask's url_for to generate the URL for the 'customer' route
    var checkstatusUrl = "{{ url_for('customer-login') }}";

    // Redirect to the customer URL
    window.location.href = checkstatusUrl;
}

// Attach the click event to the button
document.getElementById('check-status').addEventListener('click', redirectToCheckStatus);


function redirectToCreateServiceRequest() {
    // Use Flask's url_for to generate the URL for the 'customer' route
    var createservicerequestUrl = "{{ url_for('customer-login') }}";

    // Redirect to the customer URL
    window.location.href = createservicerequestUrl;
}

// Attach the click event to the button
document.getElementById('check-service-request').addEventListener('click', redirectToCreateServiceRequest);



