import streamlit as st
import pandas as pd
import numpy as np
import numpy.random as rand
import matplotlib.pyplot as plt
import japanize_matplotlib
from sklearn.preprocessing import LabelEncoder

#
# add correlation
#
def addCorrelationToQuantity(data_1, data_2, corr, noise):
  decimalpoint = int(len(str(data_2[0]).strip('0').split('.')[1]))

  x = data_1
  y = data_2

  y_adjusted = (y - y.min()) / (y.max() - y.min())  # Normalization to 0~1
  y_adjusted = y_adjusted * (x.max() - x.min()) + x.min()  # fit scale of y to x
  y_adjusted += corr * x + np.random.normal(0, noise, len(x))  # add noise

  y_min, y_max = y.min(), y.max()
  y_rescaled = (y_adjusted - y_adjusted.min()) / (y_adjusted.max() - y_adjusted.min())
  y_rescaled = y_rescaled * (y_max - y_min) + y_min

  print(decimalpoint)
  z = roundData(y_rescaled,decimalpoint)

  return z

def addCorrelationToQuantityQualitative(quantitativeData, qualitativeData, corr, noise):
  label_encoder = LabelEncoder()
  tmp = pd.DataFrame ({
    'qualitativeData_encoded': label_encoder.fit_transform(qualitativeData)
  })
  return addCorrelationToQuantity(tmp['qualitativeData_encoded'], quantitativeData, corr, noise)

def adjustCategoryData(row, data_1, value_1, data_2, value_2, weight):
  if row[data_1] == value_1 and row[data_2] != value_2:
    if np.random.rand() < weight:
        return value_2
  return row[data_2]

def addCorrelationToQualitative(df, data_1, value_1, data_2, value_2, weight):
  df[data_2] = df.apply(adjustCategoryData, axis=1, data_1=data_1, value_1=value_1, data_2=data_2, value_2=value_2, weight=weight)

def calcVarAndCorr(data_1,data_2):
  variance_1 = np.var(data_1)
  variance_2 = np.var(data_2)
  correlation = np.corrcoef(data_1,data_2)[1][0]
  return variance_1, variance_2, correlation

#
# plot graph
#
def plotLine(data_1, data_2, xTitle, yTitle):
  fig, ax = plt.subplots()
  ax.grid(True)
  ax.plot(data_1,data_2)
  ax.set_xlabel(xTitle)
  ax.set_ylabel(yTitle)
  ax.grid(True)
  st.pyplot(fig)

def plotBar(data, title):
  uniqueElement = data.value_counts()
  uniqueElement.sort_index(ascending=True, inplace=True)

  fig, ax = plt.subplots()
  ax = uniqueElement.plot.bar()
  ax.grid(True)
  ax.set_title("")
  ax.set_xlabel("要素")
  ax.set_ylabel(title)
  st.pyplot(fig)

def plotScatter(data_1, data_2, xTitle, yTitle):
  fig, ax = plt.subplots()
  ax.grid(True)
  ax.scatter(data_1,data_2)
  ax.set_xlabel(xTitle)
  ax.set_ylabel(yTitle)
  ax.grid(True)
  st.pyplot(fig)

#
# show data detail
#
def showQualitativeDetail(data):
  uniqueElement = data.value_counts()
  uniqueElement.sort_index(ascending=True, inplace=True)
  st.write(uniqueElement)

#
# adjust
#
def roundData(data, demicalPlace):
  roundData = data.round(demicalPlace)
  return roundData

def clipData(data, max, min):
  clipData = data.clip(lower=min)
  clipData = clipData.clip(upper=max)
  return clipData

#
# generate data
#
df = pd.DataFrame ({
  'ID': range(1, 100+1)
})
if 'currentDataframe' not in st.session_state:
  st.session_state.currentDataframe = df
else:
  df = st.session_state.currentDataframe

