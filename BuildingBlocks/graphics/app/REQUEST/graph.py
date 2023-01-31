import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import math
import sys
from sklearn.decomposition import PCA

def validate_att(att): #esta funcion sirve para validar que un argumento viene vacio o no
    if att =="" or att =="-":
        return False
    else:
        return True

def validate_bool(att): #esta funcion sirve para validar que un argumento viene vacio o no
    if att =="0":
        return False
    else:
        return True

def export_figures(fig,outputpath,imagefile_name,config):

    fig.update_layout(title=TITLE,
                    dragmode='select',
                    width=1000,
                    height=1000,
                    hovermode='closest')

    #fig.write_image("%s/%s.png" % (outputpath,imagefile_name))
    #fig.write_image("%s/%s.svg" % (outputpath,imagefile_name))
    fig.write_html("%s/%s.html" % (outputpath,imagefile_name),config=config,auto_open=False)

## parameters by argument
print(sys.argv)

inputpath = sys.argv[1] # "Suic_Medio_Derhab_tasasporsexo.csv"
outputpath = sys.argv[2] #  "./output/"
chart_template =int(sys.argv[3]) # 1-7

# for chart 1
TYPE_HISTOGRAM = sys.argv[4] #  "density" # ['', 'percent', 'probability', 'density', 'probability density'] 

# for chart 2
COLUMNS = sys.argv[5].split(",") # "sexo,anio".split(",")
LABEL_COLUMN = sys.argv[6] # "sexo"
# for chart 3
COLORSCALE_COLUMN = sys.argv[7] # "suicDerehab"

# for chart 4
COLUMN_X = sys.argv[8] # "suicDerehab"
COLUMN_Y = sys.argv[9] # "suicSinDerhab"
TEMPORAL_COLUMN = sys.argv[10] # ""
SUBGROUP = sys.argv[11] # "cve_ent_mun"
SIZE= sys.argv[12] # "suicSinDerhab"

LOG_SCALE = validate_bool(sys.argv[13]) # validate_bool("0")

# for chart 6
GROUPS_PATH = sys.argv[14] #  "cve_ent_mun,sexo".split(",")

#for any chart
TITLE = sys.argv[15] # "PLOT"

COLUMN_Z = sys.argv[16] # "suicSinDerhab"

#validations

config = {'displaylogo': False,
        'editable': True,
        'showLink': True,
        'plotlyServerURL': "https://chart-studio.plotly.com",
        'modeBarButtonsToAdd':['drawline','drawopenpath','drawclosedpath','drawcircle','drawrect','eraseshape']
}


#read Dataset
#df = pd.read_csv(inputpath).query("CAUSA_DEF=='C910'")
df = pd.read_csv(inputpath)

if chart_template==1: #histogram
    cant_plots = len(COLUMNS)
    col = math.ceil(cant_plots/2)
    rows =  math.ceil(cant_plots/col)
    print (col,rows)
    fig = make_subplots(rows=rows, cols=col)

    imagefile_name = "histogram_plot"
    data_matrix = []
    col_i = 1
    row_i = 1
    for c in COLUMNS:
        fig.add_trace(go.Histogram(x=df[c].to_list(),
            histnorm=TYPE_HISTOGRAM,
            name=c # name used in legend and hover labels
            ),row=row_i, col=col_i)
        col_i+=1
        if col_i > col:
            col_i=1
            row_i+=1 

    export_figures(fig,outputpath,imagefile_name,config)

    fig = make_subplots(rows=rows, cols=col)
    imagefile_name = "accumulative_plot"
    data_matrix = []
    col_i = 1
    row_i = 1
    for c in COLUMNS:
        fig.add_trace(go.Histogram(x=df[c].to_list(),
            histnorm=TYPE_HISTOGRAM,
            cumulative_enabled=True,
            name=c # name used in legend and hover labels
            ),row=row_i, col=col_i)
        col_i+=1
        if col_i > col:
            col_i=1
            row_i+=1 

    export_figures(fig,outputpath,imagefile_name,config)


if chart_template==2: # scatter matrix
    imagefile_name = "scatter_matrix"
    if validate_att(LABEL_COLUMN): # if there is a label for color
        fig = px.scatter_matrix(df,dimensions=COLUMNS,color=LABEL_COLUMN)
    else:
        fig = px.scatter_matrix(df,dimensions=COLUMNS)
    
    export_figures(fig,outputpath,imagefile_name,config)

if chart_template==3: 
    imagefile_name = "parallel_categories"
    temp_col = COLUMNS+[COLORSCALE_COLUMN]
    print(temp_col) 
    fig = px.parallel_categories(df[temp_col], color=COLORSCALE_COLUMN, color_continuous_scale=px.colors.sequential.Inferno)
    export_figures(fig,outputpath,imagefile_name,config)

if chart_template==4: #BUBBLE PLOT
    imagefile_name = "Temporal_Bubbles"
    params = dict(x=COLUMN_X, y=COLUMN_Y, animation_frame=TEMPORAL_COLUMN, size=SIZE,
    log_x=LOG_SCALE,log_y=LOG_SCALE, size_max=45)

    if validate_att(LABEL_COLUMN): # si hay colores
        params['color']=LABEL_COLUMN
        #params['facet_col']=LABEL_COLUMN

    if validate_att(SUBGROUP):# si hay subgrupos
        params['animation_group']=SUBGROUP
        params['hover_name']=SUBGROUP

    fig = px.scatter(df,**params)
    export_figures(fig,outputpath,imagefile_name,config)

