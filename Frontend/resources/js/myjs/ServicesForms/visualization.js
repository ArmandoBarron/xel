


/// SERVICOS DE PREPROCESAMIENTO
SECTION = "sec-visualitation"

ServicesArr.push(
    {
        id: "maps",
        name: "maps",
        section:SECTION,
        desc: `Visalize data in a map`,
        columns:{
            default: null,
            parent: [] 
        },
        params: {
            map_type:1,
            lat:0,
            lon:0,
            groupby:"",
            variables:"",
            class:"",
            normalize:"0",
            SAVE_DATA:true
        },
        html: `
        <div class="form-check" style="text-align: right;">
            <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
            <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
        </div>
        <br>

                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Map type: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="map_type" onchange="ChangeVisibileOptionsOfService(this)">
                                        <option value="1"> heatmap </option>
                                        <option value="2"> clustering map </option>
                                </select>
                                </div>
                        </div>


                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Latitud: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="lat" onclick=fillselect(this,mult=false)></select>
                                </div>
                        </div>

                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Longitud: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="lon" onclick=fillselect(this,mult=false)></select>
                                </div>
                        </div>

                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Group by: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="groupby" onclick=fillselect(this,mult=false)>
                                </select>
                                </div>
                        </div>

                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Variables: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="variables" onclick=fillselect(this)></select>
                                </div>
                        </div>

                        <div servopt="2" class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">class label: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="class" onclick=fillselect(this,mult=false)></select>
                                </div>
                        </div>

                        <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Normalize: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="normalize">
                                        <option value="1" selected> True </option>
                                        <option value="0"> False </option>
                                </select>
                                </div>
                        </div>

`
    }
)


ServicesArr.push(
        {
            id: "charts-sv",
            endpoint:"charts",
            name: "charts",
            section:SECTION,
            desc: `Visalize data in a map`,
            columns:{
                default: null,
                parent: [] 
            },
            params: {
                chart:1,
                histo_type:"density",
                columns:"",
                label_column:"",
                colorscale_column:"",
                column_x:"",
                column_y:"",
                column_z:"",
                temporal_column:"",
                subgroup:"",
                size:"",
                if_log_scale:0,
                groups_path:"",
                title:"",
                SAVE_DATA:true
            },
            html: `
            <div class="form-check" style="text-align: right;">
                <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
                <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
            </div>
            <br>
    
                            <div class="form-group row m-2">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Chart: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="chart" onchange="ChangeVisibileOptionsOfService(this)">
                                            <option value="1"> Density </option>
                                            <option value="2"> Scatter matrix map </option>
                                            <option value="3"> Parallel categories </option>
                                            <option value="4"> Temporal bubble plot </option>
                                            <option value="5"> Line plot </option>
                                            <option value="6"> Sunbrust </option>
                                            <option value="7"> Scatter </option>
                                            <option value="8"> 3D Scatter </option>
                                    </select>
                                    </div>
                            </div>
    
                            <div class="form-group row m-2" servopt="1">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">histogram type: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="histo_type">
                                            <option value="density"> Density </option>
                                            <option value="probability"> probability </option>
                                            <option value="percent"> percent </option>
                                            <option value="probability density"> probability density </option>
                                    </select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" servopt="1 2 3">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">columns: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="columns" onclick=fillselect(this)></select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" servopt="2 4 5 6 7 8" >
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Label variable: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="label_column" onclick=fillselect(this,multi=false)></select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" servopt="3">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Color scale column: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="colorscale_column" onclick=fillselect(this,multi=false)></select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" servopt="4 5 7 8">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Variable x: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="column_x" onclick=fillselect(this,multi=false)></select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" servopt="4 5 7 8">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Variable y: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="column_y" onclick=fillselect(this,multi=false)></select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" servopt="8">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Variable z: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="column_z" onclick=fillselect(this,multi=false)></select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" servopt="4 6">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Variable temporal: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="temporal_column" onclick=fillselect(this,multi=false)></select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" servopt="4 5">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Subgroup by: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="subgroup" onclick=fillselect(this,multi=false)></select>
                                    </div>
                            </div>
                            
                            <div class="form-group row m-2" servopt="4 6">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Column with sizes: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="size" onclick=fillselect(this,multi=false)></select>
                                    </div>
                            </div>


                            <div class="form-group row m-2" servopt="4 7">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Apply log scale: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="if_log_scale">
                                            <option value="1"> True </option>
                                            <option value="0"> False </option>
                                    </select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" servopt="6">
                                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Groups order:</label>
                                        <div class="col-sm-8">
                                                <input id="groups_path" type="text" class="form-control autocomplete-column">
                                        </div>
                                        <div class="container">
                                                <span class="help-block">Write columns names separated by comma</span>
                                                <span class="help-block">use @ to autocomplete columns</span>
                                        </div>
                            </div>

                            <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Title of the chart:</label>
                                <div class="col-sm-8">
                                        <input id="title" type="text" class="form-control">
                                </div>
                            </div>

    
    `
        }
    )

//ServicesArr.push({
//        id: "tps-s-statistics",
//        name: "TS-describe",
//        section:SECTION,
//        desc: `Returns an stadistical description of the dataset`,
//        columns:{
//            default: null,
//            parent: [] 
//        },
//        params: {
//            columns: 'all',
//            SAVE_DATA:true
//        },
//        html: `
//        <div class="form-check" style="text-align: right;">
//            <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
//            <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
//        </div>
//        <br>
//                        <div class="form-group row m-2">
//                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Columns: </label>
//                                <div class="col-sm-8">
//                                <select class="form-control" id="columns" data-actions-box="true" onclick=fillselect(this) >
//                                        <option value="all" selected > All numeric columns </option>
//                                </select>
//                                </div>
//                        </div>
//                        `
//    })