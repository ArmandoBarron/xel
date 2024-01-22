// TODO: LOOK ANOTHER FORMAT FOR THE CHAINNED BOX DATA
// TODO: WHEN REARRANGE, IT ALSO SHOULD BE REARRENGED IN DATA OBJECT


DAG = []; //GLOBAL
var PIPELINE = false;
var Download_log = false
var INIT_TIME = 0
var SERVICE_GATEWAY = ""
var LIST_TASK_OVER = []
var DATA_WORKFLOW = {'data':'','type':'DUMMY'};
var DATA_WORKFLOW_DESC;
var MESH_WORKSPACE = "Default" 
var MESH_USER = "Geoportal" //token user
var SESSION_TOKEN = ""
var ServicesArr = []
var PARAMS_MAP = {}
var TOKEN_SOLUTION=''
var ifCoordinates = ["latitud","longitud","lat","lon", "x", "y"].map(function(x){ return x.toUpperCase();}) 
var FORCE_EXECUTION_STOP= false
// variables globales pero para que funcionen algunos servicios
var ID_rule = 1 // Filtercolumn
var ID_CAR_ELEMENT = 1 // Filtercolumn
var ROOT_METADATA ={}
var STACK_LOGS = new LogerStack("logs-panel");


render_function = function(element, self, data) {
    const span_final = document.createElement('span');

    var spanElement = document.createElement('span');
    spanElement.style.fontStyle = 'italic';

    // Establecer el texto del span
    if (data.value_type=="function"){
        spanElement.textContent = ' @Function';
        spanElement.style.color = 'rgba(0, 0, 200, 0.8)';
    }
    else if (data.value_type=="var"){
        spanElement.textContent = ' @Column';
        spanElement.style.color = 'rgba(0, 255, 255, 0.8)';
    }
    else if (data.value_type=="reserved_word"){
        spanElement.textContent = ' ReservedWord';
        spanElement.style.color = 'rgba(200, 50, 0, 0.8)';
    }
    else{
        spanElement.textContent = ' @NoIdeaSorry';
        spanElement.style.color = 'rgba(0, 255, 0, 0.8)';
    }
    var span_text = document.createElement('span');
    span_text.textContent = data.displayText
    span_text.style.fontWeight  = 'bold';
    span_text.style.fontStyle  = 'italic';

    span_final.appendChild(span_text);
    span_final.appendChild(spanElement);
    element.appendChild(span_final)


  }

var Reserved_words = [
    {"displayText":"@if","text":"if sentencia: expresion;","value_type":"function","render":render_function},
    {"displayText":"@startswith","text":"COLUMN.str.startswith('A');","value_type":"function","render":render_function},
    {"displayText":"@createColumnWhitespaces","text":"{new column with whitspaces}=1+COLUMN_NAME;","value_type":"function","render":render_function},
    {"displayText":"@createColumn","text":"NEW_COLUMN=A_COLUMN-OTHER_COLUMN;","value_type":"function","render":render_function},
    {"displayText":"$inputdataframe","text":"dataset","value_type":"reserved_word","render":render_function}

]



function Clean_graph_data(){
    DATA_WORKFLOW_STATUS = false
    notificarUsuario("No dataset loaded.", 'info');
    $("#group-upload").show("fast");
    $("#cleandata_button").hide("fast");
    $(".serviceLoadingIcon-root").html("")
    $(".showOnMapIcon-root").html("")
    $(".downloadDataIcon-root").html("")

}

function Upload_graph_data(){
        sourceId = $('#modal_datasource').data('sourceId');
        raw_file= $('#files')[0].files[0];
        if (raw_file==undefined){console.log("select a data source");return 0}

        $("#"+sourceId+" > div.row > div.service-options > #serviceLoadingIcon-root").html("<img class='service_loader_img' src='resources/imgs/loading.gif'></img>")
        $("#group-upload").hide();
        //$("#cleandata_button").show();
        //$("#files").hide();

        if(raw_file.length != 0) {
            DATA_WORKFLOW_EXT = raw_file.name.split('.').pop();
            filename = raw_file.name

            // EXAMPLE OF HOW TO UPLOAD FILE TO SERVICE MESH
            var files = $('#files')[0].files;
            var upload_and_describe = true
            files_metadata={}
            xel_describe_dataset(filename=filename).done(function(result){
                description = JSON.parse(result)
                
                if(description['status']=="OK"){
                    //verify if file exist in repo. if does, get the metadata. Or 
                    if(description['file_exist']){
                        if (confirm('A file named "'+filename+'" already exists in repo, do you want to overwrite it?')) {
                            // overwrite it!
                            upload_and_describe=true
                        } else {
                            // Do nothing!
                            upload_and_describe=false
                            if (description['status']=="OK"){
                                files_metadata =description.info
                            }
                        }
                    }

                    //upload again or upload if not exist in repo
                    if(files.length > 0 && upload_and_describe){
                        xel_upload_dataset(sourceId,files,filename)
                    }
                    else{
                    // data was uploaded to the catalog MESH_WORKER by default of the user MESH USER
                        LoadExistingDataset(sourceId,filename,metadata=files_metadata)
                    }
                }
                else{
                    notificarUsuario(description['message'],'danger')
                    $("#group-upload").hide();
                }

                });
            
        }
}

function Xel_clean(){
    Set_Tokensolution("")
    flowy.deleteBlocks()
    Set_DatasourceMap('','DUMMY')
    notificarUsuario("Workspace is now clean",'info')
    canvasElementsCount=0
}

function Toggle_run_button(){
    let text= $("#output").text()
    $("#output").toggleClass("btn-outline-success btn-outline-danger");
    $("#run_dropdown").toggleClass("btn-outline-success btn-outline-danger");
    $("#output").text(text == "RUN" ? "FORCE STOP" : "RUN");
}


function Xel_run(as_copy=false,force=false){
    $('#output').prop('disabled', true);
    text= $("#output").text() 
    exec_options = {"force":force}
    console.log(exec_options)
    if (text=="RUN"){ 
        if (as_copy){
            Set_Tokensolution("")
        }
        
        Exec_graph(exec_options);
        $('#output').prop('disabled', false);
        Toggle_run_button()
    }
    else{ //stopping solution
        FORCE_EXECUTION_STOP=true
    }


}


function Exec_graph(exec_options={}){
    // ==================================== deployting phase
    Download_log = false
    DAG = [] //CLEAN
    LIST_TASK_OVER= []
    data_obj = JSON.parse(JSON.stringify(dataObject))
    SERVICE_GATEWAY = $("#ip_gateway").val()
    transform_dag(data_obj,DAG)
    console.log("EL DAG ...") ;console.log(DAG);
    $(".serviceLoadingIcon-task").html("<img class='service_loader_img' src='resources/imgs/loading.gif'></img>")
    $(".showOnMapIcon-task").html("")
    $(".downloadDataIcon-task").html("")
    $(".InspectDataIcon-task").html("")

    // send request to exec dag
    // first setp: deploy services
    var data_to_send = {'SERVICE':'deploy',"HOST":SERVICE_GATEWAY, 'REQUEST':{'DAG':JSON.stringify(DAG),
        'auth':{'user':MESH_USER,'workspace':MESH_WORKSPACE},
        'options':exec_options,
        'metadata':Metadata_collector(),
        'alias':$("#modal_save-solutions-form-name").val(),
        'dataobject': JSON.stringify(dataObject)
    }};

    if (TOKEN_SOLUTION!=""){data_to_send.REQUEST.token_solution=TOKEN_SOLUTION}

    $.ajax({
        type: "POST", // la variable type guarda el tipo de la peticion GET,POST,..
        url: 'includes/xel_Request.php', //url guarda la ruta hacia donde se hace la peticion
        data: data_to_send, // data recive un objeto con la informacion que se enviara al servidor
        beforeSend: function() {
            notificarUsuario("Deploying...", 'info');
        },
        success: function(response) { //success es una funcion que se utiliza si el servidor retorna informacion
            if (response['status']=="OK"){
                notificarUsuario("Resources have been deployed", 'info');
                Set_Tokensolution(response['token_solution'])
                //exec
                pipe_dag(DATA_WORKFLOW,exec_options=exec_options)
            }
            else{
                notificarUsuario("Resources could't have deployed", 'info');
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            notificarUsuario("Resources could't have deployed", 'info');
        },
        dataType: 'json' // El tipo de datos esperados del servidor. Valor predeterminado: Intelligent Guess (xml, json, script, text, html).
    });


}

function pipe_getdata(data_request){ //get RAW data to execute dag
    $('#mytabs a[href="#25b"]').tab('show');
    notificarUsuario("Getting data", 'info');
    var xhr = new XMLHttpRequest();
    var url = "includes/differential.php";
    xhr.open("POST", url, false); //False significa que es sincrona la consulta
    xhr.setRequestHeader("Content-Type", "application/json");
    var send = JSON.stringify(data_request); //lo convertimos en una cadena
    xhr.send(send); //se envia el json
    if (xhr.status == 200) {
        dataRet = JSON.parse(xhr.responseText);
        dataret_arr = []
        dataRet['results'].forEach(function(value, key){
            value[parseInt(key)+1]['Etiqueta_clase'] = "0"//delete etiqueta de clase
            dataret_arr.push(value[parseInt(key)+1])
        });
        PIPELINE = false
        return dataret_arr
    }
    else{
        console.log("BAD");
        return []
    }
}

// postExecutionStop Function does what should happend after the execution stopped
// either successfully or with errors, anyway, it does the same, reactivates the
// execute button, and removes the laoding icon from every box on canvas
// except root.
function RemoveLoadingIcons(){
    $('.serviceLoadingIcon-root').html("")
    $('.serviceLoadingIcon-task').html("");
}

function postExecutionStop(rn,error=true,message="Execution failed, check the parameters") {
    // reactivate button
    $('#output').prop('disabled', false);
    // remove icons
    // se remueven todos los iconos de carga
    RemoveLoadingIcons()

    //console.log('allFootersIcons: ', allFootersIcons);
    //for(let i = 0;i < allFootersIcons.length;i++) {
    //    console.log(`el ${i}: `, allFootersIcons[i]);
    //    allFootersIcons[i].innerHTML = "";
    //}
    if (error){
        notificarUsuario("ERROR: "+message, 'danger');
        Toggle_run_button()
    }
    else{
        notificarUsuario("Execution complete", 'success');
        var end = Date.now();
        tiempo_ejecucion= end-INIT_TIME
        console.log(tiempo_ejecucion);
        notificarUsuario("tiempo de ejecucion: "+tiempo_ejecucion , 'info')

        if ($("#dag_saveresults").is(":checked")){ //auto download log
            for (var i = 0; i < LIST_TASK_OVER.length; i++) {
                console.log(LIST_TASK_OVER[i]["task"])
                download_data_pipe(LIST_TASK_OVER[i]["rn"], LIST_TASK_OVER[i]["task"],LIST_TASK_OVER[i]["type"])
            }
        }

    
        if(Download_log==false){
            Download_log = true
            if ($("#dag_savelog").is(":checked")){ //auto download log
                let data_request = {"rn":rn,'host':SERVICE_GATEWAY}
                $.ajax({
                    url: 'includes/dag_getlogfile.php',
                    type: 'POST',
                    data:data_request,
                    success: function(liga) {  
                        $(".serviceLoadingIcon-root").html(`<a id='temporal_log_link' href='${liga}' target='_blank' ></a>`)
                        $('#temporal_log_link').get(0).click();
                        $(".serviceLoadingIcon-root").html("")
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown){
                        error_result = XMLHttpRequest['responseJSON']
                        if (XMLHttpRequest.status==401){ //session expired
                            sesionExpirada()
                        }
                    }
                });
            }
            // execute again if there are more iterations
            itt = parseInt($("#dag_iterations").val())
            if(itt>=2){
                $("#dag_iterations").val(itt-1)
                Set_Tokensolution("") //se vacía esta variable, de esta forma se fuerza a ejecutar todo desde 0
                setTimeout(Xel_run(),2000)
                
            }
            else{
                console.log("no more iterations")
            }
        }

    }
}





function pipe_dag(data_for_workflow,exec_options={}){ // launch dag
    var data_to_send = {'SERVICE':'executeDAG',"HOST":SERVICE_GATEWAY, 'REQUEST':{'DAG':JSON.stringify(DAG),
        'data_map':data_for_workflow, 
        'auth':{'user':MESH_USER,'workspace':MESH_WORKSPACE},
        'options':exec_options,
        'metadata': Metadata_collector(),
        'alias':$("#modal_save-solutions-form-name").val(),
        'dataobject': JSON.stringify(dataObject)
    }};
    
    if (TOKEN_SOLUTION!=""){data_to_send.REQUEST.token_solution=TOKEN_SOLUTION}

    console.log(data_to_send)
    
    INIT_TIME = Date.now();
    $.ajax({
        type: "POST", // la variable type guarda el tipo de la peticion GET,POST,..
        url: 'includes/xel_Request.php', //url guarda la ruta hacia donde se hace la peticion
        data: data_to_send, // data recive un objeto con la informacion que se enviara al servidor
        success: function(response) { //success es una funcion que se utiliza si el servidor retorna informacion
            if (response['status']=="OK"){
                notificarUsuario("Resquest Sent", 'info');

                if (response['is_already_running']){
                    notificarUsuario("The solution is already running...", 'warning');
                }

                Set_Tokensolution(response['token_solution'])

                lista_tareas = Listar_tareas([],dataObject.children)
                setTimeout(function() {
                    ServiceMonitor(MESH_USER,TOKEN_SOLUTION,lista_tareas)
                }, 2000)    
                
            }
            else{
                postExecutionStop(0,true,message=response['message'])
            }

        },

        error: function(XMLHttpRequest, textStatus, errorThrown){
            error_result = XMLHttpRequest['responseJSON']
            postExecutionStop(0,true,message=error_result['message'])
        },
        dataType: 'json' // El tipo de datos esperados del servidor. Valor predeterminado: Intelligent Guess (xml, json, script, text, html).
    });
}

function xel_describe_dataset(filename=null,force=false,context={token_solution:null,task:null,type_dataset:"LAKE",catalog:MESH_WORKSPACE},delimiter=","){
    // filename, force, context = {token_solution,task,type_dataset,tacalog},delimiter=","
    /// dataset = "LAKE,SOLUTION,RECORDS"
    // if SOLUTION:
    // {data:{token_user,token_solution,task,filename},type:SOLUTION,metadata} #un catalogo del usuario
    // if RECORDS:
    //     {data:[],type:RECORDS}
    // if LAKE:
    //     {data:{token_user,catalog(workspace),filename},type:LAKE}
    // ///
    if (context == null){context={token_solution:null,task:null,type_dataset:"LAKE",catalog:MESH_WORKSPACE}}

    let data_request = {'SERVICE':'DescribeDataset/v2' ,'REQUEST':{'data':{},'type':context.type_dataset}}
    if (filename!=null){    data_request.REQUEST.data.filename=filename     }
    data_request.REQUEST.data.token_user=MESH_USER //por defecto solo se usa este usuario
    data_request.REQUEST.data.token_solution=context.token_solution 
    data_request.REQUEST.data.task=context.task 
    data_request.REQUEST.data.catalog=context.catalog 
    if (force){ data_request.REQUEST.force=true}
    data_request.REQUEST.delimiter=delimiter
    return $.ajax({
        url: 'includes/xel_Request.php',
        type: 'POST',
        data: data_request,
        cache: false,
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            notificarUsuario("Something went wrong at mining metadata.","danger");
         }
    })
    ;

}
function xel_upload_dataset(sourceId,files,filename){

    // EXAMPLE OF HOW TO UPLOAD FILE TO SERVICE MESH
    var fd = new FormData();

    console.log("Uploading...")
    fd.append('file',files[0]);
    fd.append('workspace',MESH_WORKSPACE);
    fd.append('user',MESH_USER);
    separator = $("#file_delimiter").val()
    force_describe = $("#force_describe").val()
    
    $.ajax({
      url: 'includes/dag_UploadDataset.php',
      type: 'POST',
      data: fd,
      contentType: false,
      processData: false,
      cache: false,
      beforeSend: function() {
        $('#progress-div').show("fast") //mostrar barra de progreso
      },
      xhr: function() {
        var xhr = new window.XMLHttpRequest();
    
        xhr.upload.addEventListener("progress", function(evt) {
          if (evt.lengthComputable) {
            var percentComplete = evt.loaded / evt.total;
            percentComplete = parseInt(percentComplete * 100);
            //$('#progress_upload_dataset .progress-text').text(progression + '%');
            $('#progress_upload_dataset').css({'width':percentComplete+'%'});
            // actualizar progressbar

          }
        }, false);
    
        return xhr;
      },
      success: function(result) {
        result = JSON.parse(result)
        if (result['status']=="OK"){
            Toggle_Loader("show","Mining dataset...")
            xel_describe_dataset(filename=filename,force=force_describe,context=null,delimiter=separator).done(function(result2){
                files_metadata = JSON.parse(result2).info
                LoadExistingDataset(sourceId,filename,metadata=files_metadata)
            });
        }
      },
      complete: function() {
        setTimeout(function(){
            $('#progress-div').hide("slow") //esconder barra de progreso
            $("#cleandata_button").show("fast");
        }, 1000);
    },
    error: function(XMLHttpRequest, textStatus, errorThrown){
        error_result = XMLHttpRequest['responseJSON']
        if (XMLHttpRequest.status==401){ //session expired
            sesionExpirada()
        }
    }
    });

    return 0
}