def generateQuantitativeData(defaultDf, name, average, max, min, deviation, decimalpoint):
  df = pd.DataFrame ({
    name : rand.normal(average, deviation, 100)
  })
  df[name] = roundData(df[name], decimalpoint)
  df[name] = clipData(df[name], max, min)
  defaultDf[name] = df[name]
  return defaultDf

def generateQualitativeData(defaultDf, name, choice, weights):
  df = pd.DataFrame ({
    name : rand.choice(choice, 100, p = weights)
  })
  defaultDf[name] = df[name]
  return defaultDf

#----------------------------------#
# streamlit view
#----------------------------------#
st.title('Generate dataset')

#
# generate data frame
#
# set quantitative field
if "quantitativeData" not in st.session_state:
  st.session_state["quantitativeData"] = ['']
# delete　process
def deleteQuantitativeField(target_no):
  if len(st.session_state["quantitativeData"]) > 1:
    new_values = []
    # save in new values
    for index, value in enumerate(st.session_state["quantitativeData"]):
      if index == len(st.session_state["quantitativeData"]):
        break
      elif index == target_no:
        continue
      new_values.append(st.session_state[f"quantitative_text_{str(index+1)}"])
      new_values.append(st.session_state[f"quantitative_average_{str(index+1)}"])
      new_values.append(st.session_state[f"quantitative_range_{str(index+1)}"])
      new_values.append(st.session_state[f"quantitative_deviation_{str(index+1)}"])
      new_values.append(st.session_state[f"quantitative_decimalpoint_{str(index+1)}"])
      # delete
    del st.session_state["quantitativeData"][target_no]
    # insert from new values
    for index, value in enumerate(st.session_state["quantitativeData"]):
      if index == len(st.session_state["quantitativeData"]):
        break
      st.session_state[f"quantitative_text_{str(index+1)}"] = new_values[0+(index*5)]
      st.session_state[f"quantitative_average_{str(index+1)}"] = new_values[1+(index*5)]
      st.session_state[f"quantitative_range_{str(index+1)}"] = new_values[2+(index*5)]
      st.session_state[f"quantitative_deviation_{str(index+1)}"] = new_values[3+(index*5)]
      st.session_state[f"quantitative_decimalpoint_{str(index+1)}"] = new_values[4+(index*5)]
# set text field
for index, text in enumerate(st.session_state["quantitativeData"]):
  st.write(f":orange[量的データ{index+1}]")
  col_1, col_2, col_3, col_4, col_5 = st.columns(5)
  with col_1:
    st.text_input(
      key = f"quantitative_text_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '属性名',
      label_visibility= "collapsed"
    )
  with col_2:
    st.text_input(
      key = f"quantitative_average_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '平均値',
      label_visibility= "collapsed"
    )
  with col_3:
    st.text_input(
      key = f"quantitative_range_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '最大 , 最小',
      label_visibility= "collapsed"
    )
  with col_4:
    st.text_input(
      key = f"quantitative_deviation_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '標準偏差',
      label_visibility= "collapsed"
    )
  with col_5:
    st.text_input(
      key = f"quantitative_decimalpoint_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '小数桁数',
      label_visibility= "collapsed"
    )
  delete_button = st.button("", key=f"quantitative_delete_{str(index+1)}", on_click=deleteQuantitativeField, args=(index, ), icon=":material/delete:")
# add text field of quantitative
def addQuantitativeField():
  st.session_state["quantitativeData"].append('')
# set button of adding
addQuantitativeButton = st.button('', key="add_quantitative", on_click=addQuantitativeField, icon=":material/add:")



# set qualitative field
if "qualitativeData" not in st.session_state:
  st.session_state["qualitativeData"] = ['']
