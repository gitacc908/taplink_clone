function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);

            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');


$('body').on('click', function (e) {
    if (e.target.id === 'f_name_icon') {
        $('#f_name').prop("disabled", false);
    } else if (e.target.id === 'f_name' || e.target.id === 'l_name') {
        return;
    } else if (e.target.id === 'l_name_icon') {
        $('#l_name').prop("disabled", false);
    } else {
        $('#f_name').prop("disabled", true)
        $('#l_name').prop("disabled", true);
    }
});


$("#f_name").change(function () {
    update($(this).val(), null)
});


$("#l_name").change(function () {
    update(null, $(this).val())
})

function update(first_name, last_name) {
    // Изменение имени и фамилии в профиле
    if (first_name != null) {
        var data = {
            first_name: first_name
        }
    } else {
        var data = {
            last_name: last_name
        }
    }
    fetch($('#url').attr("data-url"), {
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify(data),
        headers: new Headers({
            'X-CSRFToken': csrftoken,
        })
    })
};