function Handler_condition_GetData(task_id,description,isRaw,filename=null,token_solution=null,dataRet=null){
    // si es raw, solo se usa filename. si no es raw, se usa el token_solution y el dataRet
    var if_metadata = true // por defecto se va a manejar metadata, lo cual corersponde a los nombres de archivos, columnas, etc
    var isMarkable=false
    if (dataRet != null){     //si dataRet no es nulo y tiene un status de error, entonces se omite la gestion de la metadata
        if (dataRet['status']=="ERROR" || dataRet['status']=="FAILED"){if_metadata=false}
    }

    if (if_metadata){
        console.log(description)
        if (description==undefined){
            notificarUsuario(`Results produced by ${task_id} were not found. `)
        }
        else{
            tsk = demoflowy_lookForParent(task_id) //obtener los valores de la caja (json) por su id, se obtiene una instancia del json
            parentfilename = description.parent_filename
            tsk.service_metadata.this = description
            tsk.it_produced_data = true
            if (isRaw){ ROOT_METADATA = description} // se guardan la metadata del dataset root
    
            if (description.files_info[parentfilename]==undefined){
                columnas_del_servicio=[]
            }
            else{
                 //columnas que procesa el servicio en mayusculas  
                columnas_del_servicio = [...tsk.service_metadata.this.files_info[parentfilename].columns ].map(function(x){ return x.toUpperCase(); })  
            }
            //buscar si el servicio tiene columnas para geolocalizar en el mapa
            isMarkable = columnas_del_servicio.some( ai => ifCoordinates.includes(ai) ); 
        }
    }


    //$(`#${task_id} > div.row > div.service-options > #serviceLoadingIcon`).html("") //icono de carga
    $(`#${task_id}_serviceLoadingIcon`).html("") //icono de carga
    
    if (isRaw)//los botones cambian dependiendo de si es la caja root o una de BB
    {  
        $(`#${task_id}_inspect`).html(`<i class="fas fa-search fa-xl elementhover" onclick="Inspect_datasource(filename='${filename}')" ></i>`)
        $(`#${task_id}_downloadDataIcon`).html(`<i class="fas fa-cloud-download-alt fa-xl elementhover" onclick="download_data_pipe('','','','${filename}',raw=true)"></i>`)
        //if (isMarkable){
        //    $(`#${task_id}_showOnMapIcon`).html(`<i class="fas fa-map-marked-alt fa-lg elementhover" onclick="ShowModal_map_AAS('${token_solution}','${task_id}')"></i>`)
        //}
        extencion = filename.split(".")[1]
        if (extencion=="csv"){
            $(`#${task_id}`).find(`.row:last`).attr('id', `${task_id}_icons`); //se añade el id
            $(`#${task_id} > #${task_id}_icons > #${task_id}_DataviewIcon`).length  ? null : $(`#${task_id} > #${task_id}_icons`).append(`<div class="col-2 preview-task" style="padding:5px; text-align:center;" id="${task_id}_DataviewIcon"></div>`)

            $(`#${task_id}_DataviewIcon`).html(`<i class="fa-solid fa-chart-pie fa-xl elementhover" onclick="download_data_pipe('','','','${filename}',true,true)"></i>`)
        }
    }
    else
    {
        // para conciderar que una tarea terminó su procesamiento, esta debe arrojar un estatus de FINISHED o FAILED. caso contrario, aun no termina.
        if (dataRet['status']=="FAILED" || dataRet['status']=="FINISHED"){
            LIST_TASK_OVER.push({"rn":token_solution,"task":task_id,"type":dataRet['type'],"ifdownload":dataRet['index']}) //se añade a la lista de tareas completadas
        }

        // añadir boton de inspect a la caja con una funcion que haga el describe. Solamente si el la tarea no falló
        if (dataRet['status']!="ERROR" && dataRet['status']!="FAILED"){
            $("#"+task_id+"_inspect").html(`<i class="fas fa-search fa-xl elementhover" onclick="Inspect_datasource(filename=null,force=false,token_solution='${token_solution}',task='${task_id}',type_dataset='SOLUTION')"></i>`)
        
            if (isMarkable){
                $(`#${task_id}_showOnMapIcon`).html(`<i class="fas fa-map-marked-alt fa-xl elementhover" onclick="ShowModal_map_AAS('${token_solution}','${task_id}')"></i>`)
            }

            if (dataRet['index']){
                $(`#${task_id}_downloadDataIcon`).html(`<i class="fas fa-cloud-download-alt fa-xl elementhover" onclick="download_data_pipe('${token_solution}','${task_id}','${dataRet['type']}')"></i>`)
            }

            if (dataRet['type']=='csv'){
                $(`#${task_id}`).find(`.row:last`).attr('id', `${task_id}_icons`); //se añade el id
                $(`#${task_id} > #${task_id}_icons > #${task_id}_DataviewIcon`).length  ? null : $(`#${task_id} > #${task_id}_icons`).append(`<div class="col-2 preview-task" style="padding:5px; text-align:center;" id="${task_id}_DataviewIcon"></div>`)

                $(`#${task_id}_DataviewIcon`).html(`<i class="fa-solid fa-chart-pie fa-xl elementhover" onclick="download_data_pipe('${token_solution}','${task_id}','${dataRet['type']}','',false,true)"></i>`)
            }
            // preview option

            let data_request = {'SERVICE':`locate/${TOKEN_SOLUTION}/${task_id}`}

            $.ajax({ // ajax para rellenar valores de workspaces
                url: 'includes/xel_get_Request.php',
                type: 'POST',
                dataType: 'json',
                data:data_request,
                success: function(result_location) {  
                    console.log("intentando localizar para visualziar")
                    if (result_location['location']!=""){
                        //if div not exist
                        $(`#${task_id}`).find(`.row:last`).attr('id', `${task_id}_icons`); //se añade el id
                        $(`#${task_id} > #${task_id}_icons > #${task_id}_previewIcon`).length  ? null : $(`#${task_id} > #${task_id}_icons`).append(`<div class="col-2 preview-task" style="padding:5px; text-align:center;" id="${task_id}_previewIcon"></div>`)

                        $(`#${task_id}_previewIcon`).html(`<i class="far fa-eye fa-xl elementhover" onclick="window.open('${result_location['location']}', '_blank')" ></i>`)

                    } 
                },
                error: function(XMLHttpRequest, textStatus, errorThrown){
                    error_result = XMLHttpRequest['responseJSON']
                    if (XMLHttpRequest.status==401){ //session expired
                        sesionExpirada()
                    }
                }
            }).fail(function(){console.log("error al conectarse")});


        }

    }
    //notificarUsuario(`${task_id}: Data loaded.`,"success")

}

function ServiceMonitor(token_project,token_solution,list_remain_task){

    let data_request = {'SERVICE':`monitor/v2/${token_project}/${token_solution}`}
    $.ajax({ // ajax para rellenar valores de workspaces
        url: 'includes/xel_get_Request.php',
        type: 'POST',
        dataType: 'json',
        data:data_request,
        success: function(result) {  
            console.log(result)
            if (result['status']=="OK"){ //se recibieron los datos, ahora se va a iterar cada tarea
                list_remain_task.forEach(function(task){ 
                    task_info = result.list_task[task]
                    if (task_info!==undefined){
                        if (task_info['status']=="FINISHED")
                        {
                            // describir dataset intermedio
                            let task_id = task_info['task']
                            let is_recovered = !task_info['is_recovered']
                            let task_data = CloneJSON(task_info)
                            let context={token_solution:token_solution,task:task_id,type_dataset:"SOLUTION",catalog:MESH_WORKSPACE}
                            list_remain_task = arrayRemove(list_remain_task,task) // se elimina de la lista
                            xel_describe_dataset(filename=null,force=is_recovered,context=context).done(function(result_desc){
                                description = JSON.parse(result_desc).info
                                Handler_condition_GetData(task_id,description,false,'',token_solution,task_data)
                                if(is_recovered){ //es lo contrario, es decir, si es falso
                                    notificarUsuario("Task "+task_id+" has finished", 'success');
                                }
                            });
                        }
                        if (task_info['status']=="ERROR"){
                            let task_id = task_info['task']
                            notificarUsuario("ERROR "+task_id+": "+ task_info['message'], 'warning');
                        }
                        if (task_info['status']=="FAILED")
                        {
                            let task_id = task_info['task']
                            let task_data = CloneJSON(task_info)
                            Handler_condition_GetData(task_id,{},false,'',token_solution,task_data)
                            notificarUsuario("FAILURE in "+task_id+": "+ task_info['message'], 'danger');
                            list_remain_task = arrayRemove(list_remain_task,task) // se elimina de la lista
                        }

                        if (task_info['status']=="WAITING" || task_info['status']=="RUNNING" || task_info['status']=="OK"){
                            console.log(`${task_info['task']}: ${task_info['status']}`)
                        }
    
                    }


                }); //end foreach

                // se revisan posibles mensajes adicionales
                result['additional_messages'].forEach(function(Adit_mess){
                    if (Adit_mess['status']=="RECOVERING"){ list_remain_task.push(Adit_mess['task'])}
                    notificarUsuario(Adit_mess['message'], 'warning');
                });

                //despues de revisar el estatus de cada tarea, la funcion se llama a si misma si aun existen valores en la lista
                if (FORCE_EXECUTION_STOP){ //detener el monitoreo
                    var tiempo_ejecucion = ((Date.now() -INIT_TIME)/1000) -2 ; // se le quitan los 2 segundos que se agregan
                    notificarUsuario("Solution has been stopped. Response Time: "+tiempo_ejecucion , 'warning')
                    FORCE_EXECUTION_STOP =false
                    Toggle_run_button()
                    $('#output').prop('disabled', false);

                }
                else if(list_remain_task.length>=1){
                    setTimeout(function() {
                        ServiceMonitor(token_project,token_solution,list_remain_task)
                    }, 2000)                    
                }
                else{ // esto quiere decir que todas las task devolvieron ya un status, pero puede que aun no terminen
                    
                    lista_tareas = Listar_tareas([],dataObject.children)
                    if (lista_tareas.length == LIST_TASK_OVER.length){ //si esta condicion se cumple, entonces todas las tareas terminaron
                        
                        // se remueven todos los iconos de carga
                        $('.serviceLoadingIcon-root').html("")

                        var tiempo_ejecucion = ((Date.now() -INIT_TIME)/1000) -2 ; // se le quitan los 2 segundos que se agregan
                        notificarUsuario("Solution Complete. Response Time: "+tiempo_ejecucion , 'info')
                        // trigger autosave
                        BTN_save_solution()

                        if ($("#dag_saveresults").is(":checked")){ //auto download data
                            for (var i = 0; i < LIST_TASK_OVER.length; i++) {
                                if (LIST_TASK_OVER[i]["ifdownload"]){
                                    download_data_pipe(LIST_TASK_OVER[i]["rn"], LIST_TASK_OVER[i]["task"],LIST_TASK_OVER[i]["type"])
                                }
                            }
                        }
                    
                        if(Download_log==false){
                            Download_log = true
                            if ($("#dag_savelog").is(":checked")){ //auto download log
                                let data_request = {"rn":rn,'host':SERVICE_GATEWAY}
                                $.ajax({
                                    url: 'includes/dag_getlogfile.php',
                                    type: 'POST',
                                    data:data_request,
                                    success: function(liga) {  
                                        $(".serviceLoadingIcon-root").html(`<a id='temporal_log_link' href='${liga}' target='_blank' ></a>`)
                                        $('#temporal_log_link').get(0).click();
                                        $(".serviceLoadingIcon-root").html("")
                                    }
                                });
                            }
                        }
    
                        // para finalizar, se elimina el stack, a menos que se especifique lo contrario (futu wok (future work))
                        if ($("#if_keep_resources").is(":checked")){ // keep resources
                        
                            notificarUsuario("Resources still up", 'info')
                            Toggle_run_button()

                            itt = parseInt($("#dag_iterations").val()) // execute again if there are more iterations
                            if(itt>=2){
                                $("#dag_iterations").val(itt-1)
                                setTimeout(Exec_graph({"force":true}),1000)
                            }
                            else{console.log("no more iterations")}
                            
      
                        }
                        else{
                            var data_to_send = {'SERVICE':'removestack',"HOST":SERVICE_GATEWAY, 'REQUEST':{'token_solution':TOKEN_SOLUTION,
                            'auth':{'user':MESH_USER,'workspace':MESH_WORKSPACE}}};
    
                            $.ajax({
                                type: "POST", // la variable type guarda el tipo de la peticion GET,POST,..
                                url: 'includes/xel_Request.php', //url guarda la ruta hacia donde se hace la peticion
                                data: data_to_send, // data recive un objeto con la informacion que se enviara al servidor
                                beforeSend: function() {
                                    notificarUsuario("Removing stack", 'info')
                                },
                                success: function(result) {  
                                    notificarUsuario(result['message'], 'warning')
                                    Toggle_run_button()

                                    itt = parseInt($("#dag_iterations").val()) // execute again if there are more iterations
                                    if(itt>=2){
                                        $("#dag_iterations").val(itt-1)
                                        setTimeout(Exec_graph({"force":true}),1000)
                                    }
                                    else{console.log("no more iterations")}

                                },
                                error: function(XMLHttpRequest, textStatus, errorThrown){
                                    error_result = XMLHttpRequest['responseJSON']
                                    postExecutionStop(0,true,message=error_result['message'])
                                },
                                dataType: 'json' // El tipo de datos esperados del servidor. Valor predeterminado: Intelligent Guess (xml, json, script, text, html).
                            });
                            // end remove stack

                        }

                    }
                    else{
                        console.log(LIST_TASK_OVER)
                        setTimeout(function() {
                            ServiceMonitor(token_project,token_solution,list_remain_task)
                        }, 2000)
                        //setTimeout(ServiceMonitor(token_project,token_solution,list_remain_task), 4000);
                    }

                }

            }
            else{console.log("algo salio mal al obtener el status de los procesos")}

        },error: function(XMLHttpRequest, textStatus, errorThrown){
            error_result = XMLHttpRequest['responseJSON']
            if (XMLHttpRequest.status==401){ //session expired
                sesionExpirada()
            }
            if (XMLHttpRequest.status==404){ //session expired
                console.log("something happend, trying again")
                console.log(token_project)
                console.log(token_solution)
                console.log(data_request)
                //ServiceMonitor(token_project,token_solution,list_remain_task)
            }
        }
    }).fail(function(){
        notificarUsuario("Solution has stopped by an unexpected failure.", 'warning')
        Toggle_run_button()
        $(".serviceLoadingIcon").html("")
    });
}

