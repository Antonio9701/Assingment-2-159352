function open_new_win() {
    const uri = window.location.href + "form";
    const config = "toolbar=no";  // Configuration for new separate window
    window.open(uri, "", config);
}

function Users_Input() {
    const httpRequest = new XMLHttpRequest();
    httpRequest.onload = function () {
        try {
            const input = JSON.parse(httpRequest.responseText);
            displayInputData(input);
        } catch (error) {
            console.error("Error parsing input JSON:", error);
        }
    };
    httpRequest.open("GET", "input.json", true);
    httpRequest.send();
}

function displayInputData(input) {
    let httpReq = new XMLHttpRequest();
    httpReq.onload = function () {
        const input = JSON.parse(httpReq.responseText);

        // Populate individual input fields
        document.getElementById("name").innerHTML = "Input your name: " + input['name'];
        document.getElementById("gender").innerHTML = "What is your gender? " + input['gender'];
        document.getElementById("birthyear").innerHTML = "In what year were you born? " + input['birthyear'];
        document.getElementById("birthplace").innerHTML = "What is the country of your birth? " + input['birthplace'];
        document.getElementById("residence").innerHTML = "What country do you live in now? " + input['residence'];

        // Populate answers to questions
        for (let i = 1; i <= 20; i++) {
            const question = `q${i}`;
            const answer = input[i];
            const answerElem = document.getElementById(question);
            answerElem.innerHTML = answerElem.innerHTML.replace(/\d/g, '');
            answerElem.innerHTML += answer;
        }

        // Populate additional input fields
        document.getElementById("job").innerHTML = "Which of these jobs would be most appealing to you? " + input['job'];
        document.getElementById("pet").innerHTML = "Which of these animals would appeal to you as a pet? " + input['pets'];
        document.getElementById("message").innerHTML = "Enter a message or comment if you have one: " + input['message'];

        // Toggle display of containers
        const questionsContainer = document.getElementById("questions");
        questionsContainer.style.display = questionsContainer.style.display === "none" ? "block" : "none";
        const resultsContainer = document.getElementById("results");
        resultsContainer.style.display = "none"; // Hide the results container
    };

    // Send XMLHttpRequest to fetch input data
    httpReq.open("GET", "input.json", true);
    httpReq.send();
}



function Analyses() {
    const xmlhttp = new XMLHttpRequest();
    xmlhttp.onload = function () {
        try {
            const input = JSON.parse(xmlhttp.responseText);
            displayResultsData(input);
        } catch (error) {
            console.error("Error parsing results JSON:", error);
        }
    };
    xmlhttp.open("GET", "profile.json", true);
    xmlhttp.send();
}
function setCanvasSize(canvas, img) {
    canvas.width = img.width;
    canvas.height = img.height;
}
function displayResultsData(input) {
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Display selected pet images
    if (input.pets) {
        console.log("Pet images:", input.pets); // Log the pet images data
        input.pets.forEach((pet, index) => {
            console.log("Loading pet image:", pet.image); // Log each pet image path before loading
            const img = new Image();
            img.onload = function () {
                console.log("Pet image loaded successfully:", pet.image);
                setCanvasSize(canvas, img); // Set canvas size based on image dimensions
                ctx.drawImage(img, index * 200, 0, 200, 200);
             };
            img.onerror = function() {
                console.error("Error loading pet image:", pet.image); // Log if there's an error loading the image
            };
            // Use relative path as source for the image
            img.src = pet.image;
        });
        canvas.style.display = "block";
    } else {
        // Hide the canvas if there are no pets to display
        canvas.style.display = "none";
    }

    // Populate other result data
    document.getElementById("desired_job").innerHTML = "You chose '" + input.desired_job + "' as your desired job";
    document.getElementById("suitability").innerHTML = "Our algorithm has calculated your suitability for this job as " + input.suitability_for_chosen_job + "/5";
    document.getElementById("best_job").innerHTML = "Based on your results of our personality test, we have concluded that the most suitable job for you is '" + input.best_suited_job + "'";
    document.getElementById("movie").innerHTML = "Because you selected '" + input.desired_job + "' as your desired job, we believe this movie may be of interest to you: " + input.movie.Title + " - " + input.movie.Plot;

    // Show the results container
    const resultsContainer = document.getElementById("results");
    resultsContainer.style.display = "block";

    // Hide the questions container
    const questionsContainer = document.getElementById("questions");
    questionsContainer.style.display = "none";
}

/***
Define the function and first instantiate the XMLHttpRequest
class
function getInfo() {
const xmlhttp = new XMLHttpRequest();
}

const c = document.getElementById("myCanvas");
    const ctx = c.getContext("2d");
    ctx.moveTo(0, 0);
    ctx.lineTo(200, 100);

 ***/
