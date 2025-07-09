# 2025_07_01 지도 by.VIVA

# 지도 시각화를 위한 folium 라이브러리와 pandas 라이브러리를 사용.
import folium
from folium.plugins import HeatMap, MarkerCluster
import pandas as pd

# 엑셀 파일 읽기
df = pd.read_excel('학교주소좌표.xlsx')
print("엑셀 파일을 불러옵니다.")
print(f"총 {len(df)}개의 학교 데이터가 있습니다.")

# 전체 데이터를 리스트로 변환
data_list = df.values.tolist()
print("엑셀 데이터를 리스트로 변환합니다.")

# 특정 컬럼을 리스트로 변환
school_names = df['학교명'].tolist()
school_address = df['주소'].tolist()
longitudes = df['경도'].tolist()
latitudes = df['위도'].tolist()

print("컬럼을 리스트로 변환 완료!")

# # 변환된 리스트 형식 확인?
# for i in range(len(data_list)):
#     print(data_list[i])

# 결측치 제거하고 유효한 좌표 데이터만 필터링
valid_data = []
for i in range(len(latitudes)):
    if latitudes[i] != 0 and longitudes[i] != 0:
        valid_data.append([latitudes[i], longitudes[i]])

print(f"유효한 좌표 데이터: {len(valid_data)}개")

# 기본 지도 생성 (한국 중심)
map_kr = folium.Map(
    location=[36.5, 127.5],  # 위도, 경도
    zoom_start=7,
    tiles='OpenStreetMap'
)
print("기본 지도를 생성합니다.")

# 히트맵 생성
print("히트맵을 생성합니다.")
heat_data = [[lat, lng, 1] for lat, lng in valid_data]

heatmap = HeatMap(
    heat_data,
    name='학교 분포 히트맵',
    min_opacity=0.5,
    max_zoom=12,  # 확대 레벨 10까지만 히트맵 표시
    radius=20,
    blur=10,
    gradient={
        0.001: 'blue',
        0.4: 'cyan', 
        0.6: 'lime',
        0.8: 'yellow',
        1.0: 'red'
    }
)
heatmap.add_to(map_kr)
print("히트맵이 생성되었습니다.")

# 마커 클러스터 생성
print("마커 클러스터를 생성합니다.")
marker_cluster = MarkerCluster(
    name='개별 학교 마커',
    overlay=True,
    control=True
)

# 마커 클러스터에 학교 마커 추가
print("학교 마커를 클러스터에 추가합니다.")
for i in range(len(school_names)):
    if latitudes[i] == 0 or longitudes[i] == 0:  # 위도나 경도가 0인 경우 건너뜀
        print(f"건너뜀: {school_names[i]} (위도: {latitudes[i]}, 경도: {longitudes[i]})")
        continue
    else:
        folium.Marker(
            [latitudes[i], longitudes[i]],
            popup=school_names[i],
            tooltip=school_names[i]
        ).add_to(marker_cluster)

# 마커 클러스터를 지도에 추가
print("마커 클러스터를 지도에 추가합니다.")
marker_cluster.add_to(map_kr)
print(f"마커들을 클러스터에 추가하고 지도에 연결했습니다.")

# 🆕 줌 레벨에 따른 마커 표시/숨김 JavaScript 추가
zoom_control_js = '''
<script>
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        // 지도 객체 찾기
        var mapFound = false;
        for (let key in window) {
            if (key.includes('map_') && window[key] && window[key].getZoom) {
                var leafletMap = window[key];
                mapFound = true;
                
                // 마커 클러스터 그룹 찾기
                var markerLayer = null;
                leafletMap.eachLayer(function(layer) {
                    if (layer instanceof L.MarkerClusterGroup) {
                        markerLayer = layer;
                    }
                });
                
                // 줌 레벨에 따른 마커 표시/숨김 함수
                function toggleMarkersBasedOnZoom() {
                    var currentZoom = leafletMap.getZoom();
                    
                    if (markerLayer) {
                        if (currentZoom <= 10) {
                            // 줌 10 이하: 마커 숨김
                            if (leafletMap.hasLayer(markerLayer)) {
                                leafletMap.removeLayer(markerLayer);
                            }
                            console.log('줌', currentZoom, '- 마커 숨김, 히트맵 표시');
                        } else {
                            // 줌 11 이상: 마커 표시
                            if (!leafletMap.hasLayer(markerLayer)) {
                                leafletMap.addLayer(markerLayer);
                            }
                            console.log('줌', currentZoom, '- 마커 표시');
                        }
                    }
                }
                
                // 줌 이벤트 리스너
                leafletMap.on('zoomend', toggleMarkersBasedOnZoom);
                leafletMap.on('zoom', toggleMarkersBasedOnZoom);
                
                // 초기 실행
                toggleMarkersBasedOnZoom();
                
                break;
            }
        }
    }, 1500);
});
</script>
'''

# 줌 제어 스크립트 추가
map_kr.get_root().html.add_child(folium.Element(zoom_control_js))