function DownloadProject(){
    let data_request = {'SERVICE':'getfile' ,'REQUEST':{'data':{},'type':""},"METADATA":{}}
    data_request.REQUEST.data.token_user=MESH_USER //por defecto solo se usa este usuario
    data_request.REQUEST.data.token_solution=TOKEN_SOLUTION 
    data_request.REQUEST.type ="PROJECT"
    get_file(data_request,false)

}

function download_data_pipe(rn,task,file_ext,file_name=null,raw=false,To_DataView=false){ //descargar datos de cualquier punto de el grafo
    notificarUsuario("Data is almost ready", 'info');
    //formatar peticion dependiendo de si son datos crudos o no
    let data_request = {'SERVICE':'getfile' ,'REQUEST':{'data':{},'type':""},"METADATA":{}}
    data_request.REQUEST.data.token_user=MESH_USER //por defecto solo se usa este usuario
    data_request.REQUEST.data.token_solution=rn 
    data_request.REQUEST.data.task=task
    data_request.REQUEST.data.catalog=MESH_WORKSPACE

    if (file_ext!=""){
        data_request.METADATA.file_ext=file_ext
    }
    else{
        data_request.METADATA.file_name=file_name
        data_request.REQUEST.data.filename=file_name // solo se agrega filename si se cumple esta condicion
    }

    if (raw){ //si raw es true, se obtienen los datos iniciales
        data_request.REQUEST.type ="LAKE"
        get_file(data_request,To_DataView)
    } 
    else {
        data_request.REQUEST.type ="SOLUTION"
        get_file(data_request,To_DataView)
    } 
}

function descargarArchivo(url,jsonDatos) {
    var jsonDatos = JSON.stringify(jsonDatos);

    // Crear una instancia de XMLHttpRequest
    var xhr = new XMLHttpRequest();
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.withCredentials = true; // Enviar las cookies
    xhr.responseType = 'blob'; // Establecer el tipo de respuesta como Blob


    // Manejar el evento de carga
    xhr.onload = function() {
      if (xhr.status === 200) {
        // Obtener el nombre del archivo del encabezado Content-Disposition
        var contentDisposition = xhr.getResponseHeader('Content-Disposition');

        var filename = contentDisposition.match(/filename=([^;\n]+)/)[1];

        // Crear un enlace para la descarga
        var link = document.createElement('a');
        link.href = window.URL.createObjectURL(xhr.response);
        link.download = filename;
  
        // Simular el clic en el enlace para iniciar la descarga
        link.click();
      } else {
        console.error("Error al descargar el archivo.");
      }
    };
    // Manejar el evento de error
    xhr.onerror = function() {
      console.error("Error en la solicitud.");
    };
    // Enviar la solicitud AJAX con los datos del JSON como cuerpo de la petición
    xhr.send(jsonDatos);
  }
  


function get_file(data_request,To_DataView=false){

    if (To_DataView){
        $.ajax({ // ajax para rellenar valores de temporal
            url: 'includes/xel_getdata.php',
            type: 'POST',
            data:data_request,
            success: function(liga) {  
                console.log(liga)
                if(To_DataView){
                    liga=`DataView.php?url=${liga}`
                    $("#invisible_link").html(`<a id='temporal_link' href='${liga}' target='_blank' ></a>`)
                    $('#temporal_link').get(0).click();
                    $("invisible_link").html("")
                }
                else{ //download
                    $("#invisible_link").html(`<a id='temporal_link' href='${liga}' target='_blank' ></a>`)
                    $('#temporal_link').get(0).click();
                    $("invisible_link").html("")
                }
                console.log(liga)
    
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                error_result = XMLHttpRequest['responseJSON']
                if (XMLHttpRequest.status==401){ //session expired
                    sesionExpirada()
                }
            }
        }).fail(function(){console.log("error al conectarse")});
    }
    else{
        descargarArchivo('includes/xel_getdata.php',data_request)

    }

}

function CreateDynamicTable(dataset,column_list,id_table,div_container_id,title,table_class="hover w-auto dt-responsive nowrap"){
    content = `<h3>${title}</h3> <table class="table ${table_class}" style="width:100%" id="${id_table}"> <thead> <tr>`

    column_list.forEach(function(h){ //headers
        content += `<th scope="col">${h}</th>`
    });

    content += `</tr></thead><tbody>`
    dataset.forEach(function(item){ //se rellena la tabla
        content +=`<tr>`
        column_list.forEach(function(h){
            content += `<td>${item[h]}</td>`
        });
        content +=`</tr>`
    });
    content +=`</tbody></table>`   
    
    $(div_container_id).html(content)
}

// funcion para inspeccionar un resumen del dataset
function Inspect_datasource(filename=null,force=false,token_solution=null,task=null,type_dataset="LAKE",catalog=MESH_WORKSPACE){
//reestructure data
    Toggle_Loader("show","Collecting metadata...")
    context={token_solution:token_solution,task:task,type_dataset:type_dataset,catalog:catalog}
    console.log(context)
    xel_describe_dataset(filename=filename,force=force,context=context).done(function(result){
        description = JSON.parse(result).info
    
        combo_label="inspctDS"
        $('#modal_inspect_body').html(`<div class="col-12"><select class="form-control selectpicker" id="select_${combo_label}" 
            onChange="SELECT_ShowValue('${combo_label}',this)"> <option value=""></option><select></div> <hr> `);
        sp = $(`#select_${combo_label}`)
        
        //create sections for each file described
        Object.keys(description.files_info).forEach(function(key) {
            name = key.replaceAll(".","-").replaceAll("/","-F-")
            sp.append(`<option value="${name}"> ${key} </option>`);
            $('#modal_inspect_body').append(`<div style="display:none;" id="${combo_label}_${name}" class="col-12 align-self-center ${combo_label}" ></div>`)
        });
        // ------------------------
    
    //describe each file
        Object.keys(description.files_info).forEach(function(key) { 
            name = key.replaceAll(".","-").replaceAll("/","-F-")
            desc = description.files_info[key]
            obj_info = []
            for (var clave in desc['info']){
                value_json = desc['info'][clave]
                new_val_json = {}
                new_val_json['column'] = clave
                new_val_json = {...new_val_json,...value_json}
                obj_info.push(new_val_json)
            }
        
            // EXTRACT VALUE FOR HTML HEADER. 
            var col = [];
            for (var i = 0; i < obj_info.length; i++) {
                for (var key in obj_info[i]) {
                    if (col.indexOf(key) === -1) {
                        col.push(key);
                    }
                }
            }
    
    
            // template for tables
            $(`#${combo_label}_${name}`).html(`
            <div class="col-12 align-self-center" id="${combo_label}_${name}_summary"></div> <hr>
            <div class="col-12 align-self-center" id="${combo_label}_${name}_sample"></div>
            `)
    
            // CREATE DYNAMIC TABLE for summary.
            id_table=`table_${combo_label}_${name}`
            div_container_id = `#${combo_label}_${name}_summary`
            CreateDynamicTable(obj_info,col,id_table,div_container_id,"Summary")
            // ========================================================
            // CREATE DYNAMIC TABLE FOR SAMPLE ROWS
            id_table=`table_sample_${combo_label}_${name}`
            div_container_id = `#${combo_label}_${name}_sample`
            CreateDynamicTable(desc.sample,desc.columns,id_table,div_container_id,"Sample",table_class="hover w-auto")
            // ========================================================
    
        });
        // SHOW MODAL
        $(`#select_${combo_label}`).selectpicker("refresh")
        Toggle_Loader("hide")
        Toggle_Modal("show",'#modal_inspect')


    });
}


function data_to_csv(datatodownload,namefile="data",ext="json"){
    console.log(typeof datatodownload)
    console.log(ext)
    if (typeof datatodownload === 'object' && !Array.isArray(datatodownload)){
        tsk = namefile.split("-")
        tsk = tsk[tsk.length -1]
        console.log(tsk)
        if (tsk =="graphics"){
            //console.log(encodeURIComponent(datatodownload['data']))
            exportBINFile(datatodownload['data'],namefile+".png")
        }
        else if (ext =="json"){
            exportTXTFile(datatodownload, namefile)
        }
        else if (ext !="json") {
            exportBINFile(datatodownload,namefile+"."+ext)
        }
    }
    else{
        if (ext!="csv") {
            exportBINFile(datatodownload,namefile+"."+ext)
        }
        else{
            CSVheaders = Object.keys(datatodownload[0]);
            exportCSVFile(CSVheaders, JSON.parse(JSON.stringify(datatodownload)), namefile);
        }
    }

}




// TOOL
function transform_dag(parent,dag){ //transform ignora la primera caja (la root)
    parent.children.forEach(function(value, key) {
        if (value.name.includes("-")){ service_name= value.name.split("-")[0];ac_name = value.name.split("-")[1];}
        else {service_name= value.name; ac_name = value.name}

        new_service = {
            id: value.id,
            alias: value.alias,
            service: service_name,
            children: []
        }
        dag.push(new_service)
        if('actions' in value.params){ 		// check if there are actions in params
            ACTIONS = []
            if (typeof value.params.actions === 'string' || value.params.actions instanceof String) {value.params.actions = [value.params.actions]}
            value.params.actions.forEach(function(a, index, array) {
                //ACTIONS = ACTIONS + a.charAt(0); 
                ACTIONS.push(a)
            });
            new_service['actions']=ACTIONS; console.log(ACTIONS);
        } //end if actions

        if('pattern' in value){ 	
            new_service['pattern'] = value['pattern']
        }

        //add service into params if service is TS
        if (service_name=="TS"){value.params['service']=ac_name}

        //here must be modified the params (some arrays must be string)
        Parse_params(value.params, ac_name)

        //if actions then params must be split
        new_params = {}
        if('actions' in value.params){ 		// check if there are actions in params
            value.params.actions.forEach(function(a, index, array) {
                new_params[a]= value.params
                //delete new_params[a.charAt(0)]; 
            });
        } //end if actions
        else{ new_params = value.params}

        // remove tabs and line jumps
        eliminarCaracteres(new_params)
        //add params to service
        new_service['params'] = new_params
        
        //do teh same for all childrens
        transform_dag(value,new_service.children)
    });
}

function eliminarCaracteres(objeto) {
    // Comprobamos si el objeto es un objeto y no es null
    if (typeof objeto === 'object' && objeto !== null) {
      // Iteramos sobre todas las propiedades del objeto
      for (let clave in objeto) {
        // Verificamos si el valor de la propiedad es un string
        if (typeof objeto[clave] === 'string') {
          // Eliminamos los caracteres de tabulación y salto de línea
          objeto[clave] = objeto[clave].replace(/[\t\n]/g, '');
        } else if (typeof objeto[clave] === 'object') {
          // Si el valor de la propiedad es un objeto, llamamos recursivamente a la función
          eliminarCaracteres(objeto[clave]);
        }
      }
    }
  }