# delete process
def deleteQualitativeField(target_no):
  if len(st.session_state["qualitativeData"]) > 1:
    new_values = []
    # save in new values
    for index, value in enumerate(st.session_state["qualitativeData"]):
      if index == len(st.session_state["qualitativeData"]):
        break
      elif index == target_no:
        continue
      new_values.append(st.session_state[f"qualitative_text_{str(index+1)}"])
      new_values.append(st.session_state[f"qualitative_choice_{str(index+1)}"])
      new_values.append(st.session_state[f"qualitative_weights_{str(index+1)}"])
      # delete
    del st.session_state["qualitativeData"][target_no]
    # insert from new values
    for index, value in enumerate(st.session_state["qualitativeData"]):
      if index == len(st.session_state["qualitativeData"]):
        break
      st.session_state[f"qualitative_text_{str(index+1)}"] = new_values[0+(index*3)]
      st.session_state[f"qualitative_choice_{str(index+1)}"] = new_values[1+(index*3)]
      st.session_state[f"qualitative_weights_{str(index+1)}"] = new_values[2+(index*3)]
# set text field
for index, text in enumerate(st.session_state["qualitativeData"]):
  st.write(f":blue[質的データ{index+1}]")
  st.text_input(
    key = f"qualitative_text_{str(index+1)}",
    label = '',
    value=text,
    placeholder = '属性名',
    label_visibility= "collapsed"
  )
  st.text_input(
    key = f"qualitative_choice_{str(index+1)}",
    label = '',
    value=text,
    placeholder = '要素1 , 要素2 , …',
    label_visibility= "collapsed"
  )
  st.text_input(
    key = f"qualitative_weights_{str(index+1)}",
    label = '',
    value=text,
    placeholder = '割合1 , 割合2 , …',
    label_visibility= "collapsed"
  )
  delete_button = st.button("", key=f"qualitative_delete_{str(index+1)}", on_click=deleteQualitativeField, args=(index, ), icon=":material/delete:")
# add text field of qualitative
def addQualitativeField():
  st.session_state["qualitativeData"].append('')
# set button of adding
addQualitativeButton = st.button('', key="add_qualitative", on_click=addQualitativeField, icon=":material/add:")

#
# create tendency
#
# set tendency field
if "createTendency" not in st.session_state:
  st.session_state["createTendency"] = ['']
# delete process
def deleteTendencyField(target_no):
  if len(st.session_state["createTendency"]) > 1:
    new_values = []
    # save in new values
    for index, value in enumerate(st.session_state["createTendency"]):
      if index == len(st.session_state["createTendency"]):
        break
      elif index == target_no:
        continue
      new_values.append(st.session_state[f"tendency_target_1_{str(index+1)}"])
      new_values.append(st.session_state[f"tendency_target_2_{str(index+1)}"])
      new_values.append(st.session_state[f"tendency_correlation_coefficient_{str(index+1)}"])
      new_values.append(st.session_state[f"tendency_noise_{str(index+1)}"])
      # delete
    del st.session_state["createTendency"][target_no]
    # insert from new values
    for index, value in enumerate(st.session_state["createTendency"]):
      if index == len(st.session_state["createTendency"]):
        break
      st.session_state[f"tendency_target_1_{str(index+1)}"] = new_values[0+(index*4)]
      st.session_state[f"tendency_target_2_{str(index+1)}"] = new_values[1+(index*4)]
      st.session_state[f"tendency_correlation_coefficient_{str(index+1)}"] = new_values[2+(index*4)]
      st.session_state[f"tendency_noise_{str(index+1)}"] = new_values[3+(index*4)]
# set text field
for index, text in enumerate(st.session_state["createTendency"]):
  st.write(f":orange[量的データ] × :orange[量的データ] {index+1}")
  col_1, col_2, col_3 ,col_4 = st.columns(4)
  with col_1:
    st.text_input(
      key = f"tendency_target_1_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '属性1',
      label_visibility= "collapsed"
    )
  with col_2:
    st.text_input(
      key = f"tendency_target_2_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '属性2',
      label_visibility= "collapsed"
    )
  with col_3:
    st.text_input(
      key = f"tendency_correlation_coefficient_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '相関係数',
      label_visibility= "collapsed"
    )
  with col_4:
    st.text_input(
      key = f"tendency_noise_{str(index+1)}",
      label = '',
      value=text,
      placeholder = 'ノイズ',
      label_visibility= "collapsed"
    )
  delete_button = st.button("", key=f"tendency_delete_{str(index+1)}", on_click=deleteTendencyField, args=(index, ), icon=":material/delete:")
