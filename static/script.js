// Upload file:
function click_function() {
    document.getElementById('get_file').click();
}

function on_file_upload() {
    fu = document.getElementById("get_file").value;
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
        // Initialize new request:
        const request = new XMLHttpRequest();
        request.open('POST', '/')

        // Callback function for when request completes:
        request.onload = function() {
            const data = JSON.parse(request.responseText);
            if (data.success) {
                document.getElementById("uploaded_file_text").innerHTML = data.file_text;
                document.getElementById('audio_player').src = "http://127.0.0.1:5000/static/" + data.audio_file +"?q=300"
                document.getElementById("total_audios").innerHTML = data.number_of_audio_files;
            } else {
                document.getElementById("uploaded_file_text").innerHTML = "ERROR";
            }
        }

        // Create FormData and send request:
        var form = document.forms.namedItem("form1");
        var formData = new FormData(form);
        //let formData = new FormData(document.forms.form1);
        request.send(formData);
        return false;
    } else {
        return false;
    }

}

function play_audio() {

    var naudios = 20//document.getElementById("total_audios").innerHTML
    

    var i = 0;
    playSnd();

    function playSnd() {
        document.getElementById('audio_player').src = "http://127.0.0.1:5000/static/" + String(i) +".mp3?q=300";
        var audio = document.getElementById('audio_player')
        if (i == 20) return;
        audio.addEventListener('ended', playSnd);
        if (i > 0) {
            document.getElementById(String(i-1)).style.color = "#ffffff";
        }
        document.getElementById(String(i)).style.color = "#000000";
        audio.play();

        i = i + 1;
    }
        

    
}

function pause_audio() {
    document.getElementById('audio_player').pause();
}