function Parse_params(params,service_name){
    console.log("parsing params")
    services_with_string =["preprocessing","deeplearning","clustering","ANOVA","describe","transform_ds","clustering_service","statistics","regression","maps"]
    if (services_with_string.includes(service_name)){
        if ("list_var_x" in params) {params.list_var_x = params.list_var_x.toString()}
        if ("columns" in params) {params.columns = params.columns.toString()}
        else if ("variables" in params) {params.variables = params.variables.toString()}
        else if ("variable" in params) {params.variable = params.variable.toString()}
        else if ("column" in params) {params.column = params.column.toString()}
        if ("group_columns" in params) {params.group_columns = params.group_columns.toString()}

        console.log("params parsed")

        // eliminar 
        console.log(params)
    }
    //variable x, y, z
    if (service_name == "graphics")
    {
        params['variables'] = [params.x]
        if(params.y !=""){params.variables.push(params.y)}
        if(params.z !=""){params.variables.push(params.z)}
        if(params.point_label =="") {delete params.point_label}
        if(params.labels ==""){delete params.labels}
    }
    if (service_name == "cleaningtools" ){
        iconToRemove =  ` <a href="#" onclick="remove_list_element(this)" data-toggle="tooltip" title="remove this"><span class="glyphicon glyphicon-minus" aria-hidden="true"></span></a>`
        params.ReplaceWithNa.forEach(function(word, index, array) {
            neWORD = word.replace(iconToRemove,"")
            neWORD=neWORD.replace(/\s/g, "");
            if (!isNaN(Number(neWORD))){neWORD = Number(neWORD)} //to number
            console.log(neWORD)
            params.ReplaceWithNa[index] = neWORD
        });
    }
}

function Save_configurations(Modal_selector="#modal_edition"){
    sourceid = $(Modal_selector).data("sourceId")

    BOX = demoflowy_lookForParent(sourceid); //columnas del servicio

    BOX.pattern={"spec":{}}

    BOX.pattern['kind']=  $(`#patt-kind`).selectpicker('val')
    BOX.pattern['active']=  document.getElementById('patt-active').checked 
    BOX.pattern['limit_threads']=  document.getElementById('patt-limit_threads').checked 
    BOX.pattern['workers']=  $(`#patt-workers`).val()
    BOX.pattern['spec']['reduce_mode']=  $(`#patt-reduce_mode`).selectpicker('val')
    BOX.pattern['spec']['variables']=  $(`#patt-variables`).val().split(",")
    BOX.pattern['spec']['level_to_process']=  $(`#patt-level_to_process`).selectpicker('val')

    Toggle_Modal("hide","#modal_config")
}

function Show_configurations(id_servicio){
   //rellenar comboboxes
   lista_comboboxes = ["#patt-variables"]
   if (id_servicio==""){
    id_servicio = $(`#modal_edition`).data("sourceId");
   }

   BOX = demoflowy_lookForParent(id_servicio); //columnas del servicio

    Activate_Autcomplete(`.autocomplete-column`,Modal_selector="#modal_edition")

   if (Object.keys(BOX).includes("pattern")){
        p_info = BOX.pattern
        console.log(p_info)
        $(`#patt-kind`).selectpicker('val',p_info['kind'])
        if (p_info['active']){$('#patt-active').bootstrapToggle('on')}else{$('#patt-active').bootstrapToggle('off')}
        $(`#patt-variables`).val(p_info['spec']['variables'].toString() )
        if (p_info['limit_threads']){$('#patt-limit_threads').bootstrapToggle('on')}else{$('#patt-limit_threads').bootstrapToggle('off')}
        $(`#patt-workers`).val(p_info['workers'])
        $(`#patt-reduce_mode`).selectpicker('val',p_info['spec']['reduce_mode'])
        $(`#patt-level_to_process`).selectpicker('val',p_info['spec']['level_to_process'])
   }else{
    $(`#patt-kind`).selectpicker('val',"")
    $('#patt-active').bootstrapToggle('off')
    $(`#patt-variables`).val()
    $('#patt-limit_threads').bootstrapToggle('on')
    $(`#patt-workers`).val(2)
    $(`#patt-reduce_mode`).selectpicker('val',"")
    $(`#patt-level_to_process`).selectpicker('val',"")

   }

   
   //$("#modal_mapAAS").modal("show")
   Toggle_Modal("show","#modal_config")
   $('.selectpicker').selectpicker('refresh')

   OptionsHandler(document.getElementById("patt-kind"))

}

function OptionsHandler(combobox,onlyhide=false){
    //hide everything with the servopt attribute
    // el atributo se llama opt-<id>
    id_s = combobox.id
    console.log("values for " + id_s)
    $(`[opt-${id_s}]`).hide()
    if (onlyhide){return 0} //only hide option. Use it to initialize

    valor = combobox.value
    if (valor !== "undefined" && valor !== ""){
        console.log(valor)
        $( `[opt-${id_s}~=${valor}]`).show();
    }
    else{
        console.log("el valor es undefined")
    }

    //init functions
    init_visual_in_modal()

}


function ChangeVisibileOptionsOfService(combobox,onlyhide=false){
    //hide everything with the servopt attribute
    console.log("hidding..")
    $("[servopt]").hide()
    if (onlyhide){return 0} //only hide option. Use it to initialize

    // show only options with the value of combobox
    if (combobox ==""){
        //toca recorrer todos los combos con occhange en ellos
        list_comboboxes = $('#modal_edition [onchange] > option:selected')

        n = list_comboboxes.length
        
        if (n==1){
            valor = list_comboboxes[0].value
            if (valor!=""){$( "[servopt~= "+valor+" ]").show();}
        }
        else{
            $.each(list_comboboxes, function() {   
                valor = this.value
                console.log(valor)
                if (valor!=""){$( "[servopt~= "+valor+" ]").show();}
            });

        }
    }
    else{
        valor = combobox.value
        console.log(valor)
        $( "[servopt~='"+valor+"']").show();
    }
}


function show_options_graph(){
    kind_graph = $("#kind").val()
    console.log(kind_graph)
    if (kind_graph=="scatter" || kind_graph =="linear"){
        $('#option_1').show();
        $('#option_2').hide();

    } else if (kind_graph=="hist"){
        $('#option_1').hide();
        $('#option_2').show();
    } 
}


function DeleteDataset(id_row,filename,table){
    let data_request = {'SERVICE':`workspace/delete/${MESH_USER}/${MESH_WORKSPACE}/${filename}`}

    $.ajax({ // ajax para rellenar valores de workspaces
        url: 'includes/xel_get_Request.php',
        type: 'POST',
        dataType: 'json',
        data:data_request,
        success: function(result) {  
            $(`#${table}`).DataTable().row($(`#file_${id_row}`)).remove().draw()
            notificarUsuario("Dataset deleted","warning")
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            error_result = XMLHttpRequest['responseJSON']
            if (XMLHttpRequest.status==401){ //session expired
                sesionExpirada()
            }
        }
    }).fail(function(){console.log("error al conectarse")});
}

function LoadExistingDataset(sourceId,filename,metadata=null,workspace=null){
    console.log(workspace)
    if (workspace == null){
        workspace=MESH_WORKSPACE
        console.log("es nulo")
    }
    else{ MESH_WORKSPACE = workspace}
    console.log(workspace)


    Toggle_Loader("show","mining dataset...")
    demoflowy_saveChanges()
    force_describe =$("#force_describe").is(':checked')
    if (force_describe==="undefined" || force_describe==""){
        force_describe=false
    }
    else{
        Toggle_Loader("message","Mining metadata...")
    }
    notificarUsuario("Collecting metadata, please wait...","info")
    Set_DatasourceMap({'token_user':MESH_USER,'catalog':workspace,'filename':filename},'LAKE')

    if(metadata ==null){ //si no se proporciona metadata, se hace la consulta. normalmente esto es para los datos recien procesados
        xel_describe_dataset(filename=filename,force=force_describe).done(function(result){
            metadata = JSON.parse(result).info
            Handler_condition_GetData(sourceId,metadata,true,filename)
            notificarUsuario("Metadata obtained","success")
            // se fuerza el cierre del modal activo
            //$(".modal.fade.show").modal("hide")
            Toggle_Modal("hide")
            Toggle_Loader("hide")
        });

    }
    else{
        Handler_condition_GetData(sourceId,metadata,true,filename)
        notificarUsuario("Metadata obtained","success")
        Toggle_Modal("hide")
        Toggle_Loader("hide")
    }
    // data was uploaded to the catalog MESH_WORKER by default of the user MESH USER
    
}

function fill_namefiles(){

    id_box = $("#modal_edition").data("sourceId")
    if_metadata_exist = reload_metadata_fromBox(id_box)
    if (if_metadata_exist){
        let BOX_info = get_metadata_box(id_box,source=null,get_all=true)

        $('.namefiles-tree').jstree({
            'core' : {
                "themes": {"variant": "large","responsive": false},
                'data' : BOX_info.tree
            },
            "types" : {
                "default": {
                    "icon": "fa fa-folder treeFolderIcon",
                },
                "file" : {
                    "icon" : "far fa-file"
                }
                },
                "plugins" : [
                "contextmenu", "checkbox", "search",
                "state", "types", "wholerow"
                ]
        });
    }
}

function fill_namefiles_select(sp){

    id_element = sp.id
    sp = $("#"+id_element)
    
    id_box = $("#modal_edition").data("sourceId")

    

    let BOX = demoflowy_lookForParent(id_box); //fill select

    BOX_columns = BOX.service_metadata.father.list_of_files
    BOX_columns.forEach(function(col){
        sp.append('<option value="'+col+'">' + col + '</option>');
    });
    
    sp.attr("data-size","5")
    sp.attr("data-live-search","true")
    sp.addClass("selectpicker");
    sp.selectpicker('refresh');


}


function UpdateSelectBoxByClass(class_name){
    if(class_name!=null){
        console.log("se actualiza con click")
        $("."+class_name).click()
    }
}


function Handler_selectedFileNames(id_source,id_destination,from_values=null){
    // aqui se crean los formularios para cada archivo seleccionado
    if (from_values == null){
        list_selected_files = $(id_source).jstree().get_checked(["full"]) // se obtienen los nodos seleccionados
    }
    else{
        list_selected_files = from_values
    }

    $("#"+id_destination).html("")
    // div destino 
    var id_tmp = 1
    list_selected_files.forEach(function(obj){
        if (obj.type=="file"){
            pathfile = obj.original.path
            //create control
            htmlstring =`
                <div class="form-group row m-2"> 
                    <label for="txttype" class="col-sm-12 col-form-label col-form-label-sm">Keys of ${obj.original.path}</label>
                    <div class="col-sm-12">
                        <input id="file_${id_tmp}" type="text" class="form-control">
                    </div>
                </div>`
            $("#"+id_destination).append(htmlstring)
            //se le activa el autocomplete
            AutocompleteByFileInfo("file_"+id_tmp, obj.original.path)
            id_tmp++
        }
    });

}

function fillworkspaces(sp,Modal_selector="#modal_datasource"){

    var id_element = sp.id
    var sp = $("#"+id_element)
    //sp.html("<option></option>")

    let data_request = {'SERVICE':`workspace/list/${MESH_USER}`}

    $.ajax({ // ajax para rellenar valores de workspaces
        url: 'includes/xel_get_Request.php',
        type: 'POST',
        dataType: 'json',
        data:data_request,
        success: function(result) {  
            lista_workspaces = result.info.workspaces
            lista_workspaces.forEach(function(col){
                sp.append('<option value="'+col+'">' + col + '</option>');
            });
            console.log(lista_workspaces)
            sp.addClass("selectpicker");
            sp.selectpicker('refresh');

            //al ser un proceso asincrono, se debe asignar el valor guardado de los parametros desdes aqui
            // SOLO SIRVE PARA EL MODAL DE DATASOURCES
            let canvasId = $(Modal_selector).data('sourceId');
            let parent = demoflowy_lookForParent(canvasId);
            sp.selectpicker('val',  parent.params[id_element]);
            
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            error_result = XMLHttpRequest['responseJSON']
            if (XMLHttpRequest.status==401){ //session expired
                sesionExpirada()
            }
        }
    }).fail(function(){console.log("error al conectarse")});

}
function fillWorkspaceFilesliest(if_multiple=false){
    MESH_WORKSPACE= $("#user_workspace").val()
    sourceId = $('#modal_datasource').data('sourceId');


    let data_request = {'SERVICE':`workspace/list/${MESH_USER}/${MESH_WORKSPACE}`}

    $.ajax({ // ajax para rellenar valores de workspaces
        url: 'includes/xel_get_Request.php',
        type: 'POST',
        dataType: 'json',
        data:data_request,
        success: function(result) {  
            lista_workspaces = result.info.list_files_details
            //se crea la tabla 
            headeres = Object.keys(lista_workspaces[0])
            console.log(headeres)
            content = ""
            content += `
                <table class="table table-hover table-sm dt-responsive nowrap" id="table_LoadedFiles">
                    <caption>List of files in ${MESH_WORKSPACE}</caption>
                    <thead>
                        <tr>`
            headeres.forEach(function(h){
                content += `<th scope="col">${h}</th>`
            });
            content +=`<th scope="col">Actions</th>` //column to load data
            content += `</tr></thead><tbody>`


            file_id = 0
            lista_workspaces.forEach(function(file){ //se rellena la tabla
                content +=`<tr id="file_${file_id}">` // se añade un id par apoder borrarlo despues
                headeres.forEach(function(h){
                    content += `<td>${file[h]}</td>`
                });
                if (if_multiple){
                    content +=`<td><button onclick="ShoppingCar_add_element('${MESH_WORKSPACE}/${file['filename']}','${MESH_WORKSPACE}/${file['filename']}', '.ShoppingCar-list')" class="btn btn-outline-info">Add <i class="far fa-check-circle"></i></button>
                    </td>`
                }
                else{
                    content +=`<td><button onclick="LoadExistingDataset('${sourceId}','${file['filename']}')" class="btn btn-outline-info">Read <i class="far fa-check-circle"></i></button>
                    <button onclick="DeleteDataset('${file_id}','${file['filename']}','table_LoadedFiles' )" class="btn btn-outline-danger">Delete <i class="fas fa-trash"></i></button>
                    </td>`
                }

                content +=`</tr>`
                file_id+=1
            });
            content +=`</tbody></table>`

            $("#datasource-table").html(content)
            $("#table_LoadedFiles").DataTable({
                responsive: true,
                "lengthMenu": [[5, 10, 25, 50], [5, 10, 25, 50]],
                "order": [[ 2, "desc" ]]
            } );
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            error_result = XMLHttpRequest['responseJSON']
            if (XMLHttpRequest.status==401){ //session expired
                sesionExpirada()
            }
        }
    }).fail(function(){console.log("error al conectarse")});

}

