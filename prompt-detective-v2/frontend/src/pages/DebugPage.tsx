import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useUpload } from '../hooks/useUpload';
import { api } from '../services/api';

const DebugPage: React.FC = () => {
  const { user } = useAuth();
  const { listJobs } = useUpload();
  const [debugInfo, setDebugInfo] = useState<any>({});
  const [loading, setLoading] = useState(false);

  const testAuth = async () => {
    setLoading(true);
    try {
      // Test basic API call
      const response = await api.get('/jobs?limit=1&offset=0');
      setDebugInfo({
        ...debugInfo,
        authTest: 'SUCCESS',
        jobsResponse: response.data,
        timestamp: new Date().toISOString()
      });
    } catch (error: any) {
      setDebugInfo({
        ...debugInfo,
        authTest: 'FAILED',
        error: error.message,
        status: error.response?.status,
        timestamp: new Date().toISOString()
      });
    }
    setLoading(false);
  };

  const testJobStatus = async () => {
    const jobId = prompt('Enter job ID to test:');
    if (!jobId) return;

    setLoading(true);
    try {
      const response = await api.get(`/jobs/${jobId}`);
      setDebugInfo({
        ...debugInfo,
        jobTest: 'SUCCESS',
        jobResponse: response.data,
        jobId,
        timestamp: new Date().toISOString()
      });
    } catch (error: any) {
      setDebugInfo({
        ...debugInfo,
        jobTest: 'FAILED',
        jobError: error.message,
        jobStatus: error.response?.status,
        jobId,
        timestamp: new Date().toISOString()
      });
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Debug Dashboard</h1>

        {/* User Info */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">User Information</h2>
          <pre className="bg-gray-100 p-4 rounded text-sm overflow-x-auto">
            {JSON.stringify(user, null, 2)}
          </pre>
        </div>

        {/* API Tests */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">API Tests</h2>
          <div className="space-y-4">
            <button
              onClick={testAuth}
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              Test Auth & List Jobs
            </button>
            <button
              onClick={testJobStatus}
              disabled={loading}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50 ml-4"
            >
              Test Job Status
            </button>
          </div>
        </div>

        {/* Debug Results */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Debug Results</h2>
          <pre className="bg-gray-100 p-4 rounded text-sm overflow-x-auto">
            {JSON.stringify(debugInfo, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default DebugPage;