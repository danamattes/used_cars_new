#Importing all the necessary libraries 
import streamlit as st
import pandas as pd 
import plotly.express as px
import numpy as np
import altair as alt

#Reading the df into pandas and getting a sample of the information.
df=pd.read_csv("vehicles_us.csv")

#Converting the "date_posted" column to datetime object.
df['date_posted']=pd.to_datetime(df['date_posted'], format='%Y-%m-%d')

#Creating a new column containing the make only. The reasoning here is that the model seems to be the first word of each value, so the first word is being extracted to this new column.
df['make'] = df['model'].str.split().str[0]

#Dealing with measing values on 'model_year"
df['model_year'] = df.groupby('make')['model_year'].transform(lambda x: x.fillna(x.mode().iloc[0]))
df['model_year'] = df['model_year'].astype(int)

#Dealing with missing values on 'cylinders' column
df['cylinders'] = df.groupby('type')['cylinders'].transform(lambda x: x.fillna(x.median()))

#Dealing with missing values in 'odometer' column
df['odometer'] = df.groupby('model_year')['odometer'].transform(lambda x: x.fillna(x.mean()))
df['odometer'] = df['odometer'].round(0)

#Dealing with missing values in 'paint_color' column
group_mode = df.groupby('make')['paint_color'].apply(lambda x: x.mode()[0])
df['paint_color'] = df.groupby('make')['paint_color'].transform(lambda x: x.fillna(group_mode[x.name]))

#Replacing missing values in 'is_4wd' with '0'
df['is_4wd'] = df['is_4wd'].fillna(0)

#Creating a new column containing the day, month and year the product was posted.
#I later decided to get rid of these columns as the analysis I performed based on the time didn't give a lot of relevant information.
#df['day_posted']=df['date_posted'].dt.day
#df['month_posted']=df['date_posted'].dt.month
#df['year_posted']=df['date_posted'].dt.year

#Adding a column classifying the vehicles by their age
def age_clasification(row):
    """
    The function returns a category according to the car's year model, using the following rules:
    —'nearly_new' for model_year >= 2017
    —'late_model' for model_year >= 2009 
    —'modern'  for model_year >= 2000
    —'classic' for model_year >= 1974
    —'antique' for year >= 1931 
    —'vintage' for year < 1931

    """

    year = row['model_year']
    
    if year >= 2017:
        return 'nearly_new'
    else:
        if year >= 2009:
            return 'late_model'
        else:
            if year >= 2000:
                return 'modern'
            else:
                if year >= 1974:
                    return 'classic'
                else:
                    if year >= 1931:
                        return 'antique'
                    else:
                        if year < 1931:
                            return 'vintage'
   


df['classification'] = df.apply(age_clasification, axis=1)
#Creating a title
st.title('Used Cars Advertisements :car:')

st.text('On this web service we will be analyzing the data of used cars adversiments \nposted from May-2018 to April-2019.')

#Creating first header
st.header('Data Viewer')

#Displaying the data
st.dataframe(df)

#Creating a bar plot showing the amount of cars advertised according to their type, classification and make.
st.header('Vehicle types and their classification by age')
st.text('The vehicles were sorted according to the following age parameters:')
st.text('Nearly new: Cars from 2017 to 2019. \nLate model: Cars from 2009 to 2016. \nModern: Cars from 2000 to 2008. \nClassic: Cars from 1974 to 1999.\nAntique: Cars from 1931 to 1973.\nVintage: Any cars from before 1931.')  


type_options = df['type'].unique().tolist()
type = st.selectbox('Which type of vehicle would you like to see?', type_options, 0)

fig = px.bar(df, x='classification', color='make', hover_name='make')
fig.update_xaxes(type='category')
fig.update_layout()
st.write(fig)

#Histogram of condition vs days_listed
st.header("Histogram of 'condition' vs 'days_listed'" )
make_options = df['make'].unique().tolist()
make = st.selectbox('Which make would you like to see?', make_options, 0)
fig = px.histogram(df, x='days_listed', color='condition')
st.write(fig)

#Distribution of price according to the vehicle type
st.header('Distribution of price according to the vehicle type')
type_vehicles = sorted(df['type'].unique())
#First dropdown menu
type_1 = st.selectbox(label='Select vehicle type 1', options=type_vehicles, index=type_vehicles.index('sedan'))
#Second dropdown menu
type_2 = st.selectbox(label='Select vehicle type 2', options=type_vehicles, index=type_vehicles.index('SUV'))
#Filtering the dataframe
mask_type = (df['type'] == type_1) | (df['type'] == type_2)
df_masked = df[mask_type]

#Adding a checkbox to normalize histogram
normalize = st.checkbox('Normalize histogram', value=True)
if normalize:
    histnorm = 'percent'
else:
    histnorm = None

#Creating a plotly histogram figure
fig = px.histogram(df_masked, x='price', nbins=25, color='type', histnorm=histnorm, barmode='overlay', color_discrete_sequence=["green", "blue"], opacity=0.5)
st.write(fig)
