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
document.getElementById("click").addEventListener("click", function (event) {
    const startYear = parseInt(document.getElementById("start-year").value);
    const endYear = parseInt(document.getElementById("end-year").value);

    if (endYear < startYear) {
        event.preventDefault(); // Prevent default button behavior
        alert("Invalid year range. End year cannot be less than start year.");
        return;
    }
});




function sendRequests() {
    // Get user input
    $('#loadingIndicator').show();
    var userInput = $('#userInput').val();
    var strat_year = $('#start-year').val();
    var end_year = $('#end-year').val();
    // Display or hide results-box based on the content
    // Show loading message or spinner

    // Make a request to API 1 with user input
    $.get('/llm', { input: userInput }, function (api1Data) {
        // Display API 1 response to the user

        $('#llmResponse').text(api1Data.data);
        toggleResultsBox1(api1Data.data)
    });

    // Make a request to API 2 with user input
    $.get('/search', { input: userInput, sy: strat_year, ey: end_year }, function (api2Data) {
        $('#loadingIndicator').hide();

        displayApi2Results(api2Data);
        toggleResultsBox2(api2Data.data);
    }
    );

}

function displayApi2Results(api2Data) {
    // Parse the JSON string in the 'data' field
    console.log('api2Data.data', api2Data.data);
    var data = JSON.parse(api2Data.data);

    $('#searchResponse').empty();

    // Append API 2 results to the existing HTML
    var resultsList = $('#searchResponse');

    data.forEach(function (result) {

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