if chart_template==5: #LINE PLOT
    imagefile_name = "Line"
    params = dict(x=COLUMN_X, y=COLUMN_Y, line_shape="linear", render_mode="svg")

    if validate_att(LABEL_COLUMN): # si hay colores
        params['color']=LABEL_COLUMN

    if validate_att(SUBGROUP):# si hay subgrupos
        params['line_group']=SUBGROUP
        params['hover_name']=SUBGROUP



    # try to convert DT
    try:
        df[COLUMN_X]=pd.to_datetime(df[COLUMN_X])
    except Exception: #Can't cnvrt some
        print("NO SE CONVIRTIO A DATETIME")
    
    df= df.sort_values(by=COLUMN_X)


    fig = px.line(df, **params)

    export_figures(fig,outputpath,imagefile_name,config)


if chart_template==6:
    imagefile_name = "SUNBRUST"
    params = dict(path=GROUPS_PATH, values=SIZE)
    ## aqui se aplica un équeño preprocesdamiento para quitar datos en blanco
    df.dropna(subset=GROUPS_PATH+[SIZE], how='any', inplace=True)
    #df[GROUPS_PATH] = df[GROUPS_PATH].fillna('NE/NA')
    df[SIZE] = df[SIZE].fillna(0)


    if validate_att(LABEL_COLUMN): # si hay colores
        params['color']=LABEL_COLUMN


    if validate_att(TEMPORAL_COLUMN): # si hay una columna de temporal, se crean multiples graficas para cada valor de temporal
        df_grouped = df.groupby(TEMPORAL_COLUMN)
        for namedf,group_df in df_grouped:
            imagefile_name = "SUNBRUST_%s" %namedf
            print(imagefile_name)
            fig = px.sunburst(group_df, **params)
            export_figures(fig,outputpath,imagefile_name,config)

    else:
        fig = px.sunburst(df, **params)
        export_figures(fig,outputpath,imagefile_name,config)


if chart_template==7:
    imagefile_name = "simple_scatter"
    params = dict(x=COLUMN_X, y=COLUMN_Y, marginal_y="violin", marginal_x="violin", trendline="ols", log_x=LOG_SCALE,log_y=LOG_SCALE)

    if validate_att(LABEL_COLUMN): # si hay colores
        params['color']=LABEL_COLUMN

    fig = px.scatter(df, **params)

    export_figures(fig,outputpath,imagefile_name,config)

if chart_template==8: # 3D scatter matrix
    imagefile_name = "3d_scatter"
    params = dict(x=COLUMN_X, y=COLUMN_Y,z=COLUMN_Z)

    if validate_att(LABEL_COLUMN): # si hay colores
        params['color']=LABEL_COLUMN

    fig = px.scatter_3d(df, **params)

    export_figures(fig,outputpath,imagefile_name,config)

if chart_template==9: # 3D scatter with PCA
    imagefile_name = "3d_scatter"
    pca = PCA(n_components=3)
    principalComponents = pca.fit_transform(df[COLUMNS])
    pca_df = pd.DataFrame(principalComponents,columns=["x","y","z"])
    pca_df.index.name="id"

    params = dict(x="x", y="y",z="z")

    if validate_att(LABEL_COLUMN): # si hay colores
        pca_df = pca_df.join(df[LABEL_COLUMN])

        #pca_df = pca_df.merge(df[LABEL_COLUMN],on=["id"],how="inner")
        params['color']=LABEL_COLUMN

    fig = px.scatter_3d(pca_df, **params)

    export_figures(fig,outputpath,imagefile_name,config)


if chart_template==10: # Bar chart
    imagefile_name = "Bars"

    params = dict(x=COLUMN_X, y=COLUMN_Y)

    if validate_att(LABEL_COLUMN): # si hay colores
        params['color']=LABEL_COLUMN

    fig = px.bar(df, **params)

    export_figures(fig,outputpath,imagefile_name,config)

if chart_template==11: # Boxplot
    imagefile_name = "Box"

    params = dict(x=COLUMN_X, y=COLUMN_Y,points=False)

    if validate_att(LABEL_COLUMN): # si hay colores
        params['color']=LABEL_COLUMN

    if validate_att(TEMPORAL_COLUMN): # si hay colores
        params['animation_frame']=TEMPORAL_COLUMN

        df= df.sort_values(by=[COLUMN_X,TEMPORAL_COLUMN])
    else:
        df= df.sort_values(by=COLUMN_X)

    fig = px.box(df, **params)
    #fig.show()
    export_figures(fig,outputpath,imagefile_name,config)

if chart_template==12: # coumulative barplot
    #print(df["RANGO_EDAD"].unique())
    #df["RANGO_EDAD"].replace("05-14", "05_14",inplace=True)
    #df["RANGO_EDAD"].replace("00-04", "00_04",inplace=True)
    #df["RANGO_EDAD"].replace("15-24", "15_24",inplace=True)
    #df["RANGO_EDAD"].replace("25-44", "25_44",inplace=True)
    #df["RANGO_EDAD"].replace("45-64", "45_64",inplace=True)
    #print(df)
    #df.to_csv("conteo_graficas_correcto.csv",index=False)
    #exit()

    imagefile_name = "Histogram_c"
    bins = len(df[COLUMN_X].unique())

    params = dict(x=COLUMN_X, y=COLUMN_Y,barmode='relative', histfunc='sum',marginal="box",nbins=bins)

    df= df.sort_values(by=COLUMN_X)

    if validate_att(LABEL_COLUMN): # si hay colores
        params['color']=LABEL_COLUMN

    fig = px.histogram(df, **params)

    #fig.show()
    export_figures(fig,outputpath,imagefile_name,config)

exit(0)
