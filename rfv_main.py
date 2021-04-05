import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import squarify
from mysql.connector import connection
from unidecode import unidecode
from datetime import datetime
import calendar
import datetime as dt
import streamlit as st
import os
import base64

class Rfv_Analysis:
    
    def __init__(self, csv, R_limits, F_limits, M_limits):
        """
        Description
            Construcor method
        
        Args            
            csv(csv): A csv that each row is a transaction, and has 'date_created', 'customer_id', 'net_total' columns
            R_limits(list): A list object with recency limits in ascending form
            F_limits(list): A list object with frequency limits in ascending form
            M_limits(list): A list object with monetary limits in ascending form
        """
        self.csv = csv
        self.R_limits = R_limits
        self.F_limits = F_limits
        self.M_limits = M_limits

    
    def transactions_df(self):
        """
        Description
            Transform into a dataframe that has transactions per customer_id and date_created, transform date column 
            in datetime format and drop negative net_total values.
        Args
            
        Returns
            A dataframe object
        """
        #read the csv into a pandas dataframe
        df = pd.read_csv(self.csv)
        
        #transform this df into a transactions dataframe
        transactions = df[['date_created', 'customer_id', 'net_total']].groupby(['customer_id', 'date_created'], as_index=False).count()
        transactions.columns = ['customer_id', 'date_created', 'qtd_transactions']
        transactions['net_total'] = df[['date_created', 'customer_id', 'net_total']].groupby(['customer_id', 'date_created'], as_index=False).sum()['net_total']
        transactions['order_id'] = order_id = df[['order_id', 'customer_id', 'date_created', 'net_total']].groupby(['customer_id', 'date_created'], as_index=False).agg({'order_id': lambda x: x, 'net_total': lambda x: sum(x)})['order_id']
        
        #Drop all the negative values in the net_total column
        transactions.drop(transactions[transactions['net_total'] < 0].index, axis=0, inplace=True)
        
        #Transform de date column in datetime type
        transactions['date_created'] = pd.to_datetime(transactions['date_created'])
        
        return transactions
    
    def create_rfm_table(self, transactions):
        """
        Description
            Transform into a dataframe that has the recency, frequency and monetary value for each unique customer_id.
        Args
            transactions(dataframe): A dataframe object that each row is a transaction, with customer_id, date_created and net_total
            as columns
        Returns
            A dataframe object
        """
        
        #The last register of our data
        NOW = max(transactions['date_created'])
        
        #Create the RFM table
        rfmTable = transactions.groupby('customer_id').agg({'date_created': lambda x: (NOW - x.max()).days, #recency
                                                   'order_id': lambda x: len(x), #frequency 
                                                   'net_total': lambda x: x.sum()}) #monetary value

        rfmTable['date_created'] = rfmTable['date_created'].astype(int)
        rfmTable.rename(columns={'date_created': 'recency (in days)', 
                                 'order_id': 'frequency', 
                                 'net_total': 'monetary_value'}, inplace=True)
        
        return rfmTable
    
    def quantiles_rfmTable(self, rfmTable):
        """
        Description
            Calculate the quantiles of a dataframe
        Args
            rfmTable(dataframe): A dataframe object with recency, frequency and monetary value for each unique customer_id. 
        Returns
            A dictionary object
        """
        #Returns a dictonary object with the quantiles
        quantiles = rfmTable.quantile([0.25, 0.5, 0.75])
        quantiles = quantiles.to_dict()
        
        return quantiles
    
    def segm_recency_limits(self, x):
        """
        Description
            Segments the customer within the recency dimension
        Args
            x(dataframe column): The recency column of a rfmTable 
        Returns
            A score for recency
        """
        #We test the length of the R_limits list to use the correct method 
        if len(self.R_limits) == 3:            
            if x <= self.R_limits[0]:     
                return 4
            if x <= self.R_limits[1]:     
                return 3
            if x <= self.R_limits[2]:    
                return 2            
            else:
                return 1   
        else:
            if x <= self.R_limits[0]:     
                return 4
            if x <= self.R_limits[1]:     
                return 3
            if x <= self.R_limits[2]:    
                return 2            
            if x <= self.R_limits[3]:
                return 1
            else:
                return 0
            
    def segm_frequency_limits(self, x):
        """
        Description
            Segments the customer within the frequency dimension
        Args
            x(dataframe column): The frequency column of a rfmTable 
        Returns
            A score for frequency
        """
        #We test the length of the F_limits list to use the correct method 
        if len(self.F_limits) == 3:
            if x <= self.F_limits[0]:
                return 1
            if x <= self.F_limits[1]:
                return 2
            if x <= self.F_limits[2]:
                return 3
            else:
                return 4
        else:
            if x <= self.F_limits[0]:
                return 0
            if x <= self.F_limits[1]:
                return 1
            if x <= self.F_limits[2]:
                return 2
            if x <= self.F_limits[3]:
                return 3
            else:
                return 4
            
            
    def segm_monetary_limits(self, x):
        """
        Description
            Segments the customer within the monetary dimension
        Args
            x(dataframe column): The monetary column of a rfmTable 
        Returns
            A score for monetary
        """
        #We test the length of the M_limits list to use the correct method 
        if len(self.M_limits) == 3:
            if x <= self.M_limits[0]:
                return 1
            if x <= self.M_limits[1]:
                return 2
            if x <= self.M_limits[2]:
                return 3
            else:
                return 4
        else:
            if x <= self.M_limits[0]:
                return 0
            if x <= self.M_limits[1]:
                return 1
            if x <= self.M_limits[2]:
                return 2
            if x <= self.M_limits[3]:
                return 3
            else:
                return 4
        
    def rfm_segmentation(self, rfmTable):
        """
        Description
            Segments the customer within the recency, frequency and monetary value. 
        Args
            rfmTable(dataframe): A dataframe object with recency, frequency and monetary value for each unique customer_id.  
        Returns
            A rfmTable the score in recency, frequency and monetary value.
        """
        #Adds 3 columns with score in R, F and M.
        rfmTable['R_Quartile'] = rfmTable['recency (in days)'].apply(self.segm_recency_limits)
        rfmTable['F_Quartile'] = rfmTable['frequency'].apply(self.segm_frequency_limits)
        rfmTable['M_Quartile'] = rfmTable['monetary_value'].apply(self.segm_monetary_limits)
        
        #Concatenate those 3 values
        rfmTable['RFMClass'] = rfmTable.R_Quartile.map(str) \
                            + rfmTable.F_Quartile.map(str) \
                            + rfmTable.M_Quartile.map(str)
        
        #Sum those 3 values into a single score
        rfmTable['RFM_Score'] = rfmTable[['R_Quartile', 'F_Quartile', 'M_Quartile']].sum(axis=1)
        
        return rfmTable
    
    def group_segments(self, rfmSegmentation):
        """
        Description
            Segments each client into a RFM class, and calculate statistics of each class. 
        Args
            rfmSegmentation(dataframe): A dataframe object with recency, frequency and monetary value for each unique customer_id.  
        Returns
            A RFM classes dataframe
        """
        total_value = sum(rfmSegmentation['monetary_value'])
        customers_total = rfmSegmentation.shape[0]
        
        d = []
        total = []
        total_customers = []
        percentual_customers = []
        mean_recency = []
        rows_index = []
        mean_frequency = []
        #Put each customer_id in a RFM class, and calculate descriptive statistics of each class
        for segment in rfmSegmentation['RFMClass'].unique():
            rows_index.append(segment)
            total_customers.append(rfmSegmentation[rfmSegmentation['RFMClass'] == segment].shape[0])
            percentual_customers.append(100*rfmSegmentation[rfmSegmentation['RFMClass'] == segment].shape[0]/customers_total)
            mean_recency.append(rfmSegmentation[rfmSegmentation['RFMClass'] == segment]['recency (in days)'].mean())
            total.append(rfmSegmentation[rfmSegmentation['RFMClass'] == segment]['monetary_value'].sum())
            mean_frequency.append(rfmSegmentation[rfmSegmentation['RFMClass'] == segment]['frequency'].mean())
            d.append((rfmSegmentation[rfmSegmentation['RFMClass'] == segment]['monetary_value'].sum()/total_value)*100)
        
        #Create the classes dataframe
        classes_df = pd.DataFrame(d, index=rows_index, columns=['percent of the total'])
        classes_df['total_monetary'] = total
        classes_df['total_customers'] = total_customers
        classes_df['percentual_customers'] = percentual_customers
        classes_df['mean_recency'] = mean_recency
        classes_df['mean_frequency'] = mean_frequency
        classes_df = classes_df.reindex(columns=['total_monetary', 'percent of the total', 'total_customers', 'percentual_customers', 'mean_recency', 'mean_frequency'])
        
        return classes_df
    
    def defining_clusters(self, classes_df):
        """
        Description
            Divide customer_id in 4 categories define as:
            Vips: The customers with max score in RFM
            Valiosos: The least percentual of customers with 20% of the revenue
            Potenciais: 30% of the customers with the highest revenue
            Descompromissados: The rest of the customers
        Args
            classes_df(dataframe): A dataframe object with descriptive statistcs of each RFM's classes.  
        Returns
            Lists of valiosos, potenciais and descompromissados
        """
        #Valiosos
        valiosos = classes_df.sort_values('percent of the total', ascending=False)['percent of the total'][1:5].index

        #Potenciais
        potenciais = classes_df.sort_values('percent of the total', ascending=False)['percent of the total'][5:12].index

        #Descompromissados
        descompromissados = classes_df.sort_values('percent of the total', ascending=False)['percent of the total'][12:52].index
        
        return valiosos, potenciais, descompromissados
    
    def rfm_level(self, df, valiosos, potenciais, descompromissados):
        """
        Description
            Segment each RFM class into Vips, Valiosos, Potenciais or Descompromissados.
        Args
            df(dataframe's column):A dataframe's column that has RFM class   
        Returns
            A classification for each class
        """
        
        if (df['RFMClass'] == '444'):
            return 'Vips'

        if (df['RFMClass'] in valiosos):
            return 'Valiosos'

        if (df['RFMClass'] in potenciais):
            return 'Potenciais'

        if (df['RFMClass'] in descompromissados):
            return 'Descompromissados'
    
    def customer_moment(self, df):
        """
        Description
            Classifies the moment of the customer into 4 categories:
            Entrantes: recency <= 30 days
            Manutenção: 30 < recency <= 100
            Recuperação: 100 < recency <= 200
            Inativo: recency > 200 days
        Args
            df(dataframe's column):A dataframe's column with recency of each customer 
        Returns
            A classification for each customer
        """
        if (df['recency (in days)'] <= 30):
            return 'Entrantes'
        if ((df['recency (in days)'] > 30) and (df['recency (in days)'] <= 100)):
            return 'Manutenção'
        if ((df['recency (in days)'] > 100) and (df['recency (in days)'] <= 200)):
            return 'Recuperação'
        if (df['recency (in days)'] > 200):
            return 'Inativo'

        
    def clusters_percentual(self, rfmSegmentation):
        """
        Description
            Calculates the percentual of customers in each segment of customers (Vips, Valiosos, Potenciais and Descompromissados)
        Args
            rfmSegmentation(dataframe): A dataframe object with recency, frequency and monetary value for each unique customer_id. 
        Returns
            The percentual of each segment in the form:
            vips_customers_perc, valiosos_customers_perc, potenciais_customers_perc, descompromissados_customers_perc
        """
        #Vips
        vips_customers = rfmSegmentation[rfmSegmentation['RFM_Level'] == 'Vips']
        vips_customers_perc = (vips_customers.shape[0]/rfmSegmentation.shape[0])*100


        #Valiosos
        valiosos_customers = rfmSegmentation[rfmSegmentation['RFM_Level'] == 'Valiosos']
        valiosos_customers_perc = (valiosos_customers.shape[0]/rfmSegmentation.shape[0])*100


        #Potenciais
        potenciais_customers = rfmSegmentation[rfmSegmentation['RFM_Level'] == 'Potenciais']
        potenciais_customers_perc = (potenciais_customers.shape[0]/rfmSegmentation.shape[0])*100


        #Descompromissados
        descompromissados_customers = rfmSegmentation[rfmSegmentation['RFM_Level'] == 'Descompromissados']
        descompromissados_customers_perc = (descompromissados_customers.shape[0]/rfmSegmentation.shape[0])*100

        return vips_customers_perc, valiosos_customers_perc, potenciais_customers_perc, descompromissados_customers_perc
    
    def rfm_graphic(self, rfmSegmentation):
        
        """
        Description
            Plot the segments of customers with it's respective percentuals
        Args
            rfmSegmentation(dataframe): A dataframe object with recency, frequency and monetary value for each unique customer_id. 
        Returns
            A function with rfmSegmentation as a parameter
        """
        rfm_level_agg = rfmSegmentation.groupby('RFM_Level').agg({
        'recency (in days)': 'mean',
        'frequency': 'mean',
        'monetary_value': ['mean', 'count']}).round(1)
        
        
        vips_customers_perc, valiosos_customers_perc, potenciais_customers_perc, descompromissados_customers_perc = self.clusters_percentual(rfmSegmentation)
        #rfm_level_agg.columns = rfm_level_agg.columns.droplevel()
        rfm_level_agg.columns = ['RecencyMean','FrequencyMean','MonetaryMean', 'Count']
        #Create our plot and resize it.
        fig = plt.gcf()
        ax = fig.add_subplot()
        fig.set_size_inches(16, 9)
        squarify.plot(sizes=rfm_level_agg['Count'], 
                      label=[f'Descompromissados {round(descompromissados_customers_perc,2)}%',
                             f'Potenciais {round(potenciais_customers_perc,2)}%',
                             f'Valiosos {round(valiosos_customers_perc, 2)}%',
                             f'Vips {round(vips_customers_perc, 2)}%'], alpha=.6)
        plt.title("RFM Segments",fontsize=18,fontweight="bold")
        plt.axis('off')
        #plt.savefig('RFMSegments')
        plt.show()
            
    
    def pipeline(self):
        """
        Description
            Pipeline that apply all the transformations on the data
        Args
            
        Returns
            Returns a dataframe with the RFM classes, a dataframe with segmentation per customer and a function to plot RFM classes
        """
        
        #Creates the transactions dataframe
        transactions = self.transactions_df()
        
        #Creates the rfm table
        rfmTable = self.create_rfm_table(transactions)
        
        #Segments the rfm table
        rfmSegmentation = self.rfm_segmentation(rfmTable)
        
        classes_df = self.group_segments(rfmSegmentation)
        
        #Defining the clusters
        valiosos, potenciais, descompromissados = self.defining_clusters(classes_df)
        
        #Create two new columns to segment the customers
        rfmSegmentation['RFM_Level'] = rfmSegmentation.apply(self.rfm_level,valiosos=valiosos, potenciais=potenciais, descompromissados=descompromissados,axis=1)
        rfmSegmentation['Customer_momento'] = rfmSegmentation.apply(self.customer_moment, axis=1)        
        
        return classes_df, rfmSegmentation


