import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Package, Users, DollarSign, AlertTriangle, Calendar, Target } from 'lucide-react';

const DashboardInteligente = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastCommand, setLastCommand] = useState('');

  useEffect(() => {
    // Listener para comandos da Lua
    const handleLuaDashboardUpdate = (event) => {
      const { type, data, explanation, command } = event.detail;
      setDashboardData({ type, data, explanation });
      setLastCommand(command);
      setIsLoading(false);
    };

    window.addEventListener('updateDashboard', handleLuaDashboardUpdate);
    
    // Dashboard padrão inicial
    loadDefaultDashboard();

    return () => {
      window.removeEventListener('updateDashboard', handleLuaDashboardUpdate);
    };
  }, []);

  const loadDefaultDashboard = () => {
    setDashboardData({
      type: 'overview',
      data: {
        title: 'Visão Geral da Joalheria',
        subtitle: 'Use comandos de voz para personalizar este dashboard',
        metrics: [
          { label: 'Faturamento Mensal', value: 'R$ 15.420,00', trend: 'up', change: '+12%' },
          { label: 'Encomendas Ativas', value: '23', trend: 'up', change: '+5' },
          { label: 'Funcionários Ativos', value: '6', trend: 'stable', change: '0' },
          { label: 'Produtos em Estoque', value: '156', trend: 'down', change: '-8' }
        ]
      },
      explanation: 'Dashboard padrão com métricas gerais. Use comandos de voz para focar em informações específicas.'
    });
  };

  const renderLucroMensal = () => {
    const { data } = dashboardData;
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-green-800 mb-4">
              💰 Análise de Lucro Mensal
            </h1>
            <p className="text-green-600 text-lg">{lastCommand}</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Lucro Principal */}
            <div className="bg-white rounded-2xl shadow-2xl p-8 border-l-8 border-green-500">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">Lucro Líquido</h2>
                  <p className="text-gray-600">Agosto 2025</p>
                </div>
                <div className="bg-green-100 p-4 rounded-full">
                  <TrendingUp className="text-green-600" size={32} />
                </div>
              </div>
              <div className="text-5xl font-bold text-green-600 mb-4">
                R$ {data.lucro_liquido.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
              </div>
              <div className="flex items-center text-green-600">
                <TrendingUp size={20} className="mr-2" />
                <span className="font-semibold">+{data.crescimento}% vs mês anterior</span>
              </div>
            </div>

            {/* Margem de Lucro */}
            <div className="bg-white rounded-2xl shadow-2xl p-8 border-l-8 border-blue-500">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-800">Margem de Lucro</h2>
                  <p className="text-gray-600">Percentual sobre vendas</p>
                </div>
                <div className="bg-blue-100 p-4 rounded-full">
                  <Target className="text-blue-600" size={32} />
                </div>
              </div>
              <div className="text-5xl font-bold text-blue-600 mb-4">
                {data.margem_lucro}%
              </div>
              <div className="text-blue-600">
                <span className="font-semibold">Meta: 35% | Atual: {data.margem_lucro}%</span>
              </div>
            </div>
          </div>

          {/* Breakdown do Lucro */}
          <div className="bg-white rounded-2xl shadow-2xl p-8 mb-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">📊 Composição do Lucro</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-6 bg-green-50 rounded-xl">
                <div className="text-3xl font-bold text-green-600 mb-2">
                  R$ {data.receita_total.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                </div>
                <div className="text-green-800 font-semibold">Receita Total</div>
                <div className="text-sm text-green-600 mt-2">Vendas + Serviços</div>
              </div>
              <div className="text-center p-6 bg-red-50 rounded-xl">
                <div className="text-3xl font-bold text-red-600 mb-2">
                  R$ {data.custos_total.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                </div>
                <div className="text-red-800 font-semibold">Custos Totais</div>
                <div className="text-sm text-red-600 mt-2">Material + Mão de obra</div>
              </div>
              <div className="text-center p-6 bg-yellow-50 rounded-xl">
                <div className="text-3xl font-bold text-yellow-600 mb-2">
                  R$ {data.despesas_operacionais.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                </div>
                <div className="text-yellow-800 font-semibold">Despesas Operacionais</div>
                <div className="text-sm text-yellow-600 mt-2">Salários + Aluguel + Outros</div>
              </div>
            </div>
          </div>

          {/* Explicação */}
          <div className="bg-white rounded-2xl shadow-2xl p-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-4">🧠 Análise Inteligente</h3>
            <div className="text-gray-700 text-lg leading-relaxed">
              {dashboardData.explanation}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderEncomendas = () => {
    const { data } = dashboardData;
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-blue-800 mb-4">
              📦 Encomendas de Hoje
            </h1>
            <p className="text-blue-600 text-lg">{lastCommand}</p>
          </div>

          {/* Resumo */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">{data.total}</div>
              <div className="text-blue-800 font-semibold">Total de Encomendas</div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">{data.concluidas}</div>
              <div className="text-green-800 font-semibold">Concluídas</div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-3xl font-bold text-yellow-600 mb-2">{data.em_producao}</div>
              <div className="text-yellow-800 font-semibold">Em Produção</div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-3xl font-bold text-red-600 mb-2">{data.atrasadas}</div>
              <div className="text-red-800 font-semibold">Atrasadas</div>
            </div>
          </div>

          {/* Lista de Encomendas */}
          <div className="bg-white rounded-2xl shadow-2xl p-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">📋 Detalhes das Encomendas</h3>
            <div className="space-y-4">
              {data.encomendas.map((encomenda, index) => (
                <div key={index} className={`p-6 rounded-xl border-l-4 ${
                  encomenda.status === 'concluida' ? 'border-green-500 bg-green-50' :
                  encomenda.status === 'em_producao' ? 'border-yellow-500 bg-yellow-50' :
                  'border-red-500 bg-red-50'
                }`}>
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="text-xl font-bold text-gray-800 mb-2">{encomenda.produto}</h4>
                      <p className="text-gray-600 mb-2">Cliente: {encomenda.cliente}</p>
                      <p className="text-gray-600">Prazo: {encomenda.prazo}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600 mb-2">
                        R$ {encomenda.valor.toLocaleString('pt-BR', {minimumFractionDigits: 2})}
                      </div>
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                        encomenda.status === 'concluida' ? 'bg-green-200 text-green-800' :
                        encomenda.status === 'em_producao' ? 'bg-yellow-200 text-yellow-800' :
                        'bg-red-200 text-red-800'
                      }`}>
                        {encomenda.status_texto}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Explicação */}
          <div className="bg-white rounded-2xl shadow-2xl p-8 mt-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-4">🧠 Análise do Dia</h3>
            <div className="text-gray-700 text-lg leading-relaxed">
              {dashboardData.explanation}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderDefault = () => {
    const { data } = dashboardData;
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-4">
              🎯 {data.title}
            </h1>
            <p className="text-gray-600 text-lg">{data.subtitle}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {data.metrics.map((metric, index) => (
              <div key={index} className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="text-sm text-gray-600">{metric.label}</div>
                  {metric.trend === 'up' && <TrendingUp className="text-green-500" size={20} />}
                  {metric.trend === 'down' && <TrendingDown className="text-red-500" size={20} />}
                  {metric.trend === 'stable' && <div className="w-5 h-5 bg-gray-300 rounded-full"></div>}
                </div>
                <div className="text-3xl font-bold text-gray-800 mb-2">{metric.value}</div>
                <div className={`text-sm font-semibold ${
                  metric.trend === 'up' ? 'text-green-600' :
                  metric.trend === 'down' ? 'text-red-600' : 'text-gray-600'
                }`}>
                  {metric.change}
                </div>
              </div>
            ))}
          </div>

          <div className="bg-white rounded-2xl shadow-2xl p-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-4">🎤 Como Usar</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-lg font-semibold text-blue-600 mb-3">Comandos Financeiros:</h4>
                <ul className="space-y-2 text-gray-700">
                  <li>• "Lua, me mostra o lucro do mês"</li>
                  <li>• "Lua, fluxo de caixa de hoje"</li>
                  <li>• "Lua, faturamento da semana"</li>
                </ul>
              </div>
              <div>
                <h4 className="text-lg font-semibold text-green-600 mb-3">Comandos Operacionais:</h4>
                <ul className="space-y-2 text-gray-700">
                  <li>• "Lua, encomendas de hoje"</li>
                  <li>• "Lua, produtividade dos funcionários"</li>
                  <li>• "Lua, alertas importantes"</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-xl text-gray-600">Processando comando da Lua...</p>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-xl text-gray-600">Carregando dashboard...</p>
      </div>
    );
  }

  // Renderizar baseado no tipo de dados
  switch (dashboardData.type) {
    case 'lucro':
      return renderLucroMensal();
    case 'encomendas':
      return renderEncomendas();
    default:
      return renderDefault();
  }
};

export default DashboardInteligente;

