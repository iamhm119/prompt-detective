import React, { useRef, useState, KeyboardEvent, ClipboardEvent } from 'react';

interface OTPInputProps {
  length?: number;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  error?: boolean;
}

const PLACEHOLDER = ' ';

const OTPInput: React.FC<OTPInputProps> = ({
  length = 6,
  value,
  onChange,
  disabled = false,
  error = false,
}) => {
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const [focusedIndex, setFocusedIndex] = useState<number | null>(null);

  const isDigit = (char: string | undefined): char is string => !!char && /[0-9]/.test(char);

  const normaliseValue = () =>
    Array.from({ length }, (_, index) => {
      const char = value?.[index];
      return isDigit(char) ? char : PLACEHOLDER;
    });

  const commitDigits = (digits: string[]) => {
    const joined = digits.join('');
    onChange(joined);
  };

  const handleChange = (index: number, inputValue: string) => {
    const sanitized = inputValue.replace(/[^0-9]/g, '');
    const digits = normaliseValue();

    if (sanitized.length === 0) {
      digits[index] = PLACEHOLDER;
      commitDigits(digits);
      if (index > 0) {
        inputRefs.current[index - 1]?.focus();
      }
      return;
    }

    if (sanitized.length === 1) {
      // Single digit input
      digits[index] = sanitized;
      commitDigits(digits);

      // Move to next input
      if (index < length - 1) {
        inputRefs.current[index + 1]?.focus();
      }
    } else {
      // Pasted full OTP
      const incomingDigits = sanitized.slice(0, length).split('');
      const mergedDigits = Array.from({ length }, (_, digitIndex) => incomingDigits[digitIndex] ?? PLACEHOLDER);
      commitDigits(mergedDigits);
      const focusIndex = Math.min(incomingDigits.length, length) - 1;
      if (focusIndex >= 0) {
        inputRefs.current[focusIndex]?.focus();
      }
    }
  };

  const handleKeyDown = (index: number, e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace') {
      if (!isDigit(value?.[index]) && index > 0) {
        // Move to previous input on backspace if current is empty
        inputRefs.current[index - 1]?.focus();
      }
    } else if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus();
    } else if (e.key === 'ArrowRight' && index < length - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (e: ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text/plain');
    const digits = pastedData.replace(/[^0-9]/g, '').substring(0, length);
    const paddedDigits = Array.from({ length }, (_, index) => digits[index] ?? PLACEHOLDER);
    commitDigits(paddedDigits);
    const focusIndex = Math.min(digits.length, length) - 1;
    if (focusIndex >= 0) {
      inputRefs.current[focusIndex]?.focus();
    }
  };

  return (
    <div className="flex gap-2 justify-center">
      {Array.from({ length }, (_, index) => (
        <input
          key={index}
          ref={(el) => (inputRefs.current[index] = el)}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={isDigit(value?.[index]) ? value?.[index] ?? '' : ''}
          onChange={(e) => handleChange(index, e.target.value)}
          onKeyDown={(e) => handleKeyDown(index, e)}
          onPaste={handlePaste}
          onFocus={() => setFocusedIndex(index)}
          onBlur={() => setFocusedIndex(null)}
          disabled={disabled}
          className={`
            w-12 h-14 text-center text-2xl font-bold rounded-lg border-2
            transition-all duration-200
            ${error 
              ? 'border-red-500 bg-red-50 text-red-900' 
              : focusedIndex === index
                ? 'border-purple-500 bg-purple-50 ring-4 ring-purple-200'
                : value[index]
                  ? 'border-green-500 bg-green-50 text-green-900'
                  : 'border-gray-300 bg-white'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-purple-400 cursor-text'}
            focus:outline-none
          `}
          aria-label={`OTP digit ${index + 1}`}
        />
      ))}
    </div>
  );
};

export default OTPInput;
