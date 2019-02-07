import pandas as pd
import matplotlib.pyplot as plt
import pylab


#fie extention (_bp for Banlieue-Paris | _bb: for Banlieue-Banlieue)
fname="_bp"

#read journeys file
df_journeys = pd.read_csv('journeys'+fname+'.csv', sep=';')

metrics={
   'duration':['mean','std'],
   'walkTime':['mean', 'std'],
   'transitTime':['mean', 'std'],
   'waitingTime':['mean', 'std'],
   'walkDistance':['mean', 'std'],
   'id_journey':['count']}


df_od = df_journeys.groupby([ 'date' ],sort=False, as_index=False).agg(metrics)
df_od['walkDistance']= df_od['walkDistance'].apply(lambda x: x/10**3)
df_od['duration']= df_od['duration'].apply(lambda x: x/60)
df_od['waitingTime']= df_od['waitingTime'].apply(lambda x: x/60)
df_od['walkTime']= df_od['walkTime'].apply(lambda x: x/60)
df_od['transitTime']= df_od['transitTime'].apply(lambda x: x/60)
df_od.to_csv('stats_od'+fname+'.csv', sep=';', encoding='utf-8') #transitTime:  time duration in public transport
print("df_od",'\n',df_od.to_string())

metrics={
   'duration':['mean','std'],
   'walkTime':['mean', 'std'],
   'transitTime':['mean', 'std'],
   'waitingTime':['mean', 'std'],
   'walkDistance':['mean', 'std'],
   'id_journey':['nunique']}


# metrics for each couple of OD
df_journeys_grouped = df_journeys.groupby([ 'x_origin','y_origin', 'x_dest','y_dest' ],sort=False, as_index=False).agg(metrics)
df_journeys_grouped['walkDistance']= df_journeys_grouped['walkDistance'].apply(lambda x: x/10**3)
df_journeys_grouped['duration']= df_journeys_grouped['duration'].apply(lambda x: x/60)
df_journeys_grouped['waitingTime']= df_journeys_grouped['waitingTime'].apply(lambda x: x/60)
df_journeys_grouped['walkTime']= df_journeys_grouped['walkTime'].apply(lambda x: x/60)
df_journeys_grouped['transitTime']= df_journeys_grouped['transitTime'].apply(lambda x: x/60)
df_journeys_grouped.to_csv('stats_journeys'+fname+'.csv', sep=';', encoding='utf-8')
print("df_journeys_grouped",'\n',df_journeys_grouped.to_string())


#read the legs file
df_legs = pd.read_csv('legs'+fname+'.csv', sep=';',encoding='windows-1252')

# metrics per journey and mode for each couple of OD
df_legs_grouped_by_journeys = df_legs.groupby(['x_origin','y_origin','x_dest','y_dest','id_journey','legMode'],sort=False, as_index=False).agg({'legDistance':'sum', 'legDuration':'sum' ,'transitLeg':{lambda x:(x==True).sum()}})
df_legs_grouped_by_journeys['legDistance']= df_legs_grouped_by_journeys['legDistance'].apply(lambda x: x/10**3)
df_legs_grouped_by_journeys['legDuration']= df_legs_grouped_by_journeys['legDuration'].apply(lambda x: x/60)
df_legs_grouped_by_journeys .to_csv('stats_legs_by_journeys'+fname+'.csv', sep=';', encoding='utf-8')
df_legs_grouped_by_journeys.columns = df_legs_grouped_by_journeys.columns.droplevel(1)
print("df_legs_grouped_by_journeys",'\n',df_legs_grouped_by_journeys.to_string())


metrics={ 'legDistance':['mean','std'], 'legDuration':['mean','std'],'transitLeg':['median','std']}
# metrics per mode for each couple of OD
df_legs_grouped = df_legs_grouped_by_journeys.groupby(['x_origin','y_origin','x_dest','y_dest','legMode'],sort=False, as_index=False).agg(metrics)
df_legs_grouped.to_csv('stats_legs'+fname+'.csv', sep=';', encoding='utf-8')
print("df_legs_grouped",'\n',df_legs_grouped.to_string())


