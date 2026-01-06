# config/product_groups.py
"""
상품 그룹화 설정
- 비슷한 상품들을 하나의 대표 상품으로 그룹화
- 나중에 필요할 때 사용하기 위해 보관
"""

# 그룹 정의: 대표 product_id -> 그룹에 포함될 모든 product_id 리스트
PRODUCT_GROUPS = {
    15: [6, 7, 12, 14, 15, 13],
    40: [28, 40, 45],
    10: [9, 10],
    34: [29, 34, 35, 36, 44],
    5: [3, 5],
    42: [24, 31, 42, 8, 25],
    26: [17, 20, 46, 22, 23, 26, 43],
    32: [11, 16, 21, 32],
    38: [30, 33, 37, 38, 41],
    39: [27, 39]
}

# 제외할 상품 ID (그룹화하지 않고 목록에서도 제외)
EXCLUDED_PRODUCTS = [1, 18, 19]

# product_id -> 대표 product_id 역방향 매핑 (자동 생성)
PRODUCT_TO_REPRESENTATIVE = {}
for representative_id, product_ids in PRODUCT_GROUPS.items():
    for product_id in product_ids:
        PRODUCT_TO_REPRESENTATIVE[product_id] = representative_id


def get_representative_product_id(product_id: int) -> int:
    """
    상품 ID에 해당하는 대표 상품 ID 반환
    
    Args:
        product_id: 조회할 상품 ID
        
    Returns:
        대표 상품 ID (그룹이 없으면 자기 자신)
    """
    if product_id in EXCLUDED_PRODUCTS:
        return None
    return PRODUCT_TO_REPRESENTATIVE.get(product_id, product_id)


def get_group_product_ids(product_id: int) -> list[int]:
    """
    상품 ID가 속한 그룹의 모든 상품 ID 반환
    
    Args:
        product_id: 조회할 상품 ID
        
    Returns:
        그룹에 속한 모든 상품 ID 리스트
    """
    if product_id in EXCLUDED_PRODUCTS:
        return []
    
    representative_id = get_representative_product_id(product_id)
    return PRODUCT_GROUPS.get(representative_id, [product_id])


def get_all_representative_ids() -> list[int]:
    """
    모든 대표 상품 ID 반환 (그룹 리더들)
    
    Returns:
        대표 상품 ID 리스트
    """
    return list(PRODUCT_GROUPS.keys())


def is_excluded(product_id: int) -> bool:
    """
    제외 대상 상품인지 확인
    
    Args:
        product_id: 확인할 상품 ID
        
    Returns:
        제외 대상이면 True
    """
    return product_id in EXCLUDED_PRODUCTS


def filter_excluded_products(product_ids: list[int]) -> list[int]:
    """
    제외 대상 상품을 필터링
    
    Args:
        product_ids: 상품 ID 리스트
        
    Returns:
        제외 대상을 제외한 상품 ID 리스트
    """
    return [pid for pid in product_ids if pid not in EXCLUDED_PRODUCTS]

