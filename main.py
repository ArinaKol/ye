import networkx as nx
import pandas as pd
import csv
from math import sqrt

from bokeh.plotting import figure, from_networkx
from bokeh.models import (BoxSelectTool, Circle, EdgesAndLinkedNodes, HoverTool,
                          MultiLine, NodesAndLinkedEdges, Plot, Range1d, TapTool)
from bokeh.models import (BoxZoomTool, Circle, HoverTool,
                          MultiLine, Plot, WheelZoomTool, ResetTool)
from bokeh.palettes import Spectral4
from bokeh.layouts import column, layout
from bokeh.io import show, curdoc
from bokeh.models import Dropdown, Select, ColumnDataSource
from bokeh.models.callbacks import CustomJS


def read_relation_triples(file_path):
    print("read relation triples:", file_path)
    if file_path is None:
        return set(), set(), set()
    triples = set()
    entities, relations = set(), set()
    file = open(file_path, 'r', encoding='utf8')
    for line in file.readlines():
        params = line.strip('\n').split('\t')
        assert len(params) == 3
        h = params[0].strip()
        r = params[1].strip()
        t = params[2].strip()
        triples.add((h, r, t))
        entities.add(h)
        entities.add(t)
        relations.add(r)
    return triples, entities, relations

def find_ent(gr, num):
    for n in gr.nodes():
        wt = gr.nodes[n]['id']
        if wt == num:
            return 1, n
    return 0, 0

def set_xy_ent(gr):
    print("set")
    for n in gr.nodes():
        ax=gr.nodes[n]['x']
        ay=gr.nodes[n]['y']
        ax1=0
        ay1=0
        id_ent=gr.nodes[n]['id2']
        k, id_ent=find_ent(gr,id_ent)
        if k == 1:
            ax1=gr.nodes[id_ent]['x']
            ay1=gr.nodes[id_ent]['y']
        #xx.append(ax1)
        #yy.append(ay1)
        #dist.append(sqrt((ax1-ax)*(ax1-ax)+(ay1-ay)*(ay1-ay)))
        G.nodes[id_ent]['x_ent'] = ax
        G.nodes[id_ent]['y_ent'] = ay
        G.nodes[id_ent]['distance']=sqrt((ax1-ax)*(ax1-ax)+(ay1-ay)*(ay1-ay))
    #nx.set_node_attributes(gr, xx, "x_ent")
    #nx.set_node_attributes(gr, yy, "y_ent")
    #nx.set_node_attributes(gr, dist, "distance")

    return gr

def delete_host(uri):
    uri = uri.strip('\n').split('/')
    return uri[-1]

def find_rel(gr, v_1, v_2):
    i = 0
    j = 0
    ij = -1
    for n in gr.nodes():
        wt = gr.nodes[n]['title']
        ij = ij + 1
        if wt == v_1:
            v11 = gr.nodes[n]['id']
            i = 1
        if wt == v_2:
            v22 = gr.nodes[n]['id']
            j = 1
        if j == 1 and i == 1:
            return 1, v11, v22
    return 0, 0, 0


