import React, { useEffect, useMemo, useState } from 'react';
import clsx from 'clsx';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export interface CarouselItem {
  id: string;
  content: React.ReactNode;
}

export interface CarouselProps {
  items: CarouselItem[];
  autoPlay?: boolean;
  interval?: number;
  className?: string;
}

const Carousel: React.FC<CarouselProps> = ({ items, autoPlay = true, interval = 7000, className }) => {
  const [index, setIndex] = useState(0);

  const normalizedInterval = Math.max(interval, 3000);

  const slides = useMemo(() => items ?? [], [items]);

  useEffect(() => {
    if (!autoPlay || slides.length <= 1) return;

    const timer = setInterval(() => {
      setIndex((prev) => (prev + 1) % slides.length);
    }, normalizedInterval);

    return () => clearInterval(timer);
  }, [autoPlay, slides, normalizedInterval]);

  const next = () => setIndex((prev) => (prev + 1) % slides.length);
  const prev = () => setIndex((prev) => (prev - 1 + slides.length) % slides.length);

  if (!slides.length) return null;

  return (
    <div className={clsx('relative overflow-hidden rounded-[32px] bg-white/90 p-8 shadow-[0_28px_80px_-45px_rgba(79,70,229,0.6)] backdrop-blur-2xl', className)}>
      <div className="relative">
        {slides.map((slide, slideIdx) => {
          const isActive = slideIdx === index;
          return (
            <div
              key={slide.id}
              className={clsx(
                'transition-all duration-700 ease-out',
                isActive ? 'opacity-100 translate-x-0' : 'pointer-events-none -translate-x-6 opacity-0'
              )}
            >
              <div className="text-base text-gray-600 sm:text-lg">{slide.content}</div>
            </div>
          );
        })}
      </div>

      {slides.length > 1 && (
        <>
          <div className="mt-6 flex items-center justify-between">
            <button
              type="button"
              onClick={prev}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white/80 text-gray-600 shadow-lg shadow-gray-200 transition hover:-translate-x-1 hover:text-gray-900"
              aria-label="Previous slide"
            >
              <ChevronLeft className="h-5 w-5" />
            </button>
            <div className="flex items-center gap-2">
              {slides.map((slide, slideIdx) => (
                <button
                  key={slide.id}
                  type="button"
                  onClick={() => setIndex(slideIdx)}
                  className={clsx(
                    'h-2.5 rounded-full transition-all duration-300',
                    slideIdx === index ? 'w-6 bg-blue-600' : 'w-2 bg-gray-300'
                  )}
                  aria-label={`Go to slide ${slideIdx + 1}`}
                />
              ))}
            </div>
            <button
              type="button"
              onClick={next}
              className="flex h-10 w-10 items-center justify-center rounded-full bg-white/80 text-gray-600 shadow-lg shadow-gray-200 transition hover:translate-x-1 hover:text-gray-900"
              aria-label="Next slide"
            >
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default Carousel;
