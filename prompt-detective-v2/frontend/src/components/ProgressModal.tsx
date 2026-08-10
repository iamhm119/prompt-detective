import React, { useEffect, useState, useRef } from 'react';
import { X, FileVideo, FileImage, Loader2, CheckCircle, AlertCircle, XCircle } from 'lucide-react';
import { api } from '../services/api';

interface ProgressModalProps {
  isOpen: boolean;
  onClose: () => void;
  jobId: string;
  filename: string;
  contentType: string;
  onComplete: () => void;
}

interface JobStatus {
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  stage?: string;
  message?: string;
  error_message?: string;
}

interface ProgressUpdate {
  job_id: number;
  status: string;
  progress: number;
  stage: string;
  message: string;
  error_message?: string;
}

const ProgressModal: React.FC<ProgressModalProps> = ({
  isOpen,
  onClose,
  jobId,
  filename,
  contentType,
  onComplete
}) => {
  const [jobStatus, setJobStatus] = useState<JobStatus>({ status: 'pending', progress: 0 });
  const [stage, setStage] = useState<string>('Initializing...');
  const [pollCount, setPollCount] = useState(0);
  const [isCancelling, setIsCancelling] = useState(false);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!isOpen || !jobId) return;

    // Reset state when modal opens
    setJobStatus({ status: 'pending', progress: 0 });
    setStage('Initializing...');
    setPollCount(0);
    setIsCancelling(false);
    setShowCancelConfirm(false);

    // Check if this is a temporary job ID (starts with 'temp_')
    const isTempJobId = jobId.startsWith('temp_');
    
    if (isTempJobId) {
      console.log('🔄 Detected temporary job ID, showing upload progress...');
      setStage('Uploading and analyzing file...');
      setJobStatus({ status: 'processing', progress: 10 });
      return; // Don't start polling for temp IDs
    }

    console.log('📊 Starting job polling for real job ID:', jobId);

    const pollJob = async () => {
      try {
        setPollCount(prev => prev + 1);
        const response = await api.get(`/jobs/${jobId}`);
        
        if (response.data) {
          const data = response.data;
          const currentProgress = data.progress || 0;
          
          console.log(`📊 Job ${jobId} - Status: ${data.status}, Progress: ${currentProgress}%`);
          
          setJobStatus({
            status: data.status,
            progress: currentProgress,
            error_message: data.error_message
          });

          // Update stage description based on EXACT backend progress ranges
          if (data.status === 'pending') {
            setStage('Queuing for processing...');
          } else if (data.status === 'processing') {
            if (currentProgress <= 10) {
              setStage('File uploaded successfully');
            } else if (currentProgress <= 20) {
              setStage('Starting content analysis...');
            } else if (currentProgress <= 40) {
              setStage(contentType?.startsWith('video') ? 'Extracting key frames from video...' : 'Analyzing image structure...');
            } else if (currentProgress <= 70) {
              setStage('Running AI processing and analysis...');
            } else if (currentProgress <= 90) {
              setStage('Generating AI prompts...');
            } else if (currentProgress < 100) {
              setStage('Finalizing results...');
            }
          } else if (data.status === 'completed') {
            setStage('Analysis complete!');
            setTimeout(() => {
              onComplete();
              onClose();
            }, 1500); // Shorter delay for better UX
            if (pollingIntervalRef.current) {
              clearInterval(pollingIntervalRef.current);
            }
          } else if (data.status === 'failed') {
            setStage('Analysis failed');
            if (pollingIntervalRef.current) {
              clearInterval(pollingIntervalRef.current);
            }
          } else if (data.status === 'cancelled') {
            setStage('Cancelled by user');
            if (pollingIntervalRef.current) {
              clearInterval(pollingIntervalRef.current);
            }
          }
        }
      } catch (error) {
        console.error('Failed to poll job status:', error);
        
        // Stop polling after too many failed attempts
        if (pollCount > 15) {
          setJobStatus(prev => ({ ...prev, status: 'failed' }));
          setStage('Connection lost - please refresh and try again');
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
          }
          return;
        }
        
        // Handle different types of errors
        if (error && typeof error === 'object' && 'response' in error) {
          const axiosError = error as any;
          if (axiosError.response?.status === 401) {
            setJobStatus(prev => ({ ...prev, status: 'failed' }));
            setStage('Session expired - please refresh and login again');
            if (pollingIntervalRef.current) {
              clearInterval(pollingIntervalRef.current);
            }
          } else if (axiosError.response?.status === 404) {
            // Job might not be created yet, keep trying for a bit
            if (pollCount <= 5) {
              setStage('Connecting to analysis service...');
            } else {
              setJobStatus(prev => ({ ...prev, status: 'failed' }));
              setStage('Job not found - it may have been deleted');
              if (pollingIntervalRef.current) {
                clearInterval(pollingIntervalRef.current);
              }
            }
          } else {
            // For other errors, keep trying for a bit
            if (pollCount <= 5) {
              setStage('Retrying connection...');
            } else {
              setJobStatus(prev => ({ ...prev, status: 'failed' }));
              setStage('Error checking job status - please try again');
              if (pollingIntervalRef.current) {
                clearInterval(pollingIntervalRef.current);
              }
            }
          }
        } else {
          setJobStatus(prev => ({ ...prev, status: 'failed' }));
          setStage('Network error - please check your connection');
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
          }
        }
      }
    };

    // Only start polling for real job IDs - FASTER POLLING (1 second) FOR SMOOTHER UPDATES
    if (!isTempJobId) {
      pollingIntervalRef.current = setInterval(pollJob, 1000); // Changed from 2000 to 1000ms
      pollJob(); // Initial call
      
      return () => {
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
      };
    }
  }, [isOpen, jobId, onComplete, onClose, contentType, pollCount]);

  const handleCancelJob = async () => {
    if (isCancelling) return;
    
    setIsCancelling(true);
    
    try {
      console.log('🛑 Cancelling job:', jobId);
      const response = await api.delete(`/progress/${jobId}/cancel`);
      
      if (response.data.success) {
        console.log('✅ Job cancelled successfully');
        setJobStatus({
          status: 'cancelled',
          progress: 0,
          error_message: 'Job cancelled by user'
        });
        setStage('Cancelled by user');
        
        // Clear polling
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
        }
        
        // Close modal after brief delay
        setTimeout(() => {
          onClose();
        }, 1500);
      }
    } catch (error) {
      console.error('Failed to cancel job:', error);
      setJobStatus(prev => ({
        ...prev,
        error_message: 'Failed to cancel job. Please try again.'
      }));
    } finally {
      setIsCancelling(false);
      setShowCancelConfirm(false);
    }
  };

  if (!isOpen) return null;

  const getStatusIcon = () => {
    switch (jobStatus.status) {
      case 'completed':
        return <CheckCircle className="w-8 h-8 text-green-500" />;
      case 'failed':
        return <AlertCircle className="w-8 h-8 text-red-500" />;
      case 'cancelled':
        return <XCircle className="w-8 h-8 text-orange-500" />;
      default:
        return <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />;
    }
  };

  const getProgressColor = () => {
    switch (jobStatus.status) {
      case 'completed':
        return 'bg-green-500';
      case 'failed':
        return 'bg-red-500';
      case 'cancelled':
        return 'bg-orange-500';
      default:
        return 'bg-blue-500';
    }
  };

  const canCancel = jobStatus.status === 'pending' || jobStatus.status === 'processing';

  return (
    <div className="fixed inset-0 bg-black/60 dark:bg-black/80 flex items-center justify-center z-50 backdrop-blur-sm p-4">
      <div className="bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl rounded-3xl p-8 max-w-md w-full shadow-[0_30px_70px_-25px_rgba(79,70,229,0.5)] dark:shadow-[0_30px_70px_-25px_rgba(15,23,42,0.8)] border border-white/60 dark:border-white/10 transform transition-all">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-gray-900 dark:text-slate-100">Processing Analysis</h3>
          <div className="flex items-center space-x-2">
            {canCancel && !showCancelConfirm && (
              <button
                onClick={() => setShowCancelConfirm(true)}
                disabled={isCancelling}
                className="text-orange-600 dark:text-orange-400 hover:text-orange-700 dark:hover:text-orange-300 transition-colors text-sm font-medium px-3 py-1.5 border border-orange-500/40 dark:border-orange-400/40 rounded-full hover:bg-orange-50 dark:hover:bg-orange-500/10 disabled:opacity-50 disabled:cursor-not-allowed"
                title="Cancel job"
              >
                Cancel
              </button>
            )}
            {(jobStatus.status === 'completed' || jobStatus.status === 'failed' || jobStatus.status === 'cancelled') && (
              <button
                onClick={onClose}
                className="text-gray-400 dark:text-slate-500 hover:text-gray-600 dark:hover:text-slate-300 transition-colors p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded-full"
              >
                <X className="w-6 h-6" />
              </button>
            )}
          </div>
        </div>

        {/* Cancel Confirmation */}
        {showCancelConfirm && (
          <div className="mb-6 p-4 bg-orange-50/80 dark:bg-orange-500/10 border border-orange-200/70 dark:border-orange-400/20 rounded-2xl backdrop-blur-sm">
            <p className="text-sm font-medium text-orange-900 dark:text-orange-200 mb-3">
              Are you sure you want to cancel this analysis? This will not count towards your daily quota.
            </p>
            <div className="flex space-x-2">
              <button
                onClick={handleCancelJob}
                disabled={isCancelling}
                className="flex-1 bg-gradient-to-r from-orange-500 to-red-500 text-white px-4 py-2.5 rounded-full hover:shadow-lg hover:-translate-y-0.5 transition-all text-sm font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isCancelling ? 'Cancelling...' : 'Yes, Cancel'}
              </button>
              <button
                onClick={() => setShowCancelConfirm(false)}
                disabled={isCancelling}
                className="flex-1 bg-gray-200 dark:bg-slate-700 text-gray-700 dark:text-slate-200 px-4 py-2.5 rounded-full hover:bg-gray-300 dark:hover:bg-slate-600 transition-colors text-sm font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                No, Continue
              </button>
            </div>
          </div>
        )}

        {/* File Info */}
        <div className="flex items-center space-x-3 mb-6 p-4 bg-gradient-to-br from-blue-50/60 via-white/30 to-purple-50/60 dark:from-slate-800/60 dark:via-slate-900/30 dark:to-slate-800/60 rounded-2xl border border-blue-100/50 dark:border-slate-700/50 backdrop-blur-sm">
          {contentType === 'video' ? (
            <FileVideo className="w-8 h-8 text-blue-500 dark:text-blue-400 flex-shrink-0" />
          ) : (
            <FileImage className="w-8 h-8 text-green-500 dark:text-green-400 flex-shrink-0" />
          )}
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-slate-100 truncate">{filename}</p>
            <p className="text-xs text-gray-500 dark:text-slate-400 capitalize">{contentType} Analysis</p>
          </div>
        </div>

        {/* Status Icon and Stage */}
        <div className="text-center mb-6">
          <div className="flex justify-center mb-4">
            {getStatusIcon()}
          </div>
          <p className="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-2">
            {jobStatus.status === 'completed' ? 'Complete!' : 
             jobStatus.status === 'failed' ? 'Failed' :
             jobStatus.status === 'cancelled' ? 'Cancelled' :
             'Processing...'}
          </p>
          <p className="text-sm text-gray-600 dark:text-slate-400">{stage}</p>
          {jobStatus.error_message && (
            <p className="text-sm text-red-600 dark:text-red-400 mt-2">{jobStatus.error_message}</p>
          )}
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-slate-300">Progress</span>
            <span className="text-sm text-gray-600 dark:text-slate-400">{jobStatus.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-slate-700 rounded-full h-3 overflow-hidden shadow-inner">
            <div
              className={`h-full rounded-full transition-all duration-300 ease-out ${getProgressColor()}`}
              style={{ width: `${jobStatus.progress}%` }}
            />
          </div>
        </div>

        {/* Processing Steps Indicator - SYNCED WITH BACKEND STAGES */}
        <div className="space-y-2">
          <div className="text-xs font-medium text-gray-500 dark:text-slate-400 mb-3">Processing Steps:</div>
          {[
            { name: 'File Upload', threshold: 0, maxThreshold: 10 },
            { name: 'Content Analysis', threshold: 10, maxThreshold: 20 },
            { name: 'Scene Detection', threshold: 20, maxThreshold: 40 },
            { name: 'AI Analysis', threshold: 40, maxThreshold: 70 },
            { name: 'Prompt Generation', threshold: 70, maxThreshold: 90 },
            { name: 'Finalization', threshold: 90, maxThreshold: 100 }
          ].map((step, index) => {
            const isActive = jobStatus.progress >= step.threshold && jobStatus.progress < step.maxThreshold;
            const isCompleted = jobStatus.progress >= step.maxThreshold;
            
            return (
              <div key={index} className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full transition-all duration-300 ${
                  isCompleted
                    ? (jobStatus.status === 'failed' || jobStatus.status === 'cancelled') ? 'bg-red-500 dark:bg-red-400' : 'bg-green-500 dark:bg-green-400'
                    : isActive 
                      ? 'bg-blue-500 dark:bg-blue-400 animate-pulse ring-2 ring-blue-300 dark:ring-blue-500/50' 
                      : 'bg-gray-300 dark:bg-slate-600'
                }`} />
                <span className={`text-sm transition-colors duration-300 ${
                  isCompleted || isActive ? 'text-gray-900 dark:text-slate-100 font-medium' : 'text-gray-500 dark:text-slate-500'
                }`}>
                  {step.name}
                </span>
                {isActive && jobStatus.status === 'processing' && (
                  <span className="text-xs text-blue-600 dark:text-blue-400 ml-auto">In Progress...</span>
                )}
                {isCompleted && jobStatus.status !== 'failed' && jobStatus.status !== 'cancelled' && (
                  <CheckCircle className="w-4 h-4 text-green-500 dark:text-green-400 ml-auto" />
                )}
              </div>
            );
          })}
        </div>

        {/* Action Button */}
        {jobStatus.status === 'completed' && (
          <div className="mt-6 pt-6 border-t border-gray-200 dark:border-slate-700">
            <button
              onClick={() => {
                onComplete();
                onClose();
              }}
              className="w-full bg-gradient-to-r from-green-500 to-emerald-500 text-white py-3 px-4 rounded-full font-semibold hover:shadow-lg hover:-translate-y-0.5 transition-all"
            >
              View Results
            </button>
          </div>
        )}

        {(jobStatus.status === 'failed' || jobStatus.status === 'cancelled') && (
          <div className="mt-6 pt-6 border-t border-gray-200 dark:border-slate-700">
            <button
              onClick={onClose}
              className="w-full bg-gray-500 dark:bg-slate-700 text-white py-3 px-4 rounded-full font-semibold hover:bg-gray-600 dark:hover:bg-slate-600 transition-colors"
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressModal;
