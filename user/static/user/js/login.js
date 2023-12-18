// Ensure the code runs after the document is ready
document.addEventListener("DOMContentLoaded", function() {
    // Array of background image filenames in the static folder
    const backgroundFilenames = [
        'image1.jpg',
        'image2.jpg',
        'image3.jpg'
    ];

    // Get a random index from the array
    const randomIndex = Math.floor(Math.random() * backgroundFilenames.length);

    // Generate the full URL
    const imageUrl = staticUrl + backgroundFilenames[randomIndex];

    // Set the background image URL
    document.getElementById('backgroundImage').style.backgroundImage = `url(${imageUrl})`;
});
