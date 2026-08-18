import axios from 'axios';
import { AnalysisRequest, AnalysisResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeCluster = async (
  request: AnalysisRequest
): Promise<AnalysisResponse> => {
  const response = await apiClient.post<AnalysisResponse>('/api/analyze', request);
  return response.data;
};

export const getAnalysis = async (analysisId: string): Promise<AnalysisResponse> => {
  const response = await apiClient.get<AnalysisResponse>(`/api/analysis/${analysisId}`);
  return response.data;
};

export const downloadHtmlReport = async (analysisId: string): Promise<Blob> => {
  const response = await apiClient.get(`/api/reports/${analysisId}/html`, {
    responseType: 'blob',
  });
  return response.data;
};

export const downloadJsonReport = async (analysisId: string): Promise<Blob> => {
  const response = await apiClient.get(`/api/reports/${analysisId}/json`, {
    responseType: 'blob',
  });
  return response.data;
};

export const chatWithAI = async (
  analysisId: string,
  question: string
): Promise<{ answer: string; context_used: boolean }> => {
  const response = await apiClient.post('/api/chat/', {
    analysis_id: analysisId,
    question,
  });
  return response.data;
};
