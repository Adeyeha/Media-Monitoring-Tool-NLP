// $("#searchField").keyup(function () {
//     var value = this.value.toLowerCase().trim();

//     $("table tr").each(function (index) {
//         if (!index) return;
//         $(this).find("td").each(function () {
//             var id = $(this).text().toLowerCase().trim();
//             var not_found = (id.indexOf(value) == -1);
//             $(this).closest('tr').toggle(!not_found);
//             return not_found;
//         });
//     });
// });

jQuery(document).ready(function($) {

    $(".clickable-row").click(function() {

        window.location = $(this).data("href");

    });

});


const methodField = document.querySelector("#method");
const keywordsearchField = document.querySelector("#keywordsearchField");
const datesearchField = document.querySelector("#datesearchField");


methodField.addEventListener("change", (e) => {

    var methodVal = e.target.value;

    if (methodVal == "date"){
        keywordsearchField.value = null;
        keywordsearchField.style.display = "none";
        datesearchField.style.display = "block";
    }
    else if (methodVal == "keyword"){
        datesearchField.value = null;
        datesearchField.style.display = "none";
        keywordsearchField.style.display = "block";
    }

});