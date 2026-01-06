"""
고객 분석 API - 전체 데이터 조회 예제

이 스크립트는 고객 분석 API의 전체 데이터 조회 기능을 시연합니다.
"""

import requests
import json
from typing import Optional, Dict, List


class MemberAnalysisClient:
    """고객 분석 API 클라이언트"""
    
    def __init__(self, base_url: str, access_token: str):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_all_members(
        self, 
        grade: Optional[str] = None,
        sort_by: str = "latest_purchase",
        order: str = "desc",
        site_id: int = 1
    ) -> Dict:
        """
        전체 고객 데이터 조회 (limit=0)
        
        Args:
            grade: 등급 필터 (VIP, PLATINUM, GOLD 등)
            sort_by: 정렬 기준 (latest_purchase, purchase_count, points, name)
            order: 정렬 순서 (desc, asc)
            site_id: 사이트 ID
            
        Returns:
            전체 고객 데이터
        """
        url = f'{self.base_url}/api/v1/member-analysis/members'
        params = {
            'limit': 0,  # 전체 데이터 조회
            'sort_by': sort_by,
            'order': order,
            'site_id': site_id
        }
        
        if grade:
            params['grade'] = grade
        
        print(f"🔍 전체 고객 조회 중...")
        if grade:
            print(f"   필터: {grade} 등급")
        print(f"   정렬: {sort_by} ({order})")
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # 결과 요약 출력
        print(f"\n✅ 조회 완료!")
        print(f"   전체 고객 수: {data['total_count']:,}명")
        print(f"   반환된 데이터: {len(data['members']):,}명")
        print(f"   페이지: {data['page']}, 한계: {data['limit']}")
        
        # 10,000개 제한 경고
        if data['total_count'] > 10000:
            print(f"\n⚠️  경고: 전체 {data['total_count']:,}명 중 10,000명만 반환되었습니다.")
            print(f"   전체 데이터가 필요한 경우 페이지네이션을 사용하세요.")
        
        return data
    
    def get_members_paginated(
        self,
        page: int = 1,
        limit: int = 20,
        grade: Optional[str] = None,
        sort_by: str = "latest_purchase",
        order: str = "desc",
        site_id: int = 1
    ) -> Dict:
        """
        페이지네이션 방식으로 고객 조회
        
        Args:
            page: 페이지 번호
            limit: 페이지당 항목 수 (1~100)
            grade: 등급 필터
            sort_by: 정렬 기준
            order: 정렬 순서
            site_id: 사이트 ID
            
        Returns:
            페이지 단위 고객 데이터
        """
        url = f'{self.base_url}/api/v1/member-analysis/members'
        params = {
            'page': page,
            'limit': limit,
            'sort_by': sort_by,
            'order': order,
            'site_id': site_id
        }
        
        if grade:
            params['grade'] = grade
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def print_member_summary(self, members: List[Dict], top_n: int = 10):
        """고객 정보 요약 출력"""
        print(f"\n📊 상위 {min(top_n, len(members))}명 고객 정보:")
        print("-" * 80)
        print(f"{'순위':<6} {'고객ID':<15} {'등급':<12} {'구매횟수':<10} {'포인트':<15} {'최근구매일'}")
        print("-" * 80)
        
        for idx, member in enumerate(members[:top_n], 1):
            print(
                f"{idx:<6} "
                f"{member['member_id']:<15} "
                f"{member['grade']:<12} "
                f"{member['purchase_count']:<10} "
                f"{member['available_points']:>12,}P  "
                f"{member['last_purchase'] or '-'}"
            )
        
        if len(members) > top_n:
            print(f"\n... 외 {len(members) - top_n:,}명")
    
    def export_to_csv(self, members: List[Dict], filename: str = "members.csv"):
        """CSV 파일로 내보내기"""
        import csv
        
        if not members:
            print("❌ 내보낼 데이터가 없습니다.")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=members[0].keys())
            writer.writeheader()
            writer.writerows(members)
        
        print(f"\n💾 {len(members):,}개 데이터를 '{filename}'로 내보냈습니다.")


def main():
    """메인 실행 함수"""
    
    # 설정 (실제 값으로 변경 필요)
    BASE_URL = "http://localhost:8000"
    ACCESS_TOKEN = "your_access_token_here"
    
    # 클라이언트 생성
    client = MemberAnalysisClient(BASE_URL, ACCESS_TOKEN)
    
    try:
        print("=" * 80)
        print("고객 분석 API - 전체 데이터 조회 예제")
        print("=" * 80)
        
        # 예제 1: 전체 고객 조회
        print("\n\n[ 예제 1: 전체 고객 조회 (포인트 높은 순) ]")
        all_data = client.get_all_members(
            sort_by="points",
            order="desc"
        )
        client.print_member_summary(all_data['members'], top_n=10)
        
        # 예제 2: VIP 등급 전체 조회
        print("\n\n[ 예제 2: VIP 등급 전체 조회 ]")
        vip_data = client.get_all_members(
            grade="VIP",
            sort_by="purchase_count",
            order="desc"
        )
        client.print_member_summary(vip_data['members'], top_n=5)
        
        # 예제 3: 등급별 통계
        print("\n\n[ 예제 3: 등급별 통계 ]")
        grade_stats = {}
        for member in all_data['members']:
            grade = member['grade']
            grade_stats[grade] = grade_stats.get(grade, 0) + 1
        
        print("\n등급별 고객 수:")
        for grade, count in sorted(grade_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(all_data['members']) * 100)
            print(f"  {grade}: {count:,}명 ({percentage:.1f}%)")
        
        # 예제 4: CSV 내보내기 (선택사항)
        export = input("\n\nCSV 파일로 내보내시겠습니까? (y/n): ")
        if export.lower() == 'y':
            client.export_to_csv(all_data['members'], "all_members.csv")
        
        print("\n✅ 모든 예제 실행 완료!")
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP 에러 발생: {e}")
        print(f"   상태 코드: {e.response.status_code}")
        try:
            error_detail = e.response.json()
            print(f"   상세: {error_detail}")
        except:
            pass
    
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")


if __name__ == "__main__":
    main()


