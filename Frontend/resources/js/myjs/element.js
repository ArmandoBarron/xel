var id;
var nivel;
var busqueda;
var map;

function init(elemento,busqueda,language){
  //console.log("ELEMENTO");
  document.busqueda = busqueda;
  this.id = elemento;
  loadTexts(language);
  loadElementInfo(elemento);
  cargarComentarios();
}

/**
* CARGA LA INFORMACIÓN DE UN ELEMENTO
*/
function loadElementInfo(element){

  $.ajax({
      url: 'includes/controladores/controller.Element.php',  //Server script to process data
      type: 'POST',
      data: {element:element,action:"get_info"},
      dataType: 'json',
      success  : function(data){ //muestra la respuesta
        strHtml = '';
        if(data['tipo'] == 4 || data['tipo'] == 5){
          strHtml += '<div class="col-sm-5" id="imgelement"><img height="500px" width="100%" src="resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/Q0SEUUh7qhc0X7dvtD90K2yZd7euodNvAdE2GwdDUyEMBkuXfxkdNJyu9AQplmDoU/'+data['nombre']+'.jpg" />';
          strHtml += '<div class="comments"><div>              <div class="form-group"><label for="comment">'+document.lngarr['comments']+':</label><textarea id="txtComment" class="form-control" rows="5" id="comment"></textarea></div><div class="pull-right"><label type="submit" id="btnNewComment" onclick="newComment()" class="btn btn-primary btn-sm">'+document.lngarr['post']+'</label></div></div><div id="comments" class="users-comments"></div></div></div>';
        }
        strHtml += '<div class="col-sm-7" id="divdata"><h3>'+data['nombre']+'</h3>';
        if(data['tipopadre'] != null){
          strHtml += '<strong>'+capitalizeFirstLetter(data['tipopadre'])+':</strong> ' + capitalizeFirstLetter(data['nombrepadre']);
        }

        if(data['tipo'] == 4 ){
          strHtml += '<table  width="100%"><tr><td><strong>'+document.lngarr['path']+' : </strong> '+data['path']+'<br><strong>'+document.lngarr['row']+' : </strong> '+data['row']+'<br><strong>'+document.lngarr['datead']+': </strong> '+data['date']+'<br><strong>'+document.lngarr['projection']+': </strong> '+data['projection']+'<br><strong>'+document.lngarr['ellipsoid']+': </strong> '+data['ellipsoid']+'</td><td><strong>'+document.lngarr['download']+'s: </strong>'+data['descargas']+'<br><strong>'+document.lngarr['myrating']+': </strong><div class="likes">';
          for(var i=1;i<=5;i++){
            if(i<=data['rating']){
              strHtml += '<button id="btnStar'+data['idelemento']+i+'" onclick=\'checkSession(\"rate\",this,\"'+data['idelemento']+'\",\"'+i+'\")\' type="button" class="btn btn-default btn-xs"><span class="glyphicon glyphicon-star" aria-hidden="true"></span></button>';
            }else{
              strHtml += '<button id="btnStar'+data['idelemento']+i+'" onclick=\'checkSession(\"rate\",this,\"'+data['idelemento']+'\",\"'+i+'\")\' type="button" class="btn btn-default btn-xs"><span class="glyphicon glyphicon-star-empty" aria-hidden="true"></span></button>';
            }
          }
          strHtml += '</div><br><strong>'+document.lngarr['avgrate']+':</strong><div class="likes">';
          for(var i=1;i<=5;i++){
            if(i<=data['average']){
              strHtml += '<button type="button" class="btn btn-default btn-xs"><span class="glyphicon glyphicon-star" aria-hidden="true"></span></button>';
            }else{
              strHtml += '<button  type="button" class="btn btn-default btn-xs"><span class="glyphicon glyphicon-star-empty" aria-hidden="true"></span></button>';
            }
          }
          strHtml += "</div></td></tr></table>"
        }else if(data['tipo'] == 5){
          strHtml += '<div></div><strong>'+document.lngarr['composition']+': </strong>'+data['composition']+'<br>          <strong>'+document.lngarr['descprod']+': </strong><p>'+data['description']+'</p>'
        }

        if(data['tipo'] == 4){
          strHtml += "<button type='button' title='"+document.lngarr['descmetbtn']+"' onclick='verMeta(\""+data['hash_name']+"\")' class='btn btn-info btn-xs'><span class='glyphicon glyphicon-file' aria-hidden='true'></span>"+document.lngarr['descmetbtn']+"</button><span id='btn"+data['nombre']+"'>&nbsp&nbsp<button title='"+document.lngarr['download']+"' type='button'  onclick='checkSession(\"addToCar\",\""+data['nombre']+"\",\"add\")' class='btn btn-default btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span>"+document.lngarr['add']+"</button></span>";
        }else if(data['tipo'] == 5){
          strHtml += "<span id='btn"+data['nombre']+"'><button title='"+document.lngarr['download']+"' type='button'  onclick='checkSession(\"addToCar\",\""+data['nombre']+"\",\"add\")' class='btn btn-default btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span>"+document.lngarr['add']+"</button></span>";
        }
        strHtml += '<div class="table-responsive"  id="tblHijos"></div>';
        if(data['tipo'] == 4){
          strHtml += '<center><div id="map" style="min-height:300px;width:300px;"></div></center>';
        }

        $("#content").html(strHtml);
        document.id = data['idelemento'];
        document.nivel = data['tipo'];
        document.nombre = data['nombre'];
        cargarTabla(0);
        cargarMapa(Number(data['lat']),Number(data['lon']));
      },
      error: function(data){ //se lanza cuando ocurre un error
        console.log(data.responseText);
      }
   });
}

