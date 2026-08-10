/**
 * Keep-alive service to prevent backend from sleeping on free tier
 * Pings backend every 14 minutes to keep it active
 */

const PING_INTERVAL = 14 * 60 * 1000; // 14 minutes in milliseconds
const MAX_RETRIES = 3;

class KeepAliveService {
  private intervalId: NodeJS.Timeout | null = null;
  private isEnabled: boolean = true;

  /**
   * Start the keep-alive ping service
   */
  start(apiBaseUrl: string): void {
    if (this.intervalId) {
      console.log('Keep-alive service already running');
      return;
    }

    console.log('Starting keep-alive service...');
    
    // Ping immediately on start
    this.ping(apiBaseUrl);

    // Set up periodic pings
    this.intervalId = setInterval(() => {
      this.ping(apiBaseUrl);
    }, PING_INTERVAL);
  }

  /**
   * Stop the keep-alive service
   */
  stop(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
      console.log('Keep-alive service stopped');
    }
  }

  /**
   * Enable/disable the service
   */
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
    if (!enabled && this.intervalId) {
      this.stop();
    }
  }

  /**
   * Ping the backend health endpoint
   */
  private async ping(apiBaseUrl: string, retryCount: number = 0): Promise<void> {
    if (!this.isEnabled) return;

    try {
      const response = await fetch(`${apiBaseUrl}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        // Don't include credentials for health check
      });

      if (response.ok) {
        console.log(`✓ Keep-alive ping successful (${new Date().toLocaleTimeString()})`);
      } else {
        console.warn(`⚠ Keep-alive ping returned status ${response.status}`);
      }
    } catch (error) {
      console.error(`✗ Keep-alive ping failed:`, error);
      
      // Retry with exponential backoff
      if (retryCount < MAX_RETRIES) {
        const backoffDelay = Math.pow(2, retryCount) * 1000; // 1s, 2s, 4s
        console.log(`Retrying in ${backoffDelay / 1000}s...`);
        
        setTimeout(() => {
          this.ping(apiBaseUrl, retryCount + 1);
        }, backoffDelay);
      }
    }
  }

  /**
   * Check if service is running
   */
  isRunning(): boolean {
    return this.intervalId !== null;
  }
}

// Export singleton instance
export const keepAliveService = new KeepAliveService();
