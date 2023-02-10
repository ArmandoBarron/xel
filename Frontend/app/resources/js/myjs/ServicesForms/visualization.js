


/// SERVICOS DE PREPROCESAMIENTO
SECTION = "sec-visualitation"

ServicesArr.push(
    {
        id: "maps",
        process_tag:"geographical map",

        valid_datatypes:{input:["CSV"],output:["HTML"]},
        name: "maps",
        section:SECTION,
        desc: `Visalize data in a map`,
        columns:{
            default: null,
            parent: [] 
        },
        params: {
                actions:["MARKER"],
                geocve_column:"",
                area:"",
                title:"",
            lat:0,
            lon:0,
            groupby:"",
            variables:"",
            class:"",
            normalize:"0",
            label:"",
            size:"",
            radius:5,
            kind_poly_map:"",
            temporal_column:"",
            additional_columns:"",
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
                                <select class="form-control" id="actions" onchange="ChangeVisibileOptionsOfService(this)">
                                        <option value="POLY"> Mexico's AGEBs </option>
                                        <option value="STATES"> Mexico's States </option>
                                        <option value="MARKER"> HeatMap (lat/lon)</option>
                                        <option value="SCATTERMAP"> Labeled Map (lat/lon)</option>
                                        <option value="DENSITY"> Density Map (lat/lon)</option>

                                </select>
                                </div>
                        </div>

                        <div class="form-group row m-2" servopt="POLY STATES">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">column with geocve: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="geocve_column" onclick=fillselect(this,mult=false)></select>
                                </div>
                        </div>


                        <div class="form-group row m-2" servopt="POLY">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Zone: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="area">
                                        <option value="00"> AUTO (slow) </option>
                                        <option value="15"> Mexico </option>
                                        <option value="24"> SLP </option>
                                </select>
                                </div>
                        </div>


                        <div class="form-group row m-2" servopt="POLY SCATTERMAP DENSITY STATES">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Title of the chart:</label>
                                <div class="col-sm-8">
                                        <input id="title" type="text" class="form-control">
                                </div>
                        </div>


                        <div class="form-group row m-2" servopt="MARKER SCATTERMAP DENSITY">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Latitud: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="lat" onclick=fillselect(this,mult=false)></select>
                                </div>
                        </div>

                        <div class="form-group row m-2" servopt="MARKER SCATTERMAP DENSITY">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Longitud: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="lon" onclick=fillselect(this,mult=false)></select>
                                </div>
                        </div>

                        <div class="form-group row m-2" servopt="DENSITY">
                                <label class="col-sm-4 col-form-label col-form-label-sm">Radius:</label>
                                <div class="col-sm-4">
                                        <input type="number" class="form-control solo-numero" min="2" id="radius">
                                </div>
                        </div>

                        <div class="form-group row m-2" servopt="MARKER SCATTERMAP">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">(optional) Group by: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="groupby" onclick=fillselect(this,mult=false)>
                                </select>
                                </div>
                        </div>

                        <div class="form-group row m-2" servopt="MARKER">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Variables: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="variables" onclick=fillselect(this)></select>
                                </div>
                        </div>


                        <div class="form-group row m-2" servopt="STATES">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Kind of polygon map: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="kind_poly_map">
                                        <option value="HEATMAP"> Heatmap (for float column class) </option>
                                        <option value="CLASS"> Label (for string or categorical column class) </option>
                                </select>
                                </div>
                        </div>

                        <div servopt="POLY SCATTERMAP STATES" class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">class column (used for color map):  </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="class" onclick=fillselect(this,mult=false,source=null,add="clase")>
                                        <option value="clase"> clase </option>
                                </select>
                                </div>
                        </div>

                        <div servopt="MARKER POLY SCATTERMAP STATES" class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">ID (to identify the points in the map): </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="label" onclick=fillselect(this,mult=false)></select>
                                </div>
                        </div>

                        <div servopt="SCATTERMAP" class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Size of markers (optional): </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="size" onclick=fillselect(this,mult=false,source=null,add="clase")></select>
                                </div>
                        </div>

                        <div servopt="MARKER" class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Normalize: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="normalize">
                                        <option value="1" selected> True </option>
                                        <option value="0"> False </option>
                                </select>
                                </div>
                        </div>

                        <div servopt="STATES" class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Temporal column (optional) </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="temporal_column" onclick=fillselect(this,mult=false,source=null,add="clase")></select>
                                </div>
                        </div>

                        <div servopt="STATES" class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Additional columns to show </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="additional_columns" onclick=fillselect(this,mult=true,source=null,add="clase")></select>
                                </div>
                        </div>

`
    }
)


ServicesArr.push(
        {
            id: "charts-sv",
            process_tag:"charts",
            endpoint:"charts",
            valid_datatypes:{input:["CSV"],output:["HTML","ZIP"]},
            name: "charts",
            section:SECTION,
            desc: `Visalize data in a graph`,
            columns:{
                default: null,
                parent: [] 
            },
            params: {
                actions:[""],
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
                topk_temporal:"",
                topk_value:"",
                topk_name:"",
                topk_n:"",
                topk_func:"",
                SAVE_DATA:true
            },
            html: `
            <div class="form-check" style="text-align: right;">
                <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
                <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
            </div>
            <br>
                        <div class="form-group row m-2">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Product: </label>
                                    <div class="col-sm-8">
                                        <select class="form-control" id="actions" onchange="OptionsHandler(this)">
                                                <option value="REQUEST"> Charts </option>
                                                <option value="TOP_K"> TOP K Race </option>
                                        </select>
                                    </div>
                        </div>
                            
                
                        <div opth opt-actions="TOP_K">

                                <div class="form-group row m-2">
                                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Temporal: </label>
                                        <div class="col-sm-8">
                                        <select class="form-control" id="topk_temporal" onclick=fillselect(this,multi=false)></select>
                                        </div>
                                </div>
                                <div class="form-group row m-2">
                                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">value column: </label>
                                        <div class="col-sm-8">
                                        <select class="form-control" id="topk_value" onclick=fillselect(this,multi=false)></select>
                                        </div>
                                </div>
                                <div class="form-group row m-2">
                                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Name columns: </label>
                                        <div class="col-sm-8">
                                        <select class="form-control" id="topk_name" onclick=fillselect(this)></select>
                                        </div>
                                </div>


                                <div class="form-group row m-2">
                                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Race function: </label>
                                        <div class="col-sm-8">
                                        <select class="form-control" id="topk_func">
                                                <option value="sum" selected> sum </option>
                                                <option value="mean"> mean </option>
                                        </select>
                                        </div>
                                </div>

                                <div class="form-group row m-2">
                                        <label class="col-sm-4 col-form-label col-form-label-sm">TOP:</label>
                                        <div class="col-sm-4">
                                                <input type="number" class="form-control solo-numero" min="3" id="topk_n">
                                        </div>
                                </div>

                        </div>

                        <div opth opt-actions="REQUEST">
                        

                            <div class="form-group row m-2">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Chart: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="chart" onchange="OptionsHandler(this)">
                                            <option value="1"> Density </option>
                                            <option value="2"> Scatter matrix map </option>
                                            <option value="3"> Parallel categories </option>
                                            <option value="4"> Temporal bubble plot </option>
                                            <option value="5"> Line plot </option>
                                            <option value="6"> Sunbrust </option>
                                            <option value="7"> Scatter </option>
                                            <option value="8"> 3D Scatter </option>
                                            <option value="9"> 3D Scatter with PCA </option>
                                            <option value="10"> Bar plot </option>
                                            <option value="11"> Box plot </option>
                                            <option value="12"> Cumulative bar plot </option>

                                    </select>
                                    </div>
                            </div>
    
                            <div class="form-group row m-2" opth opt-chart="1">
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

                            <div class="form-group row m-2" opth opt-chart="1 2 3 9">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">columns: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="columns" onclick=fillselect(this)></select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" opth opt-chart="2 4 5 6 7 8 9 10 11 12" >
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Label variable: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="label_column" onclick=fillselect(this,multi=false)></select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" opth opt-chart="3">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Color scale column: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="colorscale_column" onclick=fillselect(this,multi=false)></select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" opth opt-chart="4 5 7 8 10 11 12">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Variable x: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="column_x" onclick=fillselect(this,multi=false)></select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" opth opt-chart="4 5 7 8 10 11 12">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Variable y: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="column_y" onclick=fillselect(this,multi=false)></select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" opth opt-chart="8">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Variable z: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="column_z" onclick=fillselect(this,multi=false)></select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" opth opt-chart="4 6 11">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Variable temporal: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="temporal_column" onclick=fillselect(this,multi=false)></select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" opth opt-chart="4 5">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Subgroup by: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="subgroup" onclick=fillselect(this,multi=false)></select>
                                    </div>
                            </div>
                            
                            <div class="form-group row m-2" opth opt-chart="4 6">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Column with sizes: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="size" onclick=fillselect(this,multi=false)></select>
                                    </div>
                            </div>


                            <div class="form-group row m-2" opth opt-chart="4 7">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Apply log scale: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="if_log_scale">
                                            <option value="1"> True </option>
                                            <option value="0"> False </option>
                                    </select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" opth opt-chart="6">
                                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Groups order:</label>
                                        <div class="col-sm-8">
                                                <input id="groups_path" type="text" class="form-control autocomplete-column">
                                        </div>
                                        <div class="container">
                                                <span class="help-block">Write columns names separated by comma</span>
                                                <span class="help-block">use @ to autocomplete columns</span>
                                        </div>
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



ServicesArr.push(
        {
            id: "AdvMap",
            process_tag:"geographical map",
            valid_datatypes:{input:["ZIP"],output:["HTML"]},
            name: "advanced_maps",
            section:SECTION,
            desc: `Visalize data in a map`,
            columns:{
                default: null,
                parent: [] 
            },
            params: {
                actions:"",
                poly_file:"",
                geocve_column:"",
                area:"",
                title:"",
                class:"",
                label:"",
                scatter_file:"",
                lat:0,
                lon:0,
                scatter_class:"",
                scatter_id:"",
                marker_size:"",
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
                                <select class="form-control" id="actions" onchange="OptionsHandler(this)">
                                        <option value="AGEB"> By AGEB code </option>
                                        <option value="STATES"> By State code </option>
                                </select>
                                </div>
                        </div>
    
                            <div class="form-group row m-2">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Filename for map</label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="poly_file" onclick=fill_namefiles_select(this) onChange=UpdateSelectBoxByClass("poly") ></select>
                                    </div>
                            </div>

                            <div class="form-group row m-2">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">column with geocve: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control poly" id="geocve_column" onclick=fillselect(this,mult=false,"#poly_file")></select>
                                    </div>
                            </div>
    
                            <div class="form-group row m-2">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">String label for polygon </label>
                                    <div class="col-sm-8">
                                    <select class="form-control poly" id="label" onclick=fillselect(this,mult=false,"#poly_file")></select>
                                    </div>
                            </div>

                            <div class="form-group row m-2">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Column for color scale in polygon </label>
                                    <div class="col-sm-8">
                                    <select class="form-control poly" id="class" onclick=fillselect(this,mult=false,"#poly_file")></select>
                                    </div>
                            </div>

                            <div class="form-group row m-2" opth opt-actions="AGEB">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Zone: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="area">
                                            <option value="00"> AUTO (slow) </option>
                                            <option value="15"> Mexico </option>
                                            <option value="24"> SLP </option>
                                    </select>
                                    </div>
                            </div>
                            
                            <div class="form-group row m-2">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Title of the chart:</label>
                                    <div class="col-sm-8">
                                            <input id="title" type="text" class="form-control">
                                    </div>
                            </div>
                        
                            <hr>

                            <div class="form-group row m-2">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Scatter data filename: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control" id="scatter_file" onclick=fill_namefiles_select(this) onChange=UpdateSelectBoxByClass("scatter")></select>
                                    </div>
                            </div>
                            <div class="form-group row m-2">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Latitud: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control scatter" id="lat" onclick=fillselect(this,mult=false,"#scatter_file")></select>
                                    </div>
                            </div>
    
                            <div class="form-group row m-2">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Longitud: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control scatter" id="lon" onclick=fillselect(this,mult=false,"#scatter_file")></select>
                                    </div>
                            </div>
                            <div class="form-group row m-2">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">scatter class: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control scatter" id="scatter_class" onclick=fillselect(this,mult=false,"#scatter_file")></select>
                                    </div>
                            </div>
                            <div class="form-group row m-2">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">scatter id: </label>
                                    <div class="col-sm-8">
                                    <select class="form-control scatter" id="scatter_id" onclick=fillselect(this,mult=false,"#scatter_file")></select>
                                    </div>
                            </div>
        
                            <div class="form-group row m-2" opth opt-actions="STATES">
                                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Marker size (optional) </label>
                                    <div class="col-sm-8">
                                    <select class="form-control scatter" id="marker_size" onclick=fillselect(this,mult=false,"#scatter_file")></select>
                                    </div>
                            </div>
                            


    
    `
        }
    )
    