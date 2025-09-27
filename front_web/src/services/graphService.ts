import { apiClient } from '@/lib/api/client';
import { WordCloudResponse, GraphResponse } from '@/lib/types/graph';
// 갑자기 든 생각인데
// graph도메인 --> 이름이 생각보다 구린것같기도하고
//작명가데려와


/**
 * 인기 키워드/워드클라우드 데이터를 조회(캬 눈물나네)
 */
export const getWordCloudData = async ({
  organizationName,
  limit = 30,
}: {
  organizationName?: string;
  limit?: number;
}): Promise<WordCloudResponse> => {
  const response = await apiClient.get<WordCloudResponse>('/graph/wordcloud', {
    params: {
      organization_name: organizationName,
      limit,
    },
  });
  return response.data;
};

/**
 * 키워드 기반의 초기 마인드맵 데이터를 조회
 */
export const getExploreData = async (keyword: string): Promise<GraphResponse> => {
  const response = await apiClient.get<GraphResponse>('/graph/explore', {
    params: { keyword },
  });
  return response.data;
};

/**
 * 특정 노드를 중심으로 마인드맵을 확장
 */
export const getExpandData = async ({
  nodeId,
  nodeType,
}: {
  nodeId: string;
  nodeType: string;
}): Promise<GraphResponse> => {
  const response = await apiClient.get<GraphResponse>('/graph/expand', {
    params: {
      node_id: nodeId,
      node_type: nodeType,
    },
  });
  return response.data;
};