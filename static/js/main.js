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

// Add event listener to the form submission
document.getElementById("search-form").addEventListener("submit", function (event) {
    const startYear = parseInt(document.getElementById("start-year").value);
    const endYear = parseInt(document.getElementById("end-year").value);

    if (endYear < startYear) {
        event.preventDefault(); // Prevent form submission
        alert("Invalid year range. End year cannot be less than start year.");
        return;
    }
});
