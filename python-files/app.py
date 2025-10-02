"""
YouTube Shorts Finder - 48시간 내 웃긴 영상 Top 30
실행: streamlit run app.py
설치: pip install streamlit requests pandas
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="웃긴 YouTube Shorts", page_icon="😂", layout="wide")

# 제목
st.title("😂 48시간 내 웃긴 YouTube Shorts Top 30")

# API 키 입력
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''

api_key = st.text_input(
    "YouTube Data API v3 Key",
    value=st.session_state.api_key,
    type="password",
    help="Google Cloud Console에서 발급받은 API 키를 입력하세요"
)
st.session_state.api_key = api_key

# 국가 선택
country_options = {
    "한국 (KR)": "KR",
    "미국 (US)": "US",
    "일본 (JP)": "JP",
    "캐나다 (CA)": "CA",
    "인도네시아 (ID)": "ID"
}
selected_country = st.selectbox("국가 선택", list(country_options.keys()))
region_code = country_options[selected_country]

# 검색 버튼
search_button = st.button("🔍 검색", type="primary")


def get_published_after():
    """48시간 전 시간을 ISO 8601 형식으로 반환"""
    time_48h_ago = datetime.utcnow() - timedelta(hours=48)
    return time_48h_ago.strftime('%Y-%m-%dT%H:%M:%SZ')


def search_shorts(api_key, region_code, published_after):
    """YouTube Shorts 검색"""
    search_url = "https://www.googleapis.com/youtube/v3/search"
    
    # 검색 쿼리: 영어/한국어 혼합
    query = "funny shorts OR 웃긴 쇼츠"
    
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'videoDuration': 'short',
        'publishedAfter': published_after,
        'order': 'viewCount',
        'regionCode': region_code,
        'maxResults': 50,
        'key': api_key
    }
    
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API 호출 오류: {str(e)}")
        return None


def get_video_details(api_key, video_ids):
    """비디오 상세 정보 조회"""
    videos_url = "https://www.googleapis.com/youtube/v3/videos"
    
    params = {
        'part': 'snippet,statistics',
        'id': ','.join(video_ids),
        'key': api_key
    }
    
    try:
        response = requests.get(videos_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ 상세 정보 조회 오류: {str(e)}")
        return None


def format_view_count(count):
    """조회수 포맷 (1,234 형식)"""
    return f"{int(count):,}"


def parse_videos(search_data, details_data):
    """비디오 데이터 파싱"""
    videos = []
    
    for item in details_data.get('items', []):
        video_id = item['id']
        snippet = item['snippet']
        statistics = item.get('statistics', {})
        
        videos.append({
            '제목': snippet['title'],
            '채널명': snippet['channelTitle'],
            '조회수': int(statistics.get('viewCount', 0)),
            '조회수_표시': format_view_count(statistics.get('viewCount', 0)),
            '업로드 시간': snippet['publishedAt'][:10] + ' ' + snippet['publishedAt'][11:19],
            '썸네일 URL': snippet['thumbnails']['high']['url'],
            'YouTube 링크': f"https://www.youtube.com/watch?v={video_id}"
        })
    
    return videos


# 검색 실행
if search_button:
    if not api_key or api_key == 'YOUR_API_KEY':
        st.warning("⚠️ API 키를 입력해주세요.")
    else:
        with st.spinner('🔎 검색 중...'):
            published_after = get_published_after()
            search_results = search_shorts(api_key, region_code, published_after)
            
            if search_results and 'items' in search_results:
                video_ids = [item['id']['videoId'] for item in search_results['items']]
                
                if video_ids:
                    video_details = get_video_details(api_key, video_ids)
                    
                    if video_details and 'items' in video_details:
                        videos = parse_videos(search_results, video_details)
                        
                        if videos:
                            df = pd.DataFrame(videos)
                            df = df.sort_values('조회수', ascending=False).head(30)
                            df = df.reset_index(drop=True)
                            df.index = df.index + 1
                            
                            st.success(f"✅ {len(df)}개의 결과를 찾았습니다!")
                            
                            display_df = df[['제목', '채널명', '조회수_표시', '업로드 시간', 'YouTube 링크']]
                            display_df.columns = ['제목', '채널명', '조회수', '업로드 시간', 'YouTube 링크']
                            st.dataframe(display_df, use_container_width=True)
                            
                            show_thumbnails = st.checkbox("🖼️ 썸네일 그리드 보기")
                            
                            if show_thumbnails:
                                st.subheader("썸네일 미리보기")
                                cols = st.columns(3)
                                for idx, row in df.iterrows():
                                    col_idx = (idx - 1) % 3
                                    with cols[col_idx]:
                                        st.image(row['썸네일 URL'], use_container_width=True)
                                        st.markdown(f"**{idx}. {row['제목'][:50]}...**")
                                        st.markdown(f"👁️ {row['조회수_표시']} | 📺 {row['채널명']}")
                                        st.markdown(f"[▶️ 시청하기]({row['YouTube 링크']})")
                                        st.divider()
                        else:
                            st.warning("⚠️ 데이터가 없습니다.")
                    else:
                        st.error("❌ 비디오 상세 정보를 가져올 수 없습니다.")
                else:
                    st.warning("⚠️ 검색 결과가 없습니다.")
            else:
                st.warning("⚠️ 검색 결과가 없습니다. 다른 국가를 선택해보세요.")

# 사이드바
st.sidebar.header("📖 사용 가이드")
st.sidebar.markdown("""
### API 키 발급
1. Google Cloud Console 접속
2. 프로젝트 생성
3. YouTube Data API v3 활성화
4. API 키 생성
""")