import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import math
import sys
import numpy as np
import janitor #!pip install pyjanitor==0.23.1
from pandas.api.types import is_numeric_dtype
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor




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

def export_figures(fig,outputpath,imagefile_name,config,format_ticks =True):
    imagefile_name = "chart"
    fig.update_layout(title=TITLE,
                    dragmode='select',
                    width=900,
                    height=700,
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
    if format_ticks:
        fig.update_xaxes(tickangle=45)

    try:

        fig['layout']['updatemenus'][0]['pad']=dict(r= 10, t= 100)
        fig['layout']['sliders'][0]['pad']=dict(r= 10, t= 100)
    except Exception as e:
        print("no temporal")
    #fig.write_image("%s/%s.png" % (outputpath,imagefile_name))
    #fig.write_image("%s/%s.svg" % (outputpath,imagefile_name))
    fig.write_html("%s/%s.html" % (outputpath,imagefile_name),config=config,auto_open=False)

## parameters by argument
print(sys.argv)

"""

python3 graph.py inputpath outputpath '11' 'TYPE_HISTOGRAM' 'COLUMNS' 'LABEL_COLUMN' 'COLORSCALE_COLUMN' 'COLUMN_X' 'COLUMN_Y' 'TEMPORAL_COLUMN' 'SUBGROUP' 'SIZE' 'LOG_SCALE' 'GROUPS_PATH' 'title' 'COLUMN_Z' 'ORIENT' 


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
REFERENCE_VALUE = validate_att(sys.argv[18]) # 

if not ORIENT:
    ORIENT="v"
else:
    ORIENT = sys.argv[17]

if not REFERENCE_VALUE:
    REFERENCE_VALUE=[]
else:
    REFERENCE_VALUE = sys.argv[18].split(",")
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

    df = df[GROUPS_PATH+[SIZE]].reset_index()
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
    
    python3 graph.py Contaminantes_Final.csv ./output '6' 'density' '0' 'contamiantes_value' '' '' '' '' '' 'contamiantes_value' '0' 'Entidad,Alcaldia,Clave,year' 'índice de contaminación' '' 'h'
    
    python3 graph.py Contaminantes_Final.csv ./output '10' 'density' '0' 'contamiantes' '' 'contamiantes_value' 'Clave' 'year' '' '' '0' '' 'indice de contaminacion' '' 'h'
    """
    print(COLUMN_Y)
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
            if is_numeric_dtype(df[LABEL_COLUMN]):
                df = df.complete(COLUMN_X, TEMPORAL_COLUMN).fillna(0, downcast='infer')
            else:
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

if chart_template==14: # Sorted histogram
    """
    python3 graph.py cancer_infantil_00_14.csv ./output '14' 'density' 'SEXO,ENT_OCURR,MUN_OCURR,NAME_CAUSA' '0' '' '0' 'TASA_AJUSTADA' 'ANIO_REGIS' '' '' '0' '' '' '' 'h'
    
    python3 graph.py cancer_infantil_00_14.csv ./output '14' 'density' 'CAUSA_DEF' '' '' '' 'TASA_AJUSTADA' 'ANIO_REGIS' '' '' '0' '' 'Mortalidad por cancer infantil' ''
    
    """
    LIMIT = 10
    def sort_and_filter(df):
        df= df.sort_values(by=[COLUMN_Y],ascending=False)
        df = df.head(LIMIT)
        return df
    
    


    imagefile_name = "Bar_chart"
    print(ORIENT)
    if ORIENT =="h":
        params = dict(x=COLUMN_Y, y="GROUP")
        range_axis="x"
    else:
        params = dict(x="GROUP", y=COLUMN_Y)
        range_axis="y"

    if validate_att(TEMPORAL_COLUMN): # si hay colores
        params['animation_frame']=TEMPORAL_COLUMN

        #df = df.complete(*COLUMNS, TEMPORAL_COLUMN).fillna(0, downcast='infer')

        df = df.groupby(TEMPORAL_COLUMN).apply(sort_and_filter)
    else:
        #df = df.complete(*COLUMNS).fillna(0, downcast='infer')
        df = sort_and_filter(df)

    colors_n = len(df)
    c = ['hsl('+str(h)+',50%'+',50%)' for h in np.linspace(0, 360, colors_n)]



    maxy= df[COLUMN_Y].max()
    maxy= maxy+(maxy/4)
    miny= df[COLUMN_Y].min()
    miny= 0
    params['range_'+range_axis] =[miny ,maxy]
    df['GROUP'] = df[COLUMNS].apply(lambda row: '_'.join(row.values.astype(str)), axis=1)
    df['NAME_GROUP'] = df['GROUP'].str[:7]+"..."+ df['GROUP'].str[-5:]
    params['color']=COLUMN_Y
    params['hover_data']=COLUMNS
    params['hover_name']="GROUP"
    #if validate_att(TEMPORAL_COLUMN): # si hay colores
    #    params['animation_group']="GROUP"
     
    params['color_continuous_scale']="tealrose"

    fig = px.bar(df, **params)

    if range_axis=="y":
        fig.update_layout(showlegend=False)
        fig.update(layout_coloraxis_showscale=False)
        if validate_att(TEMPORAL_COLUMN):
            fig.update_xaxes(
                tickmode="array",
                title=None,
                tickvals = df['GROUP'],
                ticktext=df['NAME_GROUP'],
            )
        else:
            fig.update_xaxes(
                tickmode="array",
                title=None,
                tickvals = df['GROUP'],
                ticktext=df['GROUP'],
                tickwidth=8,
                tickfont_family="Arial Black",
                tickfont=dict(size=15)
            )
    else:
        fig.update_layout(showlegend=False)
        fig.update(layout_coloraxis_showscale=False)
        if validate_att(TEMPORAL_COLUMN):
            fig.update_yaxes(
                tickmode="array",
                title=None,
                tickvals = df['GROUP'],
                ticktext=df['NAME_GROUP']
            )
        else:
            fig.update_yaxes(
                tickmode="array",
                title=None,
                tickvals = df['GROUP'],
                ticktext=df['GROUP'],
                ticklabelposition= "inside",
                tickwidth=8,
                tickfont_family="Arial Black",
                tickfont=dict(size=15)
            )

    export_figures(fig,outputpath,imagefile_name,config,format_ticks=False)


if chart_template==15: # Custom Heatmap
    """
    python3 graph.py inputpath outputpath '15' '' '' '' '' 'COLUMN_X' 'COLUMN_Y' 'TEMPORAL_COLUMN' '' '' '' '' 'title' 'COLUMN_Z' '' 
    python3 graph.py conteos_cancer_98_20.csv ./output '15' '' '' '' '' 'nombre entidad' 'CAUSA_DEF' 'ANIO_REGIS' '' '' '' '' 'title' 'cve' '' 

    """
    
    imagefile_name = "heatmap"

    df = df.complete(TEMPORAL_COLUMN,COLUMN_X,COLUMN_Y).fillna(0, downcast='infer')
    df = df.sort_values(by=([TEMPORAL_COLUMN,COLUMN_X,COLUMN_Y]))
    # Graph
    minValue = df[COLUMN_Z].min()
    maxValue = df[COLUMN_Z].max()
    fig = px.density_heatmap(df, 
                            x=COLUMN_X, 
                            y=COLUMN_Y, 
                            z=COLUMN_Z, 
                            animation_frame=TEMPORAL_COLUMN, 
                            histfunc="max",
                            range_color=(minValue, maxValue))
    export_figures(fig, outputpath,imagefile_name,config)

if chart_template==16: # regresion
    """
    python3 graph.py test_solo_CO.csv ./output '16' '' '' '' '' 'year' 'contamiantes_value' '' '' '' '' '' 'title' '' '' mexico=5

    """

    imagefile_name = "Regression"
    df = df.sort_values(COLUMN_X)
    X = df[[COLUMN_X]]
    X_train = X
    y_train = df[COLUMN_Y]

    model = LinearRegression()
    model.fit(X_train, y_train)

    x_range = X[COLUMN_X].tolist()
    y_range = model.predict(X)

    #valores x a predecir
    x_value = df[COLUMN_X].unique()
    #se añaden valores de tendencia
    #porcentaje = 0.2  # Porcentaje de elementos a añadir
    #cantidad_a_anadir = int(len(x_value) * porcentaje)  # Cantidad de elementos a añadir
    #ultimo_valor = x_value[-1]  # Último valor de la lista original
    #patron = x_value[1] - x_value[0]  # Patrón entre los primeros dos valores
    #valores_a_anadir = [ultimo_valor + (i + 1) * patron for i in range(cantidad_a_anadir)]  # Generar los nuevos valores
    #x_value = np.concatenate((x_value,valores_a_anadir))  # Concatenar la lista original con los nuevos valores

    #polinomial
    poly_features = PolynomialFeatures(degree=2)
    x_poly = poly_features.fit_transform(df[COLUMN_X].values.reshape(-1, 1))
    model_poly = LinearRegression()
    model_poly.fit(x_poly, y_train)
    x_poly_test = poly_features.fit_transform(x_value.reshape(-1, 1))
    y_poly= model_poly.predict(x_poly_test)

    #dessicion tree
    model_dt = DecisionTreeRegressor()
    model_dt.fit(df[COLUMN_X].values.reshape(-1, 1), y_train)
    y_dt = model_dt.predict(x_value.reshape(-1, 1))

    # KNN 
    k = 3  # Número de vecinos a considerar
    model_knn = KNeighborsRegressor(n_neighbors=k)
    model_knn.fit(df[COLUMN_X].values.reshape(-1, 1), y_train)
    y_knn = model_knn.predict(x_value.reshape(-1, 1))

    

    fig = go.Figure([
        go.Scatter(x=X_train.squeeze(), y=y_train, name='records', mode='markers', marker=dict(opacity=0.4)),
        go.Scatter(x=x_range, y=y_range, name='Linear Reg.'),
        go.Scatter(x=x_value, y=y_poly, mode='lines', name='Polinomial Reg.',visible="legendonly"),
        go.Scatter(x=x_value, y=y_dt, mode='lines', name='Decision tree Reg.',visible="legendonly"),
        go.Scatter(x=x_value, y=y_knn, mode='lines', name='KNN Reg. (K=3)',visible="legendonly")

    ])

    for ref in REFERENCE_VALUE:
        name,value = ref.split("=")

        fig.add_traces(go.Scatter(x=x_value, y=[value]*len(x_value), mode='lines', line=dict(dash='dash'), name=name))

    fig.update_layout(
        yaxis=dict(
            title=COLUMN_Y,  # Nombre del eje y
            titlefont=dict(size=16)  # Tamaño de la fuente del nombre del eje y
        ),
        xaxis=dict(
            title=COLUMN_X,  # Nombre del eje y
            titlefont=dict(size=16)  # Tamaño de la fuente del nombre del eje y
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(0, 0, 0, 0)'
        )
    )

    export_figures(fig, outputpath,imagefile_name,config)

if chart_template==17: # multiple Lin regresion
    """
    python3 graph.py test_solo_CO.csv ./output '17' '' '' '' '' 'year' 'contamiantes_value' '' '' '' '' '' 'title' '' '' mexico=5

    """

    imagefile_name = "Regression"

    list_layers = []
    df_grouped = df.groupby(SUBGROUP)
    for namedf,group_df in df_grouped:
        df_temp = group_df.sort_values(COLUMN_X)
        X = df_temp[[COLUMN_X]]
        X_train = X
        y_train = df_temp[COLUMN_Y]

        reg_name = "reg. %s" %namedf
        data_name = "%s" %namedf

        model = LinearRegression()
        model.fit(X_train, y_train)

        x_range = X[COLUMN_X].tolist()
        y_range = model.predict(X)

        #valores x a predecir
        x_value = df[COLUMN_X].unique()
        list_layers.append(go.Scatter(x=X_train.squeeze(), y=y_train, name=data_name, mode='markers', marker=dict(opacity=0.4))) #data
        list_layers.append(go.Scatter(x=x_range, y=y_range, name=reg_name)) #data

           
        fig = go.Figure(list_layers)

    for ref in REFERENCE_VALUE:
        name,value = ref.split("=")
        fig.add_traces(go.Scatter(x=x_value, y=[value]*len(x_value), mode='lines', line=dict(dash='dash'), name=name))

    fig.update_layout(
        yaxis=dict(
            title=COLUMN_Y,  # Nombre del eje y
            titlefont=dict(size=16)  # Tamaño de la fuente del nombre del eje y
        ),
        xaxis=dict(
            title=COLUMN_X,  # Nombre del eje y
            titlefont=dict(size=16)  # Tamaño de la fuente del nombre del eje y
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(0, 0, 0, 0)'
        )
    )

    export_figures(fig, outputpath,imagefile_name,config)

exit(0)
