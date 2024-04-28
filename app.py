import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
import textwrap
from jupyter_dash import JupyterDash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output


## Data cleaning and setup...
gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 

gss_clean = gss[mycols]

gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)

gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

sex_replace_map = {
    'male':'Male',
    'female':'Female'
}

sat_replace_map = {
    'very dissatisfied':'Very dissatisfied',
    'a little dissat':'A little dissatisfied',
    'mod. satisfied':'Moderately satisfied',
    'very satisfied':'Very satisfied'
}

agree1_replace_map = {
    'strongly disagree':'Strongly disagree',
    'disagree':'Disagree',
    'agree':'Agree',
    'strongly agree':'Strongly agree'
}

agree2_replace_map = {
    'disagree':'Disagree',
    'agree':'Agree'
}

agree3_replace_map = {
    'strongly disagree':'Strongly disagree',
    'disagree':'Disagree',
    'neither agree nor disagree':'Neither agree nor disagree',
    'agree':'Agree',
    'strongly agree':'Strongly agree'
}

gss_clean.sex = gss_clean.sex.map(sex_replace_map)
gss_clean.satjob = gss_clean.satjob.map(sat_replace_map)
gss_clean.relationship = gss_clean.relationship.map(agree1_replace_map)
gss_clean.male_breadwinner = gss_clean.male_breadwinner.map(agree1_replace_map)
gss_clean.men_bettersuited = gss_clean.men_bettersuited.map(agree2_replace_map)
gss_clean.child_suffer = gss_clean.child_suffer.map(agree1_replace_map)
gss_clean.men_overwork = gss_clean.men_overwork.map(agree3_replace_map)

gss_clean['sex'] = gss_clean['sex'].astype('category').cat.reorder_categories([
    'Male',
    'Female'
])

gss_clean['satjob'] = gss_clean['satjob'].astype('category').cat.reorder_categories([
    'Very dissatisfied',
    'A little dissatisfied',
    'Moderately satisfied',
    'Very satisfied'
])

gss_clean['relationship'] = gss_clean['relationship'].astype('category').cat.reorder_categories([
    'Strongly disagree',
    'Disagree',
    'Agree',
    'Strongly agree'
])

gss_clean['male_breadwinner'] = gss_clean['male_breadwinner'].astype('category').cat.reorder_categories([
    'Strongly disagree',
    'Disagree',
    'Agree',
    'Strongly agree'
])

gss_clean['men_bettersuited'] = gss_clean['men_bettersuited'].astype('category').cat.reorder_categories([
    'Disagree',
    'Agree'
])

gss_clean['child_suffer'] = gss_clean['child_suffer'].astype('category').cat.reorder_categories([
    'Strongly disagree',
    'Disagree',
    'Agree',
    'Strongly agree'
])

gss_clean['men_overwork'] = gss_clean['men_overwork'].astype('category').cat.reorder_categories([
    'Strongly disagree',
    'Disagree',
    'Neither agree nor disagree',
    'Agree',
    'Strongly agree'
])

gss_clean['region'] = gss_clean['region'].astype('category').cat.reorder_categories([
    'south atlantic',
    'e. nor. central',
    'pacific',
    'w. sou. central',
    'middle atlantic',
    'mountain',
    'e. sou. central',
    'w. nor. central',
    'new england'
])

gss_clean['edu_cat'] = gss_clean['education'].astype('category')

gss_interactive = gss_clean.copy()

my_groups = [
    ['sex', 'satjob'],
    ['sex', 'relationship'],
    ['sex', 'male_breadwinner'],
    ['sex', 'men_bettersuited'],
    ['sex', 'child_suffer'],
    ['sex', 'men_overwork'],
    ['region', 'satjob'],
    ['region', 'relationship'],
    ['region', 'male_breadwinner'],
    ['region', 'men_bettersuited'],
    ['region', 'child_suffer'],
    ['region', 'men_overwork'],
    ['edu_cat', 'satjob'],
    ['edu_cat', 'relationship'],
    ['edu_cat', 'male_breadwinner'],
    ['edu_cat', 'men_bettersuited'],
    ['edu_cat', 'child_suffer'],
    ['edu_cat', 'men_overwork']
]

