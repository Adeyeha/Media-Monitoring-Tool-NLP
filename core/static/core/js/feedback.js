    function handleChange(radio,id,model_source) {
    console.log('In News Update');
    if (typeof $ === "undefined") {
        $ = parent.$;
        jQuery = parent.jQuery;
    }
        // alert('Click OK to update records');
        var dataJson = {'value':radio.value,'id':id,'model_source':model_source};
        console.log(dataJson);
    $.ajaxSetup({ headers: { "X-CSRFToken": '{{ csrf_token }}' }});
        $.ajax({
        url: "update-feedback",
        type: "POST",
        data: JSON.stringify(dataJson),
        dataType: "json",
        contentType: "application/json",
            success: function (response) {
            console.log(response.message)
            // alert('Record Updated');
        },
        error: function (xhr, ajaxOptions, thrownError) {
        // alert('failed');
        }
        });
    }
