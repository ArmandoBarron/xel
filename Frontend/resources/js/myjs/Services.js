// TODO: LOOK ANOTHER FORMAT FOR THE CHAINNED BOX DATA
// TODO: WHEN REARRANGE, IT ALSO SHOULD BE REARRENGED IN DATA OBJECT

DAG = []; //GLOBAL
var PIPELINE = false;
var Download_log = false
var INIT_TIME = 0
var SERVICE_GATEWAY = ""
var TO_DOWNLOAD = []
var DATA_WORKFLOW = {'data':'','type':'DUMMY'};
var DATA_WORKFLOW_DESC;
var MESH_WORKSPACE = "Default"
var MESH_USER = "Geoportal"
var ServicesArr = []
var PARAMS_MAP = {}
var TOKEN_SOLUTION=''
var ifCoordinates = ["latitud","longitud","lat","lon"].map(function(x){ return x.toUpperCase();}) 

function Clean_graph_data(){
    DATA_WORKFLOW_STATUS = false
    notificarUsuario("No dataset loaded.", 'info');
    //$("#files").hide();
    $("#group-upload").show("fast");
    $("#cleandata_button").hide("fast");
    //$("#rawdata_button").show();
    $(".serviceLoadingIcon-raw").html("")
    $(".showOnMapIcon-raw").html("")
    $(".downloadDataIcon-raw").html("")
    //$("#files").show();
    $("#listOfDatasources").html("no data source selected.")

}

function Upload_graph_data(){
        sourceId = $('#modal_datasource').data('sourceId');
        raw_file= $('#files')[0].files[0];
        if (raw_file==undefined){console.log("select a data source");return 0}

        $("#"+sourceId+" > div.container > div.service-options > #serviceLoadingIcon").html("<img style='width:25%; height:100%' src='resources/imgs/loading.gif'></img>")
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
            });
            
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
}

function Pre_exe_graph(){ //get data from data source
    if(DATA_WORKFLOW_STATUS==false) {
        console.log("IS VOID");
        $("#serviceLoadingIcon-raw").html("<img style='width:25%; height:100%' src='resources/imgs/loading.gif'></img>")
        $("#showOnMapIcon-raw").html("")
        $("#downloadDataIcon-raw").html("")
        PIPELINE= true;
        setTimeout(toResults, 1000);
        //toResults() //exec function to results
        DATA_WORKFLOW_STATUS = true
        $("#files").hide();
        $("#files_button").hide();
        $("#cleandata_button").show();
        $("#rawdata_button").hide();
    }
}

function Exec_graph(){
    Download_log = false
    DAG = [] //CLEAN
    TO_DOWNLOAD= []
    data_obj = JSON.parse(JSON.stringify(dataObject))
    SERVICE_GATEWAY = $("#ip_gateway").val()
    transform_dag(data_obj,DAG)
    console.log("EL DAG ...") ;console.log(DAG);
    $(".serviceLoadingIcon").html("<img style='width:25%; height:100%' src='resources/imgs/loading.gif'></img>")
    $(".showOnMapIcon").html("")
    $(".downloadDataIcon").html("")
    // send request to exec dag
    pipe_dag(DATA_WORKFLOW)
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
function postExecutionStop(rn,error=true,message="Execution failed, check the parameters") {
    // reactivate button
    $('#output').prop('disabled', false);
    // remove icons
    var allFootersIcons = $('.serviceLoadingIcon');
    console.log('allFootersIcons: ', allFootersIcons);
    for(let i = 0;i < allFootersIcons.length;i++) {
        console.log(`el ${i}: `, allFootersIcons[i]);
        allFootersIcons[i].innerHTML = "";
    }
    if (error){notificarUsuario("ERROR: "+message, 'danger');}
    else{
        notificarUsuario("Execution complete", 'success');
        var end = Date.now();
        tiempo_ejecucion= end-INIT_TIME
        console.log(tiempo_ejecucion);
        notificarUsuario("tiempo de ejecucion: "+tiempo_ejecucion , 'info')

        if ($("#dag_saveresults").is(":checked")){ //auto download log
            for (var i = 0; i < TO_DOWNLOAD.length; i++) {
                console.log(TO_DOWNLOAD[i]["task"])
                download_data_pipe(TO_DOWNLOAD[i]["rn"], TO_DOWNLOAD[i]["task"],TO_DOWNLOAD[i]["type"])
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
                        $(".serviceLoadingIcon-raw").html(`<a id='temporal_log_link' href='${liga}' target='_blank' ></a>`)
                        $('#temporal_log_link').get(0).click();
                        $(".serviceLoadingIcon-raw").html("")
                    }
                });
            }
            // execute again if there are more iterations
            itt = parseInt($("#dag_iterations").val())
            if(itt>=2){
                $("#dag_iterations").val(itt-1)
                TOKEN_SOLUTION = "" //se vacía esta variable, de esta forma se fuerza a ejecutar todo desde 0
                setTimeout(Exec_graph(),2000)
            }
            else{
                console.log("no more iterations")
            }
        }

    }
}