# add text field of tendency
def addTendencyField():
  st.session_state["createTendency"].append('')
# set button of adding
addTendencyButton = st.button('', key="add_tendency", on_click=addTendencyField, icon=":material/add:")



# set tendency field
if "createTendencyQuantityQualitative" not in st.session_state:
  st.session_state["createTendencyQuantityQualitative"] = ['']
# delete process
def deleteTendencyQuantityQualitativeField(target_no):
  if len(st.session_state["createTendencyQuantityQualitative"]) > 1:
    new_values = []
    # save in new values
    for index, value in enumerate(st.session_state["createTendencyQuantityQualitative"]):
      if index == len(st.session_state["createTendencyQuantityQualitative"]):
        break
      elif index == target_no:
        continue
      new_values.append(st.session_state[f"tendency_quantity_qualitative_target_1_{str(index+1)}"])
      new_values.append(st.session_state[f"tendency_quantity_qualitative_target_2_{str(index+1)}"])
      new_values.append(st.session_state[f"tendency_quantity_qualitative_correlation_coefficient_{str(index+1)}"])
      new_values.append(st.session_state[f"tendency_quantity_qualitative_noise_{str(index+1)}"])
      # delete
    del st.session_state["createTendencyQuantityQualitative"][target_no]
    # insert from new values
    for index, value in enumerate(st.session_state["createTendencyQuantityQualitative"]):
      if index == len(st.session_state["createTendencyQuantityQualitative"]):
        break
      st.session_state[f"tendency_quantity_qualitative_target_1_{str(index+1)}"] = new_values[0+(index*4)]
      st.session_state[f"tendency_quantity_qualitative_target_2_{str(index+1)}"] = new_values[1+(index*4)]
      st.session_state[f"tendency_quantity_qualitative_correlation_coefficient_{str(index+1)}"] = new_values[2+(index*4)]
      st.session_state[f"tendency_quantity_qualitative_noise_{str(index+1)}"] = new_values[3+(index*4)]
# set text field
for index, text in enumerate(st.session_state["createTendencyQuantityQualitative"]):
  st.write(f":orange[量的データ] × :blue[質的データ] {index+1}")
  col_1, col_2, col_3 ,col_4 = st.columns(4)
  with col_1:
    st.text_input(
      key = f"tendency_quantity_qualitative_target_1_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '量的属性1',
      label_visibility= "collapsed"
    )
  with col_2:
    st.text_input(
      key = f"tendency_quantity_qualitative_target_2_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '質的属性2',
      label_visibility= "collapsed"
    )
  with col_3:
    st.text_input(
      key = f"tendency_quantity_qualitative_correlation_coefficient_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '相関係数',
      label_visibility= "collapsed"
    )
  with col_4:
    st.text_input(
      key = f"tendency_quantity_qualitative_noise_{str(index+1)}",
      label = '',
      value=text,
      placeholder = 'ノイズ',
      label_visibility= "collapsed"
    )
  delete_button = st.button("", key=f"tendency_quantity_qualitative_delete_{str(index+1)}", on_click=deleteTendencyQuantityQualitativeField, args=(index, ), icon=":material/delete:")
# add text field of tendency
def addTendencyQuantityQualitativeField():
  st.session_state["createTendencyQuantityQualitative"].append('')
# set button of adding
addTendencyButton = st.button('', key="add_tendency_quantity_qualitative", on_click=addTendencyQuantityQualitativeField, icon=":material/add:")



# set tendency field
if "createTendencyQualitative" not in st.session_state:
  st.session_state["createTendencyQualitative"] = ['']