function get_metadata_box(box_id,source=null,get_all=false,source_mode="select"){

    if_metadata_exist = reload_metadata_fromBox(box_id)
    if (!if_metadata_exist){ console.log("no existen columnas para rellenar los comboboxes"); return {};}
    
    let BOX = demoflowy_lookForParent(box_id); //fill select

    if (source== null){
        parentfilename = BOX.service_metadata.father.parent_filename
    }
    else{
        if (source_mode=="select"){
            parentfilename =$(source).val()
        }
        else if (source_mode=="filename"){
            parentfilename =source
        }
        else{
            parentfilename=null
        }

        if (parentfilename == null){
            notificarUsuario(`No FileSource selected`,"warning")
            parentfilename = ROOT_METADATA.parent_filename
            if (get_all){ return ROOT_METADATA }       
            return ROOT_METADATA.files_info[parentfilename]
        }
    }

    if (BOX.service_metadata.father.files_info[parentfilename]===undefined){
        //notificarUsuario(`File ${parentfilename} has no columns (could be a zip). Check the configuration of the box. `,"warning")
        parentfilename = ROOT_METADATA.parent_filename   
        if (get_all){ return ROOT_METADATA }          
        return ROOT_METADATA.files_info[parentfilename]
    }

    //console.log("se obtuvo la metadata del padre")
    if (get_all){ return BOX.service_metadata.father } 
    return BOX.service_metadata.father.files_info[parentfilename]
}


function fillselect(sp,mult=true,source=null,add=null){
    id_element = sp.id
    console.log(id_element)
    sp = $("#"+id_element)
    sp.empty()
    sp.addClass("selectpicker");

    id_box = $("#modal_edition").data("sourceId")

    BOX_info = get_metadata_box(id_box,source=source)

    const isEmpty = Object.keys(BOX_info).length === 0 //si es null no se hace nada
    if(isEmpty){return false}


    if (add!=null){
        sp.append('<option value="'+add+'">' + add + '</option>');
    }

    BOX_columns = BOX_info.columns
    BOX_columns.forEach(function(col){
        sp.append('<option value="'+col+'">' + col + '</option>');
    });
    
    // addd multiple attributte

    if(mult){
        console.log("se activan las multiples opciones")
        sp.attr("multiple","multiple")
        sp.attr("data-actions-box","true")
    }

    sp.attr("data-size","5")
    sp.attr("data-live-search","true")
    sp.selectpicker('refresh');

}


function ChangeOrientationJSON(obj_json){
    Columnas = Object.keys(obj_json[0]);

    Result_json={}
    for(var j = 0; j < Columnas.length; j++){ // se recorre cada columna
        Result_json[Columnas[j]]=[] //inicializar arrays
    }

    for(var i = 0; i < obj_json.length; i++){ // se recorre cada registro
        for(var j = 0; j < Columnas.length; j++){ // se recorre cada columna
            Result_json[Columnas[j]].push(obj_json[i][Columnas[j]])
        }
    }

    return Result_json
}


function ShowModal_map_AAS(rn,id_servicio){

    // vaciar lista del selectbox 
    $(`select[name=SOM-lat]`).empty();
    $(`select[name=SOM-lon]`).empty();
    $(`select[name=SOM-temporal]`).empty();
    $(`select[name=SOM-spatial-filter]`).empty();
    $(`select[name=SOM-value-filter]`).empty();
    $(`select[name=SOM-columna_class]`).empty();
    $(`select[name=SOM-values]`).empty();
    $(`select[name=SOM-id]`).empty();

    //rellenar comboboxes
    lista_comboboxes = ["#SOM-lat","#SOM-lon","#SOM-temporal","#SOM-spatial-filter","#SOM-value-filter","#SOM-columna_class","#SOM-values","#SOM-id"]
    lista_comboboxes.forEach(function(combo){
        sp = $(combo)
        let BOX = demoflowy_lookForParent(id_servicio); //columnas del servicio
        c = BOX.service_metadata.this //columnas que procesa el servicio
        columnas_del_servicio = c.files_info[c.parent_filename].columns

        if (!(columnas_del_servicio===null)){
            BOX_columns = columnas_del_servicio
            sp.append('<option value=""> </option>');
            BOX_columns.forEach(function(col){
                sp.append('<option value="'+col+'">' + col + '</option>');
            });
        }
    })

    $(`#SOM-id_service`).val(id_servicio)
    $(`#SOM-rn`).val(rn)
    console.log('lon' in PARAMS_MAP)

    var_lat =  ('lat' in PARAMS_MAP) ? PARAMS_MAP.lat:'lat';
    var_lon = ('lon' in PARAMS_MAP) ? PARAMS_MAP.lon : 'lon';
    var_temporal = ('temporal' in PARAMS_MAP) ? PARAMS_MAP.temporal : 'year';
    var_spatial_filter = ('spatial_filter' in PARAMS_MAP) ? PARAMS_MAP.spatial_filter : 'ent_ocurr';
    var_value_filter = ('value_filter' in PARAMS_MAP) ?  PARAMS_MAP.value_filter :'';
    var_label = ('label' in PARAMS_MAP) ? PARAMS_MAP.label :'class';
    var_values = ('values' in PARAMS_MAP) ? PARAMS_MAP.values :'';
    var_k = ('k' in PARAMS_MAP) ?  PARAMS_MAP.k :'k';
    var_id = ('id' in PARAMS_MAP) ? PARAMS_MAP.id : '';


    $(`#SOM-lat`).selectpicker('val', var_lat);
    $(`#SOM-lon`).selectpicker("val",var_lon);
    $(`#SOM-temporal`).selectpicker('val', var_temporal);
    $(`#SOM-spatial-filter`).selectpicker('val', var_spatial_filter);
    $(`#SOM-value-filter`).selectpicker('val', var_value_filter);
    $(`#SOM-columna_class`).selectpicker('val', var_label);
    $(`#SOM-values`).selectpicker('val', var_values);
    $(`#SOM-k`).selectpicker('val', var_k);
    $(`#SOM-id`).selectpicker('val', var_id);

    
    //$("#modal_mapAAS").modal("show")
    Toggle_Modal("show","#modal_mapAAS")
    $('.selectpicker').selectpicker('refresh')
}


function Handler_map(raw=false){ //rellena los comboboxes y prepara funciones para consulta
    // validar
    var form = document.getElementById('form_map');
    if (form.checkValidity() === false) {
        console.log("hay datos sin rellenar")
        return 0
    }


    PARAMS_MAP.opcion_espacial= $(`select[name=SOM-lat]`).val();
    PARAMS_MAP.method=$(`select[name=SOM-type]`).val();
    PARAMS_MAP.lat= $(`select[name=SOM-lat]`).val();
    PARAMS_MAP.lon= $(`select[name=SOM-lon]`).val();
    PARAMS_MAP.temporal= $(`select[name=SOM-temporal]`).val();
    PARAMS_MAP.spatial_filter= $(`select[name=SOM-spatial-filter]`).val();
    PARAMS_MAP.value_filter= $(`select[name=SOM-value-filter]`).val();
    PARAMS_MAP.values= $(`select[name=SOM-values]`).val();
    PARAMS_MAP.id=$(`select[name=SOM-id]`).val();
    PARAMS_MAP.label=$(`select[name=SOM-columna_class]`).val();
    PARAMS_MAP.k=$(`#SOM-k`).val();
    PARAMS_MAP.task= $("#SOM-id_service").val();
    PARAMS_MAP.rn= $("#SOM-rn").val();

    //aqui se descargan los datos y se guardan en PARAMS_MAP

    //$("#SOM-loading").html("<img style='width:25%; height: 160px; margin-top: 50px; position: fixed; margin-left: 170px;' src='resources/imgs/loading.gif'></img")

    rn = $("#SOM-rn").val();
    task = $("#SOM-id_service").val();


    // aqui creo el combobox y mando llamar Show_data_on_map con un posible valor temporal
    $("#results_panel").html("")
    $("#results_panel").append("<div id='aas_temporal_combo' class='row col-12 justify-content-md-center'></div>"); //div para combo de fechas
    $("#results_panel").append("<div id='aas_criteria' class='row col-12 justify-content-md-center'></div>"); // div para combo de criterios
    $("#results_panel").append(`<button onclick="Show_data_on_map()" class="btn btn-outline-info btn-block" style="margin:5px">Request</button>`); // boton para mostrar resultados
    $("#results_panel").append("<div id='filtros-dinamicos' class='row col-12' style='max-height:400px; overflow-y:auto;'></div>"); //div para filtros
    $("#results_panel").append("<div id='clust_res' class='row col-12'></div>"); //div para resultados

    //vaciar lista de filtros global
    lista_global_filtros={}


    if (PARAMS_MAP.temporal=="" || PARAMS_MAP.lat=="" || PARAMS_MAP.lon==""){
        notificarUsuario("Error")
        return 0
    }

    let data_request = {'SERVICE':'DatasetQuery' ,'REQUEST':{'data':{},'type':"SOLUTION"}}
    data_request.REQUEST.data.token_user=MESH_USER //por defecto solo se usa este usuario
    data_request.REQUEST.data.token_solution=PARAMS_MAP.rn
    data_request.REQUEST.data.task=PARAMS_MAP.task

    data_request.REQUEST.ask = [{"request":"unique","value":PARAMS_MAP.temporal}]
    $.ajax({ // ajax para rellenar valores de temporal
        url: 'includes/xel_Request.php',
        type: 'POST',
        dataType: 'json',
        data:data_request,
        success: function(result) {  
            console.log(result)
            lista_temporal = result.info[0]
            lista_temporal = lista_temporal.sort(function(a, b) {return a - b;});
            dates="<option value=''> </option>"
            lista_temporal.forEach(function(item, index) {
                dates += "<option value='" + item + "'>" + item + "</option>";
            });
            //rellenar combobox de criterios
            $("#aas_temporal_combo").append(`<label>Temporal: </label> <select class='form-control selectpicker idfechas' data-live-search="true" data-size="5" data-style="btn-info" width='80%' name="combo_temporalAAS">${dates}</select><hr>`);
            $(`select[name=combo_temporalAAS]`).selectpicker("refresh")
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            error_result = XMLHttpRequest['responseJSON']
            if (XMLHttpRequest.status==401){ //session expired
                sesionExpirada()
            }
        }
    }).fail(function(){console.log("error al conectarse")});

    let data_request2 = {'SERVICE':'DatasetQuery' ,'REQUEST':{'data':{},'type':"SOLUTION"}}
    data_request2.REQUEST.data.token_user=MESH_USER //por defecto solo se usa este usuario
    data_request2.REQUEST.data.token_solution=PARAMS_MAP.rn
    data_request2.REQUEST.data.task=PARAMS_MAP.task

    if (PARAMS_MAP.value_filter!=null && PARAMS_MAP.value_filter!=undefined && PARAMS_MAP.value_filter!=""){ //el filtro por valor es opcional
        data_request2.REQUEST.ask = [{"request":"unique","value":PARAMS_MAP.value_filter}]
        $.ajax({ // ajax para rellenar valores de criterio
            url: 'includes/xel_Request.php',
            type: 'POST',
            dataType: 'json',
            data:data_request2,
            success: function(result) {  
                console.log(result)
                lista_criteria = result.info[0]
                //lista_temporal = JSON.parse(result).info[0]
    
                criterios="<option value=''> </option>"
                lista_criteria.forEach(function(item, index) {
                    criterios += "<option value='" + item + "'>" + item + "</option>";
                });
                //rellenar combobox de fechas
                $("#aas_criteria").append(`<label>Special criteria: </label> <select data-actions-box="true" class='form-control selectpicker idfechas' data-live-search="true" data-size="5" data-style="btn-info" width='80%' name="combo_criteriosAAS">${criterios}</select><hr>`);
                $(`select[name=combo_criteriosAAS]`).selectpicker("refresh")
                $("#SOM-loading").html("")
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                error_result = XMLHttpRequest['responseJSON']
                if (XMLHttpRequest.status==401){ //session expired
                    sesionExpirada()
                }
            }
        }).fail(function(){console.log("error al conectarse")});
    }   

    $('[opth]').hide()
    Toggle_Modal("hide","#modal_mapAAS")
    $('#mytabs a[href="#results-tab"]').tab('show');
    $('#tabs_show a[href="#mapContainer"]').tab('show');

}

