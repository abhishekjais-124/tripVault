document.addEventListener('DOMContentLoaded', function () {
    function showDiv() {
        document.getElementById('hiddenDiv').style.display = 'block';
    }

    function hideDiv() {
        document.getElementById('hiddenDiv').style.display = 'none';
    }

    // Attach event listeners after DOMContentLoaded
    document.querySelector('.navbar-brand').addEventListener('mouseover', showDiv);
    document.querySelector('.navbar-brand').addEventListener('mouseout', hideDiv);
});