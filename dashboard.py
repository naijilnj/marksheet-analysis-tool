import streamlit as st
import tabula
import plotly.express as px
import pandas as pd
import os
import re
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: Result Analysis")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file",type=(["pdf"]))
filename = None
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = tabula.read_pdf(fl, pages=1,
                      relative_area=True,
                      relative_columns=True,
                      area=[30, 0, 60, 100],
                      columns=[6, 15, 22, 28, 32, 39, 44, 49, 55, 60, 66, 72, 78, 83, 90, 98], encoding = "ISO-8859-1")
    df = df[0]
    df.rename(columns={'Unnamed: 0':'Seat Number', 'Unnamed: 1':'Name', 'Unnamed: 2':'Exams', 'Unnamed: 3':'ST', 'Unnamed: 4':'AI',
                           'Unnamed: 5':'ST Pr', 'Unnamed: 6':'AI Pr', 'Unnamed: 7':'DT', 'Unnamed: 8':'NGD', 'Unnamed: 9':'NGD Pr',
                           'Unnamed: 10':'WS', 'Unnamed: 11':'SIC', 'Unnamed: 12':'WS Pr', 'Unnamed: 13':'SIC Pr',
                           'Unnamed: 14':'Total', 'Unnamed: 15':'CGPA'}, inplace=True)
    df = df.drop([df.index[4], df.index[5], df.index[6]])
    df = df.fillna(0)
    pr_columns = [col for col in df.columns if col.endswith('Pr')]
    df.loc[0, pr_columns] = '0'

    dfss = df.drop([df.index[0]])
    dfss = dfss.drop(["Seat Number","Name","CGPA" ], axis = 1)
    dfss = dfss.replace(to_replace='@.*', value='', regex=True)

    swap_dfss=dfss.transpose()
    swap_dfss = swap_dfss.reset_index()
    swap_dfss.columns = swap_dfss.iloc[0]
    swap_dfss = swap_dfss[1:]

    st.sidebar.header("Sem 5 Result")
    st.subheader('Name')
    cell_value = df.iloc[0, 1]
    char_values = re.findall(r'[a-zA-Z]+', cell_value)
    char_values_str = ' '.join(char_values)
    st.write(char_values_str)
    
    st.subheader('Unit Test Marks')
    st.write('Marks out of 40')
    filtered_dfss = swap_dfss[~swap_dfss['Exams'].str.endswith('Pr')]
    columns_to_exclude = ['ESE', 'Total']
    filtered_dfss = filtered_dfss.drop(columns=columns_to_exclude)

    fig = px.bar(filtered_dfss[(filtered_dfss['CA'] != 0) & (filtered_dfss['Exams'] != 'Total')], x='Exams', y='CA', labels={'CA':'Unit Test Marks', 'Exams':'Subjects'}, height=500, width = 1000, text_auto=True, color='Exams')
    fig.update_yaxes(range=[0, 40])
    st.plotly_chart(fig,use_container_width=True)

    with st.expander("View Unit Test Result:"):
      st.write(filtered_dfss.style.background_gradient(cmap="Blues"))
      csv = filtered_dfss.to_csv(index=False).encode("utf-8")
      st.download_button('Download Unit Test Marks', data = csv, file_name = "UnitTest.csv", mime ='text/csv')

    col1, col2 = st.columns((2))
    with col1:
      st.subheader("End Sem Theory Exam Result")
      st.write('Marks out of 60')
      filtered_ese = swap_dfss[swap_dfss['Exams'] != 'Total']
      filtered_ese = filtered_ese.drop(columns=['Total'])
      filtered_ese = filtered_ese[~filtered_ese['Exams'].str.endswith('Pr')]
      filtered_ese = filtered_ese.drop(columns=['CA'])

      fig = px.bar(filtered_ese, x='Exams', y='ESE', labels={'ESE':'End-Sem Exam Marks', 'Exams':'Subjects'}, height = 500, width = 400, text_auto=True)
      fig.update_yaxes(range=[0, 60])
      st.plotly_chart(fig,use_container_width=True)

    with col2:
      st.subheader("End Sem Practical Exam Result")
      st.write('Marks out of 50')
      filtered_esepr = swap_dfss[swap_dfss['Exams'].str.endswith('Pr')]
      columns_to_exclude = ['CA', 'Total']
      filtered_esepr = filtered_esepr.drop(columns=columns_to_exclude)

      fig = px.bar(filtered_esepr, x='Exams', y='ESE', labels={'ESE':'End-Sem Exam Marks', 'Exams':'Subjects'}, height = 500, width = 400, text_auto=True)
      fig.update_yaxes(range=[0, 50])
      st.plotly_chart(fig,use_container_width=True)

    cl1, cl2 = st.columns((2))
    with cl1:
      with st.expander("View ESE Theory Exam Result"):
        st.write(filtered_ese.style.background_gradient(cmap="Blues"))
        csv = filtered_ese.to_csv(index = False).encode('utf-8')
        st.download_button("Download ESE Result", data = csv, file_name = "ese.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

    with cl2:
      with st.expander("View ESE Practical Exam Reult"):
        st.write(filtered_esepr.style.background_gradient(cmap="Oranges"))
        csv = filtered_esepr.to_csv(index = False).encode('utf-8')
        st.download_button("Download ESE Practical Result", data = csv, file_name = "esepractical.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file')
        
    filtered_swap_dfss = swap_dfss[swap_dfss['Exams'] != 'Total']
    filtered_swap_dfss = filtered_swap_dfss.drop(columns=['Total'])
    filtered_swap_dfss = filtered_swap_dfss[~filtered_swap_dfss['Exams'].str.endswith('Pr')]

    st.subheader("Subjectwise Distribution in Unit Test")
    fig = px.pie(filtered_swap_dfss, values="CA", names="Exams", hole=0.5)
    fig.update_traces(text=filtered_swap_dfss["Exams"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    clmn1, clmn2 = st.columns((2))
    with clmn1:
      st.subheader("Subjectwise Distribution in ESE Theory Exam")
      fig = px.pie(filtered_swap_dfss, values="ESE", names="Exams", hole=0.5)
      fig.update_traces(text=filtered_swap_dfss["Exams"], textposition="outside")
      st.plotly_chart(fig, use_container_width=True)

    with clmn2:
      st.subheader("Subjectwise Distribution in ESE Practical Exam")
      filtered_swap_pr = swap_dfss[swap_dfss['Exams'] != 'Total']
      filtered_swap_pr = filtered_swap_pr.drop(columns=['Total'])
      filtered_swap_pr = filtered_swap_pr[filtered_swap_pr['Exams'].str.endswith('Pr')]

      fig = px.pie(filtered_swap_pr, values="ESE", names="Exams", hole=0.5)
      fig.update_traces(text=filtered_swap_pr["Exams"], textposition="outside")
      st.plotly_chart(fig, use_container_width=True)
