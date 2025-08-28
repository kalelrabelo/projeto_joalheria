import React, { useState, useEffect } from 'react';
import { Pencil, Trash2, Plus, Search, Calendar, User, DollarSign, FileText, ChevronLeft, ChevronRight, Filter, Printer, Receipt } from 'lucide-react';

function Vales() {
  const [vales, setVales] = useState([]);
  const [valeEditando, setValeEditando] = useState(null);
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [termoBusca, setTermoBusca] = useState('');
  const [valesFiltrados, setValesFiltrados] = useState([]);
  const [paginaAtual, setPaginaAtual] = useState(1);
  const [valesPorPagina] = useState(20);
  const [filtroMes, setFiltroMes] = useState('');
  const [filtroAno, setFiltroAno] = useState('');
  const [filtroFuncionario, setFiltroFuncionario] = useState('');
  const [filtroTipo, setFiltroTipo] = useState('');
  const [funcionarios, setFuncionarios] = useState([]);

  const indiceUltimoVale = paginaAtual * valesPorPagina;
  const indicePrimeiroVale = indiceUltimoVale - valesPorPagina;
  const valesAtuais = valesFiltrados.slice(indicePrimeiroVale, indiceUltimoVale);
  const totalPaginas = Math.ceil(valesFiltrados.length / valesPorPagina);

  const anosDisponiveis = [...new Set(vales.map(v => new Date(v.date).getFullYear()))].filter(ano => !isNaN(ano) && ano > 2005).sort((a, b) => b - a);
  const funcionariosDisponiveis = [...new Set(vales.map(v => v.employee_name))].sort();
  const tiposDisponiveis = [...new Set(vales.map(v => v.description ? (v.description.toLowerCase().includes('vale') ? 'Vale' : 'Outros') : 'Outros'))].sort();

  const mesesNomes = [
    '', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
  ];

  useEffect(() => {
    fetchVales();
    fetchFuncionarios();
  }, []);

  useEffect(() => {
    let filtrados = vales.filter(vale => {
      const valeDate = new Date(vale.date);
      const matchBusca = vale.employee_name.toLowerCase().includes(termoBusca.toLowerCase()) ||
                        vale.description.toLowerCase().includes(termoBusca.toLowerCase());
      const matchMes = !filtroMes || (valeDate.getMonth() + 1).toString() === filtroMes;
      const matchAno = !filtroAno || valeDate.getFullYear().toString() === filtroAno;
      const matchFuncionario = !filtroFuncionario || vale.employee_name === filtroFuncionario;
      const matchTipo = !filtroTipo || getTipoVale(vale.description, '') === filtroTipo;
      
      return matchBusca && matchMes && matchAno && matchFuncionario && matchTipo;
    });
    
    setValesFiltrados(filtrados);
    setPaginaAtual(1);
  }, [termoBusca, filtroMes, filtroAno, filtroFuncionario, filtroTipo, vales]);

  const fetchVales = async () => {
    try {
      const response = await fetch('/api/vales');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      // Garantir que temos um array
      const valesData = data.data || data || [];
      setVales(Array.isArray(valesData) ? valesData : []);
    } catch (error) {
      console.error("Erro ao buscar vales:", error);
      // Fallback com array vazio
      setVales([]);
    }
  };

  const fetchFuncionarios = async () => {
    try {
      const response = await fetch('/api/employees');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setFuncionarios(data);
    } catch (error) {
      console.error("Erro ao buscar funcionários:", error);
    }
  };

  const formatarMoeda = (valor) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  };

  const formatarData = (data) => {
    if (!data) return 'Data não informada';
    try {
      return new Date(data).toLocaleDateString('pt-BR');
    } catch {
      return data;
    }
  };

  const getTipoVale = (descricao) => {
    const desc = descricao.toLowerCase();
    if (desc.includes('vale')) return 'Vale';
    if (desc.includes('salário')) return 'Salário';
    if (desc.includes('alimentação')) return 'Alimentação';
    if (desc.includes('combustivel')) return 'Combustível';
    if (desc.includes('rescisão')) return 'Rescisão';
    return 'Outros';
  };

  const getCorTipo = (tipo) => {
    switch (tipo.toLowerCase()) {
      case 'vale': return 'bg-blue-100 text-blue-800';
      case 'salário': return 'bg-green-100 text-green-800';
      case 'alimentação': return 'bg-orange-100 text-orange-800';
      case 'combustível': return 'bg-red-100 text-red-800';
      case 'operacional': return 'bg-purple-100 text-purple-800';
      case 'retirada': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleSalvarVale = async (vale) => {
    try {
      const method = vale.id ? 'PUT' : 'POST';
      const url = vale.id ? `/api/vales/${vale.id}` : '/api/vales';
      
      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          employee_id: vale.employee_id,
          amount: parseFloat(vale.amount),
          date: vale.date,
          description: vale.description,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      await fetchVales(); // Recarrega os vales após salvar
      setValeEditando(null);
      setMostrarFormulario(false);
    } catch (error) {
      console.error("Erro ao salvar vale:", error);
      alert(`Erro ao salvar vale: ${error.message}`);
    }
  };

  const handleExcluirVale = async (id) => {
    if (window.confirm("Tem certeza que deseja excluir este vale?")) {
      try {
        const response = await fetch(`/api/vales/${id}`, {
          method: 'DELETE',
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        await fetchVales(); // Recarrega os vales após excluir
      } catch (error) {
        console.error("Erro ao excluir vale:", error);
        alert(`Erro ao excluir vale: ${error.message}`);
      }
    }
  };

  const handleNovoVale = () => {
    setValeEditando(null);
    setMostrarFormulario(true);
  };

  const handlePaginaAnterior = () => {
    setPaginaAtual(prev => Math.max(prev - 1, 1));
  };

  const handleProximaPagina = () => {
    setPaginaAtual(prev => Math.min(prev + 1, totalPaginas));
  };

  const handleImprimirVale = (vale) => {
    const conteudoImpressao = `
      <html>
        <head>
          <title>Comprovante de Vale - ${vale.employee_name}</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .info { margin-bottom: 20px; }
            .table { width: 100%; border-collapse: collapse; }
            .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            .table th { background-color: #f2f2f2; }
            .assinatura { margin-top: 50px; }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>COMPROVANTE DE VALE</h1>
            <h2>Antônio Rabelo</h2>
          </div>
          
          <div class="info">
            <p><strong>Funcionário:</strong> ${vale.employee_name}</p>
            <p><strong>Data:</strong> ${formatarData(vale.date)}</p>
            <p><strong>Tipo:</strong> ${getTipoVale(vale.description)}</p>
            <p><strong>Descrição:</strong> ${vale.description}</p>
          </div>
          
          <table class="table">
            <tr><th>Valor do Vale</th><td>${formatarMoeda(vale.amount)}</td></tr>
          </table>
          
          <div class="assinatura">
            <p>_________________________</p>
            <p>Assinatura do Funcionário</p>
            <br>
            <p>_________________________</p>
            <p>Assinatura do Responsável</p>
          </div>
        </body>
      </html>
    `;
    
    const janelaImpressao = window.open('', '_blank');
    janelaImpressao.document.write(conteudoImpressao);
    janelaImpressao.document.close();
    janelaImpressao.print();
  };

  const limparFiltros = () => {
    setFiltroMes('');
    setFiltroAno('');
    setFiltroFuncionario('');
    setFiltroTipo('');
    setTermoBusca('');
  };

  const calcularTotalVales = () => {
    return valesFiltrados.reduce((total, vale) => total + vale.amount, 0);
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Gestão de Vales</h2>
          <p className="text-gray-600">Gerenciamento de {valesFiltrados.length} registros de vales</p>
          <p className="text-sm text-blue-600 font-semibold">
            Total em vales: {formatarMoeda(calcularTotalVales())}
          </p>
        </div>
        <button
          onClick={handleNovoVale}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
        >
          <Plus size={20} />
          Novo Vale
        </button>
      </div>

      {/* Filtros */}
      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter size={20} className="text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Filtros</h3>
          <button
            onClick={limparFiltros}
            className="ml-auto text-sm text-blue-600 hover:text-blue-800"
          >
            Limpar Filtros
          </button>
        </div>
        
        <div className="grid md:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Buscar</label>
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Funcionário ou descrição..."
                value={termoBusca}
                onChange={(e) => setTermoBusca(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Mês</label>
            <select
              value={filtroMes}
              onChange={(e) => setFiltroMes(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos os meses</option>
              {mesesNomes.slice(1).map((mes, index) => (
                <option key={index + 1} value={index + 1}>{mes}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Ano</label>
            <select
              value={filtroAno}
              onChange={(e) => setFiltroAno(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos os anos</option>
              {anosDisponiveis.map(ano => (
                <option key={ano} value={ano}>{ano}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Funcionário</label>
            <select
              value={filtroFuncionario}
              onChange={(e) => setFiltroFuncionario(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos os funcionários</option>
              {funcionarios.map(funcionario => (
                <option key={funcionario.id} value={funcionario.name}>{funcionario.name}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
            <select
              value={filtroTipo}
              onChange={(e) => setFiltroTipo(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos os tipos</option>
              {tiposDisponiveis.map(tipo => (
                <option key={tipo} value={tipo}>{tipo}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Informações de paginação */}
      <div className="mb-4 text-sm text-gray-600">
        Mostrando {indicePrimeiroVale + 1} a {Math.min(indiceUltimoVale, valesFiltrados.length)} de {valesFiltrados.length} registros
      </div>

      {/* Tabela de Vales */}
      <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Funcionário</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Valor</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descrição</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {valesAtuais.map((vale) => (
              <tr key={vale.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{vale.id}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{vale.employee_name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatarMoeda(vale.amount)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatarData(vale.date)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{vale.description}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getCorTipo(getTipoVale(vale.description))}`}>
                    {getTipoVale(vale.description)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => {
                        setValeEditando(vale);
                        setMostrarFormulario(true);
                      }}
                      className="text-blue-600 hover:text-blue-900"
                      title="Editar Vale"
                    >
                      <Pencil size={18} />
                    </button>
                    <button
                      onClick={() => handleExcluirVale(vale.id)}
                      className="text-red-600 hover:text-red-900"
                      title="Excluir Vale"
                    >
                      <Trash2 size={18} />
                    </button>
                    <button
                      onClick={() => handleImprimirVale(vale)}
                      className="text-green-600 hover:text-green-900"
                      title="Imprimir Comprovante"
                    >
                      <Printer size={18} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {valesFiltrados.length === 0 && (
        <div className="text-center py-12">
          <DollarSign size={48} className="mx-auto text-gray-400 mb-4" />
          <p className="text-gray-500">Nenhum vale encontrado</p>
        </div>
      )}

      {/* Controles de paginação */}
      {totalPaginas > 1 && (
        <div className="flex justify-center items-center gap-4 mt-6">
          <button
            onClick={handlePaginaAnterior}
            disabled={paginaAtual === 1}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft size={16} />
            Anterior
          </button>
          
          <span className="text-sm text-gray-600">
            Página {paginaAtual} de {totalPaginas}
          </span>
          
          <button
            onClick={handleProximaPagina}
            disabled={paginaAtual === totalPaginas}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Próxima
            <ChevronRight size={16} />
          </button>
        </div>
      )}

      {/* Formulário de Novo/Editar Vale */}
      {mostrarFormulario && (
        <FormularioVale
          vale={valeEditando}
          onSave={handleSalvarVale}
          onCancel={() => setMostrarFormulario(false)}
          funcionarios={funcionarios}
        />
      )}
    </div>
  );
}

function FormularioVale({ vale, onSave, onCancel, funcionarios }) {
  const [formData, setFormData] = useState({
    employee_id: vale ? vale.employee_id : '',
    amount: vale ? vale.amount : '',
    date: vale ? vale.date.split('T')[0] : new Date().toISOString().split('T')[0],
    description: vale ? vale.description : '',
  });

  useEffect(() => {
    if (vale) {
      setFormData({
        employee_id: vale.employee_id,
        amount: vale.amount,
        date: vale.date.split('T')[0],
        description: vale.description,
      });
    } else {
      setFormData({
        employee_id: '',
        amount: '',
        date: new Date().toISOString().split('T')[0],
        description: '',
      });
    }
  }, [vale]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({ ...vale, ...formData });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-full overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">{vale ? 'Editar Vale' : 'Novo Vale'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="employee_id" className="block text-sm font-medium text-gray-700">Funcionário</label>
            <select
              id="employee_id"
              name="employee_id"
              value={formData.employee_id}
              onChange={handleChange}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              required
            >
              <option value="">Selecione um funcionário</option>
              {funcionarios.map(func => (
                <option key={func.id} value={func.id}>{func.name}</option>
              ))}
            </select>
          </div>
          <div className="mb-4">
            <label htmlFor="amount" className="block text-sm font-medium text-gray-700">Valor</label>
            <input
              type="number"
              id="amount"
              name="amount"
              value={formData.amount}
              onChange={handleChange}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              step="0.01"
              required
            />
          </div>
          <div className="mb-4">
            <label htmlFor="date" className="block text-sm font-medium text-gray-700">Data</label>
            <input
              type="date"
              id="date"
              name="date"
              value={formData.date}
              onChange={handleChange}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              required
            />
          </div>
          <div className="mb-4">
            <label htmlFor="description" className="block text-sm font-medium text-gray-700">Descrição</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows="3"
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            ></textarea>
          </div>
          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Salvar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default Vales;


