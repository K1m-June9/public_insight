import logging
import networkx as nx
from typing import Dict, List, Tuple
from neo4j import AsyncDriver
from node2vec import Node2Vec
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# FastAPI 서버가 시작될 때 한번만 로드하여 메모리에 유지하기 위함.
NODE_EMBEDDINGS: Dict[str, np.ndarray] | None = None

async def fetch_graph_data_from_neo4j(driver: AsyncDriver) -> nx.Graph:
    """
    Neo4j에 연결하여 모든 노드와 관계를 가져와 NetworkX 그래프를 생성함.

    이 함수는 우리 ML 파이프라인 전체의 시작점임.
    """
    logger.info("NetworkX 그래프 생성을 위해 Neo4j에서 그래프 데이터 가져오는 중...")
    
    # 이 쿼리는 그래프의 모든 관계를 가져옴.
    # 관계를 가져옴으로써, 관계에 포함된 모든 노드 정보도 자연스럽게 얻을 수 있음.
    cypher_query = """
    MATCH (n)-[r]->(m)
    RETURN n.id AS source_id, labels(n)[0] AS source_label, 
           m.id AS target_id, labels(m)[0] AS target_label,
           type(r) AS relationship_type
    """
    
    # Node2Vec을 위해, 단순하고 방향성이 없는 그래프를 사용할 것임.
    # 다양한 종류의 관계들은 모두 동일한 '연결'로 취급함.
    G = nx.Graph()

    try:
        async with driver.session() as session:
            result = await session.run(cypher_query)
            # 비동기 결과를 처리하는 가장 효율적인 방식
            records = [record.data() async for record in result]

        for record in records:
            # 프론트엔드에서 했던 것과 동일하게, 노드 타입별로 고유한 ID를 생성
            source_id = f"{record['source_label'].lower()}_{record['source_id']}"
            target_id = f"{record['target_label'].lower()}_{record['target_id']}"

            # 노드 추가 (NetworkX는 중복된 노드를 알아서 처리함)
            G.add_node(source_id, label=record['source_label'])
            G.add_node(target_id, label=record['target_label'])
            
            # 두 노드를 잇는 엣지(관계) 추가
            G.add_edge(source_id, target_id)

        logger.info(f"NetworkX 그래프 생성 성공. 노드: {G.number_of_nodes()}개, 엣지: {G.number_of_edges()}개.")
        return G

    except Exception as e:
        logger.error(f"Neo4j에서 그래프 데이터를 가져오거나 생성하는 데 실패함: {e}", exc_info=True)
        # 실패 시, 빈 그래프를 반환하여 파이프라인이 멈추지 않도록 함.
        return nx.Graph()
    
def train_and_save_node2vec_model(
    graph: nx.Graph, 
    save_path: str,
    dimensions: int = 64,  # 각 노드를 표현할 벡터의 차원 수 (숫자의 개수)
    walk_length: int = 30, # 랜덤 워크가 한 번에 움직이는 걸음 수
    num_walks: int = 100,  # 각 노드에서 랜덤 워크를 시작하는 횟수
    workers: int = 4       # 학습에 사용할 CPU 코어 수
) -> Dict[str, list[float]]:
    """
    주어진 NetworkX 그래프로 Node2Vec 모델을 학습시키고,
    학습된 노드 임베딩(벡터)을 파일에 저장함.

    :param graph: 학습에 사용할 NetworkX 그래프 객체.
    :param save_path: 학습된 임베딩 결과를 저장할 파일 경로.
    :return: {'node_id': [vector], ...} 형태의 딕셔너리.
    """
    if not graph.nodes():
        logger.warning("학습할 노드가 없는 빈 그래프이므로, 모델 학습을 건너뜀.")
        return {}

    logger.info(f"Node2Vec 모델 학습 시작... (노드: {len(graph.nodes())}개)")
    
    # 1. Node2Vec 모델 객체 생성 및 설정
    #    p, q는 랜덤 워크의 행동을 제어하는 파라미터 (보통 기본값 1을 사용)
    node2vec = Node2Vec(
        graph, 
        dimensions=dimensions, 
        walk_length=walk_length, 
        num_walks=num_walks, 
        workers=workers,
        quiet=True # 학습 과정 로그를 숨김
    )

    # 2. 모델 학습 (가장 많은 시간이 소요되는 부분)
    #    Word2Vec 모델을 사용하여 그래프 구조를 학습함.
    #    window: 주변 몇 개의 노드까지를 '문맥'으로 볼 것인가
    #    min_count: 최소 등장 횟수 (1은 모든 노드를 고려)
    #    batch_words: 한 번에 처리할 단어(노드) 수
    model = node2vec.fit(window=10, min_count=1, batch_words=4)
    logger.info("Node2Vec 모델 학습 완료.")

    # 3. 학습된 임베딩(벡터) 추출
    #    model.wv는 학습된 모든 노드의 벡터를 담고 있는 객체임.
    embeddings = {node_id: model.wv[node_id].tolist() for node_id in model.wv.index_to_key}
    
    # 4. 결과를 파일로 저장 (pickle 포맷)
    #    'wb'는 'write binary'의 약자로, 바이너리 쓰기 모드를 의미함.
    try:
        with open(save_path, 'wb') as f:
            pickle.dump(embeddings, f)
        logger.info(f"학습된 노드 임베딩을 '{save_path}' 파일에 성공적으로 저장함.")
    except Exception as e:
        logger.error(f"임베딩 파일 저장 실패: {e}", exc_info=True)

    return embeddings