gss_interactive = gss_interactive.dropna()

interactive_results = [
    pd.pivot(
        pd.DataFrame(gss_interactive.groupby(group, as_index = False).size()).unstack().reset_index().rename({0:'level_3'}, axis = 'columns'), 
            values = 'level_3', 
            index = 'level_1', 
            columns = 'level_0'
            ).reset_index(drop = True)
    for group in my_groups
]

interactive_cols = [list(pd.DataFrame(result).columns) for result in interactive_results]

## Formatting specs and reference...
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

my_colors = {
    'Female':'#fde725',
    'Male':'#21918c',
    'south atlantic':'#fde725', 
    'e. nor. central':'#c2df23',
    'pacific':'#86d549',
    'w. sou. central':'#52c569',
    'middle atlantic':'#2ab07f',
    'mountain':'#1e9b8a',
    'e. sou. central':'#25858e',
    'w. nor. central':'#2d708e',
    'new england':'#38588c',
    20.0:'#fde725',
    19.0:'#e5e419',
    18.0:'#c8e020',
    17.0:'#addc30',
    16.0:'#90d743',
    15.0:'#75d054',
    14.0:'#5ec962',
    13.0:'#48c16e',
    12.0:'#35b779',
    11.0:'#28ae80',
    10.0:'#20a486',
    9.0:'#1f9a8a',
    8.0:'#21918c',
    7.0:'#24868e',
    6.0:'#287c8e',
    5.0:'#2c728e',
    4.0:'#31688e',
    3.0:'#365d8d',
    2.0:'#3b528b',
    1.0:'#404688',
    0.0:'#443983'
}

xdropdown_cols = ['satjob', 'relationship', 'male_breadwinner', 'men_bettersuited', 'child_suffer', 'men_overwork']
group_dropdown_cols = ['sex', 'region', 'edu_cat']


## Dashboard object definitions...
gender_wage_gap = '''
The gender wage gap refers to the significant difference between the income earned by men and that earned by women, which has persisted since recordkeeping began. While this gap has decreased over time, it is still present today and is known to have significant effects on women, families, and the social structures and economy of the US. The Center for American Progress and the Center for Economic Policy Research found that the 2012 US GDP would have been 11 percent lower had the gender wage gap not improved since 1979. Women's lower income is also implicated in driving them from the workforce in the face of increased family caregiving demands, which in turn further increases the gender wage gap, producing a positive feedback loop - one of many causes behind the gap. The wage gap has many additional causes: lower-income occupations and industries tend to be women-dominated, the demands of family limit the number of hours and types of jobs women can work, and outright discrimination also plays a role. While the wage gap has been narrowing - driven in part by the higher educational achievements of women compared to men - it has not closed, and women today make 84 cents on average to every dollar made by men, with larger gaps present depending on the effects of a worker's race. This complex issue has far-reaching consequences and can be addressed by state and federal policy, but a thorough understanding of the contributing factors is necessary to implement the most effective interventions. 

[https://www.dol.gov/sites/dolgov/files/WB/UnderstandingTheGenderWageGap.pdf](https://www.dol.gov/sites/dolgov/files/WB/UnderstandingTheGenderWageGap.pdf)

[https://www.americanprogress.org/article/playbook-for-the-advancement-of-women-in-the-economy/closing-the-gender-pay-gap/](https://www.americanprogress.org/article/playbook-for-the-advancement-of-women-in-the-economy/closing-the-gender-pay-gap/)
'''

gss_summary = '''
The GSS, or General Social Survey, is a biyearly survey collected by NORC on behaf of the National Science Foundation. The survey is composed of questions designed to gain data on a range of social and political topics, including demographics, social group interactions, and respondants' attitudes, expectations, and priorities. Several thousand interviews are conducted, with selected participants forming a representative sample of the English or Spanish speaking adult US population. Survey data is available dating as far back as 1972, making the GSS a valuable tool for social researchers.

[https://gss.norc.org/About-The-GSS](https://gss.norc.org/About-The-GSS)

[https://www.norc.org/about/who-we-are.html](https://www.norc.org/about/who-we-are.html)
'''