function contar_servicios(DAG){
    contador = DAG.length
    for (let i = 0; i < DAG.length; i++) {
        contador= contador + contar_servicios(DAG[i].children)
    }
    return contador
}

function pipe_dag(data_for_workflow){ // launch dag
    var data_to_send = {'SERVICE':'executeDAG',"HOST":SERVICE_GATEWAY, 'REQUEST':{'DAG':JSON.stringify(DAG),
        'data_map':data_for_workflow, 
        'auth':{'user':MESH_USER,'workspace':MESH_WORKSPACE}}};
    
    if (TOKEN_SOLUTION!=""){data_to_send.REQUEST.token_solution=TOKEN_SOLUTION}

    INIT_TIME = Date.now();
    $.ajax({
        type: "POST", // la variable type guarda el tipo de la peticion GET,POST,..
        url: 'includes/xel_Request.php', //url guarda la ruta hacia donde se hace la peticion
        data: data_to_send, // data recive un objeto con la informacion que se enviara al servidor
        success: function(response) { //success es una funcion que se utiliza si el servidor retorna informacion
            if (response['status']=="OK"){
                notificarUsuario("DAG is now in execution", 'info');
                TOKEN_SOLUTION = response['token_solution']

                var config_monitoring = {max_errors:10000000,errors:0,i:1,monitor: false}
                var interv = setInterval(pipe_monitoring,1000,TOKEN_SOLUTION,config_monitoring)
                config_monitoring.interv = interv    

                $("#modal_save-solutions-form-tokensolution").val(TOKEN_SOLUTION)
            }
            else{
                postExecutionStop(0,true,message=response['message'])
            }

        },
        error: function() { //se lanza cuando ocurre un error
            postExecutionStop(0,true,message="Resource in "+SERVICE_GATEWAY+" is not responding, try again.")
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
        async: false,
        cache: false,
        timeout: 30000,
    });

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
            xel_describe_dataset(filename=filename,force=force_describe,context=null,delimiter=separator).done(function(result2){
                files_metadata = JSON.parse(result2).info
            });
            LoadExistingDataset(sourceId,filename,metadata=files_metadata)
        }
      },
      complete: function() {
        setTimeout(function(){
            $('#progress-div').hide("slow") //esconder barra de progreso
            $("#cleandata_button").show("fast");
        }, 1000);
    },
    });

    return 0
}