function Show_data_on_map(){
    //temporal_value = combobox.value
    temporal_value = $(`select[name=combo_temporalAAS]`).val()
    if (temporal_value==""){return 0}
    criterio_value =  $(`select[name=combo_criteriosAAS]`).val()

    // se obtienen los metadatos
    opcion_espacial  = PARAMS_MAP.opcion_espacial //entidad, entidad-municipio, latitud-longitud  
    col_temporal  = PARAMS_MAP.temporal 
    col_values  = PARAMS_MAP.values 
    col_value_filter = PARAMS_MAP.value_filter

    col_lat  = PARAMS_MAP.lat 
    col_lon  = PARAMS_MAP.lon

    //variable_temporal= PARAMS_MAP.columna_temporal

    //variable_clase = PARAMS_MAP.columna_class.toLowerCase()
    //variable_entidad =PARAMS_MAP.columna_entidad.toLowerCase()
    //variable_municipio =PARAMS_MAP.columna_municipio.toLowerCase()
    //lista_filtros = PARAMS_MAP.filtros
    task = PARAMS_MAP.task
    token_solution = PARAMS_MAP.rn

    let data_request = {'SERVICE':'DatasetQuery' ,'REQUEST':{'data':{},'type':"SOLUTION"}}
    data_request.REQUEST.data.token_user=MESH_USER //por defecto solo se usa este usuario
    data_request.REQUEST.data.token_solution=rn 
    data_request.REQUEST.data.task=task 

    query = "(`"+col_temporal+"` == \""+temporal_value+"\")" // QUERY CON DATOS DE TEMPORAL. ejemplo: fecha < 2019

    lista_c=""
    if (criterio_value != undefined){
        if(criterio_value.length>0){
            //criterio_value.forEach(function(criterio, c_id) {
            //    lista_c+=col_value_filter+"=='"+criterio+"' or " 
            //});
            //eliminar el ultimo or
            //lista_c = lista_c.slice(0, -4);
            lista_c+="`"+col_value_filter+"`=='"+criterio_value+"'" 
            lista_c= "("+lista_c+")" //se encierran entre parentesis
            query+= " and "+lista_c // se añade al query
        }
    }
    
    console.log(query)
    data_request.REQUEST.ask = [{"request":"query","value":query }]
    $.ajax({
        url: 'includes/xel_Request.php',
        type: 'POST',
        dataType: 'json',
        data:data_request,
        success: function(result) {  
            datos = JSON.parse(result.info[0])
            console.log(datos)
            if (datos.length < 1){
                notificarUsuario("No data for the selected values.","warning")
            }
            else{
                datatemp = ChangeOrientationJSON(datos)
                //document.bkp_data = datatemp // se guardan los datos en memoria
                SetDataOnMap(datatemp)
                $('#mytabs a[href="#3b"]').tab('show');
                $('#tabs_show a[href="#mapContainer"]').tab('show');
            }


        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            error_result = XMLHttpRequest['responseJSON']
            if (XMLHttpRequest.status==401){ //session expired
                sesionExpirada()
            }
        }
    }).fail(function(){console.log("error al conectarse")});

}

function SetDataOnMap(dataset) {
       
    method  =  PARAMS_MAP.method
    opcion_espacial  = PARAMS_MAP.opcion_espacial //entidad, entidad-municipio, latitud-longitud  
    col_temporal  = PARAMS_MAP.temporal 
    columns  = PARAMS_MAP.values 
    lista_filtros  = PARAMS_MAP.spatial_filter 
    col_label  = PARAMS_MAP.label 

    col_lat  = PARAMS_MAP.lat 
    col_lon  = PARAMS_MAP.lon
    col_id  = PARAMS_MAP.id
    col_value_filter = PARAMS_MAP.value_filter
    CantidadClusters = PARAMS_MAP.k


    $("#clust_res").html("");
    $("#clust_res").append("<div id='cluster-plot-container' style='width:100%;'></div><br>");
    $("#clust_res").append("<div id='color_scale' style='width:100%'></div><br>");
    $("#clust_res").append("<div id='boxplot-plot-container' style='width:100%;'></div><br>");
    $("#clust_res").append("<div id='Clusters_res' style='width:100%;'></div>")
    

    Crear_filtros = false
    if ($("#filtros-dinamicos").html()==""){
        Crear_filtros = true
    }


    // ============ opciones cuando no hay etiquetas de cluster ======================
    if (method=="heat"){
        // se aplica una escala de colores en base a los valores
        lista_colores = chroma.scale(["#e50000","#feffa0"]).mode('lch').colors(CantidadClusters)
        resumenes = {}
        cantidades_para_escala = []

        //se obtiene un total de todos las columnas numericas (y se crea un vector de datos)
        vector_dataset=[]
        dataset[col_id].forEach(function(row, row_idx) {
            vector_row = []
            columns.forEach(function(columna, columna_idx) {
                vector_row.push(dataset[columna][row_idx])
            });
            vector_dataset.push(vector_row)
        });

        kmeans_result = kmeans(vector_dataset,CantidadClusters)
        labels = kmeans_result.labels
        centroids = kmeans_result.centroids
        console.log(kmeans_result)
        // se añaden los resultados de kmeans 
        etiquetas_por_marcador={}
        dataset[col_id].forEach(function(id_marcador, row_idx) {
            etiquetas_por_marcador[id_marcador]= labels[row_idx]
        });

        //obtener indice de la suma de los valores deel centroide
        lista_indices_centroids =[]
        centroids.forEach(function(c, c_i) {
            indice_centroid= 0
            c.forEach(function(v, v_i) {
                indice_centroid+=v
            });
            lista_indices_centroids.push(indice_centroid)
        });

        //crear lista ordenada de los clusters
        lista_clusters_ordenados =[]
        for (i=0;i<CantidadClusters;i++){
                max_of_array = Math.max.apply(Math, lista_indices_centroids); //se obtiene el valor mayor
                cluster_id = lista_indices_centroids.indexOf(max_of_array);
        
                if (~cluster_id) {
                    lista_clusters_ordenados.push(cluster_id)
                    lista_indices_centroids[cluster_id] = null; //se remplaza por null
                }
        }

    }
    if (method=="clust"){

        
        etiquetas_por_marcador={}
        dataset[col_id].forEach(function(id_marcador, row_idx) {
            etiquetas_por_marcador[id_marcador] = dataset[col_label][row_idx]
        });

        lista_clusters_ordenados =[]
        for(var i = 0; i < CantidadClusters; i++) {
            lista_clusters_ordenados.push(i);
        }
        lista_colores = chroma.scale(["#feffa0","#e50000"]).mode('lch').colors(CantidadClusters)
    }

    //GRAFICAS
    if (columns.length>=2){ CreatePlotCluster(dataset[columns[0]],dataset[columns[1]], dataset[col_label],lista_clusters_ordenados,xlabel = columns[0], ylabel=columns[1],color_list=lista_colores,div_container="cluster-plot-container")}
    else { CreatePlotCluster(dataset[columns[0]],dataset[columns[0]],dataset[col_label],lista_clusters_ordenados,xlabel = columns[0], ylabel=columns[0],color_list=lista_colores,div_container="cluster-plot-container")}
 
    CreatePlotHistogram(dataset,columns,div_container="boxplot-plot-container")

    //cantidades_para_escala_custom = cantidades_para_escala
    //cantidades_para_escala_custom[-1] = String(cantidades_para_escala[-2])+"+"
    renderPalette('color_scale', lista_colores,lista_clusters_ordenados);


    clean_AAS() //se limpian los marcadores anteriores
    dataset[col_id].forEach(function(row, row_idx) {
        label_marcador = etiquetas_por_marcador[row]
        index_color = lista_clusters_ordenados.indexOf(label_marcador);

        if (index_color==-1){ //try as int
            index_color = lista_clusters_ordenados.indexOf(parseInt(label_marcador));
        } 

        color = lista_colores[index_color]
        

        //if(index_color==0){console.log(row)}
        var pinImage = new google.maps.MarkerImage('http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|'+color.substring(1),
        new google.maps.Size(21, 34),
        new google.maps.Point(0, 0),
        new google.maps.Point(10, 34));
        
        //contenido de la ventana
        content_window_head = "<h4>"+row+"</h4> "
        content_window_head += "<h4>lat:"+dataset[col_lat][row_idx]+"</h4> "
        content_window_head += "<h4>lon:"+dataset[col_lon][row_idx]+"</h4> "
        content_window_head += "<h4>class:"+etiquetas_por_marcador[row]+"</h4> "

        sum=0
        content_window = ""
        if (col_value_filter!=""){
            content_window += "<p style='font-size: 18px;' ><b>"+col_value_filter+":"+dataset[col_value_filter][row_idx]+"</p> <hr>"
        }

        columns.forEach(function(columna, columna_idx) { //añadir a la ventana cada parametro
            sum+=dataset[columna][row_idx]
            content_window += "<p style='font-size: 16px;' ><b>"+columna+":"+dataset[columna][row_idx]+"</p> "
        });
        content_window+= "<p style='font-size: 17px;' ><b>sub total of record</b>: "+sum+ "</p>"

        if(document.dataAAS[row]){ //si ya existe se añade mas info
            content_window +=  document.dataAAS[row].content_window
            document.dataAAS[row].content_window = content_window
            window_frame = "<div style='float: left;width: 100%;max-width: 500px; margin: 2px; padding: 2px;max-height: 500px;overflow:auto'>"+content_window_head+content_window+"</div>"
            document.dataAAS[row].infowindow.setContent(window_frame)
        }
        else{
            window_frame = "<div style='float: left;width: 100%;max-width: 500px; margin: 2px; padding: 2px;max-height: 500px;overflow:auto'>"+content_window_head+content_window+"</div>"
            // se crea el marcador
            var infowindow = new google.maps.InfoWindow({
                content: window_frame
            });
            infowindow.opened = false;
    
            coors = { lat: dataset[col_lat][row_idx], lng: dataset[col_lon][row_idx] };
    
            var marker = new google.maps.Marker({
                position: coors,
                map: document.map,
                icon: pinImage
            });
            marker.addListener('click', function() {
                infowindow.open(document.map, marker);
            });
            //console.log("se añadio marcador al mapa")
            obj_marcador = {"marker": marker,"infowindow":infowindow,"content_window":content_window,filtros:{}}
        
            //crar datos de filtros segun la lista otorgada
            lista_filtros.forEach(function(flt){
               //caso especial
                temp = String(dataset[flt][row_idx]).toLowerCase()
                obj_marcador[flt] = temp
                obj_marcador["filtros"][flt]=true
    
            })
            document.dataAAS[row] = obj_marcador; //Guardar poligono en un conjunto lleno de poligonos

        }

    });
    console.log(document.dataAAS)

    lista_filtros.forEach(function(flt){
        HabiltarFiltroDinamico("#filtros-dinamicos",flt,encabezado=Crear_filtros)
    });
    Actualizar_Filtro_datos()

}

function formatDate(date) {
    let datePart = [
      date.getMonth() + 1,
      date.getDate(),
      date.getFullYear()
    ].map((n, i) => n.toString().padStart(i === 2 ? 4 : 2, "0")).join("/");
    let timePart = [
      date.getHours(),
      date.getMinutes(),
      date.getSeconds()
    ].map((n, i) => n.toString().padStart(2, "0")).join(":");
    return datePart + " " + timePart;
  }
  

// Guardar solucion en BD
function BTN_save_solution(){
    //AUTH
    let data_request = {"SERVICE":"solution/store",'REQUEST':{'auth':{'user':MESH_USER,'workspace':MESH_WORKSPACE},'metadata':{},'DAG':[]}}

    DAG=CloneJSON(dataObject) //DAG
    data_request.REQUEST.DAG = JSON.stringify(DAG) //list of task is sent as a string, not as a dict

    if(Object.keys(DAG.children).length > 0){
        data_request.REQUEST.metadata = Metadata_collector()    //metadata
        if (data_request.REQUEST.metadata.token!=""){data_request.REQUEST.token_solution= data_request.REQUEST.metadata.token}     //TOKEN
    
        //-------------------------
        $.ajax({
            url: 'includes/xel_Request.php',
            type: 'POST',
            dataType: 'json',
            data:data_request,
            beforeSend: function() {
                $("#modal_save-solutions-icon-load").html("<div style='width:100%; height:10px;'></div><img src='resources/imgs/loader.gif'></img>");
                $("#span_solution_save_status").html("<img style='width:2vh; height:2vh;' src='resources/imgs/loading-buffering.gif'></img> Saving changes");
            },
            success: function(response) {  
                $("#modal_save-solutions-icon-load").html("")
                date = new Date()
                $("#span_solution_save_status").html('<i class="fas fa-cloud"></i> project saved. Last update: '+formatDate(date));
                
                //notificarUsuario("Solution was saved.","success")
                Set_Tokensolution(response['info']['token_solution'])
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                error_result = XMLHttpRequest['responseJSON']
                if (XMLHttpRequest.status==401){ //session expired
                    sesionExpirada()
                }
            }
        }).fail(function(){
            $("#span_solution_save_status").html('<i class="fas fa-cloud-upload-alt"></i> Unable to save changes. Last update: ')
        });

    }
    else{
        notificarUsuario("no hay un grafo para guardar","warning")
    }

}

