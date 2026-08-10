import React, { useState, useEffect } from 'react';
import { Loader2, Shield, Check, X, CreditCard, Smartphone } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuthStore } from '../../stores/authStore';

// Declare Razorpay on window
declare global {
  interface Window {
    Razorpay: any;
  }
}

interface RazorpayCheckoutProps {
  amount: number;
  planId: string;
  planName: string;
  billingCycle: 'monthly' | 'yearly';
  onSuccess: (response: any) => void;
  onFailure: (error: any) => void;
  buttonText?: string;
  buttonClassName?: string;
  disabled?: boolean;
  children?: React.ReactNode;
}

interface RazorpayOptions {
  key: string;
  amount: number;
  currency: string;
  name: string;
  description: string;
  order_id: string;
  handler: (response: any) => void;
  prefill: {
    name: string;
    email: string;
    contact: string;
  };
  theme: {
    color: string;
  };
  modal: {
    ondismiss: () => void;
  };
}

export const RazorpayCheckout: React.FC<RazorpayCheckoutProps> = ({
  amount,
  planId,
  planName,
  billingCycle,
  onSuccess,
  onFailure,
  buttonText,
  buttonClassName,
  disabled = false,
  children
}) => {
  const [loading, setLoading] = useState(false);
  const [scriptLoaded, setScriptLoaded] = useState(false);

  // Load Razorpay script
  useEffect(() => {
    const loadRazorpayScript = () => {
      return new Promise((resolve) => {
        // Check if script already loaded
        if (window.Razorpay) {
          setScriptLoaded(true);
          resolve(true);
          return;
        }

        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.async = true;
        script.onload = () => {
          setScriptLoaded(true);
          resolve(true);
        };
        script.onerror = () => {
          console.error('Failed to load Razorpay script');
          resolve(false);
        };
        document.body.appendChild(script);
      });
    };

    loadRazorpayScript();
  }, []);

  const handlePayment = async () => {
    if (!scriptLoaded) {
      toast.error('Payment system is loading. Please wait...');
      return;
    }

    setLoading(true);

    try {
      // Get auth token from auth store
      const { accessToken, user, isAuthenticated } = useAuthStore.getState();
      
      if (!isAuthenticated || !accessToken) {
        toast.error('Please login to continue');
        window.location.href = '/login';
        return;
      }

      // 1. Create order from backend
      console.log('🔄 Creating payment order...');
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
      
      const createOrderResponse = await fetch(`${apiUrl}/payments/create-order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          order_type: 'subscription',
          plan: planId,
          billing_cycle: billingCycle
        })
      });

      if (!createOrderResponse.ok) {
        const errorData = await createOrderResponse.json();
        throw new Error(errorData.detail || 'Failed to create order');
      }

      const orderData = await createOrderResponse.json();
      console.log('✅ Order created:', orderData.order_id);

      // 2. Open Razorpay checkout
      const options: RazorpayOptions = {
        key: orderData.key_id,
        amount: orderData.amount,
        currency: orderData.currency,
        name: 'Prompt Detective',
        description: `${planName} Plan - ${billingCycle}`,
        order_id: orderData.order_id,
        handler: async function (response: any) {
          console.log('✅ Payment successful:', response.razorpay_payment_id);
          
          // Show loading toast
          const verifyToast = toast.loading('Verifying payment...');
          
          // Get fresh token from store
          const { accessToken } = useAuthStore.getState();
          
          try {
            // 3. Verify payment on backend
            const verifyResponse = await fetch(`${apiUrl}/payments/verify-payment`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
              },
              body: JSON.stringify({
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
                order_type: 'subscription',
                plan: planId,
                billing_cycle: billingCycle
              })
            });

            if (!verifyResponse.ok) {
              const errorData = await verifyResponse.json();
              throw new Error(errorData.detail || 'Payment verification failed');
            }

            const result = await verifyResponse.json();
            console.log('✅ Payment verified:', result);

            // Dismiss loading toast and show success
            toast.dismiss(verifyToast);
            toast.success(result.message || 'Subscription activated! 🎉', {
              duration: 5000,
              icon: '🎉'
            });

            // Call success callback
            onSuccess(result);
          } catch (error: any) {
            console.error('❌ Payment verification error:', error);
            toast.dismiss(verifyToast);
            toast.error(error.message || 'Payment verification failed');
            onFailure(error);
          } finally {
            setLoading(false);
          }
        },
        prefill: {
          name: user?.full_name || '',
          email: user?.email || '',
          contact: '' // Phone not in user model
        },
        theme: {
          color: '#8B5CF6' // Purple brand color
        },
        modal: {
          ondismiss: function() {
            console.log('❌ Payment cancelled by user');
            setLoading(false);
            toast.error('Payment cancelled');
          }
        }
      };

      const razorpay = new window.Razorpay(options);
      
      razorpay.on('payment.failed', function (response: any) {
        console.error('❌ Payment failed:', response.error);
        setLoading(false);
        toast.error(response.error.description || 'Payment failed. Please try again.');
        onFailure(response.error);
      });

      razorpay.open();

    } catch (error: any) {
      console.error('❌ Payment error:', error);
      setLoading(false);
      toast.error(error.message || 'Failed to initiate payment');
      onFailure(error);
    }
  };

  const defaultButtonClassName = buttonClassName || 
    'w-full py-3 px-6 rounded-xl text-center font-semibold transition-all duration-200 bg-gradient-to-r from-purple-600 to-purple-700 text-white hover:from-purple-700 hover:to-purple-800 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed';

  return (
    <>
      {children ? (
        <div onClick={handlePayment} className="cursor-pointer">
          {children}
        </div>
      ) : (
        <button
          onClick={handlePayment}
          disabled={disabled || loading || !scriptLoaded}
          className={defaultButtonClassName}
        >
          {loading ? (
            <span className="flex items-center justify-center">
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Processing...
            </span>
          ) : !scriptLoaded ? (
            <span className="flex items-center justify-center">
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Loading...
            </span>
          ) : (
            <span className="flex items-center justify-center">
              <Shield className="w-5 h-5 mr-2" />
              {buttonText || `Pay ₹${amount}`}
            </span>
          )}
        </button>
      )}
    </>
  );
};

interface CreditPackCheckoutProps {
  packName: string;
  amount: number;
  onSuccess: (response: any) => void;
  onFailure: (error: any) => void;
  buttonText?: string;
  buttonClassName?: string;
  disabled?: boolean;
}

export const CreditPackCheckout: React.FC<CreditPackCheckoutProps> = ({
  packName,
  amount,
  onSuccess,
  onFailure,
  buttonText,
  buttonClassName,
  disabled = false
}) => {
  const [loading, setLoading] = useState(false);
  const [scriptLoaded, setScriptLoaded] = useState(false);

  useEffect(() => {
    const loadRazorpayScript = () => {
      return new Promise((resolve) => {
        if (window.Razorpay) {
          setScriptLoaded(true);
          resolve(true);
          return;
        }

        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.async = true;
        script.onload = () => {
          setScriptLoaded(true);
          resolve(true);
        };
        script.onerror = () => {
          console.error('Failed to load Razorpay script');
          resolve(false);
        };
        document.body.appendChild(script);
      });
    };

    loadRazorpayScript();
  }, []);

  const handlePayment = async () => {
    if (!scriptLoaded) {
      toast.error('Payment system is loading. Please wait...');
      return;
    }

    setLoading(true);

    try {
      // Get auth token from auth store
      const { accessToken, user, isAuthenticated } = useAuthStore.getState();
      
      if (!isAuthenticated || !accessToken) {
        toast.error('Please login to continue');
        window.location.href = '/login';
        return;
      }

      console.log('🔄 Creating credit pack order...');
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
      
      const createOrderResponse = await fetch(`${apiUrl}/payments/create-order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          order_type: 'credit_pack',
          pack_name: packName
        })
      });

      if (!createOrderResponse.ok) {
        const errorData = await createOrderResponse.json();
        throw new Error(errorData.detail || 'Failed to create order');
      }

      const orderData = await createOrderResponse.json();
      console.log('✅ Order created:', orderData.order_id);

      const options: RazorpayOptions = {
        key: orderData.key_id,
        amount: orderData.amount,
        currency: orderData.currency,
        name: 'Prompt Detective',
        description: `${packName} Credit Pack`,
        order_id: orderData.order_id,
        handler: async function (response: any) {
          console.log('✅ Payment successful:', response.razorpay_payment_id);
          
          const verifyToast = toast.loading('Verifying payment...');
          
          // Get fresh token from store
          const { accessToken } = useAuthStore.getState();
          
          try {
            const verifyResponse = await fetch(`${apiUrl}/payments/verify-payment`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
              },
              body: JSON.stringify({
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
                order_type: 'credit_pack',
                pack_name: packName
              })
            });

            if (!verifyResponse.ok) {
              const errorData = await verifyResponse.json();
              throw new Error(errorData.detail || 'Payment verification failed');
            }

            const result = await verifyResponse.json();
            console.log('✅ Payment verified:', result);

            toast.dismiss(verifyToast);
            toast.success(result.message || 'Credit pack purchased! 🎉', {
              duration: 5000,
              icon: '🎉'
            });

            onSuccess(result);
          } catch (error: any) {
            console.error('❌ Payment verification error:', error);
            toast.dismiss(verifyToast);
            toast.error(error.message || 'Payment verification failed');
            onFailure(error);
          } finally {
            setLoading(false);
          }
        },
        prefill: {
          name: user?.full_name || '',
          email: user?.email || '',
          contact: '' // Phone not in user model
        },
        theme: {
          color: '#3B82F6' // Blue for credit packs
        },
        modal: {
          ondismiss: function() {
            console.log('❌ Payment cancelled by user');
            setLoading(false);
            toast.error('Payment cancelled');
          }
        }
      };

      const razorpay = new window.Razorpay(options);
      
      razorpay.on('payment.failed', function (response: any) {
        console.error('❌ Payment failed:', response.error);
        setLoading(false);
        toast.error(response.error.description || 'Payment failed. Please try again.');
        onFailure(response.error);
      });

      razorpay.open();

    } catch (error: any) {
      console.error('❌ Payment error:', error);
      setLoading(false);
      toast.error(error.message || 'Failed to initiate payment');
      onFailure(error);
    }
  };

  const defaultButtonClassName = buttonClassName || 
    'w-full py-2 px-4 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold hover:from-blue-700 hover:to-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed';

  return (
    <button
      onClick={handlePayment}
      disabled={disabled || loading || !scriptLoaded}
      className={defaultButtonClassName}
    >
      {loading ? (
        <span className="flex items-center justify-center">
          <Loader2 className="w-5 h-5 mr-2 animate-spin" />
          Processing...
        </span>
      ) : !scriptLoaded ? (
        <span className="flex items-center justify-center">
          <Loader2 className="w-5 h-5 mr-2 animate-spin" />
          Loading...
        </span>
      ) : (
        buttonText || 'Buy Now'
      )}
    </button>
  );
};

