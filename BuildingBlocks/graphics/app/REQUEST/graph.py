import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import math
import sys
from sklearn.decomposition import PCA
import numpy as np
import janitor #!pip install pyjanitor==0.23.1

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
    imagefile_name = "chart"
    fig.update_layout(title=TITLE,
                    dragmode='select',
                    width=1200,
                    height=800,
                    hovermode='closest',
                    #transition  = dict(duration=2000,easing="elastic"),
                    font=dict(
                        family="Courier New, monospace",
                        size=18,
                    ),
                    margin=dict(
                        l=20,
                        r=20,
                        b=50,
                        t=50,
                    ),
                    paper_bgcolor='rgb(243, 243, 243)',
                    plot_bgcolor='rgb(243, 243, 243)',
                    )
    fig.update_xaxes(tickangle=45)

    fig['layout']['updatemenus'][0]['pad']=dict(r= 10, t= 100)
    fig['layout']['sliders'][0]['pad']=dict(r= 10, t= 100)

    #fig.write_image("%s/%s.png" % (outputpath,imagefile_name))
    #fig.write_image("%s/%s.svg" % (outputpath,imagefile_name))
    fig.write_html("%s/%s.html" % (outputpath,imagefile_name),config=config,auto_open=False)

## parameters by argument
print(sys.argv)

"""
python3 graph.py cancer_mama.csv ./output/ '11' '' '' 'label' 'colorscale' 'color_col' 'RANGO_EDAD' 'TASA_AJUSTADA' 'ANIO_REGIS' 'subgroup' 'size' 'log_scale' '' 'title' 'z' 


"""


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
GROUPS_PATH = sys.argv[14].split(",") #  "cve_ent_mun,sexo".split(",")

#for any chart
TITLE = sys.argv[15] # "PLOT"

COLUMN_Z = sys.argv[16] # "suicSinDerhab"
ORIENT = validate_att(sys.argv[17]) # h o v
if not ORIENT:
    ORIENT="v"
else:
    ORIENT = sys.argv[17]
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

    #fig = make_subplots(rows=rows, cols=col)
    #imagefile_name = "accumulative_plot"
    #data_matrix = []
    #col_i = 1
    #row_i = 1
    #for c in COLUMNS:
    #    fig.add_trace(go.Histogram(x=df[c].to_list(),
    #        histnorm=TYPE_HISTOGRAM,
    #        cumulative_enabled=True,
    #        name=c # name used in legend and hover labels
    #        ),row=row_i, col=col_i)
    #    col_i+=1
    #    if col_i > col:
    #        col_i=1
    #        row_i+=1 
    #export_figures(fig,outputpath,imagefile_name,config)

if chart_template==2: # scatter matrix
    imagefile_name = "scatter_matrix"
    if validate_att(LABEL_COLUMN): # if there is a label for color
        fig = px.scatter_matrix(df,dimensions=COLUMNS,color=LABEL_COLUMN)
    else:
        fig = px.scatter_matrix(df,dimensions=COLUMNS)
    
    export_figures(fig,outputpath,imagefile_name,config)

if chart_template==3: #parallel_categories
    """
    python3 graph.py FtesContSLP_2.csv output/ '3' 'density' 'categoria 1,categoria 2,categoria 3,conglomerado' '' 'porcentaje' '' '' '' '' '' '0' '' 'Porcentaje por categoria' ''
    """

    imagefile_name = "parallel_categories"
    temp_col = COLUMNS
    fig = px.parallel_categories(df, dimensions=temp_col, color=COLORSCALE_COLUMN, color_continuous_scale=px.colors.sequential.Inferno)
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

if chart_template==6: #SUNBRUST
    """
    e.g. python3 graph.py FtesContSLP_2.csv output/ '6' 'density' '0' 'porcentaje' '' '' '' '' '' 'casos totales' '0' 'conglomerado,categoria 1,categoria 2,categoria 3,categoria 4,categoria 5' 'Casos SLP' ''
    """
    imagefile_name = "SUNBRUST"
    params = dict(path=GROUPS_PATH, values=SIZE)
    ## aqui se aplica un équeño preprocesdamiento para quitar datos en blanco
    df.dropna(subset=GROUPS_PATH+[SIZE], how='any', inplace=True)
    #df[GROUPS_PATH] = df[GROUPS_PATH].fillna('NE/NA')
    df[SIZE] = df[SIZE].fillna(0)

    if validate_att(LABEL_COLUMN): # si hay colores
        params['color']=LABEL_COLUMN

    #if validate_att(TEMPORAL_COLUMN): # si hay una columna de temporal, se crean multiples graficas para cada valor de temporal
    #    df_grouped = df.groupby(TEMPORAL_COLUMN)
    #    for namedf,group_df in df_grouped:
    #        imagefile_name = "SUNBRUST_%s" %namedf
    #        print(imagefile_name)
    #        fig = px.sunburst(group_df, **params)
    #        export_figures(fig,outputpath,imagefile_name,config)
    #else:
    fig = px.sunburst(df, **params)
    export_figures(fig,outputpath,imagefile_name,config)

if chart_template==7: #simple_scatter
    imagefile_name = "simple_scatter"
    params = dict(x=COLUMN_X, y=COLUMN_Y, marginal_y="violin", marginal_x="violin", trendline="ols", log_x=LOG_SCALE,log_y=LOG_SCALE)

    if validate_att(LABEL_COLUMN): # si hay colores
        params['color']=LABEL_COLUMN

    fig = px.scatter(df, **params)

    export_figures(fig,outputpath,imagefile_name,config)

