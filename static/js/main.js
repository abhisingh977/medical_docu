let startYear = 1900;
let endYear = new Date().getFullYear();
let defaultStartYear = 1984;
let defaultEndYear = new Date().getFullYear();
let optionsStart = "";
let optionsEnd = "";

for (let year = startYear; year <= endYear; year++) {
    optionsStart += "<option" + (year === defaultStartYear ? " selected" : "") + ">" + year + "</option>";
    optionsEnd += "<option" + (year === defaultEndYear ? " selected" : "") + ">" + year + "</option>";
}

document.getElementById("start-year").innerHTML = optionsStart;
document.getElementById("end-year").innerHTML = optionsEnd;

// Add event listener to the button click
document.getElementById("click").addEventListener("click", function(event) {
    const startYear = parseInt(document.getElementById("start-year").value);
    const endYear = parseInt(document.getElementById("end-year").value);

    if (endYear < startYear) {
        event.preventDefault(); // Prevent default button behavior
        alert("Invalid year range. End year cannot be less than start year.");
        return;
    }
});

// Global variable to store selected options
var selectedOptions = [];

// Apply button click event using jQuery
$('#apply-btn').on('click', function() {
    console.log('Apply button clicked');
    // Get selected checkbox values
    selectedOptions = $('input[type=checkbox]:checked').map(function() {
        console.log(this.id);
        return this.id;
    }).get();

    // You can display a message or update the UI to show that options are applied
    console.log("Options applied:", selectedOptions);

    // Hide the filter options
    $('#filter-options').hide();
});

// JavaScript to toggle the visibility of the filter options using jQuery
$('#filter-btn').on('click', function() {
    $('#filter-options').toggle();
});

function sendRequests2() {
    // Get user input
    $('#loadingIndicator').show();
    var userInput = $('#userInput').val();
    var strat_year = $('#start-year').val();
    var end_year = $('#end-year').val();
    var specialization_name = 'gynecology'
    var api1Completed = false;
    var api2Completed = false;

    // Make a request to API 1 with user input
    $.get('/llm', { input: userInput, specialization: specialization_name }, function(api1Data) {
        // Display API 1 response to the user

        $('#llmResponse').text(api1Data.data);
        toggleResultsBox1(api1Data.data)
        api1Completed = true
        if (api2Completed) {
            sendHtmlContentToServer();
        }
    });

    // Make a request to API 2 with user input
    $.get('/search2', { input: userInput, sy: strat_year, ey: end_year, options: selectedOptions.join(',') }, function(api3Data) {
        $('#loadingIndicator').hide();

        displayApi2Results(api3Data);
        toggleResultsBox2(api3Data.data);
        api2Completed = true
        if (api1Completed) {
            sendHtmlContentToServer();
        }
    });
}


function sendRequests() {
    // Get user input
    $('#loadingIndicator').show();
    var userInput = $('#userInput').val();
    var strat_year = $('#start-year').val();
    var end_year = $('#end-year').val();
    var specialization_name = 'anesthesia'
    var api1Completed = false;
    var api2Completed = false;

    // Make a request to API 1 with user input
    $.get('/llm', { input: userInput, specialization: specialization_name }, function(api1Data) {
        // Display API 1 response to the user

        $('#llmResponse').text(api1Data.data);
        toggleResultsBox1(api1Data.data);
        api1Completed = true
            // Check if both requests are completed before sending the HTML content to the server
        if (api2Completed) {
            sendHtmlContentToServer();
        }
    });

    // Make a request to API 2 with user input
    $.get('/search', { input: userInput, sy: strat_year, ey: end_year, options: selectedOptions.join(',') }, function(api2Data) {
        $('#loadingIndicator').hide();

        displayApi2Results(api2Data);
        toggleResultsBox2(api2Data.data);
        api2Completed = true
            // Check if both requests are completed before sending the HTML content to the server
        if (api1Completed) {
            sendHtmlContentToServer();
        }
    });
}

