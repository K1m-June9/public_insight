import { DataResponse } from './base';

/**
 * 워드클라우드 API가 반환하는 개별 키워드 항목의 타입
 */
export interface WordCloudItem {
  text: string;
  value: number; 
}

/**
 * 워드클라우드 API의 전체 응답 타입
 */
export type WordCloudResponse = DataResponse<WordCloudItem[]>;

// --------------------------------------------------------------------
// [미래 준비] Explore 및 Expand API를 위한 타입도 미리 정의해 둡니다.
// --------------------------------------------------------------------

/**
 * 마인드맵의 개별 노드를 나타내는 타입
 */
export interface GraphNode {
  id: string;
  type: 'keyword' | 'feed' | 'organization' | 'user' | 'anonymous_user';
  label: string;
  metadata: Record<string, any>;
}

/**
 * 마인드맵의 엣지(관계)를 나타내는 타입
 */
export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string | null;
}

/**
 * Explore/Expand API의 성공 응답 데이터 타입
 */
export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

/**
 * Explore/Expand API의 전체 응답 타입
 */
export type GraphResponse = DataResponse<GraphData>;