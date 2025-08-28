import React from 'react';
import { toast } from 'sonner';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // Log do erro para monitoramento
    console.error('ErrorBoundary capturou um erro:', error, errorInfo);

    // Mostrar toast de erro
    toast.error('Ocorreu um erro inesperado. A página será recarregada automaticamente.');

    // Enviar erro para serviço de monitoramento (se configurado)
    if (import.meta.env.VITE_ERROR_REPORTING_URL) {
      this.reportError(error, errorInfo);
    }
  }

  reportError = async (error, errorInfo) => {
    try {
      await fetch(import.meta.env.VITE_ERROR_REPORTING_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          error: error.toString(),
          errorInfo: errorInfo.componentStack,
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent,
          url: window.location.href
        })
      });
    } catch (reportingError) {
      console.error('Falha ao reportar erro:', reportingError);
    }
  };

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black text-white flex items-center justify-center p-4">
          <div className="max-w-lg mx-auto text-center">
            <div className="mb-8">
              <div className="w-24 h-24 mx-auto mb-6 bg-red-500/20 rounded-full flex items-center justify-center">
                <svg className="w-12 h-12 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-white mb-4">Oops! Algo deu errado</h2>
              <p className="text-gray-400 mb-8 leading-relaxed">
                Ocorreu um erro inesperado no sistema. Nossa equipe foi notificada automaticamente. 
                Por favor, tente recarregar a página ou voltar ao início.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={this.handleReload}
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900"
              >
                Recarregar Página
              </button>
              <button
                onClick={this.handleGoHome}
                className="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 focus:ring-offset-gray-900"
              >
                Voltar ao Início
              </button>
            </div>

            {(import.meta.env.DEV || import.meta.env.VITE_DEBUG_MODE === 'true') && (
              <details className="mt-8 text-left bg-gray-800/50 rounded-lg p-4">
                <summary className="cursor-pointer text-gray-400 hover:text-white transition-colors">
                  Detalhes do erro (desenvolvimento)
                </summary>
                <div className="mt-4 space-y-4">
                  <div>
                    <h4 className="text-sm font-semibold text-red-400 mb-2">Erro:</h4>
                    <pre className="text-xs text-red-300 bg-gray-900 p-3 rounded overflow-auto">
                      {this.state.error && this.state.error.toString()}
                    </pre>
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-red-400 mb-2">Stack Trace:</h4>
                    <pre className="text-xs text-red-300 bg-gray-900 p-3 rounded overflow-auto max-h-40">
                      {this.state.errorInfo && this.state.errorInfo.componentStack}
                    </pre>
                  </div>
                </div>
              </details>
            )}

            <div className="mt-8 text-sm text-gray-500">
              <p>Se o problema persistir, entre em contato com o suporte técnico.</p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

