import { useEffect, useRef, useState } from 'react';

// Hook para gerenciar foco e navegação por teclado
export const useKeyboardNavigation = (items = [], options = {}) => {
  const [currentIndex, setCurrentIndex] = useState(options.initialIndex || 0);
  const [isNavigating, setIsNavigating] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (!isNavigating || items.length === 0) return;

      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault();
          setCurrentIndex((prev) => (prev + 1) % items.length);
          break;
        case 'ArrowUp':
          event.preventDefault();
          setCurrentIndex((prev) => (prev - 1 + items.length) % items.length);
          break;
        case 'Enter':
        case ' ':
          event.preventDefault();
          if (options.onSelect) {
            options.onSelect(items[currentIndex], currentIndex);
          }
          break;
        case 'Escape':
          event.preventDefault();
          setIsNavigating(false);
          if (options.onEscape) {
            options.onEscape();
          }
          break;
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [currentIndex, isNavigating, items, options]);

  const startNavigation = () => setIsNavigating(true);
  const stopNavigation = () => setIsNavigating(false);

  return {
    currentIndex,
    setCurrentIndex,
    isNavigating,
    startNavigation,
    stopNavigation,
    containerRef
  };
};

// Hook para gerenciar foco automático
export const useAutoFocus = (condition = true, delay = 0) => {
  const ref = useRef(null);

  useEffect(() => {
    if (condition && ref.current) {
      const timer = setTimeout(() => {
        ref.current.focus();
      }, delay);

      return () => clearTimeout(timer);
    }
  }, [condition, delay]);

  return ref;
};

// Hook para detectar se o usuário está navegando por teclado
export const useKeyboardUser = () => {
  const [isKeyboardUser, setIsKeyboardUser] = useState(false);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Tab') {
        setIsKeyboardUser(true);
      }
    };

    const handleMouseDown = () => {
      setIsKeyboardUser(false);
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousedown', handleMouseDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleMouseDown);
    };
  }, []);

  return isKeyboardUser;
};

// Hook para anúncios de screen reader
export const useScreenReader = () => {
  const [announcements, setAnnouncements] = useState([]);
  const announcementRef = useRef(null);

  const announce = (message, priority = 'polite') => {
    const id = Date.now();
    const announcement = { id, message, priority };
    
    setAnnouncements(prev => [...prev, announcement]);

    // Remover anúncio após um tempo
    setTimeout(() => {
      setAnnouncements(prev => prev.filter(a => a.id !== id));
    }, 5000);
  };

  const announceError = (message) => announce(message, 'assertive');
  const announceSuccess = (message) => announce(message, 'polite');
  const announceInfo = (message) => announce(message, 'polite');

  return {
    announce,
    announceError,
    announceSuccess,
    announceInfo,
    announcements,
    announcementRef
  };
};

// Hook para gerenciar preferências de acessibilidade
export const useAccessibilityPreferences = () => {
  const [preferences, setPreferences] = useState(() => {
    const saved = localStorage.getItem('accessibility-preferences');
    return saved ? JSON.parse(saved) : {
      reducedMotion: false,
      highContrast: false,
      largeText: false,
      screenReaderOptimized: false,
      keyboardNavigation: true
    };
  });

  useEffect(() => {
    localStorage.setItem('accessibility-preferences', JSON.stringify(preferences));
    
    // Aplicar preferências ao documento
    document.documentElement.classList.toggle('reduced-motion', preferences.reducedMotion);
    document.documentElement.classList.toggle('high-contrast', preferences.highContrast);
    document.documentElement.classList.toggle('large-text', preferences.largeText);
    document.documentElement.classList.toggle('screen-reader-optimized', preferences.screenReaderOptimized);
  }, [preferences]);

  const updatePreference = (key, value) => {
    setPreferences(prev => ({ ...prev, [key]: value }));
  };

  return { preferences, updatePreference };
};

