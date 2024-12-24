import pandas as pd
import warnings
import matplotlib.pyplot as plt
import geopandas as gpd
from mpl_toolkits.axes_grid1 import make_axes_locatable
from shapely.geometry import Point
import geopandas as gpd

# openpyxl 경고 무시
warnings.simplefilter("ignore", UserWarning)

# Load the Excel file into a pandas DataFrame
data = pd.read_excel("서울시 행정동 고령자 현황.xlsx")

# GeoJSON 파일에서 행정동 경계 데이터 불러오기
map_data = gpd.read_file("HangJeongDong_ver20230701.geojson")
gcg = map_data[map_data['sidonm'] == "서울특별시"]

# 병원 위치 데이터 불러오기 (shp 파일)
hospital_data = gpd.read_file("서울특별시 병원 정보(shp)/hsptl_info.shp")

# 좌표계 변환 (WGS84 좌표계로 변환)
hospital_data = hospital_data.to_crs(epsg=4326)

# gcg의 좌표계를 hospital_data의 좌표계로 변환
gcg = gcg.to_crs(hospital_data.crs)

# 데이터 전처리
data = data[data['동별(3)'] != '소계']
person_data = data['2022.2']
city_data = data['동별(2)']
region_data = data['동별(3)']

# '동별(2)'와 '동별(3)'를 합쳐서 'temp'라는 새로운 열을 만들지 않음
combined_column = city_data.str.cat(region_data, sep=' ')

# 두 데이터프레임을 수평으로 결합
merged_data = pd.concat([combined_column, person_data], axis=1)
merged_data = merged_data.iloc[3:].reset_index(drop=True)

# 선택한 구 (여기서 지역구를 선택해주세요)
selected_gu = '송파구'
selected_map_data = gcg[gcg['sggnm'] == selected_gu]

filtered_df_person = merged_data[merged_data['동별(2)'].str.contains(selected_gu)]
#print(filtered_df_person)

# 행정동 경계와 병원 위치 데이터를 조인
gdf_selected_gu = gpd.sjoin(selected_map_data, hospital_data, op='intersects')




# 선택한 구의 행정동 경계와 인구 데이터 병합
merged_data = pd.merge(selected_map_data, merged_data, left_on='temp', right_on='동별(2)', how='inner')

# 선택한 구에 해당하는 병원 위치만 추출
selected_hospitals = gpd.sjoin(hospital_data, selected_map_data, op='within')

kor_ft={'font':'NanumGothic'}
# 지도 생성
fig, ax = plt.subplots(figsize=(10, 10))

# GeoDataFrame의 '2022.2' 열을 기반으로 색상 매핑
selected_map_data.plot(ax=ax, color='lightgray', edgecolor='black')
merged_data.plot(column='2022.2', cmap='YlOrRd', linewidth=0.8, ax=ax, edgecolor='0.8', legend=False)

# 병원 위치 데이터 플로팅
selected_hospitals.plot(ax=ax, color='blue', markersize=10, label='Hospital Locations')

# 가로 세로의 비율을 동일하게 설정
ax.axis('equal')

# 축 숨기기
ax.axis('off')
# 그래프 제목 설정
plt.title('행정동별 인구 수와 병원 위치', fontdict=kor_ft)

# 색상 막대 그래프 생성
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1)
sm = plt.cm.ScalarMappable(cmap='YlOrRd', norm=plt.Normalize(vmin=merged_data['2022.2'].min(), vmax=merged_data['2022.2'].max()))
sm._A = []
cbar = plt.colorbar(sm, cax=cax, format="%d")

# 범례 추가
ax.legend()

# 출력
plt.show()