function newComment(){
  var comment = $.trim($("#txtComment").val());
  if(comment.length > 0 && comment != ""){
    $.ajax({
        url: 'includes/controladores/controller.Session.php',  //Server script to process data
        type: 'POST',
        data: {comment:comment,element:id,action:"comment"},
        dataType: 'json',
        beforeSend: function(){
        },
        success  : function(data){ //muestra la respuesta
          console.log(data);
          $("#txtComment").val("");

          if(data['status'] == -1){
            notificarUsuario(data['mensaje'],"danger");
          }else{
            notificarUsuario(data['mensaje'],"success");
            cargarComentarios();
          }
        },
        error: function(data){ //se lanza cuando ocurre un error
          console.log(data.responseText);
        }
     });
  }
}

function cargarMapa(lat,lon) {
  console.log(lat);
  console.log(lon);
  var myLatLng = {lat: lat, lng: lon};
  console.log(myLatLng);
  map = new google.maps.Map(document.getElementById('map'), {
    center:myLatLng,
    zoom: 8
  });
  var marker = new google.maps.Marker({
    position: myLatLng,
    map: map,
    title: 'Center'
  });
}

function cargarTabla(page){
  $.ajax({
    type    : 'POST',
    url     : 'includes/controladores/controller.Element.php',
    data    : {action:"show_childs",page:page,id:document.id,nivel:document.nivel,busqueda:document.busqueda,nombre:document.nombre},
    beforeSend: function(){
      $("#tblHijos").html(document.lngarr['loaddata']);
    },
    success : function(response) {
      $("#tblHijos").html(response);
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

function cargarComentarios(){
  $.ajax({
      url: 'includes/controladores/controller.Session.php',  //Server script to process data
      type: 'POST',
      data: {element:id,action:"getcomments"},
      dataType: 'json',
      beforeSend: function(){
      },
      success  : function(data){ //muestra la respuesta
        $("#comments").html("");
        data.forEach(function(item,index){
          $("#comments").append("<div class='comment'><strong class='username'>"+item['nombre_usuario']+" </strong><span class='date'>"+item['date']+"</span><div>"+item['comment']+"</div></div><hr class='linea'>");
        });

      },
      error: function(data){ //se lanza cuando ocurre un error
        console.log(data.responseText);
      }
   });
}