function displayApi2Results(api2Data) {
    // Parse the JSON string in the 'data' field
    var data = JSON.parse(api2Data.data);
    $('#searchResponse').empty();

    // Append API 2 results to the existing HTML
    var resultsList = $('#searchResponse');

    data.forEach(function(result) {

        var listItem = $('<ul>');
        listItem.append('<br>')
            // Relevant Text
        listItem.append('<b>Relevant text:</b> ' + result.text + '<br>');
        // Name
        listItem.append('<b>Name:</b> ' + result.name + '<br>');
        // Year of Publication
        listItem.append('<b>Year of Publication:</b> ' + result.year + '<br>');
        var imageContainer = $('<div class="image-container">');
        imageContainer.append('<img src="data:image/jpeg;base64, ' + result.pdf_image + '" alt="Relevant Page">');
        listItem.append(imageContainer);
        listItem.append('<br>');
        listItem.append('<a href="' + result.pdf_link + '" target="_blank">Continue with this PDF </a> <br> <br>');
        listItem.append('<br>');
        resultsList.append(listItem);
    });
}

function toggleResultsBox2(api2Data) {
    // Display or hide the results-box based on the content of API 2 response
    var resultsBox = $('#searchResponse');
    if (api2Data && api2Data.length > 0) {
        resultsBox.show(); // Display the results-box
    } else {
        resultsBox.hide(); // Hide the results-box
    }
}

function toggleResultsBox1(api1Data) {
    // Display or hide the results-box based on the content of API 2 response
    var resultsBox = $('#llmResponse');
    if (api1Data && api1Data.length > 0) {
        resultsBox.show(); // Display the results-box
    } else {
        resultsBox.hide(); // Hide the results-box
    }
}

document.getElementById("book-click").addEventListener("click", function() {
    // Assuming 'html_content' is the content you want to send to the server
    saveHtmlContentToServer();
});

function sendHtmlContentToServer() {
    var htmlContent = $('html').html(); // Get the HTML content of the entire page

    // Send the HTML content to the server
    $.post('/save_page', { html_content: htmlContent }, function() {
        console.log('HTML content saved successfully.');
    });
}

function saveHtmlContentToServer() {
    var htmlContent = $('html').html(); // Get the HTML content of the entire page

    // Send the HTML content to the server
    $.post('/save_html', { html_content: htmlContent }, function() {
        console.log('HTML content saved successfully.');
    });
}

// document.getElementById("share").addEventListener("click", function() {
//     // Assuming 'html_content' is the content you want to send to the server
//     saveHtmlContentToServer();
// });

// function shareHtmlContentToServer() {
//     var htmlContent = $('html').html(); // Get the HTML content of the entire page

//     // Send the HTML content to the server
//     $.post('/share', { html_content: htmlContent }, function() {
//         console.log('HTML content share successfully.');
//     });
// }
document.getElementById('shareButton').addEventListener('click', function() {
    // Make an HTTP request to your Flask route
    fetch('/share', {
            method: 'POST', // Assuming your Flask route uses POST method
            headers: {
                'Content-Type': 'application/json',
            },
            // Add any necessary body data if required by your Flask route
            // body: JSON.stringify({ key: 'value' }),
        })
        .then(response => response.json())
        .then(data => {
            // Use the data received from the server to update the currentUrl variable
            var currentUrl = data.link;
            console.log(currentUrl);
            // Use the Clipboard API to write text to the clipboard
            navigator.clipboard.writeText(currentUrl)
                .then(function() {
                    // Provide feedback to the user (you can customize this part)
                    alert('The Link is copied to your clipboard!! Share it with your Friends :', currentUrl);
                })
                .catch(function(err) {
                    console.error('Unable to copy to clipboard', err);
                    // Handle errors as needed
                });
        })
        .catch(error => {
            console.error('Error:', error);
            // Handle errors as needed
        });
});