def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'    

st.title('RFM Analysis')
st.markdown("Segmentation of customers")
uploaded_files = st.file_uploader("Upload CSV", type="csv")

st.markdown('Input the Recency limits in ascending form')
r1 = st.number_input('Enter first recency limit')
r2 = st.number_input('Enter second recency limit')
r3 = st.number_input('Enter third recency limit')
r4 = st.number_input('Enter forth recency limit')

st.markdown('Input the Frequency limits in ascending form')
f1 = st.number_input('Enter first frequency limit')
f2 = st.number_input('Enter second frequency limit')
f3 = st.number_input('Enter third frequency limit')
f4 = st.number_input('Enter forth frequency limit')

st.markdown('Input the Monetary limits in ascending form')
m1 = st.number_input('Enter first monetary limit')
m2 = st.number_input('Enter second monetary limit')
m3 = st.number_input('Enter third monetary limit')
m4 = st.number_input('Enter forth monetary limit')

button_run = st.button('Click to run')

if (button_run):    
    rfv = Rfv_Analysis(uploaded_files, [int(r1), int(r2), int(r3), int(r4)], [int(f1), int(f2), int(f3), int(f4)], [m1, m2, m3, m4])
    classes_df, rfmSegmentation = rfv.pipeline()
    classes_df
    rfmSegmentation


    csv = rfmSegmentation.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a> (right-click and save as &lt;some_name&gt;.csv)'
    st.markdown(href, unsafe_allow_html=True)

