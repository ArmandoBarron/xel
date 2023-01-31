$('#login').click(function() {
    // Traemos los datos de los inputs
    var user = $('#email').val();
    var clave = $('#password').val();
    if (user == "" || clave == "") {
        swal('Error', 'Ingrese todos los campos', 'error');
    } else {
        var d = {};
        d['email'] = user;
        d['password'] = clave;
        d['location'] = window.location;
        //d['origin'] = window.location.origin;
        dd = JSON.stringify(d);
        // Envio de datos mediante Ajax
        $.ajax({
                method: 'POST',
                url: 'login.php',
                data: dd,
                // Esta funcion se ejecuta antes de enviar la información al archivo indicado en el parametro url
                beforeSend: function() {
                    $('#load').html('<div class="col-xs-12 center text-accent">' +
                        '<span>Validando datos...</span>' +
                        '</div>');
                    $('#load').show();
                }
        })
        .done(function(res) {
            console.log(res);
                $('#load').hide();
                if (res=='ok') {
                    location.reload(true);
                } else {
                    swal('Error', 'Something went wrong12.', 'error');
                }
        })
        .fail(function(res) {
            console.log(res)
                $('#load').hide();
                resJson = res.responseJSON;
                switch (resJson.message) {
                    case '':
                        swal('Error', '', 'error');
                        break;
                    default:
                        swal('Error', resJson.message, 'error');
                        break;
                }
        });
    }
});

// para obtener informacion de geolocalizacion
//$.getJSON('http://ip-api.com/json?callback=?', function(data) { console.log(JSON.stringify(data, null, 2)); });


// FUNCION PARA REGISTRAR UN NUEVO USUARIO
$('#registro').click(function() {

    var user = $('#username').val();
    var email = $('#email').val();
    var clave = $('#password').val();
    var clave2 = $('#password2').val();
    if (user == "" || clave == "" || email == "" || clave2 == "") {
        swal('Error', 'Ingrese todos los campos.', 'error');
    } else if(clave == clave2){
        var dd = {};
        var d = $('#formulario_registro').serializeArray();
        d.forEach(function(elem) {
            dd[elem.name] = elem.value;
        });
        var ddd = JSON.stringify(dd);
        //console.log(ddd);
        $.ajax({
            url: window.location.origin+'/auth/v1/users/create',
                type: 'POST',
                dataType: 'JSON',
                data: ddd,
                beforeSend: function() {
                    $('#load').html('<div class="col-xs-12 center text-accent">' +
                        '<span>Espere...</span>' +
                        '</div>');
                    $('#load').show();
                }
            })
            .done(function(res) {
                switch (res.message) {
                    case 'User created, please check your email.':
                        $('#load').html('<div class="col-xs-12 center text-accent">' +
                            '<span>'+res.message+'</span>' +
                            '</div>');
                        window.setTimeout(function() { $('#load').hide(); }, 4000);
                        window.location.assign("../index.php");
                        break;
                    default:
                        $('#load').hide();
                        swal('', 'Please, try again.', '');                     
                        break;
                }
            })
            .fail(function(res) {
                $('#load').hide();
                if (res.responseJSON) {
                    resJson = res.responseJSON;
                    switch (resJson.message) {
                        case '':
                            swal('Error', '', 'error');
                            break;
                        default:
                            swal('Error', resJson.message, 'error');
                            break;
                    }
                } else {
                    swal('Error', 'Something went wrong.', 'error');
                }
            });
    }else{
        swal('Error', 'Passwords dont match.', 'error');
    }

});

// FUNCION PARA CAMBIAR EL NOMBRE DE UN USUARIO
$('#c_username').click(function() {
    var key = document.getElementById('keyuser').value;
    var user = document.getElementById('username').value;
    if (key == '' || user == '') {
        swal('Error', 'Faltan datos.', 'error');
    } else {
        var dd = {};
        dd['keyuser'] = key;
        dd['username'] = user;
        $.ajax({
                url: 'auth/v1/users/' + key + '/edit/username',
                type: 'PUT',
                dataType: 'JSON',
                data: JSON.stringify(dd),
                beforeSend: function() {
                    $('#resp').html('...');
                }
            })
            .done(function(res) {
                if (res.message == 'Done.') {
                    window.location = "listaUsuarios.php";
                }
            })
            .fail(function(res) {
                $('#resp').html('');
                resJson = res.responseJSON;
                switch (resJson.message) {
                    case '':
                        swal('Error', '', 'error');
                        break;
                    default:
                        swal('Error', resJson.message, 'error');
                        break;
                }
            });

    }
});

// FUNCION PARA CAMBIAR EL CORREO DE UN USUARIO
$('#c_email').click(function() {
    var key = document.getElementById('keyuser').value;
    var email = document.getElementById('email').value;
    if (key == '' || email == '') {
        swal('Error', 'Faltan datos.', 'error');
    } else {
        var dd = {};
        dd['keyuser'] = key;
        dd['email'] = email;
        $.ajax({
                url: '/auth/v1/users/' + key + '/edit/email',
                type: 'PUT',
                dataType: 'JSON',
                data: JSON.stringify(dd),
                beforeSend: function() {
                    $('#resp').html('...');
                }
            })
            .done(function(res) {
                if (res.message == 'Done.') {
                    window.location = "listaUsuarios.php";
                }
            })
            .fail(function(res) {
                $('#resp').html('');
                resJson = res.responseJSON;
                switch (resJson.message) {
                    case '':
                        swal('Error', '', 'error');
                        break;
                    default:
                        swal('Error', resJson.message, 'error');
                        break;
                }
            });

    }
});

// FUNCION PARA CAMBIAR LA CONTRASEÑA DE UN USUARIO
$('#c_pass').click(function() {
    var key = document.getElementById('keyuser').value;
    var pass = document.getElementById('password').value;
    if (key == '' || pass == '') {
        swal('Error', 'Faltan datos.', 'error');
    } else {
        var dd = {};
        dd['keyuser'] = key;
        dd['password'] = pass;
        $.ajax({
                url: '/auth/v1/users/' + key + '/edit/password',
                type: 'PUT',
                dataType: 'JSON',
                data: JSON.stringify(dd),
                beforeSend: function() {
                    $('#resp').html('...');
                }
            })
            .done(function(res) {
                if (res.message == 'Done.') {
                    window.location = "listaUsuarios.php";
                }
            })
            .fail(function(res) {
                console.log(res);
                $('#resp').html('');
                resJson = res.responseJSON;
                switch (resJson.message) {
                    case '':
                        swal('Error', '', 'error');
                        break;
                    default:
                        swal('Error', resJson.message, 'error');
                        break;
                }
            });

    }
});