function Handler_condition_GetData(task_id,description,isRaw,filename=null,token_solution=null,dataRet=null){
    // si es raw, solo se usa filename
    // si no es raw, se usa el token_solution y el dataRet

    tsk = demoflowy_lookForParent(task_id) //obtener los valores de la caja (json) por su id, se obtiene una instancia del json

    parentfilename = description.parent_filename

    if (description.files_info[parentfilename]==undefined){
        columnas_del_servicio=[]
    }
    else{
        tsk.service_metadata = description
         //columnas que procesa el servicio en mayusculas  
        columnas_del_servicio = [...tsk.service_metadata.files_info[parentfilename].columns ].map(function(x){ return x.toUpperCase(); })  
    }

    //buscar si el servicio tiene columnas para geolocalizar en el mapa
    isMarkable = columnas_del_servicio.some( ai => ifCoordinates.includes(ai) ); 
    $(`#${task_id} > div.container > div.service-options > #serviceLoadingIcon`).html("") //icono de carga

    if (isRaw)//los botones cambian dependiendo de si es la caja root o una de bb
    {  
        $(`#${task_id}_inspect`).html(`<i class="fas fa-search fa-xl elementhover" onclick="Inspect_datasource(filename='${filename}')" ></i>`)
        $(`#${task_id}_downloadDataIcon`).html(`<i class="fas fa-cloud-download-alt fa-xl elementhover" onclick="download_data_pipe('','','','${filename}',raw=true)"></i>`)
        //if (isMarkable){
        //    $(`#${task_id}_showOnMapIcon`).html(`<i class="fas fa-map-marked-alt fa-lg elementhover" onclick="ShowModal_map_AAS('${token_solution}','${task_id}')"></i>`)
        //}
    }
    else
    {
        // añadir boton de inspect a la caja con una funcion que haga el describe 
        $("#"+task_id+"_inspect").html(`<i class="fas fa-search fa-xl elementhover" onclick="Inspect_datasource(filename=null,force=false,token_solution='${token_solution}',task='${task_id}',type_dataset='SOLUTION')"></i>`)
        
        if (isMarkable){
            $(`#${task_id}_showOnMapIcon`).html(`<i class="fas fa-map-marked-alt fa-xl elementhover" onclick="ShowModal_map_AAS('${token_solution}','${task_id}')"></i>`)
        }
        if (dataRet['index']){
            TO_DOWNLOAD.push({"rn":token_solution,"task":task_id,"type":dataRet['type']}) //se añade a la lista de descargas
            $(`#${task_id}_downloadDataIcon`).html(`<i class="fas fa-cloud-download-alt fa-xl elementhover" onclick="download_data_pipe('${token_solution}','${task_id}','${dataRet['type']}')"></i>`)
        }
    }
}

function pipe_monitoring(RN,cfg) {
    if (cfg.monitor==true){
        console.log("THERE IS ALREADY A MONITOR")
        return 0
    }
    cfg.monitor=true
    //list_task_showOnMap = ["preproc","clustering","cleanning","clustering_service"]
    ifclass = ["class","Etiqueta_clase"].map(function(x){ return x.toUpperCase();}) 

    let data_request = {"rn":RN,'host':SERVICE_GATEWAY}
    var xhr = new XMLHttpRequest();
    var url = "includes/dag_monitor.php";
    xhr.open("POST", url, true); //False significa que es sincrona la consulta
    xhr.setRequestHeader("Content-Type", "application/json");
    var send = JSON.stringify(data_request); //lo convertimos en una cadena
    xhr.onreadystatechange = function (aEvt) {
        if (xhr.status == 200 && xhr.readyState===4) {
            if (xhr.responseText != ""){dataRet = JSON.parse(xhr.responseText);}
            else {dataRet={'status':""}}

            if (dataRet['status']=="OK")
            {
                // describir dataset intermedio
                task_id = dataRet['task']
                context={token_solution:RN,task:task_id,type_dataset:"SOLUTION",catalog:MESH_WORKSPACE}
                xel_describe_dataset(filename=null,force=true,context=context).done(function(result){description = JSON.parse(result).info});

                Handler_condition_GetData(task_id,description,false,'',RN,dataRet)

                cfg.errors=0 //reset errors counter
                notificarUsuario("Task "+task_id+" has finished", 'success');
                cfg.i++
            }
            if (dataRet['status']=="INFO")
            {
                notificarUsuario('An error was detected...'+dataRet['message'], 'info');
            }
            if (dataRet['status']=="ERROR")
            {
                //get data
                task_id = dataRet['task']
                tsk = task_id.split("-")
                tsk = tsk[tsk.length -1]
                console.log(dataRet)
                $("#"+task_id+" > div.container > div.service-options > #serviceLoadingIcon").html("")
                cfg.errors=0
                notificarUsuario("ERROR "+task_id+": "+ dataRet['message'], 'danger');
                cfg.i++
            }
            else{
                console.log("monitoring:" + cfg.errors)
                if(cfg.errors == 15)notificarUsuario('We keep working in your request...', 'info');
                if (cfg.errors>=cfg.max_errors){
                    //clearInterval(cfg.interv);	
                    //PIPELINE = false;
                    //postExecutionStop(RN);
                } //debuging option
                if (cfg.i>contar_servicios(dataObject.children)){clearInterval(cfg.interv);	PIPELINE = false; postExecutionStop(RN,error=false);} //debuging option
                cfg.errors++
            }
    
        } 
        cfg.monitor=false
    };
    xhr.send(send); //se envia el json

}