# metrics per mode for the whole OD per mode
df_legs_grouped__by_mode = df_legs_grouped_by_journeys.groupby(['legMode'],sort=False, as_index=False).agg(metrics)
df_legs_grouped__by_mode.to_csv('stats_modes'+fname+'.csv', sep=';', encoding='utf-8')
print("df_legs_grouped__by_mode",'\n',df_legs_grouped__by_mode.to_string())
print(df_legs_grouped_by_journeys.groupby(['legDistance'],sort=False, as_index=False))




# plot the travel distance
data_car = df_legs_grouped_by_journeys.loc[df_legs_grouped_by_journeys['legMode'] == 'CAR', 'legDistance']
data_bus = df_legs_grouped_by_journeys.loc[df_legs_grouped_by_journeys['legMode'] == 'BUS', 'legDistance']
data_rail = df_legs_grouped_by_journeys.loc[df_legs_grouped_by_journeys['legMode'] == 'RAIL', 'legDistance']
data_subway = df_legs_grouped_by_journeys.loc[df_legs_grouped_by_journeys['legMode'] == 'SUBWAY', 'legDistance']
data_walk = df_legs_grouped_by_journeys.loc[df_legs_grouped_by_journeys['legMode'] == 'WALK', 'legDistance']
BoxName = ['CAR','BUS','RAIL','SUBWAY','WALK']
plt.title('Travel distance per mode', fontsize=14)
plt.boxplot([data_car,data_bus,data_rail,data_subway,data_walk])
plt.xlabel('Modes')
plt.ylabel('Distance')
pylab.xticks([1,2,3,4,5], BoxName)
plt.savefig('distance_modes'+fname+'.png')
plt.show()


# plot the travel duration
data_car = df_legs_grouped_by_journeys.loc[df_legs_grouped_by_journeys['legMode'] == 'CAR', 'legDuration']
data_bus = df_legs_grouped_by_journeys.loc[df_legs_grouped_by_journeys['legMode'] == 'BUS', 'legDuration']
data_rail = df_legs_grouped_by_journeys.loc[df_legs_grouped_by_journeys['legMode'] == 'RAIL', 'legDuration']
data_subway = df_legs_grouped_by_journeys.loc[df_legs_grouped_by_journeys['legMode'] == 'SUBWAY', 'legDuration']
data_walk = df_legs_grouped_by_journeys.loc[df_legs_grouped_by_journeys['legMode'] == 'WALK', 'legDuration']
BoxName = ['CAR','BUS','RAIL','SUBWAY','WALK']
plt.title('Travel time per mode', fontsize=14)
plt.boxplot([data_car,data_bus,data_rail,data_subway,data_walk])
plt.xlabel('Modes')
plt.ylabel('Duartion')
pylab.xticks([1,2,3,4,5], BoxName)
plt.savefig('duration_modes'+fname+'.png')
plt.show()


# plot the transit
data_car = df_legs_grouped_by_journeys.loc[df_legs_grouped_by_journeys['legMode'] == 'CAR', 'transitLeg']
data_bus = df_legs_grouped_by_journeys.loc[df_legs_grouped_by_journeys['legMode'] == 'BUS', 'transitLeg']
data_rail = df_legs_grouped_by_journeys.loc[df_legs_grouped_by_journeys['legMode'] == 'RAIL', 'transitLeg']
data_subway = df_legs_grouped_by_journeys.loc[df_legs_grouped_by_journeys['legMode'] == 'SUBWAY', 'transitLeg']
data_walk = df_legs_grouped_by_journeys.loc[df_legs_grouped_by_journeys['legMode'] == 'WALK', 'transitLeg']
BoxName = ['CAR','BUS','RAIL','SUBWAY','WALK']
plt.title('Transit per mode', fontsize=14)
plt.boxplot([data_car,data_bus,data_rail,data_subway,data_walk])

plt.xlabel('Modes')
plt.ylabel('Transit')

pylab.xticks([1,2,3,4,5], BoxName)
plt.savefig('transit_modes'+fname+'.png')
plt.show()