function BTN_delete_solution(token_solution,id_row,id_table){
    let data_request = {"SERVICE":"solution/delete",'REQUEST':{'auth':{'user':MESH_USER,'workspace':MESH_WORKSPACE},"token_solution":token_solution}}
    $.ajax({
        url: 'includes/xel_Request.php',
        type: 'POST',
        dataType: 'json',
        data:data_request,
        success: function(result) {  
            console.log(result)
            if (result.status=="OK"){
                $(`#${id_table}`).DataTable().row($(`#${id_row}`)).remove().draw()
                notificarUsuario("Dataset deleted","warning")
            }
            else{
                notificarUsuario("Dataset could not be deleted","danger")
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            error_result = XMLHttpRequest['responseJSON']
            if (XMLHttpRequest.status==401){ //session expired
                sesionExpirada()
            }
        }
    }).fail(function(){console.log("error al conectarse")});

}
function BTN_retrieve_solution(token_solution,as_copy=false){
    let data_request = {"SERVICE":"solution/retrieve",'REQUEST':{'auth':{'user':MESH_USER,'workspace':MESH_WORKSPACE},"token_solution":token_solution}}
    $.ajax({
        url: 'includes/xel_Request.php',
        type: 'POST',
        dataType: 'json',
        data:data_request,
        success: function(result) {  
            console.log(result)
            result= result['info']
            // Change dataObject with the imported data.
            dataObject = JSON.parse(result.DAG);
            // Use Flowy import to add the boxes to the canvas.
            flowy.import(result.metadata.frontend);
            currentLayout = [...flowy.output().blockarr]
            // load metadata into page


            Metadata_assign(result.metadata,ignore_context=as_copy,token_solution=result.token_solution)
            canvasElementsCount = result.metadata.canvasElementsCount
            Toggle_Modal("hide")
            
            // show tab
            toDesign()

            $(".block-hoverinfo").hoverIntent( confighover )
            RemoveLoadingIcons()
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            error_result = XMLHttpRequest['responseJSON']
            if (XMLHttpRequest.status==401){ //session expired
                sesionExpirada()
            }
        }
    }).fail(function(){console.log("error al conectarse")});

}


function create_table_templates(div_container){
    // create_table_templates("table_templates")
    $(`#${div_container}`).html("")

    let data_request = {"SERVICE":"solution/list",'REQUEST':{'auth':{'user':MESH_USER,'workspace':MESH_WORKSPACE},'params':{'metadata.tags':'TEMPLATE'} }}
    
    $.ajax({
        url: 'includes/xel_Request.php',
        type: 'POST',
        dataType: 'json',
        data:data_request,
        success: function(response) {  
            console.log(response)
            id_table_container = div_container + "_modal_list-solutions-table"
            id_table = div_container + "_table-solutions"

            $('#'+div_container).append(`<div id='${id_table_container}' class='form-group col-12 table-responsive'></div>`);
            
            //headers_list = ['Enrichment','Mining','Preproccesing','Proccesing.','Validation','Visualization']
            //headers_only_print = ['name','last_update','tags','desc',"actions"]
            headers_never_print = ["name","desc","actions"]

            headers_only_print = ["for search","SPATIAL","TEMPORAL",'Fusion','Transform','Query or filter','Filter by rule','clean','Imputation','Class.','Clustering','stats','Regression','Chart','Map']
            headers= ['fusion','transform','query or filter','filter by rule','cleanning','imputation','classification','clustering','statistics','regression','charts','geographical map']

            content = ""
            content += `
                <table class="hover compact dt-responsive" id="${id_table}" width="100%">
                    <caption>List of solutions</caption>
                    <thead>
                        <tr>`
                        //headers_list.forEach(function(h){
                        //    content += `<th class="all" scope="col">${h}</th>`
                        //});
                        //content+="</tr><tr>"
                        headers_never_print.forEach(function(h){
                            content += `<th class="none" scope="col">${h}</th>`
                        });
                        headers_only_print.forEach(function(h){
                            content += `<th class="all" scope="col">${h}</th>`
                        });
            content += `</tr></thead><tbody>`


            solution_id = 0
            response['info'].forEach(function(value){ //se rellena la tabla
                if(value['metadata'].hasOwnProperty('process_tags')){ //tags exist
                    content +=`<tr id="solution_${solution_id}">` // se añade un id par apoder borrarlo despues

                    content +=`<td class="none">${value.metadata.name}</td>`
                    content +=`<td class="none">${value.metadata.desc}</td>`
                    content +=`<td>
                                <button type='button' onclick='BTN_retrieve_solution("${value["token_solution"]}",as_copy=true)' class="btn btn-outline-primary btn-block">Retrive</button>
                            </td>`

                    content +=`<td >${value.metadata.process_tags.general.join(" ")}</td>` //for search

                    spatio_temporal_tags = ["SPATIAL","TEMPORAL"] //methodology
                    //console.log(value.metadata.tags)

                    spatio_temporal_tags.forEach(function(st){
                        if(value.metadata.tags.includes(st)){
                            content += `<td class="all"><i class="far fa-check-circle"></i></td>`
                        } 
                        else{
                            content += `<td class="all"></td>`
                        }
                    });

                    headers.forEach(function(h){
                        if(value.metadata.process_tags.general.includes(h)){
                            content += `<td class="all"><i class="far fa-check-circle"></i></td>`
                        } 
                        else{
                            content += `<td class="all"></td>`
                        }
                    });
                    content +=`</tr>`


                    solution_id+=1
                }
            });
            content +=`</tbody></table>`
            $(`#${id_table_container}`).html(content)


            // SHOW MODAL
            //$('#modal_list-solutions').modal('show');
            

            // create datatable
            $(`#${id_table}`).DataTable({
                'columnDefs' : [
                    { 'visible': false, 'targets': [3] }
                ],
                "responsive": true,
                "lengthMenu": [[5, 10, 25, 50], [5, 10, 25, 50]],
                "order": [[ 1, "desc" ]]

            } );
            console.log("id tabla:" + id_table)

        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            error_result = XMLHttpRequest['responseJSON']
            if (XMLHttpRequest.status==401){ //session expired
                sesionExpirada()
            }
        }
    }).fail(function(){console.log("error al conectarse")});

}


function BTN_list_solution(){

    let data_request = {"SERVICE":"solution/list",'REQUEST':{'auth':{'user':MESH_USER,'workspace':MESH_WORKSPACE}}}
    Toggle_Modal("show","#modal_list-solutions")
    $.ajax({
        url: 'includes/xel_Request.php',
        type: 'POST',
        dataType: 'json',
        data:data_request,
        success: function(response) {  
            console.log(response)
            $('#modal_list-solutions-body').append("<div id='modal_list-solutions-table' ></div>");
            
            headeres_always_show = ['name','last_update','tags']
            headeres_never_show = ['token_solution','desc', 'actions']

            headeres = ['name','last_update','tags','token_solution','desc']

            content = ""
            content += `
                <table class="table table-hover" id="table-solutions" style="width:100%">
                    <caption>List of solutions</caption>
                    <thead>
                        <tr>`
                        headeres_always_show.forEach(function(h){
                            content += `<th class="all" scope="col">${h}</th>`
                        });
                        headeres_never_show.forEach(function(h){
                            content += `<th class="none" scope="col">${h}</th>`
                        });
            content += `</tr></thead><tbody>`


            solution_id = 0
            response['info'].forEach(function(value){ //se rellena la tabla
                content +=`<tr id="solution_${solution_id}">` // se añade un id par apoder borrarlo despues
                headeres.forEach(function(h){
                    if (h=="token_solution" || h =="last_update"){
                        content += `<td>${value[h]}</td>`
                    }
                    //text-break
                    else if (h=="desc"){
                        content += `<td>${value['metadata'][h]}</td>`
                    }
                    else{
                        content += `<td>${value['metadata'][h]}</td>`
                    }
                });
                content +=`<td>
                            <button type='button' onclick='BTN_retrieve_solution("${value["token_solution"]}")' class="btn btn-outline-info">Retrive</button>
                            <button type='button' onclick='BTN_delete_solution("${value["token_solution"]}","solution_${solution_id}", "table-solutions")' class="btn btn-outline-dark">Delete</button>
                        </td>`
                content +=`</tr>`
                solution_id+=1
            });
            content +=`</tbody></table>`
            $("#modal_list-solutions-table").html(content)


            // SHOW MODAL
            //$('#modal_list-solutions').modal('show');

            // create datatable
            $("#table-solutions").DataTable({
                responsive: true,
                "scrollX": true,
                "scrollY": 250,
                buttons: [
                    {
                        text: 'Reload',
                        action: function ( e, dt, node, config ) {
                            dt.ajax.reload();
                        }
                    }
                ],
                columnDefs: [{ 'targets': 1, type: 'date-euro' }],
                "order": [[ 1, "desc" ]]
            } );
            $("#table-solutions").DataTable().draw()

            console.log("dibujando tabla")
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            error_result = XMLHttpRequest['responseJSON']
            if (XMLHttpRequest.status==401){ //session expired
                sesionExpirada()
            }
        }
    }).fail(function(){console.log("error al conectarse")});

}
///// Funciones para autocompletado de columnas en un input text
function sentence_split(val) {
    return val.split(/@\s*/);
}

function extractLast(term) {
    return sentence_split(term).pop();
}

String.prototype.replaceBetween = function(start, end, what) {
    return this.substring(0, start) + what + this.substring(end);
  };// don't navigate away from the field on tab when selecting an item



function AutocompleteByFileInfo(id_inputbox,id_file,Modal_selector=".modal.fade.show"){
    tag_4_auto = "#"+id_inputbox    // TAG FOR THE AUTOCOMPLETE

    console.log("se esta activando el autocomplete para " + id_file)

    sourceid = $(Modal_selector).data("sourceId")
    //if_metadata_exist =  reload_metadata_fromBox(sourceid)
    //if (!if_metadata_exist){ console.log("no se requiere autocomplete");return 0;}
    
    BOX_info = get_metadata_box(sourceid,source=id_file,false,"filename")
    const isEmpty = Object.keys(BOX_info).length === 0 //si es null no se hace nada
    if(isEmpty){return false}

    console.log("se activara el autocomplete")

    let availableTags = BOX_info.columns
    console.log("activando")

    $(tag_4_auto).bind("keydown", function(event) {
        if (event.keyCode === $.ui.keyCode.TAB && $(this).data("autocomplete").menu.active) {
            event.preventDefault();
        }
    }).autocomplete({
        minLength: 0,
        source: function(request, response) {
            var term = request.term,
                results = [];
            if (term.indexOf("@") >= 0) {
                term = extractLast(request.term);
                if (term.includes(" ")){
                    term = term.split(" ")[0]
                }
                results = $.ui.autocomplete.filter(
                availableTags, term);
            }
            else if (term.indexOf(".") >= 1) {
                term = term.split(".")

                Fathercolumn = term[0]
                term = term[1]
                if (term.includes(" ")){
                    term = term.split(" ")[0]
                }
                
                Fathercolumn = Fathercolumn.substring(
                    Fathercolumn.lastIndexOf(" ") + 1);

                if ( Object.keys(BOX_info.unique).includes(Fathercolumn)){
                    tagscol =  BOX_info.unique[Fathercolumn] 
                    results = $.ui.autocomplete.filter(tagscol, term);
                }
            }

            response(results);
        },
        focus: function() {
            // prevent value inserted on focus
            return false;
        },
        select: function(event, ui) {
            string_value = this.value

            if (string_value.includes("@")) {
                start_ix = string_value.indexOf("@")
                end_ix = string_value.indexOf(" ",start_ix)
                if(end_ix==-1){end_ix=string_value.length}

                string_value = string_value.replaceBetween(start_ix,end_ix,ui.item.value)
                this.value = string_value
            }
            if (string_value.includes(".")) {
                start_ix = string_value.split(".")[0]
                start_ix = start_ix.lastIndexOf(" ") + 1
                end_ix = string_value.indexOf(" ",start_ix)

                if(end_ix==-1){end_ix=string_value.length}
                string_value = string_value.replaceBetween(start_ix,end_ix,ui.item.value)
                this.value = string_value
            }
            return false;

        }
});
}

var CODEAREA_POINTERS = {}
function Activate_CodeArea(id_textarea, Modal_selector= ".modal.fade.show" ){

    if ($("#"+id_textarea).hasClass( "codearea" )){

        const elem = document.getElementById(id_textarea); 
        console.log(Modal_selector)

        sourceid = $(Modal_selector).data("sourceId")

        BOX_info = get_metadata_box(sourceid,source=null)
        const isEmpty = Object.keys(BOX_info).length === 0 //si es null no se hace nada
        if(isEmpty){
            console.log("No hay datos para autocompletar")
            codeAreas = []
        }
        else{
            codeAreas = []
            BOX_info.columns.forEach(function(v){
                codeAreas.push({"displayText":v,"text":v,"value_type":"var","render":render_function})
            })
            console.log("Si hay datos para autocompletar")

        }
        codeAreas = codeAreas.concat(Reserved_words)


        CODEAREA_POINTERS[id_textarea] =CodeMirror.fromTextArea(elem,{
                                            value:"\t",
                                            lineNumbers: true,
                                            lineWrapping: true,
                                            extraKeys: {"Ctrl-Space": "autocomplete"},
                                            theme: "mdn-like",
                                            hintOptions: {
                                                hint: function(cm) {
                                                    var cursor = cm.getCursor();
                                                    var currentLine = cm.getLine(cursor.line);
                                                    var lineUntilCursor = currentLine.slice(0, cursor.ch);
                                                    var words = lineUntilCursor.split(/\s+/);

                                                    var currentWord = words[words.length - 1];
                                                    
                                                    var matches = codeAreas.filter(function(word) {
                                                      return word.displayText.includes(currentWord);
                                                    });

                                                    return {
                                                      from: CodeMirror.Pos(cursor.line, cursor.ch - currentWord.length),
                                                      to: cursor,
                                                      list: matches
                                                    };
                                                },
                                                
                                            }
        })
                                            
        
                                 
    }

}

function Activate_Autcomplete(tag_4_auto, Modal_selector= ".modal.fade.show" ) { 
    // .modal.fade.show sirve para los modal activos (debe estar activo primero)
    //tag_4_auto = ".autocomplete-column"    // TAG FOR THE AUTOCOMPLETE

    sourceid = $(Modal_selector).data("sourceId")
    
    BOX_info = get_metadata_box(sourceid,source=null)
    const isEmpty = Object.keys(BOX_info).length === 0 //si es null no se hace nada
    if(isEmpty){return false}
    //console.log("se activo el autocomplete")

    let availableTags = BOX_info.columns

    $(tag_4_auto).bind("keydown", function(event) {
        if (event.keyCode === $.ui.keyCode.TAB && $(this).data("autocomplete").menu.active) {
            event.preventDefault();
        }
    }).autocomplete({
        minLength: 0,
        source: function(request, response) {
            var term = request.term,
                results = [];
            if (term.indexOf("@") >= 0) {
                term = extractLast(request.term);
                if (term.includes(" ")){
                    term = term.split(" ")[0]
                }
                results = $.ui.autocomplete.filter(
                availableTags, term);
            }
            else if (term.indexOf(".") >= 1) {
                term = term.split(".")

                Fathercolumn = term[0]
                term = term[1]
                if (term.includes(" ")){
                    term = term.split(" ")[0]
                }
                
                Fathercolumn = Fathercolumn.substring(
                    Fathercolumn.lastIndexOf(" ") + 1);

                if ( Object.keys(BOX_info.unique).includes(Fathercolumn)){
                    tagscol =  BOX_info.unique[Fathercolumn] 
                    results = $.ui.autocomplete.filter(tagscol, term);
                }
            }

            response(results);
        },
        focus: function() {
            // prevent value inserted on focus
            return false;
        },
        select: function(event, ui) {
            string_value = this.value

            if (string_value.includes("@")) {
                start_ix = string_value.indexOf("@")
                end_ix = string_value.indexOf(" ",start_ix)
                if(end_ix==-1){end_ix=string_value.length}

                string_value = string_value.replaceBetween(start_ix,end_ix,ui.item.value)
                console.log(string_value)
                this.value = string_value
            }
            if (string_value.includes(".")) {
                start_ix = string_value.split(".")[0]
                start_ix = start_ix.lastIndexOf(" ") + 1
                end_ix = string_value.indexOf(" ",start_ix)
                console.log(start_ix,end_ix)

                if(end_ix==-1){end_ix=string_value.length}
                string_value = string_value.replaceBetween(start_ix,end_ix,ui.item.value)
                console.log(string_value)
                this.value = string_value
            }
 
            return false;

        }
    });
    
}

/////
function SELECT_ShowValue(combo_label="default", combo){
    //hide all divs with the combo_label class
    table_id = `#table_${combo_label}_${combo.value}`
    sample_table_id = `#table_sample_${combo_label}_${combo.value}`

    $('.'+combo_label).hide();
    $('#'+combo_label+'_'+combo.value).show();
    
    if ( $.fn.dataTable.isDataTable( table_id ) ) {
        table = $(table_id).DataTable();
        table.columns.adjust()
        sample_table = $(sample_table_id).DataTable();
        sample_table.columns.adjust()
    }
    else {
        $(table_id).DataTable( {responsive: true, scrollY:"30vh", scrollCollapse: true, "lengthMenu": [[5, 10, 25, 50], [5, 10, 25, 50]]} );
        $(sample_table_id).DataTable( {"scrollX": true, scrollY:"30vh", scrollCollapse: true, "lengthMenu": [[5, 10, 25, 50], [5, 10, 25, 50]] } );  
    }

}

/// funcion para abrir el modal de create
function ModalCreate(ToCreate){
    if (ToCreate=="workspace"){
        //create form
        $("#modal_create > .modal-dialog > .modal-content> .modal-body").html(`
            <div class="form-group row col-12">
                <label>Workspace</label>
                <input type="text" class="form-control" id="create_workspace-name" required>
            </div>

            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                <button id="btnSave" type="button" class="btn btn-primary" onclick="TriggerCreate('workspace')" >Create</button>
            </div>
        `)

    }

        Toggle_Modal("show","#modal_create")
}

function TriggerCreate(ToCreate){
    if (ToCreate=="workspace"){
        //create form
        workspacename = $("#create_workspace-name").val()
        let data_request = {'SERVICE':`workspace/create/${MESH_USER}/${workspacename}`}

        $.ajax({ // ajax para rellenar valores de workspaces
            url: 'includes/xel_get_Request.php',
            type: 'POST',
            dataType: 'json',
            data:data_request,
            success: function(result) {  
                if (result.status=="OK"){
                    notificarUsuario("Workspace created","success")
                    Toggle_Modal("hide","#modal_create")

                    // update list
                    $("#user_workspace").empty()
                    $("#user_workspace").click()
                    $("#user_workspace").selectpicker("refresh")
                }
                else{
                    notificarUsuario("Workspace could not be created.","danger")
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                error_result = XMLHttpRequest['responseJSON']
                if (XMLHttpRequest.status==401){ //session expired
                    sesionExpirada()
                }
            }
        }).fail(function(){console.log("error al conectarse")});
    }

}

function TriggerDelete(ToDelete){
    if (ToDelete=="workspace"){
        //create form
        workspacename = $("#user_workspace").val()
        let data_request = {'SERVICE':`workspace/delete/${MESH_USER}/${workspacename}`}

        $.ajax({ // ajax para rellenar valores de workspaces
            url: 'includes/xel_get_Request.php',
            type: 'POST',
            dataType: 'json',
            data:data_request,
            success: function(result) {  
                if (result.status=="OK"){
                    notificarUsuario("Workspace detelted","success")
                    $("#user_workspace").empty()
                    $("#user_workspace").click()
                    $("#user_workspace").selectpicker("refresh")
                }
                else{
                    notificarUsuario("Workspace could not be deleted.","danger")
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                error_result = XMLHttpRequest['responseJSON']
                if (XMLHttpRequest.status==401){ //session expired
                    sesionExpirada()
                }
            }
        }).fail(function(){console.log("error al conectarse")});
    }

}


function ShoppingCar_add_element(name,value,id_div_destination){
    htmlstring = `
    
    <div class="form-group row col-12" id='ShoppingCar_product_${ID_CAR_ELEMENT}'>
        <label for="txttype" class="col-sm-2 col-form-label col-form-label-sm">Dataset: </label>
        <div class="col-sm-7">
                <input type="text" class="form-control" readonly value='${name}'>
        </div>
        <div class="form-group col-2">
            <button type="button" onclick="$('#ShoppingCar_product_${ID_CAR_ELEMENT}').remove()" class="btn btn-block btn-outline-danger"><i class="far fa-trash-alt"></i></button>
        </div>
        <div class="col-sm-1 value" >
            <input type="text" class="form-control d-none" readonly id='ShoppingCar_product_${ID_CAR_ELEMENT}_value' value='${value}'>
        </div>
    </div>`
    ID_CAR_ELEMENT++
    $(id_div_destination).append(htmlstring)
}

function ShoppingCar_get_list(div_selector){
    list_selector = $(`${div_selector} > .form-group`)
    list_values = []
    list_selector.each(function(){
        list_values.push($(this).children("div").children("input").val())
    })

    return list_values
}


function CreateDatasetsPackage(id_list,destination_selector,packagename_selector ){
    sourceId = $('#modal_datasource').data('sourceId');    

    list_files = ShoppingCar_get_list(id_list)
    workspacename = $(destination_selector).val()
    package_name = $(packagename_selector).val()

    force_zip =$("#force_describe").is(':checked')
    if (force_zip==="undefined" || force_zip==""){
        force_zip=false
    }


    let data_request = {
        "SERVICE":"CreatePackage",
            'REQUEST':{
                "tokenuser": MESH_USER,
                "name_package":package_name,
                "list_files":list_files,
                "destination":workspacename,
                "force_creation":force_zip
    }}

    // se crea el dataset
    $.ajax({ // ajax para rellenar valores de workspaces
        url: 'includes/xel_Request.php',
        type: 'POST',
        dataType: 'json',
        data:data_request,
        success: function(result) {  
            if (result['status']=="OK"){
                // se carga el dataset
                LoadExistingDataset(sourceId,result['filename'],metadata=null,workspace=workspacename)
            }
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            error_result = XMLHttpRequest['responseJSON']
            if (XMLHttpRequest.status==401){ //session expired
                sesionExpirada()
            }
        }
    }).fail(function(){console.log("error al conectarse")});


}


//// funcione smuys especificas para servicios, en un futuro se van a cambiar

function addRule(){
    value_text= $("#addtolist").val()
    console.log(value_text)
    $("#ReplaceWithNa").append("<li id ='"+value_text+"' class='list-group-item'>"+value_text+" <a href='#' onclick='remove_list_element(this)' data-toggle='tooltip' title='remove this'><span class='glyphicon glyphicon-minus' aria-hidden='true'></span></a> </li>")
}

function Handler_Rules(div_id){ // #FilterColumn


    htmlstring = `
    <div class='container-flex' id="rule_row_${ID_rule}" >
        <div class="form-group row">
            <div class="form-group col-2">
                <button type="button" onclick="$('#rule_row_${ID_rule}').html('')" class="btn btn-block btn-outline-danger"><i class="far fa-trash-alt"></i></button>
            </div>
            <label class="col-2 text-muted"> ${ID_rule}: IF </label>

            <div class="col-4"> <select class="form-control" id="rule_${ID_rule}_column" data-actions-box="true" onclick=fillselect(this,mult=false)></select> </div>
            <div class="col-4">
                <select class="form-control" id="rule_${ID_rule}_process">
                        <option value="corr"> correlation </option>
                        <option value="cov"> covariance </option>
                </select>
            </div>
        </div>
        <div class="form-group row">
            <label class="col-3 text-muted"></label>
            <label class="col-2 text-muted"> IS </label>
            <div class="col-7">
                <select class="form-control" id="rule_${ID_rule}_operator" onChange="value_rule(${ID_rule})">
                        <option value=">"></option>
                        <option value=">"> grater than </option>
                        <option value="<"> lower than </option>
                        <option value="InRange"> in the range from </option>
                        <option value="OutRange"> out of the range from </option>
                </select>
            </div>
        </div>

        <div class="form-group row col-12" id="rule_${ID_rule}_div_value" >

        </div>
    </div><hr>`
    ID_rule++
    $(div_id).append(htmlstring)
}

function value_rule(id_rule){
id_select = `#rule_${id_rule}_operator`
div_id = `#rule_${id_rule}_div_value`
id_value1 = `rule_${id_rule}_value1`
id_value2 = `rule_${id_rule}_value2`

var val = $(id_select).val()
if (val==">" || val== "<"){
    $(div_id).html(`
    <label class="col-6 text-muted"></label>
    <div class="col-6">
        <input type="number" class="form-control solo-numero" id="${id_value1}">
    </div>
    `) 
}
else{
    $(div_id).html(`
    <label class="col-4 text-muted"></label>
    <div class="col-3">
        <input type="number" class="form-control solo-numero" id="${id_value1}">
    </div> 
    <label class="col-2 text-muted"> To </label>
    <div class="col-3">
        <input type="number" class="form-control solo-numero" id="${id_value2}">
    </div> 
    `) 
}



}





function remove_list_element(el){
    el.closest('li').remove()
}

function init_modal(){}



// funcion para crear stacks de modals
$(document).on('show.bs.modal', '.modal', function (event) {
    var zIndex = 1040 + (10 * $('.modal:visible').length);
    $(this).css('z-index', zIndex);
    setTimeout(function() {
        $('.modal-backdrop').not('.modal-stack').css('z-index', zIndex - 1).addClass('modal-stack');
    }, 0);
});


// funcion para seleccionar el workspace
function SelectWorkspace(){
    val = $("#user_workspace").val()
    if (val==null || val == undefined){
        MESH_WORKSPACE= "Default"
        setCookie("workspace",MESH_WORKSPACE,60)
    }
    else{
        MESH_WORKSPACE= $("#user_workspace").val()
        setCookie("workspace",$("#user_workspace").val(),60)
    }
    console.log("Workspace actual: " + MESH_WORKSPACE)
    //notificarUsuario("")
}




/// auth
function verifySession() {
    //setCookie
    //getCookie
    //setCookie("test","prueba",10)
    //console.log(getCookie("test2"))
    //console.log("entro a verificar sesion")
    MESH_WORKSPACE = getCookie("workspace")
    MESH_USER = getCookie("tokenuser")
    SESSION_TOKEN = getCookie("access_token")
    if (SESSION_TOKEN==""){//no hay token de session
        $('#loginmodal').modal('show');
    } 
    else{
        console.log("se cargaron las cookies")
    }
}

$('#registeruserform').submit(function () {
    return false;
   });


function RegisterNewUser() {
    var username = $("#username_register").val()
    var email = $("#email_register").val()
    var pass1 = $("#pass1_register").val()
    var pass2 = $("#pass2_register").val()
    console.log(pass1,pass2)

    if (pass1!==pass2){
        notificarUsuario("password do not match.")
    }
    else{
        let data_request = {'SERVICE':'signup' ,'REQUEST':{'username':username,"email":email,"password":pass1}}

        $.ajax({
            url: 'includes/xel_Request.php',
            type: 'POST',
            data: data_request,
            dataType: 'json',
            cache: false,
            success: function(result) {  
                console.log(result)
                if (result.codigo==1){
                    notificarUsuario(result.message,"warning");
                    console.log(result.message)
                }
                else{
                    notificarUsuario(result.message,"info");
                }

            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                notificarUsuario(XMLHttpRequest['responseJSON'].message,"warning");
             }
        });



    }
    //setCookie
    //getCookie
    //setCookie("test","prueba",10)
    //console.log(getCookie("test2"))
    //console.log("entro a verificar sesion")

}

$('#loginuserform').submit(function (event) {
    event.preventDefault();
    var username = $("#username_login").val()
    var pass = $("#password_login").val()
    LoginUser(username,pass)
   });

function LoginUser(username,password){

    if (username=="test"){
        setCookie("username","Geoportal",60)
        setCookie("tokenuser","Geoportal",60) 
        setCookie("access_token","none") // este usuario solo sirve para probar cuando no hay seguridad
        setCookie("workspace","Default",60)
    }


    let data_request = {'SERVICE':'login' ,'REQUEST':{'user':username,"password":password}}
    $.ajax({
        url: 'includes/xel_Request.php',
        type: 'POST',
        data: data_request,
        dataType: 'json',
        cache: false,
        success: function(result) {  
            console.log(result)
            if ('data' in result){
                setCookie("username",username,60)
                setCookie("tokenuser",result.data.tokenuser,60)
                setCookie("access_token",result.data.access_token,60)
                setCookie("workspace","Default",60)
    
                $.ajax({ //OBTIENE LA IP Y DATOS DE LOCALIZACION COMPLEMENTARIOS
                    url: "http://ipinfo.io",
                    dataType: "jsonp",
                    success: function(response) {
                        setCookie("ip",response.ip,60)
                        location.href = "index.php?lang=" + lang;
                    },
                    error: function(response) {
                        setCookie("ip","-",60)
                        location.href = "index.php?lang=" + lang;
                    }
                });
            }
            else{
                notificarUsuario(result.message,"danger")
            }

        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            notificarUsuario("Something wrong","danger");
            console.log(XMLHttpRequest["responseJSON"])
         }
    });

}

function sesionExpirada() {
    $("#modExpirado").modal('show');
}

function LogOutUser(){
    
    let data_request = {'SERVICE':'logout' ,'REQUEST':{'tokenuser':MESH_USER,"access_token":SESSION_TOKEN}}
    $.ajax({
        url: 'includes/xel_Request.php',
        type: 'POST',
        data: data_request,
        dataType: 'json',
        cache: false,
        success: function(result) {  
            notificarUsuario("Session closed.")
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            notificarUsuario("Something was wrong at closing the session","danger");
         },
        complete:function(result) {
            deleteAllCookies(); 
            setTimeout(function() {
                location.href = "index.php?lang=" + lang;
            }, 1000)  
        }
    });
}

$("#btnLogGhest").click(function(event) {
    var username = "Guest"
    var email = "Guest@email.com"
    var pass1 = "GuestP@ssword123"
    let data_request = {'SERVICE':'signup' ,'REQUEST':{'username':username,"email":email,"password":pass1}}
    $.ajax({
        url: 'includes/xel_Request.php',
        type: 'POST',
        data: data_request,
        dataType: 'json',
        cache: false,
        success: function(result) {  
            console.log("register guest")
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
            //notificarUsuario("Something wrong","danger");
            console.log("alredy registred")
         },
        complete: function(){
            LoginUser(username,pass1)
        }
    });

    
});

