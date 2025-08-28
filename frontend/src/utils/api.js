// Configuração centralizada da API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Configuração padrão para requests
const defaultConfig = {
  headers: {
    'Content-Type': 'application/json',
  },
};

// Interceptor para tratamento de erros
const handleResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `HTTP Error: ${response.status}`);
  }
  return response.json();
};

// Interceptor para adicionar token de autenticação
const addAuthToken = (config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers = {
      ...config.headers,
      'Authorization': `Bearer ${token}`,
    };
  }
  return config;
};

// Função base para fazer requests
const apiRequest = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    ...defaultConfig,
    ...options,
  };

  // Adicionar token de autenticação se disponível
  addAuthToken(config);

  try {
    const response = await fetch(url, config);
    return await handleResponse(response);
  } catch (error) {
    console.error(`API Error [${options.method || 'GET'}] ${endpoint}:`, error);
    throw error;
  }
};

// Métodos HTTP específicos
export const api = {
  get: (endpoint, options = {}) => 
    apiRequest(endpoint, { ...options, method: 'GET' }),

  post: (endpoint, data, options = {}) => 
    apiRequest(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    }),

  put: (endpoint, data, options = {}) => 
    apiRequest(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  patch: (endpoint, data, options = {}) => 
    apiRequest(endpoint, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  delete: (endpoint, options = {}) => 
    apiRequest(endpoint, { ...options, method: 'DELETE' }),
};

// Funções específicas para diferentes módulos
export const funcionariosApi = {
  getAll: () => api.get('/api/employees'),
  getById: (id) => api.get(`/api/employees/${id}`),
  create: (data) => api.post('/api/employees', data),
  update: (id, data) => api.put(`/api/employees/${id}`, data),
  delete: (id) => api.delete(`/api/employees/${id}`),
};

export const joiasApi = {
  getAll: () => api.get('/api/produtos'),
  getById: (id) => api.get(`/api/produtos/${id}`),
  create: (data) => api.post('/api/produtos', data),
  update: (id, data) => api.put(`/api/produtos/${id}`, data),
  delete: (id) => api.delete(`/api/produtos/${id}`)  getEstoque: () => api.get(\"/api/produtos/estoque\"),
};

export const clientesApi =   getAll: () => api.get(\"/api/clientes\"),
  getById: (id) => api.get(`/api/clientes/${id}`)  create: (data) => api.post(\"/api/clientes\", data),
  update: (id, data) => api.put(`/api/clientes/${id}`, data),
  delete: (id) => api.delete(`/api/clientes/${id}`),
};

export const vendasApi = {
  getAll: () => api.get('/api/sales'),
  getById: (id) => api.get(`/api/sales/${id}`),
  create: (data) => api.post('/api/sales', data),
  update: (id, data) => api.put(`/api/sales/${id}`, data),
  delete: (id) => api.delete(`/api/sales/${id}`),
  getRelatorio: (periodo) => api.get(`/api/relatorios?periodo=${periodo}`),
};

export const valesApi = {
  getAll: () => api.get('/api/vales'),
  getById: (id) => api.get(`/api/vales/${id}`),
  create: (data) => api.post('/api/vales', data),
  update: (id, data) => api.put(`/api/vales/${id}`, data),
  delete: (id) => api.delete(`/api/vales/${id}`),
  getByFuncionario: (funcionarioId) => api.get(`/api/vales/funcionario/${funcionarioId}`),
};

export const caixaApi = {
  getMovimentacao: () => api.get('/api/caixa'),
  addMovimentacao: (data) => api.post('/api/caixa', data),
  getRelatorio: (periodo) => api.get(`/api/caixa/relatorio?periodo=${periodo}`),
  getSaldo: () => api.get('/api/caixa/saldo'),
};

export const luaApi = {
  chat: (data) => api.post(\"/api/ia\", data),  getMetrics: () => api.get(\"/api/ia/metrics\"  getContext: (sessionId) => api.get(`/api/ia/context/${sessionId}`),
  clearContext: (sessionId) => api.delete(`/api/ia/context/${sessionId}`),
};

export const authApi = {
  login: (credentials) => api.post('/api/auth/login', credentials),
  logout: () => api.post('/api/auth/logout'),
  refresh: () => api.post('/api/auth/refresh'),
  getProfile: () => api.get('/api/auth/profile'),
};

// Utilitários para tratamento de erros
export const handleApiError = (error, defaultMessage = 'Ocorreu um erro inesperado') => {
  console.error('API Error:', error);
  
  if (error.message.includes('Failed to fetch')) {
    return 'Erro de conexão. Verifique sua internet e tente novamente.';
  }
  
  if (error.message.includes('401')) {
    return 'Sessão expirada. Faça login novamente.';
  }
  
  if (error.message.includes('403')) {
    return 'Você não tem permissão para realizar esta ação.';
  }
  
  if (error.message.includes('404')) {
    return 'Recurso não encontrado.';
  }
  
  if (error.message.includes('500')) {
    return 'Erro interno do servidor. Tente novamente mais tarde.';
  }
  
  return error.message || defaultMessage;
};

// Hook personalizado para requests com loading e error states
export const useApiRequest = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = async (apiCall) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiCall();
      return result;
    } catch (err) {
      const errorMessage = handleApiError(err);
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { execute, loading, error };
};

export default api;