if chart_template==8: # 3D scatter
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
    """
    python3 graph.py Cancer_mexico_mun_with_rates_00_14.csv ./output '10' 'density' '0' 'SEXO' '' 'NAME_CAUSA' 'TASA_AJUSTADA' 'ANIO_REGIS' '' '' '0' '' '' ''
    """

    imagefile_name = "Bar_chart"

    if ORIENT =="h":
        params = dict(x=COLUMN_Y, y=COLUMN_X,barmode='group')
        range_axis="x"
    else:
        params = dict(x=COLUMN_X, y=COLUMN_Y,barmode='group')
        range_axis="y"

    if validate_att(LABEL_COLUMN): # si hay colores
        params['color']=LABEL_COLUMN

    if validate_att(TEMPORAL_COLUMN): # si hay colores
        params['animation_frame']=TEMPORAL_COLUMN
        params['animation_group']=COLUMN_X
        #df= df.sort_values(by=[TEMPORAL_COLUMN,COLUMN_X])

        if validate_att(LABEL_COLUMN): # si hay colores
            df = df.complete(COLUMN_X, TEMPORAL_COLUMN,LABEL_COLUMN).fillna(0, downcast='infer')
        else:
            df = df.complete(COLUMN_X, TEMPORAL_COLUMN).fillna(0, downcast='infer')

        df= df.sort_values(by=[TEMPORAL_COLUMN,COLUMN_X])
        maxy= df[COLUMN_Y].max()
        maxy= maxy+(maxy/4)

        miny= df[COLUMN_Y].min()
        miny= miny+(miny/4)
        params['range_'+range_axis] =[miny,maxy]

    fig = px.bar(df, **params)

    export_figures(fig,outputpath,imagefile_name,config)

if chart_template==11: # Boxplot
    """
    python3 graph.py cancer_mama.csv ./output/ '11' '' '' 'SEXO' '' 'RANGO_EDAD' 'TASA_AJUSTADA' 'ANIO_REGIS' '' '' '' '' 'title' '' ''
    """
    imagefile_name = "Box"
 
    if ORIENT =="h":
        params = dict(x=COLUMN_Y, y=COLUMN_X,points=False,notched=True)
        range_axis="x"
    else:
        params = dict(x=COLUMN_X,  y=COLUMN_Y,points=False,notched=True)
        range_axis="y"

    if validate_att(LABEL_COLUMN): # si hay colores
        params['color']=LABEL_COLUMN

    #if validate_att(TEMPORAL_COLUMN): # si hay colores
    #    params['animation_frame']=TEMPORAL_COLUMN
    #    params['animation_group']=COLUMN_X
    #    df= df.sort_values(by=[TEMPORAL_COLUMN])

    if validate_att(TEMPORAL_COLUMN): # si hay colores
        params['animation_frame']=TEMPORAL_COLUMN
        params['animation_group']=COLUMN_X
        #df= df.sort_values(by=[TEMPORAL_COLUMN,COLUMN_X])

        if validate_att(LABEL_COLUMN): # si hay colores
            df = df.complete(COLUMN_X, TEMPORAL_COLUMN,LABEL_COLUMN).fillna(0, downcast='infer')
        else:
            df = df.complete(COLUMN_X, TEMPORAL_COLUMN).fillna(0, downcast='infer')

        df= df.sort_values(by=[TEMPORAL_COLUMN,COLUMN_X])
        maxy= df[COLUMN_Y].max()
        maxy= maxy+(maxy/4)

        miny= df[COLUMN_Y].min()
        miny= miny+(miny/4)
        params['range_'+range_axis] =[miny,maxy]

    #category_orders = np.sort(df[COLUMN_X].unique())
    #params['category_orders']={COLUMN_X:category_orders}

    fig = px.box(df, **params)
    #fig.show()
    export_figures(fig,outputpath,imagefile_name,config)

if chart_template==12: # coumulative barplot
    imagefile_name = "coumulative"
    bins = len(df[COLUMN_X].unique())

    params = dict(x=COLUMN_X, y=COLUMN_Y,barmode='relative', histfunc='sum',marginal="box",nbins=bins)

    df= df.sort_values(by=COLUMN_X)

    if validate_att(LABEL_COLUMN): # si hay colores
        params['color']=LABEL_COLUMN

    fig = px.histogram(df, **params)

    #fig.show()
    export_figures(fig,outputpath,imagefile_name,config)

if chart_template==13: # TreeMap
    """
    python3 graph.py FtesContSLP_2.csv ./output/ '13' 'density' '0' '' 'porcentaje' '' '' '' '' 'casos totales' '0' 'conglomerado,categoria 1,categoria 2,categoria 3,categoria 4,categoria 5' 'Grafica de categorias - Fuentes contaminantes SLP' ''

    """
    imagefile_name = "Treemap"

    params = dict(path=[px.Constant(SIZE)]+GROUPS_PATH, values=SIZE)

    if validate_att(COLORSCALE_COLUMN): # si hay colores
        params['color']=COLORSCALE_COLUMN
        
        # this scale is for positive and negative values
        #params['color_continuous_scale']="RdBu"
        #params['color_continuous_midpoint']=np.average(df[COLORSCALE_COLUMN], weights=df[SIZE])

    #[px.Constant("world"), 'continent', 'country']
    fig = px.treemap(df, **params)
    fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))

    export_figures(fig,outputpath,imagefile_name,config)



exit(0)
