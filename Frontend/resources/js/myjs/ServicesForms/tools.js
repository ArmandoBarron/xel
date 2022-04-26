/// SERVICOS DE PREPROCESAMIENTO
SECTION = "sec-tools"
ServicesArr.push({
    id: "Data_acquisition",
    name: "Acquisition",
    section:SECTION,
    desc: `Acquire data directly from a repository (Google Drive, HydroShare, FTP server, etc.).`,
    columns:{
        default: null,
        parent: [] 
    },
    params: {
        DOWNLOAD_server: 'URL',
        NAMEFILE: '',
        EXT: '',
        URL: '',
        ID_FILE: '',
        USER:'',
        PASS:'',
        SAVE_DATA:true
    },
    html: `
    <div class="form-check" style="text-align: right;">
        <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
        <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
    </div>
    <br>
                    <div class="form-group row m-2">
                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Server: </label>
                            <div class="col-sm-8">
                            <select class="form-control" id="DOWNLOAD_server"">
                                    <option value="URL" selected > URL </option>
                                    <option value="GOOGLE_DRIVE" > Google Drive </option>
                                    <option value="HYDROSHARE" > HydroShare </option>
                                    <option value="FTP" > FTP server </option>
                                    <option value="BB_FILES" > Test files </option>
                            </select>
                            </div>
                    </div>

                    <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">NameFile: </label>
                        <div class="col-sm-8">
                                <input id="NAMEFILE" type="text" class="form-control">
                        </div>
                    </div>
                    <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">File extention: </label>
                        <div class="col-sm-8">
                                <input id="EXT" type="text" class="form-control" placeholder="example: csv,txt,jpeg,etc.." aria-label="example: csv,txt,jpeg,etc..">
                        </div>
                    </div>
                    <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">URL: </label>
                        <div class="col-sm-8">
                                <input id="URL" type="text" class="form-control" placeholder="https://www.hyd.../file.txt or test.rebex.net/fileinftp.txt" aria-label="https://www.hyd.../file.txt or test.rebex.net/fileinftp.txt">
                        </div>
                    </div>
                    <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">ID FILE (in the case of Google Drive): </label>
                        <div class="col-sm-8">
                                <input id="ID_FILE" type="text" class="form-control">
                        </div>
                    </div>
                    <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">USERNAME: </label>
                        <div class="col-sm-8">
                                <input id="USER" type="text" class="form-control">
                        </div>
                    </div>
                    <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">PASSWORD: </label>
                        <div class="col-sm-8">
                                <input id="PASS" type="password" class="form-control">
                        </div>
                    </div>
                    `
})

ServicesArr.push(
    {
        id: "Format_converter",
        name: "Converters",
        section:SECTION,
        desc: `Convert a file to a different format.`,
        columns:{
            default: null,
            parent: [] 
        },
        params: {
            ToFormat: 'csv',
            SAVE_DATA:true
        },
        html: `
        <div class="form-check" style="text-align: right;">
            <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
            <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
        </div>
        <br>
                        <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">ToFormat: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="ToFormat"">
                                        <option value="csv" selected > csv </option>
                                        <option value="xls" > xls </option>
                                        <option value="json" > json </option>
                                        <option value="txt" > txt </option>
                                </select>
                                </div>
                        </div>
                        `
    }
)

ServicesArr.push({
    id: "grobid_service",
    name: "Grobid",
    section:SECTION,
    desc: `Text mining`,
    columns:{
        default: null,
        parent: [] 
    },
    params: {
        n: 2,
        process:'processFulltextDocument',
        SAVE_DATA:true
    },
    html: `
    <div class="form-check" style="text-align: right;">
        <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
        <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
    </div>
    <br>
                    <div class="form-group row m-2">
                        <label for="ntype" class="col-sm-4 col-form-label col-form-label-sm">parallel workers: </label>
                            <div class="col-sm-8">
                                    <input id="n" type="number" class="form-control form-control-sm" value=2 min="1" max="12">
                            </div>
                        </div>
                    <div class="form-group row m-2">
                    <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Type of process: </label>
                            <div class="col-sm-8">
                            <select class="form-control" id="process">
                                    <option value="processFulltextDocument" selected > process full text document </option>
                                    <option value="processReferences" > process references </option>
                                    <option value="processHeaderDocument" > process header document </option>
                            </select>
                            </div>
                    </div>
                    `
})
ServicesArr.push(
    {
        id: "Glove_service",
        name: "Glove",
        section:SECTION,
        desc: `Text mining`,
        columns:{
            default: null,
            parent: [] 
        },
        params: {
            actions:"REQUEST",
            vocabfile_name:"vocab.txt",
            vectorsfile_name:"vectors.txt",
            SAVE_DATA:true
        },
        html: `
        <div class="form-check" style="text-align: right;">
            <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
            <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
        </div>
        <br>
        <div class="form-group row m-2">
        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Type of process: </label>
                <div class="col-sm-8">
                <select class="form-control" id="actions">
                        <option value="REQUEST" selected > Process test</option>
                        <option value="EVAL" > Evaluate </option>
                </select>
                </div>
        </div>

        <div class="form-group row m-2">
            <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Vocab filename: </label>
            <div class="col-sm-8">
                    <input id="vocabfile_name" type="text" class="form-control">
            </div>
        </div>
        <div class="form-group row m-2">
            <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Vectors filename: </label>
            <div class="col-sm-8">
                    <input id="vectorsfile_name" type="text" class="form-control">
            </div>
        </div>


                        `
    })