# delete process
def deleteTendencyQualitativeField(target_no):
  if len(st.session_state["createTendencyQualitative"]) > 1:
    new_values = []
    # save in new values
    for index, value in enumerate(st.session_state["createTendencyQualitative"]):
      if index == len(st.session_state["createTendencyQualitative"]):
        break
      elif index == target_no:
        continue
      new_values.append(st.session_state[f"tendency_qualitative_target_1_{str(index+1)}"])
      new_values.append(st.session_state[f"tendency_qualitative_value_1_{str(index+1)}"])
      new_values.append(st.session_state[f"tendency_qualitative_target_2_{str(index+1)}"])
      new_values.append(st.session_state[f"tendency_qualitative_value_2_{str(index+1)}"])
      new_values.append(st.session_state[f"tendency_qualitative_weight_{str(index+1)}"])

      # delete
    del st.session_state["createTendencyQualitative"][target_no]
    # insert from new values
    for index, value in enumerate(st.session_state["createTendencyQualitative"]):
      if index == len(st.session_state["createTendencyQualitative"]):
        break
      st.session_state[f"tendency_qualitative_target_1_{str(index+1)}"] = new_values[0+(index*5)]
      st.session_state[f"tendency_qualitative_value_1_{str(index+1)}"] = new_values[1+(index*5)]
      st.session_state[f"tendency_qualitative_target_2_{str(index+1)}"] = new_values[2+(index*5)]
      st.session_state[f"tendency_qualitative_value_2_{str(index+1)}"] = new_values[3+(index*5)]
      st.session_state[f"tendency_qualitative_weight_{str(index+1)}"] = new_values[4+(index*5)]
# set text field
for index, text in enumerate(st.session_state["createTendencyQualitative"]):
  st.write(f":blue[質的データ] × :blue[質的データ] {index+1}")
  col_1, col_2, col_3 ,col_4, col_5 = st.columns(5)
  with col_1:
    st.text_input(
      key = f"tendency_qualitative_target_1_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '属性1',
      label_visibility= "collapsed"
    )
  with col_2:
    st.text_input(
      key = f"tendency_qualitative_value_1_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '変数1',
      label_visibility= "collapsed"
    )
  with col_3:
    st.text_input(
      key = f"tendency_qualitative_target_2_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '属性2',
      label_visibility= "collapsed"
    )
  with col_4:
    st.text_input(
      key = f"tendency_qualitative_value_2_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '変数2',
      label_visibility= "collapsed"
    )
  with col_5:
    st.text_input(
      key = f"tendency_qualitative_weight_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '出現確率',
      label_visibility= "collapsed"
    )
  delete_button = st.button("", key=f"tendency_qualitative_delete_{str(index+1)}", on_click=deleteTendencyQualitativeField, args=(index, ), icon=":material/delete:")
# add text field of tendency
def addTendencyQualitativeField():
  st.session_state["createTendencyQualitative"].append('')
# set button of adding
addTendencyButton = st.button('', key="add_tendency_qualitative", on_click=addTendencyQualitativeField, icon=":material/add:")



# update dataframe
def updateTable(df):
  st.session_state.currentDataframe = df