gss_table = gss_clean.groupby(['sex']).agg({
    'income':'mean',
    'job_prestige':'mean',
    'socioeconomic_index':'mean',
    'education':'mean'
    }).reset_index().rename({
        'sex':'Sex',
        'income':'Avg. income ($)',
        'job_prestige': 'Avg. job prestige<br>rating',
        'socioeconomic_index':'Avg. socioeconomic<br>index',
        'education':'Avg. years of<br>education'
    }, axis = 'columns')

gss_table = round(gss_table, 2)

disp_table = ff.create_table(gss_table)
disp_table.update_layout({
    'margin':dict(l=100, r=100, t=0, b=0),
    'font':dict(size=16),
    'paper_bgcolor':'rgba(0, 0, 0, 0)',
    'plot_bgcolor':'white'
    })

bar_data = pd.crosstab(gss_clean.sex, gss_clean.male_breadwinner).reset_index()

bar_data = pd.melt(bar_data, id_vars=['sex'], value_vars=['Strongly disagree', 'Disagree', 'Agree', 'Strongly agree']).rename({'value':'count'}, axis = 'columns')

bar_fig = px.bar(
    bar_data, x = 'male_breadwinner', y = 'count', color = 'sex',
    labels = {'male_breadwinner':'Response', 'count':'Number of respondants', 'sex': 'Respondant sex'},
    barmode = 'group',
    text = 'count',
    opacity = 0.9,
    color_discrete_map = my_colors
    )

bar_fig.update_layout({
    'paper_bgcolor':'rgba(0, 0, 0, 0)',
    'plot_bgcolor':'rgba(0, 0, 0, 0)',
    'font_color':'#98999A',
    'yaxis.gridcolor':'#98999A',
    'font':dict(size=20),
    'margin':dict(l=25, r=10, t=0, b=50),
    'legend':dict(x = 0.83, y = 0.9, bgcolor = 'black')
})

bar_fig.update_traces(marker = dict(line = dict(width = 0)))

scatter_fig = px.scatter(
    gss_clean, x = 'job_prestige', y = 'income', color = 'sex',
    trendline = 'ols',
    labels = {
        'job_prestige':'Job prestige rating', 
        'income':'Income',
        'sex':'Sex',
        'education':'Education',
        'socioeconomic_index':'Socioeconomic index'
        },
    hover_data = ['education', 'socioeconomic_index'],
    opacity = 0.4,
    height = 500,
    width = 1000,
    color_discrete_map = my_colors
    )

scatter_fig.update_layout({
    'paper_bgcolor':'rgba(0, 0, 0, 0)',
    'plot_bgcolor':'rgba(0, 0, 0, 0)',
    'font_color':'#98999A',
    'yaxis.gridcolor':'#98999A',
    'xaxis.gridcolor':'#98999A',
    'font':dict(size=20),
    'margin':dict(l=25, r=10, t=0, b=50)
})

scatter_fig.update_traces(marker = dict(size = 10))

box_fig1 = px.box(
    gss_clean, x = 'sex', y = 'income', color = 'sex',
    labels = {'income':'Income', 'sex':''},
    height = 500,
    width = 500,
    color_discrete_map = my_colors
)

box_fig1.update_layout(showlegend = False)
box_fig1.update_traces(opacity = 0.9)
box_fig1.update_layout({
    'paper_bgcolor':'rgba(0, 0, 0, 0)',
    'plot_bgcolor':'rgba(0, 0, 0, 0)',
    'font_color':'#98999A',
    'yaxis.gridcolor':'#98999A',
    'font':dict(size=20),
    'margin':dict(l=25, r=10, t=0, b=50)
})

