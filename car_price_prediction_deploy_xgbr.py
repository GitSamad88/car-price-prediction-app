import pickle as pk
import streamlit as st
import pandas as pd
import time
import datetime as dt
from sklearn.preprocessing import LabelEncoder

# encode make and model
make_model= pd.read_csv("https://docs.google.com/spreadsheets/d/1x4NIc242k51i-nh4hLEd4jxlvkJrDYGAXjoNGm-qZ9w/gviz/tq?tqx=out:csv&sheet=avito_cars_clean_data")[["make","model"]]
encode = LabelEncoder()
make_model["encoded_make"] = encode.fit_transform(make_model["make"])
make_model["encoded_model"] = encode.fit_transform(make_model["model"])
def get_encode_make_model(car_make,car_model):
  make = make_model[make_model["make"] == car_make]
  model = make[make["model"] == car_model]
  encoded_make = model.iloc[0]["encoded_make"]
  encoded_model = model.iloc[0]["encoded_model"]
  return encoded_make,encoded_model



# Load the saved model
with open(r'C:\Users\hp\Downloads\xgbr.pkl', 'rb') as file:
  xgbr = pk.load(file)

# Define the features
st.title("Estimation du Prix d'Une Voiture d'Occasion")
#st.image()
with st.form(key="001"):


  # Marque et Modèle
  make_options = make_model["make"].unique()
  make =st.selectbox("La marque",make_options)
  st.form_submit_button("Modèle")
  model_options =make_model[make_model["make"]==make]["model"].unique()
  model =st.selectbox("choisissez le modéle:",options=model_options)
  MakeModel = get_encode_make_model(car_make = make,car_model = model)


  # Puissance Fiscale
  hp = st.slider("Puissance Fiscale: ", 4, 12)

  # Année
  current_year = dt.datetime.now().year
  year_option = st.slider("Année-Modèle:",1995,int(current_year))
  age = current_year-year_option
  # Kilométrage:
  km = st.number_input("Kilométrage: ",min_value=1000,max_value=300000)
  # Etat general:
  car_state = {
      'Neuf': 10,
      'Excellent': 9,
      'Très bon': 8,
      'Bon': 7,
      'Correct': 6,
      'Pour Pièces': 5,
      'Endommagé': 4
  }

  state = st.selectbox("État generale :",car_state.keys())
  nam_state = car_state[state]
  #st.write(nam_state)


  # Type de transmission

  gearbox_option = st.radio("Type de transmission: ",["Manuelle","Automatique"])
  auto =[1 if gearbox_option=="Automatique" else 0][0]
  man = int(not(auto))
  # Carburant
  fuel_type = st.selectbox("Carburant: ",["Diesel","Essence","Électrique","Hybride"])
  fuel_type_mapping = {
      "Diesel": [1, 0, 0, 0],
      "Électrique": [0, 1, 0, 0],
      "Essence": [0, 0, 1, 0],
      "Hybride": [0, 0, 0, 1],
  }
  diesel, electric, gasoline, hybrid = fuel_type_mapping[fuel_type]
  # Premier main
  is_first_use = st.checkbox("Première main",help ="Cochez la case si oui")#,options=["Oui","Non"])

  # Origine
  origine = st.selectbox("Origine: ",["Dédouanée","Importée neuve","Pas encore dédouanée","WW au Maroc"])

  origine_mapping = {
      "Dédouanée": [1, 0, 0, 0],
      "Importée neuve": [0, 1, 0, 0],
      "Pas encore dédouanée": [0, 0, 1, 0],
      "WW au Maroc": [0, 0, 0, 1],
  }
  cleared, imported_new, not_cleared_yet, ww_in_morocco = origine_mapping[origine]

  my_car = pd.DataFrame(
      {
  'hp':hp,
  'is_first_use':int(is_first_use),
  'make': MakeModel[0],
  'model': MakeModel[1],
  'age': age,
  'mileage': km,
  'num_general_state': nam_state,
  'automatic': auto ,
  'manuel': man,
  'diesel': diesel,
  'electric': electric,
  'gasoline': gasoline,
  'hybrid': hybrid,
  'cleared': cleared,
  'imported_new': imported_new,
  'not_yet_cleared': not_cleared_yet,
  'ww_in_morocco': ww_in_morocco},
      index =[0])

  # Predict the price
  if st.form_submit_button('Estimation de prix',help="Une estimation de prix selon le IA "):
    price = xgbr.predict(my_car)
    st.markdown(f'<div style="background-color: #FF0000; padding: 10px; border-radius: 5px;">Le prix estimé de votre voiture est {round(price[0])} DH</div>', unsafe_allow_html=True)
    #st.markdown(f'Le prix estimé de votre voiture est {round(price[0])} DH')