function do_post() {
    shell = $(this).attr('data-shell');
    shell_error = $(this).attr('data-shell-error');

    callback_error = $(this).attr('data-callback-error');
    callback = $(this).attr('data-callback');

    url   = $(this).attr('data-show');
    form  = $(this).attr('data-form');

    var formData = new FormData($(form)[0]);

    $.ajax({
    url: url,  //Server script to process data
    type: 'POST',
    success: function(data) {
        eval(callback);
        $(shell).html(data);
    },
    error: function(data){
        eval(callback_error);
        $(shell_error).html(data.responseText);

    },
    data: formData,
    cache: false,
    contentType: false,
    processData: false
    });
}

$(document).on('click', '.e-post', do_post);