# generate process
def generate():
  for index, text in enumerate(st.session_state["quantitativeData"]):
    name = st.session_state[f"quantitative_text_{str(index+1)}"]
    average = st.session_state[f"quantitative_average_{str(index+1)}"]
    maxmin = st.session_state[f"quantitative_range_{str(index+1)}"]
    deviation = st.session_state[f"quantitative_deviation_{str(index+1)}"]
    decimalpoint = st.session_state[f"quantitative_decimalpoint_{str(index+1)}"]
    if name=="" or average=="" or maxmin=="" or deviation=="" or decimalpoint=="":
      continue
    average = float(average)
    min = float(maxmin.split(',')[0])
    max = float(maxmin.split(',')[1])
    deviation = float(deviation)
    decimalpoint = int(decimalpoint)
    generateQuantitativeData(df, name, average, max, min, deviation, decimalpoint)
  # qualitative data
  for index, text in enumerate(st.session_state["qualitativeData"]):
    name = st.session_state[f"qualitative_text_{str(index+1)}"]
    choice = st.session_state[f"qualitative_choice_{str(index+1)}"].split(',')
    weights = st.session_state[f"qualitative_weights_{str(index+1)}"].split(',')
    if name=="" or choice=="" or weights=="":
      continue
    floatWeights = []
    for value in weights:
      floatWeights.append(float(value))
    generateQualitativeData(df, name, choice, floatWeights)
  # corr of quantity
  for index, text in enumerate(st.session_state["createTendency"]):
    target_1 = st.session_state[f"tendency_target_1_{str(index+1)}"]
    target_2 = st.session_state[f"tendency_target_2_{str(index+1)}"]
    correlationCoefficient = st.session_state[f"tendency_correlation_coefficient_{str(index+1)}"]
    noise = st.session_state[f"tendency_noise_{str(index+1)}"]
    if target_1=="" or target_2=="" or correlationCoefficient=="" or noise=="":
      continue
    correlationCoefficient = float(correlationCoefficient)
    noise = float(noise)
    df[target_2] = addCorrelationToQuantity(df[target_1], df[target_2], correlationCoefficient, noise)
  # corr of qualitative
  for index, text in enumerate(st.session_state["createTendencyQualitative"]):
    target_1 = st.session_state[f"tendency_qualitative_target_1_{str(index+1)}"]
    value_1 = st.session_state[f"tendency_qualitative_value_1_{str(index+1)}"]
    target_2 = st.session_state[f"tendency_qualitative_target_2_{str(index+1)}"]
    value_2 = st.session_state[f"tendency_qualitative_value_2_{str(index+1)}"]
    weight = st.session_state[f"tendency_qualitative_weight_{str(index+1)}"]
    if target_1=="" or value_1=="" or target_2=="" or value_2=="" or weight=="":
      continue
    weight = float(weight)
    addCorrelationToQualitative(df, target_1, value_1, target_2, value_2, weight)
  # corr of qualitative and quantity
  for index, text in enumerate(st.session_state["createTendencyQuantityQualitative"]):
    target_1 = st.session_state[f"tendency_quantity_qualitative_target_1_{str(index+1)}"]
    target_2 = st.session_state[f"tendency_quantity_qualitative_target_2_{str(index+1)}"]
    correlationCoefficient = st.session_state[f"tendency_quantity_qualitative_correlation_coefficient_{str(index+1)}"]
    noise = st.session_state[f"tendency_quantity_qualitative_noise_{str(index+1)}"]
    if target_1=="" or target_2=="" or correlationCoefficient=="" or noise=="":
      continue
    correlationCoefficient = float(correlationCoefficient)
    noise = float(noise)
    addCorrelationToQuantityQualitative(target_1, target_2, correlationCoefficient, noise)
  # update table of dataframe
  updateTable(df)

# generate data button
generate_button = st.button('', key="generate data", on_click=generate, type = "primary", icon=":material/play_circle:")
st.write(df)

#
# show graph
#
# set bar graph field
if "barGraphKind" not in st.session_state:
  st.session_state["barGraphKind"] = ['']
# delete process
def deleteBarGraphField(target_no):
  if len(st.session_state["barGraphKind"]) > 1:
    new_values = []
    # save in new values
    for index, value in enumerate(st.session_state["barGraphKind"]):
      if index == len(st.session_state["barGraphKind"]):
        break
      elif index == target_no:
        continue
      new_values.append(st.session_state[f"bar_graph_target_{str(index+1)}"])
      # delete
    del st.session_state["barGraphKind"][target_no]
    # insert from new values
    for index, value in enumerate(st.session_state["barGraphKind"]):
      if index == len(st.session_state["barGraphKind"]):
        break
      st.session_state[f"bar_graph_target_{str(index+1)}"] = new_values[index]
