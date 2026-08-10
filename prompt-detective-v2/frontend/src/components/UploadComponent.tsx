import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, Video, Image, X, Download, CheckCircle, AlertCircle } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { useUpload } from '../hooks/useUpload';
import { ProgressBar } from './ProgressBar';

interface UploadedFile {
  file: File;
  id: string;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  jobId?: string;
  result?: any;
  error?: string;
}

interface UploadComponentProps {
  onUpload?: (file: File) => Promise<void>;
  maxFileSize?: number;
  acceptedTypes?: string[];
  disabled?: boolean;
}

export const UploadComponent: React.FC<UploadComponentProps> = ({ 
  onUpload,
  maxFileSize = 100 * 1024 * 1024,
  acceptedTypes = ['image/*', 'video/*'],
  disabled = false
}) => {
  const { user } = useAuth();
  const { uploadFile, getJobStatus } = useUpload();
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (disabled) return;
    
    // If external onUpload handler is provided, use it
    if (onUpload) {
      for (const file of acceptedFiles) {
        try {
          await onUpload(file);
        } catch (error) {
          console.error('Upload failed:', error);
        }
      }
      return;
    }

    // Otherwise use internal upload logic
    const newFiles: UploadedFile[] = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      progress: 0,
      status: 'uploading'
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);

    // Process each file
    for (const fileData of newFiles) {
      try {
        // Upload file and start analysis
        const response = await uploadFile(fileData.file, (progress) => {
          setUploadedFiles(prev => 
            prev.map(f => 
              f.id === fileData.id 
                ? { ...f, progress: Math.round(progress * 50) } // Upload is 50% of total
                : f
            )
          );
        });

        if (response.job_id) {
          // Update with job ID and start polling
          setUploadedFiles(prev => 
            prev.map(f => 
              f.id === fileData.id 
                ? { ...f, jobId: response.job_id, status: 'processing', progress: 50 }
                : f
            )
          );

          // Poll for job completion
          pollJobStatus(fileData.id, response.job_id);
        }
      } catch (error) {
        setUploadedFiles(prev => 
          prev.map(f => 
            f.id === fileData.id 
              ? { ...f, status: 'error', error: error instanceof Error ? error.message : 'Upload failed' }
              : f
          )
        );
      }
    }
  }, [uploadFile, onUpload, disabled]);

  const pollJobStatus = async (fileId: string, jobId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const status = await getJobStatus(jobId);
        
        setUploadedFiles(prev => 
          prev.map(f => 
            f.id === fileId 
              ? { 
                  ...f, 
                  progress: 50 + (status.progress / 2), // Processing is other 50%
                  status: status.status === 'completed' ? 'completed' : 
                         status.status === 'failed' ? 'error' : 'processing',
                  result: status.status === 'completed' ? status.result : undefined,
                  error: status.status === 'failed' ? status.error : undefined
                }
              : f
          )
        );

        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(pollInterval);
        }
      } catch (error) {
        clearInterval(pollInterval);
        setUploadedFiles(prev => 
          prev.map(f => 
            f.id === fileId 
              ? { ...f, status: 'error', error: 'Failed to get job status' }
              : f
          )
        );
      }
    }, 2000);
  };

  const removeFile = (id: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== id));
  };

  const downloadResult = (fileData: UploadedFile) => {
    if (!fileData.result) return;
    
  const prompt = fileData.result?.structured_prompt?.prompt?.main ||
          fileData.result?.quick_prompt ||
          fileData.result?.comprehensive_video_prompt || 
          fileData.result?.suggested_prompt || 
          fileData.result?.comprehensive_analysis || 
          'No prompt generated';
    
    const blob = new Blob([prompt], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${fileData.file.name.split('.')[0]}_prompt.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'],
      'image/*': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    },
    maxSize: maxFileSize,
    multiple: true,
    disabled
  });

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('video/')) {
      return <Video className="w-8 h-8 text-blue-500" />;
    }
    if (file.type.startsWith('image/')) {
      return <Image className="w-8 h-8 text-green-500" />;
    }
    return <File className="w-8 h-8 text-gray-500" />;
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      default:
        return null;
    }
  };

  if (!user) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 mb-4">Please log in to upload files</p>
        <a 
          href="/login" 
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 inline-block"
        >
          Log In
        </a>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Upload Content for Analysis
        </h2>
        <p className="text-gray-600">
          Upload videos or images to reverse-engineer their AI generation prompts
        </p>
      </div>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
          isDragActive 
            ? "border-blue-500 bg-blue-50" 
            : "border-gray-300 hover:border-gray-400"
        }`}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        {isDragActive ? (
          <p className="text-lg text-blue-600">Drop the files here...</p>
        ) : (
          <div>
            <p className="text-lg text-gray-600 mb-2">
              Drag & drop files here, or click to select
            </p>
            <p className="text-sm text-gray-500">
              Supports videos (MP4, AVI, MOV, etc.) and images (JPG, PNG, etc.)
            </p>
            <p className="text-sm text-gray-500">Max file size: 100MB</p>
          </div>
        )}
      </div>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Uploaded Files ({uploadedFiles.length})
          </h3>
          <div className="space-y-4">
            {uploadedFiles.map((fileData) => (
              <div
                key={fileData.id}
                className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    {getFileIcon(fileData.file)}
                    <div>
                      <p className="font-medium text-gray-900">
                        {fileData.file.name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {(fileData.file.size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(fileData.status)}
                    <button
                      onClick={() => removeFile(fileData.id)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                {/* Progress Bar */}
                {(fileData.status === 'uploading' || fileData.status === 'processing') && (
                  <div className="mb-3">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>
                        {fileData.status === 'uploading' ? 'Uploading...' : 'Processing...'}
                      </span>
                      <span>{Math.round(fileData.progress)}%</span>
                    </div>
                    <ProgressBar progress={fileData.progress} />
                  </div>
                )}

                {/* Error Message */}
                {fileData.status === 'error' && fileData.error && (
                  <div className="bg-red-50 border border-red-200 rounded p-3 mb-3">
                    <p className="text-red-700 text-sm">{fileData.error}</p>
                  </div>
                )}

                {/* Results */}
                {fileData.status === 'completed' && fileData.result && (
                  <div className="bg-green-50 border border-green-200 rounded p-4">
                    <div className="flex justify-between items-start mb-3">
                      <h4 className="font-medium text-green-900">Analysis Complete!</h4>
                      <button
                        onClick={() => downloadResult(fileData)}
                        className="flex items-center space-x-1 text-green-700 hover:text-green-800 text-sm"
                      >
                        <Download className="w-4 h-4" />
                        <span>Download</span>
                      </button>
                    </div>
                    <div className="text-sm text-green-800">
                      <p className="mb-2">Generated prompt preview:</p>
                      <div className="bg-white border border-green-200 rounded p-3 max-h-32 overflow-y-auto">
                        <p className="text-gray-700 text-xs font-mono">
                          {(fileData.result?.structured_prompt?.prompt?.quick ||
                            fileData.result?.quick_prompt ||
                            fileData.result?.structured_prompt?.prompt?.main ||
                            fileData.result?.comprehensive_video_prompt || 
                            fileData.result?.suggested_prompt || 
                            fileData.result?.comprehensive_analysis || 
                            'No prompt generated').substring(0, 200)}...
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};