def load_node_embeddings(load_path: str) -> bool:
    """
    파일에 저장된 노드 임베딩을 로드하여 전역 변수에 저장함.
    - FastAPI 앱 시작 시 한번만 호출될 함수.
    """
    global NODE_EMBEDDINGS
    try:
        with open(load_path, 'rb') as f:
            # Pickle 파일에서 딕셔너리를 로드
            loaded_embeddings = pickle.load(f)
            # 유사도 계산을 위해 리스트 값을 NumPy 배열로 변환
            NODE_EMBEDDINGS = {node_id: np.array(vector) for node_id, vector in loaded_embeddings.items()}
        logger.info(f"'{load_path}'에서 {len(NODE_EMBEDDINGS)}개의 노드 임베딩을 성공적으로 로드함.")
        return True
    except FileNotFoundError:
        logger.warning(f"임베딩 파일('{load_path}')을 찾을 수 없음. 예측 기능을 사용할 수 없음.")
        NODE_EMBEDDINGS = None
        return False
    except Exception as e:
        logger.error(f"임베딩 파일 로드 실패: {e}", exc_info=True)
        NODE_EMBEDDINGS = None
        return False


def predict_similar_nodes(
    start_node_id: str,
    top_n: int = 20,
    exclude_ids: set[str] = None
) -> List[Tuple[str, float]]:
    """
    주어진 노드와 가장 유사한 노드들을 예측하여 반환함.
    - 미리 로드된 NODE_EMBEDDINGS를 사용하여 실시간으로 계산.
    """
    if NODE_EMBEDDINGS is None:
        logger.warning("노드 임베딩이 로드되지 않아 예측을 수행할 수 없음.")
        return []
    
    if start_node_id not in NODE_EMBEDDINGS:
        logger.warning(f"입력된 노드 ID('{start_node_id}')에 대한 임베딩을 찾을 수 없음.")
        return []
        
    start_vector = NODE_EMBEDDINGS[start_node_id].reshape(1, -1)
    
    # 전체 노드 목록과 벡터 준비
    node_ids = list(NODE_EMBEDDINGS.keys())
    all_vectors = np.array(list(NODE_EMBEDDINGS.values()))
    
    # 코사인 유사도 계산
    similarities = cosine_similarity(start_vector, all_vectors)[0]
    
    # 결과를 (node_id, similarity) 튜플 리스트로 변환
    results = list(zip(node_ids, similarities))
    
    # 유사도 높은 순으로 정렬
    results.sort(key=lambda x: x[1], reverse=True)
    
    # 자기 자신과 이미 제외된 노드들(exclude_ids)을 결과에서 제거
    if exclude_ids is None:
        exclude_ids = set()
    exclude_ids.add(start_node_id) # 자기 자신은 항상 제외
    
    filtered_results = [res for res in results if res[0] not in exclude_ids]
    
    # 상위 N개만 반환
    return filtered_results[:top_n]