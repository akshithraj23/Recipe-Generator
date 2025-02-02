/**
 * Event listener for form submission.
 * Prevents default submission and sends an API request to generate a recipe.
 */
document.getElementById('recipeForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the form from submitting normally

    // Retrieve user input values from the form
    const ingredients = document.querySelector('input[name="ingredients"]').value;
    const cuisine = document.querySelector('input[name="cuisine"]').value;
    const cookingTime = document.querySelector('input[name="cookingTime"]').value;
    const complexity = document.querySelector('select[name="complexity"]').value;
    const mealType = document.querySelector('select[name="mealType"]').value;

    // Construct the query string with user input
    const queryString = `ingredients=${ingredients}&cuisine=${cuisine}&cookingTime=${cookingTime}&complexity=${complexity}&mealType=${mealType}`;

    // Open a connection using Server-Sent Events (SSE) for real-time streaming of recipe content
    const eventSource = new EventSource(`/recipeStream?${queryString}`);

    // Get references to the UI elements for displaying the recipe and status
    const recipeContent = document.getElementById('recipeContent');
    const statusMessage = document.getElementById('statusMessage');
    const errorOverlay = document.getElementById('errorOverlay');

    // Clear previous recipe content and display initial status message
    recipeContent.innerHTML = '';
    statusMessage.innerHTML = 'Generating your recipe...';

    /**
     * Handles incoming messages from the server.
     * The server sends chunks of the recipe which are displayed in real time.
     */
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data); // Parse the incoming JSON data

        if (data.action === 'start') {
            // Indicate that recipe generation has started
            statusMessage.innerHTML = 'Starting recipe generation...';
        }

        if (data.action === 'chunk') {
            // Append each received chunk of recipe text to the display area
            recipeContent.innerHTML += data.chunk;
        }

        if (data.action === 'close') {
            // Indicate that recipe generation is complete and close the connection
            statusMessage.innerHTML = 'Recipe generation complete!';
            eventSource.close();
        }
    };

    /**
     * Handles errors in the EventSource connection.
     * Displays an error overlay and stops the recipe generation process.
     */
    eventSource.onerror = function() {
        errorOverlay.style.display = 'flex'; // Show error overlay
        eventSource.close(); // Close the connection in case of an error
    };
});

/**
 * Closes the error overlay and resets the form.
 * Also clears previous recipe content and status messages.
 */
function closeErrorOverlay() {
    document.getElementById('errorOverlay').style.display = 'none'; // Hide error overlay
    document.getElementById('recipeForm').reset(); // Reset form fields
    document.getElementById('statusMessage').innerHTML = ''; // Clear status message
    document.getElementById('recipeContent').innerHTML = ''; // Clear recipe content
}