// Hook para detectar preferências do sistema
export const useSystemPreferences = () => {
  const [systemPreferences, setSystemPreferences] = useState({
    reducedMotion: false,
    highContrast: false,
    darkMode: false
  });

  useEffect(() => {
    // Detectar preferência de movimento reduzido
    const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const updateReducedMotion = () => setSystemPreferences(prev => ({
      ...prev,
      reducedMotion: reducedMotionQuery.matches
    }));
    updateReducedMotion();
    reducedMotionQuery.addEventListener('change', updateReducedMotion);

    // Detectar preferência de alto contraste
    const highContrastQuery = window.matchMedia('(prefers-contrast: high)');
    const updateHighContrast = () => setSystemPreferences(prev => ({
      ...prev,
      highContrast: highContrastQuery.matches
    }));
    updateHighContrast();
    highContrastQuery.addEventListener('change', updateHighContrast);

    // Detectar preferência de modo escuro
    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const updateDarkMode = () => setSystemPreferences(prev => ({
      ...prev,
      darkMode: darkModeQuery.matches
    }));
    updateDarkMode();
    darkModeQuery.addEventListener('change', updateDarkMode);

    return () => {
      reducedMotionQuery.removeEventListener('change', updateReducedMotion);
      highContrastQuery.removeEventListener('change', updateHighContrast);
      darkModeQuery.removeEventListener('change', updateDarkMode);
    };
  }, []);

  return systemPreferences;
};

// Hook para skip links
export const useSkipLinks = (links = []) => {
  const [isVisible, setIsVisible] = useState(false);
  const [currentLinkIndex, setCurrentLinkIndex] = useState(0);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Tab' && !event.shiftKey && !isVisible) {
        setIsVisible(true);
      }
    };

    const handleFocusOut = (event) => {
      if (!event.relatedTarget || !event.relatedTarget.closest('.skip-links')) {
        setIsVisible(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('focusout', handleFocusOut);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('focusout', handleFocusOut);
    };
  }, [isVisible]);

  const skipTo = (targetId) => {
    const target = document.getElementById(targetId);
    if (target) {
      target.focus();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    setIsVisible(false);
  };

  return {
    isVisible,
    currentLinkIndex,
    setCurrentLinkIndex,
    skipTo
  };
};

// Componente para anúncios de screen reader
export const ScreenReaderAnnouncements = ({ announcements }) => {
  return (
    <div className="sr-only">
      {announcements.map(announcement => (
        <div
          key={announcement.id}
          aria-live={announcement.priority}
          aria-atomic="true"
        >
          {announcement.message}
        </div>
      ))}
    </div>
  );
};

// Componente para skip links
export const SkipLinks = ({ links, isVisible }) => {
  if (!isVisible || !links.length) return null;

  return (
    <div className="skip-links fixed top-0 left-0 z-50 bg-blue-600 text-white p-2 rounded-br-lg">
      <ul className="space-y-1">
        {links.map((link, index) => (
          <li key={index}>
            <a
              href={`#${link.targetId}`}
              className="block px-2 py-1 text-sm hover:bg-blue-700 rounded focus:outline-none focus:ring-2 focus:ring-white"
              onClick={(e) => {
                e.preventDefault();
                const target = document.getElementById(link.targetId);
                if (target) {
                  target.focus();
                  target.scrollIntoView({ behavior: 'smooth' });
                }
              }}
            >
              {link.label}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};

// Utilitários de acessibilidade
export const a11yUtils = {
  // Gerar ID único para associações aria
  generateId: (prefix = 'a11y') => `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,

  // Verificar se elemento está visível
  isElementVisible: (element) => {
    if (!element) return false;
    const rect = element.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  },

  // Encontrar próximo elemento focável
  getNextFocusableElement: (currentElement, direction = 'forward') => {
    const focusableElements = document.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const elements = Array.from(focusableElements);
    const currentIndex = elements.indexOf(currentElement);
    
    if (direction === 'forward') {
      return elements[currentIndex + 1] || elements[0];
    } else {
      return elements[currentIndex - 1] || elements[elements.length - 1];
    }
  },

  // Verificar se usuário prefere movimento reduzido
  prefersReducedMotion: () => {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  },

  // Anunciar mudança de página para screen readers
  announcePageChange: (pageTitle) => {
    document.title = pageTitle;
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'assertive');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = `Navegou para ${pageTitle}`;
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }
};

