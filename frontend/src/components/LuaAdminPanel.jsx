import React, { useState, useEffect } from 'react';
import { Bot, Clock, Calendar, Users, Settings, BarChart3, FileText, Zap, Bell } from 'lucide-react';
import { Button } from '@/components/ui/button.jsx';
import { Input } from '@/components/ui/input.jsx';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx';
import { Badge } from '@/components/ui/badge.jsx';

const LuaAdminPanel = () => {
  const [schedulerConfig, setSchedulerConfig] = useState({});
  const [automaticReports, setAutomaticReports] = useState([]);
  const [insights, setInsights] = useState([]);
  const [adminInputs, setAdminInputs] = useState({
    horario_almoco: { entrada: '12:00', saida: '13:00' },
    dia_pagamento: { dia: '5' },
    folga_funcionario: { funcionario: '', data_folga: '' },
    escala: { funcionario: '', horario: '' },
    contato_dono: { 
      email: '', 
      telefone: '', 
      notif_estoque: true, 
      notif_aniversarios: true, 
      notif_vendas: false, 
      notif_financeiro: true 
    }
  });

  useEffect(() => {
    fetchSchedulerConfig();
    fetchAutomaticReports();
    fetchInsights();
  }, []);

  const fetchSchedulerConfig = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/lua/scheduler_config');
      const data = await response.json();
      if (data.status === 'success') {
        setSchedulerConfig(data.config);
      }
    } catch (error) {
      console.error('Erro ao buscar configuração do scheduler:', error);
    }
  };

  const fetchAutomaticReports = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/lua/automatic_reports');
      const data = await response.json();
      if (data.status === 'success') {
        setAutomaticReports(data.reports);
      }
    } catch (error) {
      console.error('Erro ao buscar relatórios automáticos:', error);
    }
  };

  const fetchInsights = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/lua/insights');
      const data = await response.json();
      if (data.status === 'success') {
        setInsights(data.insights);
      }
    } catch (error) {
      console.error('Erro ao buscar insights:', error);
    }
  };

  const updateSchedulerConfig = async (newConfig) => {
    try {
      const response = await fetch('http://localhost:5000/api/lua/scheduler_config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ config: newConfig })
      });
      const data = await response.json();
      if (data.status === 'success') {
        setSchedulerConfig(data.config);
        alert('Configuração atualizada com sucesso!');
      }
    } catch (error) {
      console.error('Erro ao atualizar configuração:', error);
      alert('Erro ao atualizar configuração');
    }
  };

  const submitAdminInput = async (inputType) => {
    try {
      const response = await fetch('http://localhost:5000/api/lua/admin_input', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          data: {
            type: inputType,
            ...adminInputs[inputType]
          }
        })
      });
      const data = await response.json();
      if (data.status === 'success') {
        alert(data.response);
        // Limpar campos após sucesso
        if (inputType === 'folga_funcionario' || inputType === 'escala') {
          setAdminInputs(prev => ({
            ...prev,
            [inputType]: { funcionario: '', data_folga: '', horario: '' }
          }));
        }
      }
    } catch (error) {
      console.error('Erro ao enviar dados administrativos:', error);
      alert('Erro ao processar dados administrativos');
    }
  };

  const handleInputChange = (inputType, field, value) => {
    setAdminInputs(prev => ({
      ...prev,
      [inputType]: {
        ...prev[inputType],
        [field]: value
      }
    }));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Bot className="h-8 w-8 text-blue-400" />
        <div>
          <h2 className="text-3xl font-bold text-white">Painel Administrativo da Lua</h2>
          <p className="text-gray-400">Configure e monitore a IA da Joalheria Antonio Rabelo</p>
        </div>
      </div>

      <Tabs defaultValue="insights" className="w-full">
        <TabsList className="grid w-full grid-cols-4 bg-gray-800">
          <TabsTrigger value="insights" className="text-white data-[state=active]:bg-blue-600">
            <BarChart3 className="h-4 w-4 mr-2" />
            Insights
          </TabsTrigger>
          <TabsTrigger value="reports" className="text-white data-[state=active]:bg-blue-600">
            <FileText className="h-4 w-4 mr-2" />
            Relatórios
          </TabsTrigger>
          <TabsTrigger value="scheduler" className="text-white data-[state=active]:bg-blue-600">
            <Clock className="h-4 w-4 mr-2" />
            Scheduler
          </TabsTrigger>
          <TabsTrigger value="admin" className="text-white data-[state=active]:bg-blue-600">
            <Settings className="h-4 w-4 mr-2" />
            Configurações
          </TabsTrigger>
        </TabsList>

        <TabsContent value="insights" className="space-y-4">
          <Card className="border-gray-600 bg-gray-900">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Zap className="h-5 w-5 text-yellow-400" />
                Insights Estratégicos da Lua
              </CardTitle>
              <CardDescription className="text-gray-400">
                Análises e recomendações baseadas nos dados da joalheria
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                {insights.map((insight, index) => (
                  <div key={index} className="p-4 bg-gray-800 rounded-lg border border-gray-700">
                    <p className="text-white">{insight}</p>
                  </div>
                ))}
                {insights.length === 0 && (
                  <p className="text-gray-400 text-center py-8">
                    Nenhum insight disponível no momento. A Lua está analisando os dados...
                  </p>
                )}
              </div>
              <Button 
                onClick={fetchInsights}
                className="mt-4 bg-blue-600 hover:bg-blue-700"
              >
                Atualizar Insights
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reports" className="space-y-4">
          <Card className="border-gray-600 bg-gray-900">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <FileText className="h-5 w-5 text-green-400" />
                Relatórios Automáticos
              </CardTitle>
              <CardDescription className="text-gray-400">
                Relatórios gerados automaticamente pela Lua
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {automaticReports.map((report, index) => (
                  <div key={index} className="p-4 bg-gray-800 rounded-lg border border-gray-700">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="text-white font-semibold">{report.tipo}</h4>
                      <Badge variant="outline" className="text-gray-300 border-gray-600">
                        {new Date(report.timestamp).toLocaleString()}
                      </Badge>
                    </div>
                    <p className="text-gray-300">{report.resumo}</p>
                  </div>
                ))}
                {automaticReports.length === 0 && (
                  <p className="text-gray-400 text-center py-8">
                    Nenhum relatório automático gerado ainda.
                  </p>
                )}
              </div>
              <Button 
                onClick={fetchAutomaticReports}
                className="mt-4 bg-green-600 hover:bg-green-700"
              >
                Atualizar Relatórios
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="scheduler" className="space-y-4">
          <Card className="border-gray-600 bg-gray-900">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Clock className="h-5 w-5 text-orange-400" />
                Configuração do Scheduler
              </CardTitle>
              <CardDescription className="text-gray-400">
                Configure horários para geração automática de relatórios
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                {Object.entries(schedulerConfig).map(([reportType, config]) => (
                  <div key={reportType} className="p-4 bg-gray-800 rounded-lg border border-gray-700">
                    <h4 className="text-white font-semibold mb-2 capitalize">
                      {reportType.replace('relatorio_', '').replace('_', ' ')}
                    </h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-gray-300 text-sm">Horário</label>
                        <Input
                          type="time"
                          value={config.hora}
                          onChange={(e) => {
                            const newConfig = {
                              ...schedulerConfig,
                              [reportType]: { ...config, hora: e.target.value }
                            };
                            setSchedulerConfig(newConfig);
                          }}
                          className="bg-gray-700 border-gray-600 text-white"
                        />
                      </div>
                      <div>
                        <label className="text-gray-300 text-sm">Frequência</label>
                        <select
                          value={config.frequencia}
                          onChange={(e) => {
                            const newConfig = {
                              ...schedulerConfig,
                              [reportType]: { ...config, frequencia: e.target.value }
                            };
                            setSchedulerConfig(newConfig);
                          }}
                          className="w-full p-2 bg-gray-700 border border-gray-600 text-white rounded-md"
                        >
                          <option value="diario">Diário</option>
                          <option value="semanal">Semanal</option>
                        </select>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <Button 
                onClick={() => updateSchedulerConfig(schedulerConfig)}
                className="mt-4 bg-orange-600 hover:bg-orange-700"
              >
                Salvar Configurações
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="admin" className="space-y-4">
          <div className="grid gap-4">
            {/* Horário de Almoço */}
            <Card className="border-gray-600 bg-gray-900">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Clock className="h-5 w-5 text-blue-400" />
                  Horário de Almoço
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-gray-300 text-sm">Entrada</label>
                    <Input
                      type="time"
                      value={adminInputs.horario_almoco.entrada}
                      onChange={(e) => handleInputChange('horario_almoco', 'entrada', e.target.value)}
                      className="bg-gray-700 border-gray-600 text-white"
                    />
                  </div>
                  <div>
                    <label className="text-gray-300 text-sm">Saída</label>
                    <Input
                      type="time"
                      value={adminInputs.horario_almoco.saida}
                      onChange={(e) => handleInputChange('horario_almoco', 'saida', e.target.value)}
                      className="bg-gray-700 border-gray-600 text-white"
                    />
                  </div>
                </div>
                <Button 
                  onClick={() => submitAdminInput('horario_almoco')}
                  className="mt-4 bg-blue-600 hover:bg-blue-700"
                >
                  Atualizar Horário
                </Button>
              </CardContent>
            </Card>

            {/* Dia de Pagamento */}
            <Card className="border-gray-600 bg-gray-900">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-green-400" />
                  Dia de Pagamento
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div>
                  <label className="text-gray-300 text-sm">Dia do mês</label>
                  <Input
                    type="number"
                    min="1"
                    max="31"
                    value={adminInputs.dia_pagamento.dia}
                    onChange={(e) => handleInputChange('dia_pagamento', 'dia', e.target.value)}
                    className="bg-gray-700 border-gray-600 text-white"
                    placeholder="Ex: 5"
                  />
                </div>
                <Button 
                  onClick={() => submitAdminInput('dia_pagamento')}
                  className="mt-4 bg-green-600 hover:bg-green-700"
                >
                  Definir Dia de Pagamento
                </Button>
              </CardContent>
            </Card>

            {/* Folga de Funcionário */}
            <Card className="border-gray-600 bg-gray-900">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Users className="h-5 w-5 text-yellow-400" />
                  Registrar Folga
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-gray-300 text-sm">Funcionário</label>
                    <Input
                      value={adminInputs.folga_funcionario.funcionario}
                      onChange={(e) => handleInputChange('folga_funcionario', 'funcionario', e.target.value)}
                      className="bg-gray-700 border-gray-600 text-white"
                      placeholder="Nome do funcionário"
                    />
                  </div>
                  <div>
                    <label className="text-gray-300 text-sm">Data da Folga</label>
                    <Input
                      type="date"
                      value={adminInputs.folga_funcionario.data_folga}
                      onChange={(e) => handleInputChange('folga_funcionario', 'data_folga', e.target.value)}
                      className="bg-gray-700 border-gray-600 text-white"
                    />
                  </div>
                </div>
                <Button 
                  onClick={() => submitAdminInput('folga_funcionario')}
                  className="mt-4 bg-yellow-600 hover:bg-yellow-700"
                >
                  Registrar Folga
                </Button>
              </CardContent>
            </Card>

            {/* Escala de Funcionário */}
            <Card className="border-gray-600 bg-gray-900">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Settings className="h-5 w-5 text-purple-400" />
                  Definir Escala
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-gray-300 text-sm">Funcionário</label>
                    <Input
                      value={adminInputs.escala.funcionario}
                      onChange={(e) => handleInputChange('escala', 'funcionario', e.target.value)}
                      className="bg-gray-700 border-gray-600 text-white"
                      placeholder="Nome do funcionário"
                    />
                  </div>
                  <div>
                    <label className="text-gray-300 text-sm">Horário</label>
                    <Input
                      value={adminInputs.escala.horario}
                      onChange={(e) => handleInputChange('escala', 'horario', e.target.value)}
                      className="bg-gray-700 border-gray-600 text-white"
                      placeholder="Ex: 08:00 às 17:00"
                    />
                  </div>
                </div>
                <Button 
                  onClick={() => submitAdminInput('escala')}
                  className="mt-4 bg-purple-600 hover:bg-purple-700"
                >
                  Definir Escala
                </Button>
              </CardContent>
            </Card>

            {/* Contato do Dono para Notificações */}
            <Card className="border-gray-600 bg-gray-900">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <Bell className="h-5 w-5 text-red-400" />
                  Contato para Notificações
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Configure e-mail e telefone para receber notificações automáticas sobre estoque, aniversários e alertas importantes
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 gap-4">
                  <div>
                    <label className="text-gray-300 text-sm">E-mail do Dono</label>
                    <Input
                      type="email"
                      value={adminInputs.contato_dono?.email || ''}
                      onChange={(e) => handleInputChange('contato_dono', 'email', e.target.value)}
                      className="bg-gray-700 border-gray-600 text-white"
                      placeholder="antonio@joalheriarabelo.com"
                    />
                  </div>
                  <div>
                    <label className="text-gray-300 text-sm">Telefone/WhatsApp</label>
                    <Input
                      type="tel"
                      value={adminInputs.contato_dono?.telefone || ''}
                      onChange={(e) => handleInputChange('contato_dono', 'telefone', e.target.value)}
                      className="bg-gray-700 border-gray-600 text-white"
                      placeholder="(11) 99999-9999"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="notif_estoque"
                        checked={adminInputs.contato_dono?.notif_estoque || false}
                        onChange={(e) => handleInputChange('contato_dono', 'notif_estoque', e.target.checked)}
                        className="rounded border-gray-600 bg-gray-700"
                      />
                      <label htmlFor="notif_estoque" className="text-gray-300 text-sm">
                        Alertas de Estoque
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="notif_aniversarios"
                        checked={adminInputs.contato_dono?.notif_aniversarios || false}
                        onChange={(e) => handleInputChange('contato_dono', 'notif_aniversarios', e.target.checked)}
                        className="rounded border-gray-600 bg-gray-700"
                      />
                      <label htmlFor="notif_aniversarios" className="text-gray-300 text-sm">
                        Aniversários de Clientes
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="notif_vendas"
                        checked={adminInputs.contato_dono?.notif_vendas || false}
                        onChange={(e) => handleInputChange('contato_dono', 'notif_vendas', e.target.checked)}
                        className="rounded border-gray-600 bg-gray-700"
                      />
                      <label htmlFor="notif_vendas" className="text-gray-300 text-sm">
                        Relatórios de Vendas
                      </label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="notif_financeiro"
                        checked={adminInputs.contato_dono?.notif_financeiro || false}
                        onChange={(e) => handleInputChange('contato_dono', 'notif_financeiro', e.target.checked)}
                        className="rounded border-gray-600 bg-gray-700"
                      />
                      <label htmlFor="notif_financeiro" className="text-gray-300 text-sm">
                        Alertas Financeiros
                      </label>
                    </div>
                  </div>
                </div>
                <Button 
                  onClick={() => submitAdminInput('contato_dono')}
                  className="mt-4 bg-red-600 hover:bg-red-700"
                >
                  Salvar Contato
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default LuaAdminPanel;