// Payment Methods Info Component
export const PaymentMethodsInfo: React.FC = () => {
  const methods = [
    { icon: <Smartphone />, name: 'UPI', examples: 'PhonePe, GPay, Paytm' },
    { icon: <CreditCard />, name: 'Cards', examples: 'Visa, Mastercard, RuPay' },
    { icon: <Shield />, name: 'NetBanking', examples: 'All major banks' }
  ];

  return (
    <div className="mt-4 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
      <div className="flex items-center mb-3">
        <Shield className="w-5 h-5 text-green-600 mr-2" />
        <h4 className="text-sm font-semibold text-gray-900">
          Secure Payment - 100% Safe
        </h4>
      </div>
      <div className="grid grid-cols-3 gap-4">
        {methods.map((method, index) => (
          <div key={index} className="text-center">
            <div className="flex justify-center text-gray-600 mb-1">
              {method.icon}
            </div>
            <p className="text-xs font-semibold text-gray-900">{method.name}</p>
            <p className="text-[10px] text-gray-500">{method.examples}</p>
          </div>
        ))}
      </div>
      <div className="mt-3 flex items-center justify-center space-x-4 text-[10px] text-gray-600">
        <span className="flex items-center">
          <Check className="w-3 h-3 mr-1 text-green-600" />
          256-bit SSL
        </span>
        <span className="flex items-center">
          <Check className="w-3 h-3 mr-1 text-green-600" />
          PCI DSS Compliant
        </span>
        <span className="flex items-center">
          <Check className="w-3 h-3 mr-1 text-green-600" />
          Razorpay Secured
        </span>
      </div>
    </div>
  );
};
