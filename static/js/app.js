document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("fitnessForm");

    const button = document.getElementById("generateButton");


    if (form && button) {

        form.addEventListener("submit", function () {

            button.disabled = true;

            button.innerText = "Generating Your Plan...";

        });

    }


    const deleteForms =
        document.querySelectorAll(
            "form[action^='/delete-user/']"
        );


    deleteForms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const confirmed = confirm(
                "Are you sure you want to delete this user?"
            );

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });

});