# 🆕 실시간 줌 레벨 표시 UI 추가 (수정된 버전)
zoom_ui_html = f'''
<div id="zoom-display" style="
    position: fixed;
    top: 10px;
    left: 10px;
    background: rgba(255, 255, 255, 0.95);
    border: 2px solid #333;
    border-radius: 8px;
    padding: 12px 16px;
    font-family: 'Arial', sans-serif;
    font-weight: bold;
    font-size: 16px;
    color: #333;
    z-index: 1000;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    min-width: 120px;
    text-align: center;
">
    <div style="font-size: 12px; color: #666; margin-bottom: 4px;">🔍 줌 레벨</div>
    <div id="zoom-level" style="font-size: 24px; color: #2196F3; font-weight: bold;">7</div>
    <div id="zoom-status" style="font-size: 11px; color: #888; margin-top: 4px; font-weight: normal;">히트맵 모드</div>
</div>

<script>
// DOM이 로드된 후 실행
document.addEventListener('DOMContentLoaded', function() {{
    // 잠시 후 지도 객체 찾기 (지도 생성 완료 대기)
    setTimeout(function() {{
        // 모든 Leaflet 지도 찾기
        var mapFound = false;
        
        // window 객체에서 지도 찾기
        for (let key in window) {{
            if (key.includes('map_') && window[key] && window[key].getZoom) {{
                var leafletMap = window[key];
                mapFound = true;
                console.log('지도 객체 발견:', key);
                
                // 줌 레벨 업데이트 함수
                function updateZoomDisplay() {{
                    try {{
                        var currentZoom = leafletMap.getZoom();
                        var zoomElement = document.getElementById('zoom-level');
                        var statusElement = document.getElementById('zoom-status');
                        
                        if (zoomElement) {{
                            zoomElement.textContent = currentZoom;
                        }}
                        
                        var statusText = '';
                        var statusColor = '';
                        
                        if (currentZoom <= 6) {{
                            statusText = '🌍 전국 뷰';
                            statusColor = '#4CAF50';
                        }} else if (currentZoom <= 8) {{
                            statusText = '🏙️ 지역 뷰';
                            statusColor = '#FF9800';
                        }} else if (currentZoom <= 10) {{
                            statusText = '🔥 히트맵 모드';
                            statusColor = '#2196F3';
                        }} else if (currentZoom <= 13) {{
                            statusText = '📌 마커 모드';
                            statusColor = '#E91E63';
                        }} else {{
                            statusText = '🔍 상세 뷰';
                            statusColor = '#9C27B0';
                        }}
                        
                        if (statusElement) {{
                            statusElement.textContent = statusText;
                            statusElement.style.color = statusColor;
                        }}
                        
                        console.log('줌 레벨 업데이트:', currentZoom, statusText);
                    }} catch (e) {{
                        console.error('줌 레벨 업데이트 오류:', e);
                    }}
                }}
                
                // 줌 이벤트 리스너 추가
                leafletMap.on('zoomstart', function() {{
                    console.log('줌 시작');
                }});
                
                leafletMap.on('zoomend', function() {{
                    console.log('줌 끝');
                    updateZoomDisplay();
                }});
                
                leafletMap.on('zoom', function() {{
                    updateZoomDisplay();
                }});
                
                // 초기 줌 레벨 표시
                updateZoomDisplay();
                
                break;
            }}
        }}
        
        // 지도를 못 찾은 경우 다른 방법 시도
        if (!mapFound) {{
            console.log('window에서 지도 못 찾음, 다른 방법 시도...');
            
            // Leaflet의 전역 지도 컨테이너에서 찾기
            var mapContainers = document.querySelectorAll('.folium-map');
            if (mapContainers.length > 0) {{
                var mapId = mapContainers[0].id;
                if (window[mapId] && window[mapId].getZoom) {{
                    var leafletMap = window[mapId];
                    console.log('컨테이너에서 지도 발견:', mapId);
                    
                    function updateZoomDisplay() {{
                        var currentZoom = leafletMap.getZoom();
                        document.getElementById('zoom-level').textContent = currentZoom;
                        
                        var statusText = currentZoom <= 6 ? '🌍 전국 뷰' :
                                       currentZoom <= 8 ? '🏙️ 지역 뷰' :
                                       currentZoom <= 10 ? '🔥 히트맵 모드' :
                                       currentZoom <= 13 ? '📌 마커 모드' : '🔍 상세 뷰';
                        
                        document.getElementById('zoom-status').textContent = statusText;
                        console.log('줌 레벨:', currentZoom);
                    }}
                    
                    leafletMap.on('zoomend', updateZoomDisplay);
                    leafletMap.on('zoom', updateZoomDisplay);
                    updateZoomDisplay();
                }}
            }}
        }}
    }}, 1000); // 1초 대기 후 실행
}});
</script>
'''

# 줌 UI를 지도에 추가
map_kr.get_root().html.add_child(folium.Element(zoom_ui_html))

# 추가 정보 패널
info_panel_html = '''
<div style="
    position: fixed;
    bottom: 10px;
    left: 10px;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 10px;
    border-radius: 5px;
    font-family: Arial, sans-serif;
    font-size: 12px;
    z-index: 1000;
    max-width: 300px;
">
    <div style="font-weight: bold; margin-bottom: 5px;">📍 지도 가이드</div>
    <div>🔍 줌 1-6: 전국 뷰</div>
    <div>🏙️ 줌 7-8: 지역 뷰</div>
    <div>🔥 줌 9-10: 히트맵 활성</div>
    <div>📌 줌 11+: 개별 마커 표시</div>
</div>
'''

map_kr.get_root().html.add_child(folium.Element(info_panel_html))

# HTML 파일로 저장
map_kr.save('kr_school_map.html')
print("지도를 HTML 파일로 저장합니다")