function download_data_pipe(rn,task,file_ext,file_name=null,raw=false){ //descargar datos de cualquier punto de el grafo
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
        get_file(data_request)
    } 
    else {
        data_request.REQUEST.type ="SOLUTION"
        get_file(data_request)
    } 
}

function get_file(data_request){
    $.ajax({ // ajax para rellenar valores de temporal
        url: 'includes/xel_getdata.php',
        type: 'POST',
        data:data_request,
        success: function(liga) {  
            console.log(liga)
            $("#invisible_link").html(`<a id='temporal_link' href='${liga}' target='_blank' ></a>`)
            $('#temporal_link').get(0).click();
            $("invisible_link").html("")
        }
    }).fail(function(){console.log("error al conectarse")});
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
    context={token_solution:token_solution,task:task,type_dataset:type_dataset,catalog:catalog}
    xel_describe_dataset(filename=filename,force=force,context=context).done(function(result){description = JSON.parse(result).info});

    combo_label="inspctDS"
    $('#modal_inspect_body').html(`<div class="col-12"><select class="form-control" 
        id="select_${combo_label}" onChange="SELECT_ShowValue('${combo_label}',this)" > <option value=""></option><select></div> <hr> `);
    sp = $(`#select_${combo_label}`)
    
    //create sections for each file described
    Object.keys(description.files_info).forEach(function(key) {
        console.log(key)
        name = key.replace(".","-").replace("/","-F-")
        sp.append(`<option value="${name}"> ${key} </option>`);
        $('#modal_inspect_body').append(`<div style="display:none;" id="${combo_label}_${name}" class="col-12 align-self-center ${combo_label}" ></div>`)
    });
    // ------------------------

//describe each file
    Object.keys(description.files_info).forEach(function(key) { 
        name = key.replace(".","-").replace("/","-F-")
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
    $('#modal_inspect').modal('show');
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
            service: service_name,
            childrens: []
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

        //add params to service
        new_service['params'] = new_params
        //do teh same for all childrens
        transform_dag(value,new_service.childrens)
    });
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
        }
    }).fail(function(){console.log("error al conectarse")});
}

function LoadExistingDataset(sourceId,filename,metadata=null){
    force_describe =$("#force_describe").is(':checked')
    if (force_describe==="undefined" || force_describe==""){
        force_describe=false
    }

    if(metadata ==null){ //si no se proporciona metadata, se hace la consulta. normalmente esto es para los datos recien procesados
        xel_describe_dataset(filename=filename,force=force_describe).done(function(result){
            metadata = JSON.parse(result).info
        });
    }
    // data was uploaded to the catalog MESH_WORKER by default of the user MESH USER
    DATA_WORKFLOW = {'data':{'token_user':MESH_USER,'catalog':MESH_WORKSPACE,'filename':filename},'type':'LAKE'}
    Handler_condition_GetData(sourceId,metadata,true,filename)
    notificarUsuario("Dataset loaded","info")
}

