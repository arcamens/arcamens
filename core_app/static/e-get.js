function do_get(e) {
    $('#modalWait').modal('show');

    shell = $(this).attr('data-shell');
    shell_error = $(this).attr('data-shell-error');

    callback_error = $(this).attr('data-callback-error');
    callback = $(this).attr('data-callback');
    url   = $(this).attr('data-show');

    if(shell_error == null && callback_error == null) {
        callback_error = "$('#modalError').modal('toggle');"
        shell_error = '#messageError';
    }

    $.ajax({
    url: url,  //Server script to process data
    type: 'GET',
    success: function(data) {
    $('#modalWait').modal('hide');

        eval(callback);
        $(shell).html(data);

    },
    error: function(data){
        $('#modalWait').modal('hide');
        eval(callback_error);
        $(shell_error).html(data.responseText);

    },
    cache: false,
    contentType: false,
    processData: false
    });
}

$(document).on('click', '.e-get', do_get);