box_fig2 = px.box(
    gss_clean, x = 'sex', y = 'job_prestige', color = 'sex',
    labels = {'job_prestige':'Job prestige rating', 'sex':''},
    height = 500,
    width = 500,
    color_discrete_map = my_colors
)

box_fig2.update_layout(showlegend = False)
box_fig2.update_traces(opacity = 0.9)
box_fig2.update_layout({
    'paper_bgcolor':'rgba(0, 0, 0, 0)',
    'plot_bgcolor':'rgba(0, 0, 0, 0)',
    'font_color':'#98999A',
    'yaxis.gridcolor':'#98999A',
    'font':dict(size=20),
    'margin':dict(l=25, r=10, t=0, b=50)
})

gss_sub = gss_clean[['income', 'sex', 'job_prestige']].copy()

gss_sub['prestige_category'] = pd.cut(gss_sub.job_prestige, bins = [15, 26, 37, 48, 59, 70, 81], labels = ('Very low', 'Low', 'Lower-average', 'Upper-average', 'High', 'Very high')).astype('category')

gss_sub = gss_sub.dropna()

box_facets = px.box(
    gss_sub, x = 'income', y = 'sex', color = 'sex',
    facet_col = 'prestige_category', facet_col_wrap = 2,
    labels = {'income':'Income', 'sex':''},
    color_discrete_map = my_colors,
    category_orders = {
        'prestige_category':['Very low', 'Low', 'Lower-average', 'Upper-average', 'High', 'Very high'],
        'sex':['male', 'female']},
    height = 600,
    width = 1100
)

box_facets.update_layout(showlegend = False)
box_facets.for_each_annotation(lambda a: a.update(text = a.text.replace('prestige_category=', '') + ' prestige'))
box_facets.update_xaxes(gridcolor = '#98999A')
box_facets.update_layout({
    'paper_bgcolor':'rgba(0, 0, 0, 0)',
    'plot_bgcolor':'rgba(0, 0, 0, 0)',
    'font_color':'#98999A',
    'font':dict(size=20)
})


# App building and layout arrangement...
app = dash.Dash(__name__, external_stylesheets = external_stylesheets)
app.layout = html.Div(
    [
        html.H1('The Gender Wage-Gap, as Captured in the Data of the 2018 General Social Survey'),
        html.H6('Kaz Barker, DS6001 Spring 2024'),
        html.Br(),
        html.H3(' - Background - '),
        dcc.Markdown(children = gender_wage_gap),
        html.Br(),
        dcc.Markdown(children = gss_summary),
        html.Br(),
        html.Br(),
        html.H3(' - GSS Statistics - '),
        html.H4('Average Metrics by Respondent Sex:'),
        dcc.Markdown(children = 'Male respondents exhibit higher average annual income than female respondents, despite having similar overall levels of education and job prestige.'),
        html.Center(dcc.Graph(figure = disp_table)),
        html.Br(),
        html.Br(),
        html.Br(),
        html.H4('Responses to the GSS Prompt on the Familial Roles of Men and Women:'),
        dcc.Markdown(children = 'Rated level of agreement with the GSS prompt: "It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family". Far fewer male respondents strongly disagree with the statement than female respondents do.'),
        html.Center(dcc.Graph(figure = bar_fig)),
        html.Br(),
        html.Br(),
        html.Br(),
        html.H4('Interactive plot: GSS Prompt Responses by Respondent Sex, Region of Residence, or Level of Education'),
        html.Div(className = 'row', children = [
            html.Div([
                dcc.Dropdown(
                    id = 'grouping',
                    options = [{'label':i, 'value':i} for i in group_dropdown_cols],
                    value = 'sex',
                    clearable = False)
            ], style = {'padding-left':'80%'}),

            html.Div([
                dcc.Graph(id = 'my_graph', responsive = False)
            ], style = {'float':'center'}),
            
            html.Div([
                dcc.Dropdown(
                    id = 'x-axis',
                    options = [{'label':i, 'value':i} for i in xdropdown_cols],
                    value = 'male_breadwinner',
                    clearable = False)
            ], style = {'padding-left':'35%', 'width':'30%', 'padding-top':'2%'})
        ]),

        html.Br(),
        html.Br(),
        html.Br(),
        html.H4('Income Across Job Prestige Rating:'),
        dcc.Markdown(children = 'Male income generally grows faster than female income as job prestige rating increases.'),
        html.Center(dcc.Graph(figure = scatter_fig)),
        html.Br(),
        html.Br(),
        html.Br(),
        html.H4('Income and Job Prestige for Male vs Female Respondents:'),
        dcc.Markdown(children = 'Though average, maximum, and minimum income show little sex-based difference, the middle 50% of reported income values cover a range that is higher for males than for females. At the same time, female respondents on average worked jobs with higher prestige ratings than male respondents.', style = {'width':'90%'}),
        html.Div([dcc.Graph(figure = box_fig1), html.Br(), html.Br(), html.Br(), html.Br()], style = {'width':'48%', 'float':'left'}),
        html.Div([dcc.Graph(figure = box_fig2), html.Br(), html.Br(), html.Br(), html.Br()], style = {'width':'48%', 'float':'right'}),
        html.H4('Income by Level of Job Prestige for Male and Female Respondents:'),
        dcc.Markdown(children = 'Increases in job prestige are associated with greater increases in income for male respondents than for female respondents.', style = {'width':'90%'}),
        html.Center(dcc.Graph(figure = box_facets))
    ]
)