function fillworkspaces(sp){
    id_element = sp.id
    sp = $("#"+id_element)
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
        }
    }).fail(function(){console.log("error al conectarse")});

}
function fillWorkspaceFilesliest(){
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
                content +=`<td><button onclick="LoadExistingDataset('${sourceId}','${file['filename']}')" class="btn btn-outline-info btn-block">Read <i class="far fa-check-circle"></i></button>
                                <button onclick="DeleteDataset('${file_id}','${file['filename']}','table_LoadedFiles' )" class="btn btn-outline-danger btn-block">Delete <i class="fas fa-trash"></i></button>
                </td>`
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
        }
    }).fail(function(){console.log("error al conectarse")});

}


function fillselect(sp,mult=true){
    id_element = sp.id
    console.log(id_element)
    sp = $("#"+id_element)

    let BOX = demoflowy_lookForParent($("#modal_edition").data("sourceId")); //fill select
    console.log(BOX.service_metadata)
    if (BOX.service_metadata===undefined || Object.keys(BOX.service_metadata).length == 0){ //si es null se va a forzar la herencia
        BOX.service_metadata = demoflowy_lookForFather($("#modal_edition").data("sourceId")).service_metadata //father
    }

    //sp.append('<option value=""></option>'); // se añade un valor nulo
    if (!(BOX.service_metadata===undefined)){
        parentfilename = BOX.service_metadata.parent_filename
        BOX_columns = BOX.service_metadata.files_info[parentfilename].columns
        BOX_columns.forEach(function(col){
            sp.append('<option value="'+col+'">' + col + '</option>');
        });
    }

    // addd multiple attributte
    if(mult==true){
        sp.attr("multiple","multiple")
        sp.attr("data-actions-box","true")
    }

    sp.attr("data-size","5")
    sp.attr("data-live-search","true")
    sp.addClass("selectpicker");
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

    lista_filtros = ['Entidad','class']
    variable_clase = "class"
    variable_entidad ="Entidad"
    variable_municipio ="Municipio"
    variable_temporal ="Anio"


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
        c = BOX.service_metadata //columnas que procesa el servicio
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

    $(`#SOM-lat`).selectpicker('val', 'lat');
    $(`#SOM-lon`).selectpicker("val","lon");
    $(`#SOM-temporal`).selectpicker('val', "anio_ocur");
    $(`#SOM-spatial-filter`).selectpicker('val', "ent_ocurr");
    $(`#SOM-value-filter`).selectpicker('val', "");
    $(`#SOM-columna_class`).selectpicker('val', "");
    $(`#SOM-values`).selectpicker('val', "count");
    $(`#SOM-id`).selectpicker('val', "nombre");

    
    $("#modal_mapAAS").modal("show")
    $('.selectpicker').selectpicker('refresh')
}