# set text field
for index, text in enumerate(st.session_state["barGraphKind"]):
  col_1, col_2 = st.columns(2)
  with col_1:
    st.write(f"棒グラフ{index+1}")
  with col_2:
    st.text_input(
      key = f"bar_graph_target_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '質的データ',
      label_visibility= "collapsed"
    )
  name = st.session_state[f"bar_graph_target_{str(index+1)}"]
  for attribute in df.columns:
    if name==attribute:
      with st.expander("", icon=":material/bar_chart:"):
          plotBar(df[name], name)
          showQualitativeDetail(df[name])
  dele, gene = st.columns(2)
  with dele:
    delete_button = st.button("", key=f"bar_graph_delete_{str(index+1)}", on_click=deleteBarGraphField, args=(index, ), icon=":material/delete:")
  with gene:
    generate_button = st.button('', key="bar_generate_data", on_click=generate, type = "primary", icon=":material/play_circle:")

# add text field of tendency
def addBarGraphField():
  st.session_state["barGraphKind"].append('')
# set button of adding
addbarGraphButton = st.button('', key="add_bar_graph_", on_click=addBarGraphField, icon=":material/add:")



# set scatter plot field
if "scatterPlot" not in st.session_state:
  st.session_state["scatterPlot"] = ['']
# delete process
def deleteScatterPlotField(target_no):
  if len(st.session_state["scatterPlot"]) > 1:
    new_values = []
    # save in new values
    for index, value in enumerate(st.session_state["scatterPlot"]):
      if index == len(st.session_state["scatterPlot"]):
        break
      elif index == target_no:
        continue
      new_values.append(st.session_state[f"scatter_plot_target_1_{str(index+1)}"])
      new_values.append(st.session_state[f"scatter_plot_target_2_{str(index+1)}"])
      # delete
    del st.session_state["scatterPlot"][target_no]
    # insert from new values
    for index, value in enumerate(st.session_state["scatterPlot"]):
      if index == len(st.session_state["scatterPlot"]):
        break
      st.session_state[f"scatter_plot_target_1_{str(index+1)}"] = new_values[0+(index*2)]
      st.session_state[f"scatter_plot_target_2_{str(index+1)}"] = new_values[1+(index*2)]
# set text field
for index, text in enumerate(st.session_state["scatterPlot"]):
  col_1, col_2, col_3 = st.columns(3)
  with col_1:
    st.write(f"散布図{index+1}")
  with col_2:
    st.text_input(
      key = f"scatter_plot_target_1_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '量的データ1',
      label_visibility= "collapsed"
    )
  with col_3:
    st.text_input(
      key = f"scatter_plot_target_2_{str(index+1)}",
      label = '',
      value=text,
      placeholder = '量的データ2',
      label_visibility= "collapsed"
    )
  name_1 = st.session_state[f"scatter_plot_target_1_{str(index+1)}"]
  name_2 = st.session_state[f"scatter_plot_target_2_{str(index+1)}"]
  for attribute_1 in df.columns:
    if name_1==attribute_1:
      for attribute_2 in df.columns:
        if name_2==attribute_2:
          with st.expander("", icon=":material/scatter_plot:"):
              plotScatter(df[name_1], df[name_2], name_1, name_2)
              var_1, var_2, corr = calcVarAndCorr(df[name_1], df[name_2])
              var_1 = str(var_1)
              var_2 = str(var_2)
              corr = str(corr)
              st.write(name_1 + "の分散：" + var_1 + "  \n" + name_2 + "の分散：" + var_2 + "  \n" + "相関係数：" + corr)
  dele, gene = st.columns(2)
  with dele:
    delete_button = st.button("", key=f"scatter_plot_delete_{str(index+1)}", on_click=deleteScatterPlotField, args=(index, ), icon=":material/delete:")
  with gene:
    generate_button = st.button('', key="scatter_generate_data", on_click=generate, type = "primary", icon=":material/play_circle:")

# add text field of tendency
def addScatterPlotField():
  st.session_state["scatterPlot"].append('')
# set button of adding
addbarGraphButton = st.button('', key="add_scatter_plot", on_click=addScatterPlotField, icon=":material/add:")
