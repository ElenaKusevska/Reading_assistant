// Upload file:
function click_function() {
    document.getElementById('get_file').click();
}

function on_file_upload() {
    fu = document.getElementById("get_file").value;
    document.getElementById("uploaded_file_name").style.color = "#3C3C3C";
    document.getElementById("uploaded_file_name").innerHTML = fu.split("\\").pop();
}

function submit_form_request() {
    
    var test_submit = false;
    fu = document.getElementById("uploaded_file_name").innerHTML.trim();
    if ( fu != "" ) {
        test_submit = true;
    } else {
        document.getElementById("uploaded_file_name").style.color = "#ffffff";
        document.getElementById("uploaded_file_name").innerHTML = "Please upload a file";
    }

    if (test_submit) {
        // Initialize new request
        const request = new XMLHttpRequest();
        request.open('POST', '/')

        // Callback function for when request completes
        request.onload = function() {
            const data = JSON.parse(request.responseText);
            if (data.success) {
                document.getElementById("uploaded_file_text").innerHTML = data.file_text;
            } else {
                document.getElementById("uploaded_file_text").innerHTML = "ERROR";
            }
        }

        var form = document.forms.namedItem("form1");
        var formData = new FormData(form);
        //let formData = new FormData(document.forms.form1);
        request.send(formData);
        return false;
    } else {
        return false;
    }

}