var lista_global_filtros={}
var LISTA_CLUST_ORDENADOS=[]

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

    $("#SOM-loading").html("<img style='width:25%; height: 160px; margin-top: 50px; position: fixed; margin-left: 170px;' src='resources/imgs/loading.gif'></img")

    rn = $("#SOM-rn").val();
    task = $("#SOM-id_service").val();


    // aqui creo el combobox y mando llamar Show_data_on_map con un posible valor temporal
    $("#results2").html("")
    $("#results2").append("<div id='aas_temporal_combo' style='width:100%'></div>"); //div para combo de fechas
    $("#results2").append("<div id='aas_criteria' style='width:100%'></div>"); // div para combo de criterios
    $("#results2").append(`<button onclick="Show_data_on_map()" class="btn btn-outline-info btn-block">Request</button>`); // boton para mostrar resultados
    $("#results2").append("<div id='filtros-dinamicos' style='width:100%;max-height:400px; overflow-y:auto;'></div>"); //div para filtros
    $("#results2").append("<div id='clust_res' style='width:100%'></div>"); //div para resultados

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

            $("#aas_temporal_combo").append(`<label>Temporal: </label> <select class='form-control selectpicker idfechas' data-style="btn-info" width='80%' name="combo_temporalAAS">${dates}</select><hr>`);
            $(`select[name=combo_temporalAAS]`).selectpicker("refresh")
        }
    }).fail(function(){console.log("error al conectarse")});

    let data_request2 = {'SERVICE':'DatasetQuery' ,'REQUEST':{'data':{},'type':"SOLUTION"}}
    data_request2.REQUEST.data.token_user=MESH_USER //por defecto solo se usa este usuario
    data_request2.REQUEST.data.token_solution=PARAMS_MAP.rn
    data_request2.REQUEST.data.task=PARAMS_MAP.task

    if (PARAMS_MAP.value_filter!=null){ //el filtro por valor es opcional
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
                $("#aas_criteria").append(`<label>Special criteria: </label> <select data-actions-box="true" class='form-control selectpicker idfechas' data-style="btn-info" width='80%' name="combo_criteriosAAS">${criterios}</select><hr>`);
                $(`select[name=combo_criteriosAAS]`).selectpicker("refresh")
                $("#SOM-loading").html("")
            }
        }).fail(function(){console.log("error al conectarse")});
    
        $('[opth]').hide()
        $("#modal_mapAAS").modal('toggle');
        $('#mytabs a[href="#results-tab"]').tab('show');
        $('#tabs_show a[href="#mapContainer"]').tab('show');
    }   

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

    query = "(`"+col_temporal+"` == '"+temporal_value+"')" // QUERY CON DATOS DE TEMPORAL. ejemplo: fecha < 2019

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
    
    //console.log(criterio_value.length)
    console.log(query)
    data_request.REQUEST.ask = [{"request":"query","value":query }]
    $.ajax({
        url: 'includes/xel_Request.php',
        type: 'POST',
        dataType: 'json',
        data:data_request,
        success: function(result) {  
            console.log(result)
            datos = JSON.parse(result.info[0])
            datatemp = ChangeOrientationJSON(datos)
            //document.bkp_data = datatemp // se guardan los datos en memoria
            SetDataOnMap(datatemp)
            $('#mytabs a[href="#3b"]').tab('show');
            $('#tabs_show a[href="#mapContainer"]').tab('show');

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
    if (columns.length>=2){ CreatePlotCluster(dataset[columns[0]],dataset[columns[1]],null,null,xlabel = columns[0], ylabel=columns[1],color_list=null,div_container="cluster-plot-container")}
    else { CreatePlotCluster(dataset[columns[0]],dataset[columns[0]],null,null,xlabel = columns[0], ylabel=columns[0],color_list=null,div_container="cluster-plot-container")}
 
    CreatePlotHistogram(dataset,columns,div_container="boxplot-plot-container")

    //cantidades_para_escala_custom = cantidades_para_escala
    //cantidades_para_escala_custom[-1] = String(cantidades_para_escala[-2])+"+"
    renderPalette('color_scale', lista_colores,lista_clusters_ordenados);


    clean_AAS() //se limpian los marcadores anteriores
    dataset[col_id].forEach(function(row, row_idx) {
        label_marcador = etiquetas_por_marcador[row]
        index_color = lista_clusters_ordenados.indexOf(label_marcador);
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


// LISTA DE FUNCIONES PARA COMPORTAMIENTOS DE BOTONES 

// Guardar solucion en BD
function BTN_save_solution(){
    //AUTH
    let data_request = {"SERVICE":"StoreSolution",'REQUEST':{'auth':{'user':MESH_USER,'workspace':MESH_WORKSPACE},'metadata':{},'DAG':[]}}
    //metadata
    data_request.REQUEST.metadata = Metadata_collector()
    //TOKEN
    if (data_request.REQUEST.metadata.token!=""){data_request.REQUEST.token_solution= token}
    //DAG
    DAG=JSON.parse(JSON.stringify(dataObject)) 

    //transform_dag(dataObject,DAG)
    data_request.REQUEST.DAG = JSON.stringify(DAG) //list of task is sent as a string, not as a dict
    console.log(DAG)

    if(Object.keys(DAG.children).length > 0){
        //-------------------------
        $.ajax({
            url: 'includes/xel_Request.php',
            type: 'POST',
            dataType: 'json',
            data:data_request,
            beforeSend: function() {
                $("#modal_save-solutions-icon-load").html("<div style='width:100%; height:10px;'></div><img src='resources/imgs/loader.gif'></img>");
            },
            success: function(response) {  
                $("#modal_save-solutions-icon-load").html("")
                notificarUsuario("Solution was saved.","success")
                $("#modal_save-solutions-form-tokensolution").val(response['info']['token_solution'])
            }
        }).fail(function(){console.log("error al conectarse")});

    }
    else{
        notificarUsuario("no hay un grafo para guardar","warning")
    }

}
function BTN_retrieve_solution(token_solution){
    let data_request = {"SERVICE":"RetrieveSolution",'REQUEST':{'auth':{'user':MESH_USER,'workspace':MESH_WORKSPACE},"token_solution":token_solution}}
    $.ajax({
        url: 'includes/xel_Request.php',
        type: 'POST',
        dataType: 'json',
        data:data_request,
        success: function(result) {  
            console.log(result)
            result= result['info']
            // Change dataObject with the imported data.
            //dataObject = {id: "root", boxid: 0, type: result.metadata.source_type, service_type:"DATASOURCE", columns: { default: [], parent: [] }, name: "root", root: true, children: []}
            dataObject = JSON.parse(result.DAG);
            // Use Flowy import to add the boxes to the canvas.
            flowy.import(result.metadata.frontend);
            currentLayout = [...flowy.output().blockarr]
            
            // load metadata into page
            Metadata_assign(result.metadata)

            
        }
    }).fail(function(){console.log("error al conectarse")});

}

function BTN_list_solution(){

    let data_request = {"SERVICE":"ListSolutions",'REQUEST':{'auth':{'user':MESH_USER,'workspace':MESH_WORKSPACE}}}

    $.ajax({
        url: 'includes/xel_Request.php',
        type: 'POST',
        dataType: 'json',
        data:data_request,
        success: function(response) {  
            $('#modal_list-solutions-body').append("<div id='modal_list-solutions-table' class='form-group container col-12 table-responsive courtain' style='display:none'></div>");
            headeres = ['name','desc','tags','token_solution']

            content = ""
            content += `
                <table class="table table-hover table-sm dt-responsive nowrap compact-dt" id="table-solutions">
                    <caption>List of solutions</caption>
                    <thead>
                        <tr>`
                        headeres.forEach(function(h){
                            content += `<th scope="col">${h}</th>`
                        });
            content+= `<th scope="col">options</th>`
            content += `</tr></thead><tbody>`


            solution_id = 0
            response['info'].forEach(function(value){ //se rellena la tabla
                content +=`<tr id="solution_${solution_id}">` // se añade un id par apoder borrarlo despues
                headeres.forEach(function(h){
                    if (h=="token_solution"){
                        content += `<td>${value[h]}</td>`
                    }
                    else{
                        content += `<td>${value['metadata'][h]}</td>`
                    }
                });
                content +=`<td><button type='button' onclick='BTN_retrieve_solution("${value["token_solution"]}")' class="btn btn-outline-primary">GET</button></td>`
                content +=`</tr>`
                solution_id+=1
            });
            content +=`</tbody></table>`
            $("#modal_list-solutions-table").html(content)


            // SHOW MODAL
            $('#modal_list-solutions').modal('show');

            // create datatable
            $("#table-solutions").DataTable({
                responsive: true,
                "lengthMenu": [[5, 10, 25, 50], [5, 10, 25, 50]],
                "scrollX": false
            } );
            

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
  };

// don't navigate away from the field on tab when selecting an item

function Activate_Autcomplete() { 
    Modal_selector = ".modal.fade.show" // sirve para los modal activos (debe estar activo primero)
    tag_4_auto = ".autocomplete-column"    // TAG FOR THE AUTOCOMPLETE

    sourceid = $(Modal_selector).data("sourceId")

    let BOX = demoflowy_lookForParent(sourceid); //fill select
    const isEmpty = Object.keys(BOX).length === 0
    //si es null no se hace nada
    if (BOX===null || isEmpty){ console.log("no se requiere autocomplete");return 0;}

    console.log("se activo el autocomplete")

    if (BOX.service_metadata===undefined){ //si es null se va a forzar la herencia
        console.log("heredando valores")
        let fatherBOX = demoflowy_lookForFather(sourceid) //father
        if (fatherBOX===null){ //si es null no se hace nada
            console.log("La caja padre no tiene info para autocompletar")
            return 0
        }
        BOX.service_metadata = fatherBOX.service_metadata
    }
    if (BOX.service_metadata===undefined){ //si aun asi es undefined, se cierra el proceso
        notificarUsuario("No dataset detected.", "warning")
        return 0
    }

    parentfilename = BOX.service_metadata.parent_filename
    availableTags = BOX.service_metadata.files_info[parentfilename].columns



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

                if ( Object.keys(BOX.service_metadata.files_info[parentfilename].unique).includes(Fathercolumn)){
                    tagscol =  BOX.service_metadata.files_info[parentfilename].unique[Fathercolumn] 
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

            //if (this.value.includes("@")) {// its a column
            //    var terms = sentence_split(this.value,"@");
            //}
            //else{ //its a unique value
            //    var terms = sentence_split(this.value,".");
            //}
            //console.log(terms)
            //// remove the current input
            //terms.pop();
            //// add the selected item
            //terms.push(ui.item.value);
            //// add placeholder to get the comma-and-space at the end
            //terms.push("");
            //this.value = terms.join("");   
            return false;

        }
    });
    
}


/////
function SELECT_ShowValue(combo_label="default", combo){
    //hide all divs with the combo_label class
    table_id = `#table_${combo_label}_${combo.value}`
    sample_table_id = `#table_sample_${combo_label}_${name}`
    $('.'+combo_label).hide();
    $('#'+combo_label+'_'+combo.value).show();
    
    if ( $.fn.dataTable.isDataTable( table_id ) ) {
        console.log("recalculations", table_id)
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

    
    $("#modal_create").modal("show")
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
                    $("#modal_create").modal("hide")
                    // update list
                    $("#user_workspace").click()
                    $("#user_workspace").selectpicker("refresh")
                }
                else{
                    notificarUsuario("Workspace could not be created.","danger")
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
                    $("#user_workspace").click()
                    $("#user_workspace").selectpicker("refresh")
                }
                else{
                    notificarUsuario("Workspace could not be deleted.","danger")
                }
            }
        }).fail(function(){console.log("error al conectarse")});
    }

}

//// funcione smuys especificas para servicios, en un futuro se van a cambiar

function addRule(){
    value_text= $("#addtolist").val()
    console.log(value_text)
    $("#ReplaceWithNa").append("<li id ='"+value_text+"' class='list-group-item'>"+value_text+" <a href='#' onclick='remove_list_element(this)' data-toggle='tooltip' title='remove this'><span class='glyphicon glyphicon-minus' aria-hidden='true'></span></a> </li>")
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
    MESH_WORKSPACE= $("#user_workspace").val()
    //notificarUsuario("")
}