###
G = nx.Graph()
with open('seu_EN_RU_15K_V1_ent.csv', encoding="utf8", newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
       #G.add_node(int(row['ent1_id']), id=int(row['ent1_id']), id2=int(row['ent2_id']), pos=(float(row['x']), float(row['y'])), color = 'darkblue' if row['lang'] == 'en' else 'crimson', lang=row['lang'], title=row['ent1'] if row['lang'] == 'en' else row['ent2'], type=row['type'], x=(float(row['x'])), y=float(row['y']))
       G.add_node(int(row['ent1_id']), id=int(row['ent1_id']), id2=int(row['ent2_id']),
                  pos=(float(row['x']), float(row['y'])), color='white',
                  lang=row['lang'], title=row['ent1'], type=row['type'],
                  x=(float(row['x'])), y=float(row['y']))
pos=nx.get_node_attributes(G, 'pos')

filename = 'seu_EN_RU_15K_V1_ent.csv'
filepath = filename
df_main = pd.read_csv(filepath)
# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], ent1_id=[], ent2_id=[], ent1=[], ent2=[], lang=[], type_=[], color=[], size=[], distance=[]))



#G = set_xy_ent(G)

with open('seu_EN_RU_15K_V1_rel.csv', encoding="utf8", newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
       #G.add_node(int(row['ent1_id']), id=int(row['ent1_id']), id2=int(row['ent2_id']), pos=(float(row['x']), float(row['y'])), color = 'darkblue' if row['lang'] == 'en' else 'crimson', lang=row['lang'], title=row['ent1'] if row['lang'] == 'en' else row['ent2'], type=row['type'], x=(float(row['x'])), y=float(row['y']))
       G.add_edge(int(row['id1']), int(row['id2']), rel=row['relation'])




# create graph renderer from networkx graph
graph_renderer = from_networkx(G, pos)

plot = figure(height=720, width=1280,x_range=(-100, 100), y_range=(-100, 100),
              tools="lasso_select,pan,wheel_zoom,tap,save,reset", active_scroll='wheel_zoom')
plot.add_tools(TapTool(), BoxSelectTool())
# hover tools for edges and nodes

hover_nodes = HoverTool(
    tooltips=[('title','@title'),('id','@id'),('type','@type'),('lang','@lang'),('x,y','@pos'),('id','@id2'),('x,y','@x_ent,@y_ent'),('distance','@distance')],renderers=[graph_renderer.node_renderer]
)

hover_edges = HoverTool(
    tooltips=[('relation', '@rel')], renderers=[graph_renderer.edge_renderer]
)
#graph_renderer.node_renderer.selection_glyph = Circle(size=5, fill_color='white')
graph_renderer.node_renderer.glyph = Circle(size=5, fill_color='white', line_alpha=0)
#graph_renderer.node_renderer.glyph = Circle(size=5, line_alpha=0.2)
graph_renderer.edge_renderer.glyph = MultiLine(line_color="white", line_alpha=0.8, line_width=2)
graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=2)
#graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=2)

graph_renderer.selection_policy = NodesAndLinkedEdges()
graph_renderer.inspection_policy = NodesAndLinkedEdges()

plot.add_tools(hover_edges)

plot.renderers.append(graph_renderer)

############################################
types = list(df_main['type'].unique())
types=list(set(types))
types = sorted(types)
types.insert(0, 'All')
select_type = Select(name='select_type', title='Тип', options=types, value=types[0])

ids = list(df_main['ent1_id'])
ids = list(map(str, ids))
ids.insert(0, '-1')
select_id = Select(name='select_id', title='Номер', options=ids, value=ids[0], visible=False)
# Form screens
#select_tools = ['pan', 'wheel_zoom', 'tap', 'reset', 'save']
#tooltips = [('Entity', '@ent1' + ' (@lang)'), ('Type', '@type_')]
#p1 = figure(plot_height=720, plot_width=1280, tools=select_tools, title='Векторное пространство')
#p1.toolbar.active_scroll = p1.select_one(WheelZoomTool)
#p1.add_tools(HoverTool(tooltips=tooltips))

callback = CustomJS(args=dict(source=source), code="""
    const selector = document.getElementsByName('select_id')[0];
    const indices = source.selected.indices;
    if (indices.length !== 0) {
        selector.value = indices[0];
    } else {
        selector.value = -1;
    }
    var event = new Event('change');
    const cancelled = !selector.dispatchEvent(event);
""")
plot.js_on_event('tap', callback)

s=plot.circle(x='x',
          y='y',
          source=source,
          color='color',
          size='size',
          nonselection_alpha=0.5)
hover_nodes = HoverTool(
    tooltips=[('title','@ent1'),('id','@ent1_id'),('type','@type_'),('lang','@lang')],renderers=[s]
)
plot.add_tools(hover_nodes)

def set_colors(df):
    languages = list(df['lang'])
    colors = list(map(lambda x: 'darkblue' if x == 'en' else 'crimson', languages))
    df['color'] = colors
    return df

def set_params(df):
    df = set_colors(df)
    df['size'] = 5
    df['distance'] = 0
    return df

def get_color(index):
    color = 'darkblue'
    if index % 2 != 0:
        color = 'crimson'
    return color

def emphasize_pair(df, df_ids, id1):
    row = df.loc[df['ent1_id'] == id1]
    id2 = row['ent2_id'].values[0]
    pair = [id1, id2]
    colors = list(map(lambda x: get_color(x) if x in pair else 'lightgray', df_ids))
    df['color'] = colors
    sizes = list(map(lambda x: 20 if x in pair else 5, df_ids))
    df['size'] = sizes
    return df

def get_data():
    current_type = select_type.value
    df = df_main.copy()
    df = set_params(df)
    if current_type != 'All':
        df = df.loc[df['type'] == current_type]
    current_id = int(select_id.value)
    df_ids = list(df['ent1_id'])
    if current_id != -1:
        if current_id < len(df_ids):
            if len(df) < len(df_main):
                current_id = df_ids[current_id]
            df = emphasize_pair(df, df_ids, current_id)
        else:
            source.selected.indices = []
    return df

def update():
    df = get_data()
    source.data = dict(
        x=df['x'], y=df['y'],
        ent1_id=df['ent1_id'], ent2_id=df['ent2_id'],
        ent1=df['ent1'], ent2=df['ent2'],
        lang=df['lang'], type_=df['type'],
        color=df['color'], size=df['size'],
        distance=df['distance']
    )

# declare controls
controls = [select_type, select_id]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

inputs = column(*controls)
series = column(plot)
fields = column(layout([[inputs, series]]), sizing_mode="scale_both")
update()  # initial load of the data
curdoc().add_root(fields)

#output_file(filename="templates/home.html", title="graph")
#save(fields)
