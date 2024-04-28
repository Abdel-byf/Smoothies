# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col 
import requests
import pandas

# Write directly to the app
st.title(":cup_with_straw: Customize your smoothie :cup_with_straw:")
st.write(
    """Choose the fruit you want in your custom smothie.
    """
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)

pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'choose up to 5 ingredients:'
    , my_dataframe
    , max_selections = 5
)
if ingredients_list:
    ingredients_string = ''
  
    for each_fruit in ingredients_list:
        ingredients_string += each_fruit + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == each_fruit, 'SEARCH_ON'].iloc[0]
        
        st.subheader(each_fruit + ' Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        #fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + each_fruit)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        
    #st.write(ingredients_string) 

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order+ """')"""

    #st.write(my_insert_stmt)
    #st.stop()
    
    time_to_insert = st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered! {name_on_order}', icon="✅")



