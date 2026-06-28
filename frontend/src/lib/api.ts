import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_URL,
});

export const getCampaigns = () => api.get('/campaigns').then(res => res.data);
export const getCampaign = (id: number) => api.get(`/campaigns/${id}`).then(res => res.data);
export const createCampaign = (name: string) => api.post('/campaigns', { name }).then(res => res.data);
export const updateCampaign = (id: number, data: any) => api.put(`/campaigns/${id}`, data).then(res => res.data);
export const deleteCampaign = (id: number) => api.delete(`/campaigns/${id}`).then(res => res.data);

export const uploadResume = (campaignId: number, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post(`/campaigns/${campaignId}/upload-resume`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }).then(res => res.data);
};

export const uploadTargets = (campaignId: number, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post(`/campaigns/${campaignId}/upload-targets`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }).then(res => res.data);
};

export const processAllTargets = (campaignId: number) => api.post(`/campaigns/${campaignId}/process-all`).then(res => res.data);
export const updateTarget = (targetId: number, data: any) => api.put(`/targets/${targetId}`, data).then(res => res.data);
export const sendTargetEmail = (targetId: number) => api.post(`/targets/${targetId}/send`).then(res => res.data);
export const approveAllTargets = (campaignId: number) => api.post(`/campaigns/${campaignId}/approve-all`).then(res => res.data);
export const sendAllApprovedTargets = (campaignId: number) => api.post(`/campaigns/${campaignId}/send-all`).then(res => res.data);

export const getConfig = () => api.get('/config').then(res => res.data);
export const updateConfig = (data: any) => api.post('/config', data).then(res => res.data);
export const testSmtp = (data: any) => api.post('/config/test-smtp', data).then(res => res.data);

export const getApiKeys = () => api.get('/apikeys').then(res => res.data);
export const createApiKey = (data: any) => api.post('/apikeys', data).then(res => res.data);
export const deleteApiKey = (id: number) => api.delete(`/apikeys/${id}`).then(res => res.data);
export const updateApiKeyPriority = (id: number, priority: number) => api.put(`/apikeys/${id}/priority?priority=${priority}`).then(res => res.data);