# Callback...
@app.callback(
    Output(component_id = 'my_graph', component_property = 'figure'),
    [
        Input(component_id = 'x-axis', component_property = 'value'),
        Input(component_id = 'grouping', component_property = 'value')
    ]
)

def make_graph(x, group):
    frame_index = [i for i in range(0, len(interactive_results)) if x in interactive_cols[i] and group in interactive_cols[i]]
    label_replace_map = {
            'satjob':'GSS prompt: "On the whole, how satisfied are you with the work you do?"',
            'relationship':'GSS prompt: "A preschool child is likely to suffer if his or her mother works."',
            'male_breadwinner':'GSS prompt: "It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family."',
            'men_bettersuited':'GSS prompt: "Most men are better suited emotionally for politics than are most women."',
            'child_suffer':'GSS prompt: "A preschool child is likely to suffer if his or her mother works."',
            'men_overwork':'GSS prompt: "Family life often suffers because men concentrate too much on their work."',
            'sex':'Sex',
            'region':'Region of residence',
            'edu_cat':'Years of education',
            'size':'Size'
        }

    hover_replace_map = {
            'satjob':'GSS prompt response',
            'relationship':'GSS prompt response',
            'male_breadwinner':'GSS prompt response',
            'men_bettersuited':'GSS prompt response',
            'child_suffer':'GSS prompt response',
            'men_overwork':'GSS prompt response',
            'sex':'Sex',
            'region':'Region of residence',
            'edu_cat':'Years of education',
            'size':'Size'
        }

    frame_title = [label_replace_map.get(item, item) for item in  [col for col in interactive_cols[frame_index[0]] if col == x]]
    
    func_graph = px.bar(
        interactive_results[frame_index[0]],
        x = x,
        y = 'size',
        title = '<br>'.join(textwrap.wrap(frame_title[0], width = 80)),
        labels = hover_replace_map,
        color = group,
        barmode = 'group',
        text = 'size',
        opacity = 0.9,
        color_discrete_map = my_colors)
    
    func_graph.update_layout({
        'paper_bgcolor':'rgba(0, 0, 0, 0)',
        'plot_bgcolor':'rgba(0, 0, 0, 0)',
        'font_color':'#98999A',
        'yaxis.gridcolor':'#98999A',
        'font':dict(size=20),
        'margin':dict(l=10, r=10, t=90, b=0),
        'xaxis_title':None,
        'title.y':1,
        'title_pad':dict(t=40)
        })
    
    func_graph.update_traces(marker = dict(line = dict(width = 0)))

    return(func_graph)


# Running...
if __name__ == '__main__':
    app.run_server(debug = True, port = 8080)
