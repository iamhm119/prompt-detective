import { useCallback, useState } from 'react';
import { api } from '../services/api';
import { resolveBackendAssetUrl } from '../lib/media';

interface UploadProgress {
  (progress: number): void;
}

interface UploadResponse {
  job_id: string;
  status: string;
  message: string;
}

interface JobStatus {
  job_id: string;
  filename: string;
  content_type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  error?: string;
  result?: any;
  created_at: string;
  completed_at?: string;
  thumbnail_url?: string;
}

export const useUpload = () => {
  const [uploadProgress, setUploadProgress] = useState<{ [key: string]: number }>({});

  const resolveThumbnail = useCallback(<T extends { thumbnail_url?: string | null }>(job: T): T => {
    if (!job) return job;
    return {
      ...job,
      thumbnail_url: resolveBackendAssetUrl(job.thumbnail_url),
    };
  }, []);

  const uploadFile = useCallback(async (file: File, onProgress?: UploadProgress): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/uploads', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const progress = (progressEvent.loaded / progressEvent.total) * 100;
          setUploadProgress(prev => ({ ...prev, [file.name]: progress }));
          onProgress?.(progress / 100);
        }
      },
    });

    return response.data;
  }, []);

  const getJobStatus = useCallback(async (jobId: string): Promise<JobStatus> => {
    const response = await api.get(`/jobs/${jobId}`);
    return resolveThumbnail(response.data);
  }, [resolveThumbnail]);

  const getJobResults = useCallback(async (jobId: string) => {
    const response = await api.get(`/jobs/${jobId}/results`);
    if (response?.data?.job) {
      response.data.job = resolveThumbnail(response.data.job);
    }
    return response.data;
  }, [resolveThumbnail]);

  const listJobs = useCallback(async (statusFilter?: string, limit = 20, offset = 0) => {
    const params = new URLSearchParams();
    if (statusFilter) params.append('status_filter', statusFilter);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    const response = await api.get(`/jobs?${params}`);
    const data = response.data ?? {};

    if (Array.isArray(data.jobs)) {
      data.jobs = data.jobs.map((job: any) => resolveThumbnail(job));
    }

    return data;
  }, [resolveThumbnail]);

  return {
    uploadFile,
    getJobStatus,
    getJobResults,
    listJobs,
    uploadProgress
  };
};